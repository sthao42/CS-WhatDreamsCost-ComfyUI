import json
import logging
from uuid import uuid4

import torch

import comfy.model_management
from comfy_api.latest import io

from .ltx_director import (
    GuideData,
    _build_combined_audio,
    _encode_relay,
    _load_image_tensor,
)
from .ltx_auto_director import (
    MAX_AUTO_SEGMENTS,
    _empty_audio_latent,
    _normalize_lengths,
    _parse_prompts,
    _process_image_tensor,
    _strengths_for_count,
    _to_float,
    _to_int,
    _to_str,
)

log = logging.getLogger(__name__)

PARSE_MODE_ALIASES = {
    "auto": "auto",
    "\u81ea\u52a8": "auto",
    "json": "json",
    "JSON": "json",
    "\u7ed3\u6784\u5316 JSON": "json",
    "numbered_text": "numbered_text",
    "\u7f16\u53f7\u6587\u672c": "numbered_text",
}

RESIZE_METHOD_ALIASES = {
    "maintain aspect ratio": "maintain aspect ratio",
    "\u4fdd\u6301\u6bd4\u4f8b": "maintain aspect ratio",
    "stretch to fit": "stretch to fit",
    "\u62c9\u4f38\u586b\u6ee1": "stretch to fit",
    "pad": "pad",
    "\u7559\u767d\u586b\u5145": "pad",
    "crop": "crop",
    "\u88c1\u526a\u586b\u6ee1": "crop",
}


def _normalize_choice(value, aliases, default):
    return aliases.get(_to_str(value).strip(), default)


def _fallback_prompt(index: int) -> str:
    return f"\u7b2c {index + 1} \u4e2a\u5206\u955c\u4fdd\u6301\u7535\u5f71\u611f\u8fde\u7eed\u8fd0\u52a8\u3002"


def _image_segment_count(timeline):
    return len([
        seg for seg in timeline.get("segments", [])
        if seg.get("type", "image") == "image"
    ])


def _split_single_six_grid_image(storyboard_images, count, cols=3, rows=2):
    if storyboard_images is None or count <= 1:
        return storyboard_images
    if int(storyboard_images.shape[0]) != 1:
        return storyboard_images

    _, height, width, _ = storyboard_images.shape
    cell_w = max(1, int(width) // cols)
    cell_h = max(1, int(height) // rows)
    crops = []
    for idx in range(min(MAX_AUTO_SEGMENTS, count, cols * rows)):
        col = idx % cols
        row = idx // cols
        x0 = col * cell_w
        y0 = row * cell_h
        crops.append(storyboard_images[:, y0:y0 + cell_h, x0:x0 + cell_w, :])

    if not crops:
        return storyboard_images
    return torch.cat(crops, dim=0)


def _build_default_timeline(storyboard_images, llm_response, duration_frames, frame_rate,
                            segment_lengths, guide_strength, parse_mode):
    batch_count = int(storyboard_images.shape[0]) if storyboard_images is not None else 0
    prompts, json_lengths = _parse_prompts(llm_response, parse_mode)
    if batch_count == 1:
        count = min(MAX_AUTO_SEGMENTS, len(prompts) or MAX_AUTO_SEGMENTS)
    else:
        count = max(1, min(MAX_AUTO_SEGMENTS, batch_count or MAX_AUTO_SEGMENTS))
    prompts = (prompts + [_fallback_prompt(i) for i in range(count)])[:count]
    lengths = _normalize_lengths(segment_lengths, json_lengths, duration_frames, count, frame_rate)
    strengths = _strengths_for_count(guide_strength, count)

    cursor = 0
    segments = []
    for idx in range(count):
        segments.append({
            "id": uuid4().hex[:12],
            "start": int(cursor),
            "length": int(lengths[idx]),
            "prompt": prompts[idx],
            "type": "image",
            "source": "storyboard_images",
            "batch_index": idx,
            "guideStrength": float(strengths[idx]),
        })
        cursor += int(lengths[idx])

    return {"segments": segments, "audioSegments": []}


def _decode_timeline(timeline_data):
    try:
        data = json.loads(timeline_data) if timeline_data else {}
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    if not isinstance(data.get("segments"), list):
        data["segments"] = []
    if not isinstance(data.get("audioSegments"), list):
        data["audioSegments"] = []
    return data


def _prompt_for_segment(seg, index, parsed_prompts):
    prompt = _to_str(seg.get("prompt")).strip()
    if prompt:
        return prompt

    batch_index = seg.get("batch_index")
    try:
        batch_index = int(batch_index)
    except (TypeError, ValueError):
        batch_index = index

    if 0 <= batch_index < len(parsed_prompts):
        return parsed_prompts[batch_index]
    if index < len(parsed_prompts):
        return parsed_prompts[index]
    return _fallback_prompt(index)


def _contiguous_prompts_and_lengths(segments, parsed_prompts, duration_frames):
    sorted_segments = sorted(segments, key=lambda seg: float(seg.get("start", 0)))
    prompts = []
    lengths = []
    current_cursor = 0
    pending_gap = 0

    for idx, seg in enumerate(sorted_segments):
        start = max(0, int(float(seg.get("start", 0))))
        length = max(1, int(float(seg.get("length", 1))))
        if start >= duration_frames:
            break

        if start > current_cursor:
            gap_length = min(start, duration_frames) - current_cursor
            if lengths:
                lengths[-1] += gap_length
            else:
                pending_gap += gap_length

        clipped_end = min(start + length, duration_frames)
        clipped_length = max(1, clipped_end - start)
        prompts.append(_prompt_for_segment(seg, idx, parsed_prompts))
        lengths.append(clipped_length + pending_gap)
        pending_gap = 0
        current_cursor = start + length

    clamped_cursor = min(current_cursor, duration_frames)
    if lengths and clamped_cursor < duration_frames:
        lengths[-1] += duration_frames - clamped_cursor

    if not prompts:
        prompts = [_fallback_prompt(0)]
        lengths = [duration_frames]

    return " | ".join(prompts), ",".join(str(int(v)) for v in lengths)


def _load_segment_image(seg, storyboard_images, fallback_index, custom_width, custom_height,
                        resize_method, divisible_by, img_compression):
    tensor = None

    if storyboard_images is not None:
        batch_index = seg.get("batch_index")
        try:
            batch_index = int(batch_index)
        except (TypeError, ValueError):
            batch_index = fallback_index

        if 0 <= batch_index < int(storyboard_images.shape[0]):
            tensor = storyboard_images[batch_index:batch_index + 1]

    if tensor is None:
        tensor = _load_image_tensor(seg)

    return _process_image_tensor(
        tensor,
        custom_width,
        custom_height,
        resize_method,
        divisible_by,
        img_compression,
    )


def _build_guide_data(timeline, storyboard_images, duration_frames, frame_rate, guide_strength,
                      custom_width, custom_height, resize_method, divisible_by, img_compression):
    guide_data = {"images": [], "insert_frames": [], "strengths": [], "frame_rate": frame_rate}
    derived_w, derived_h = custom_width, custom_height
    strengths = _strengths_for_count(guide_strength, MAX_AUTO_SEGMENTS)
    image_segments = [
        seg for seg in timeline.get("segments", [])
        if seg.get("type", "image") == "image"
        and int(float(seg.get("start", 0))) < duration_frames
    ]
    image_segments.sort(key=lambda seg: float(seg.get("start", 0)))

    for idx, seg in enumerate(image_segments):
        has_batch = storyboard_images is not None and (
            seg.get("source") == "storyboard_images" or seg.get("batch_index") is not None
        )
        has_file = seg.get("imageFile") or seg.get("imageB64")
        if not has_batch and not has_file:
            continue

        tensor = _load_segment_image(
            seg,
            storyboard_images,
            idx,
            custom_width,
            custom_height,
            resize_method,
            divisible_by,
            img_compression,
        )
        if idx == 0:
            derived_h = int(tensor.shape[1])
            derived_w = int(tensor.shape[2])

        strength = seg.get("guideStrength")
        if strength is None:
            strength = strengths[idx] if idx < len(strengths) else 1.0

        guide_data["images"].append(tensor)
        guide_data["insert_frames"].append(int(float(seg.get("start", 0))))
        guide_data["strengths"].append(float(strength))

    if not guide_data["images"]:
        w = derived_w if derived_w > 0 else 768
        h = derived_h if derived_h > 0 else 512
        w = max(32, (int(w) // 32) * 32)
        h = max(32, (int(h) // 32) * 32)
        guide_data["images"].append(torch.zeros((1, h, w, 3), dtype=torch.float32))
        guide_data["insert_frames"].append(0)
        guide_data["strengths"].append(0.0)
        derived_w, derived_h = w, h

    return guide_data, derived_w, derived_h


class LTXSixGridDirector(io.ComfyNode):
    """Original LTX Director timeline with automatic six-grid image and LLM prompt fill."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="CS-LTXSixGridDirector",
            display_name="CS-LTX \u516d\u5bab\u683c\u5bfc\u6f14\u53f0",
            category="CS-WhatDreamsCost",
            description=(
                "LTX \u5bfc\u6f14\u53f0\u7684\u516d\u5bab\u683c\u81ea\u52a8\u7248\uff1a\u81ea\u52a8\u63a5\u6536\u62c6\u5206\u56fe\u548c GPT \u5206\u955c\u6587\u672c\uff0c"
                "\u540c\u65f6\u4fdd\u7559\u53ef\u624b\u52a8\u7f16\u8f91\u7684\u65f6\u95f4\u7ebf\u3002"
            ),
            inputs=[
                io.Model.Input("model", display_name="\u6a21\u578b"),
                io.Clip.Input("clip", display_name="\u6587\u672c\u7f16\u7801\u5668"),
                io.Image.Input("storyboard_images", display_name="\u516d\u5bab\u683c\u62c6\u5206\u56fe", optional=True),
                io.String.Input("llm_response", display_name="GPT \u5206\u955c\u6587\u672c", multiline=True, default=""),
                io.Vae.Input("audio_vae", display_name="\u97f3\u9891 VAE", optional=True),
                io.Latent.Input("optional_latent", display_name="\u53ef\u9009\u6f5c\u7a7a\u95f4", optional=True),
                io.String.Input("global_prompt", display_name="\u5168\u5c40\u63d0\u793a\u8bcd", multiline=True, default=""),
                io.Int.Input("duration_frames", display_name="\u603b\u5e27\u6570", default=120, min=1, max=10000, step=1),
                io.Float.Input("duration_seconds", display_name="\u603b\u79d2\u6570", default=5.0, min=0.1, max=1000.0, step=0.01),
                io.String.Input("timeline_data", display_name="\u65f6\u95f4\u7ebf\u6570\u636e", default=""),
                io.Boolean.Input("use_custom_audio", display_name="\u4f7f\u7528\u81ea\u5b9a\u4e49\u97f3\u9891", default=False, optional=True),
                io.String.Input("local_prompts", display_name="\u5206\u955c\u63d0\u793a\u8bcd", multiline=True, default=""),
                io.String.Input("segment_lengths", display_name="\u6bcf\u6bb5\u5e27\u6570", default=""),
                io.String.Input("epsilon", display_name="\u5206\u6bb5\u8fb9\u754c\u9510\u5ea6", default="0.001"),
                io.Float.Input("frame_rate", display_name="\u5e27\u7387", default=24, min=1, max=240, step=1, optional=True),
                io.String.Input("display_mode", display_name="\u65f6\u95f4\u663e\u793a", default="\u79d2", optional=True),
                io.String.Input("guide_strength", display_name="\u56fe\u50cf\u5f15\u5bfc\u5f3a\u5ea6", default="1.0"),
                io.Combo.Input("parse_mode", display_name="\u6587\u672c\u89e3\u6790\u65b9\u5f0f", options=["\u81ea\u52a8", "JSON", "\u7f16\u53f7\u6587\u672c"], default="\u81ea\u52a8", optional=True),
                io.Int.Input("custom_width", display_name="\u8f93\u51fa\u5bbd\u5ea6", default=0, min=0, max=8192, step=1, optional=True),
                io.Int.Input("custom_height", display_name="\u8f93\u51fa\u9ad8\u5ea6", default=0, min=0, max=8192, step=1, optional=True),
                io.Combo.Input(
                    "resize_method",
                    display_name="\u56fe\u50cf\u9002\u914d\u65b9\u5f0f",
                    options=["\u4fdd\u6301\u6bd4\u4f8b", "\u62c9\u4f38\u586b\u6ee1", "\u7559\u767d\u586b\u5145", "\u88c1\u526a\u586b\u6ee1"],
                    default="\u4fdd\u6301\u6bd4\u4f8b",
                    optional=True,
                ),
                io.Int.Input("divisible_by", display_name="\u5c3a\u5bf8\u6574\u9664", default=32, min=1, max=256, step=1, optional=True),
                io.Int.Input("img_compression", display_name="\u56fe\u50cf\u538b\u7f29", default=18, min=0, max=100, step=1, optional=True),
            ],
            outputs=[
                io.Model.Output(display_name="\u6a21\u578b"),
                io.Conditioning.Output(display_name="\u6b63\u5411\u6761\u4ef6"),
                io.Latent.Output(display_name="\u89c6\u9891\u6f5c\u7a7a\u95f4"),
                io.Latent.Output(display_name="\u97f3\u9891\u6f5c\u7a7a\u95f4"),
                GuideData.Output(display_name="\u5f15\u5bfc\u6570\u636e"),
                io.Float.Output(display_name="\u5e27\u7387"),
                io.Audio.Output(display_name="\u5408\u6210\u97f3\u9891"),
            ],
        )

    @classmethod
    def execute(cls, model, clip, global_prompt, duration_frames, duration_seconds,
                timeline_data, local_prompts, segment_lengths, guide_strength="1.0", epsilon=1e-3,
                frame_rate=24, display_mode="seconds", custom_width=0, custom_height=0,
                resize_method="maintain aspect ratio", divisible_by=32, img_compression=18,
                storyboard_images=None, llm_response="", audio_vae=None, optional_latent=None,
                use_custom_audio=False, parse_mode="auto") -> io.NodeOutput:
        llm_response = _to_str(llm_response)
        global_prompt = _to_str(global_prompt)
        segment_lengths = _to_str(segment_lengths)
        guide_strength = _to_str(guide_strength)
        duration_frames = max(1, _to_int(duration_frames, 120))
        frame_rate = _to_float(frame_rate, 24.0)
        epsilon = _to_float(epsilon, 0.001)
        custom_width = max(0, _to_int(custom_width, 0))
        custom_height = max(0, _to_int(custom_height, 0))
        divisible_by = max(1, _to_int(divisible_by, 32))
        img_compression = max(0, _to_int(img_compression, 18))
        parse_mode = _normalize_choice(parse_mode, PARSE_MODE_ALIASES, "auto")
        resize_method = _normalize_choice(resize_method, RESIZE_METHOD_ALIASES, "maintain aspect ratio")

        parsed_prompts, _ = _parse_prompts(llm_response, parse_mode)
        timeline = _decode_timeline(timeline_data)

        if not timeline["segments"] and storyboard_images is not None:
            timeline = _build_default_timeline(
                storyboard_images,
                llm_response,
                duration_frames,
                frame_rate,
                segment_lengths,
                guide_strength,
                parse_mode,
            )

        timeline_json = json.dumps(timeline, ensure_ascii=False)
        local_prompts, segment_lengths_out = _contiguous_prompts_and_lengths(
            timeline["segments"],
            parsed_prompts,
            duration_frames,
        )
        storyboard_images_for_guides = _split_single_six_grid_image(
            storyboard_images,
            _image_segment_count(timeline),
        )

        guide_data, derived_w, derived_h = _build_guide_data(
            timeline,
            storyboard_images_for_guides,
            duration_frames,
            frame_rate,
            guide_strength,
            custom_width,
            custom_height,
            resize_method,
            divisible_by,
            img_compression,
        )

        ltxv_length = duration_frames + 1
        if optional_latent is None:
            latent_w = max(32, (int(derived_w) // 32) * 32)
            latent_h = max(32, (int(derived_h) // 32) * 32)
            latent_t = ((ltxv_length - 1) // 8) + 1
            samples = torch.zeros(
                [1, 128, latent_t, latent_h // 32, latent_w // 32],
                device=comfy.model_management.intermediate_device(),
            )
            latent = {"samples": samples}
        else:
            latent = optional_latent

        patched, conditioning = _encode_relay(
            model,
            clip,
            latent,
            global_prompt,
            local_prompts,
            segment_lengths_out,
            epsilon,
        )

        audio_out = _build_combined_audio(timeline_json, ltxv_length, frame_rate)
        audio_latent = {}
        if audio_vae is not None:
            if use_custom_audio:
                try:
                    waveform = audio_out["waveform"]
                    if waveform.ndim == 2:
                        waveform = waveform.unsqueeze(0)
                    if hasattr(audio_vae, "first_stage_model"):
                        latent_samples = audio_vae.encode(waveform.movedim(1, -1))
                    else:
                        latent_samples = audio_vae.encode({
                            "waveform": waveform,
                            "sample_rate": audio_out["sample_rate"],
                        })
                    mask = torch.full(
                        (1, latent_samples.shape[-2], latent_samples.shape[-1]),
                        0.0,
                        dtype=torch.float32,
                        device=comfy.model_management.intermediate_device(),
                    )
                    audio_latent = {
                        "samples": latent_samples,
                        "type": "audio",
                        "noise_mask": mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])),
                    }
                except Exception as exc:
                    log.error("[LTX Six Grid Director] Failed to encode custom audio: %s", exc)
                    raise exc
            else:
                audio_latent = _empty_audio_latent(audio_vae, ltxv_length, frame_rate)

        return io.NodeOutput(patched, conditioning, latent, audio_latent, guide_data, frame_rate, audio_out)


NODE_CLASS_MAPPINGS = {
    "CS-LTXSixGridDirector": LTXSixGridDirector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CS-LTXSixGridDirector": "CS-LTX \u516d\u5bab\u683c\u5bfc\u6f14\u53f0",
}
