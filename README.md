# CS-WhatDreamsCost-ComfyUI

## Source and Attribution

This project is based on [WhatDreamsCost/WhatDreamsCost-ComfyUI](https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI).
The original author is credited here as the pre-existing source. This repository is a CS fork that adds a separate `CS-` namespace, so it can be installed beside the original plugin without replacing the original WhatDreamsCost node IDs.

## Overview

`CS-WhatDreamsCost-ComfyUI` focuses on an automated LTX storyboard workflow:

- Split a single 3x2 six-grid storyboard image into six ordered shots.
- Pass LLM/GPT/Qwen shot text into the director timeline.
- Review and manually edit each shot prompt, duration, image guide, and audio segment before generation.
- Keep the original LTX Director timeline workflow, while registering all public nodes under `CS-...` IDs.
- Add guide latent size alignment in `CS-LTXDirectorGuide` to reduce LTX guide insertion size errors.

这个分支的核心目标是把“六宫格图像 -> 六段分镜 -> 可编辑导演台时间线 -> LTX 生成”尽量自动化，同时保留前端手动修改能力。

## CS Namespace

This fork intentionally registers public nodes with `CS-` IDs. The legacy WhatDreamsCost node IDs are not registered here, so shared platforms such as RunningHub should not treat this package as a replacement for the original plugin.

| Original-style node | CS fork node ID |
| --- | --- |
| `LTXDirector` | `CS-LTXDirector` |
| `LTXAutoDirector` | `CS-LTXAutoDirector` |
| `LTXSixGridDirector` | `CS-LTXSixGridDirector` |
| `LTXDirectorGuide` | `CS-LTXDirectorGuide` |
| `LTXKeyframer` | `CS-LTXKeyframer` |
| `LTXSequencer` | `CS-LTXSequencer` |
| `MultiImageLoader` | `CS-MultiImageLoader` |
| `SpeechLengthCalculator` | `CS-SpeechLengthCalculator` |
| `LoadAudioUI` | `CS-LoadAudioUI` |
| `LoadVideoUI` | `CS-LoadVideoUI` |

Old workflows that reference unprefixed WhatDreamsCost node IDs need to be updated to the matching `CS-...` node IDs before they can use this fork.

## ▶️ YouTube Tutorial Videos

<table>
  <tr>
    <td>
      <p align="center">LTX Director Trailer</p>
      <a href="https://www.youtube.com/watch?v=fZgtkRcu4_k">
        <img src="https://img.youtube.com/vi/fZgtkRcu4_k/0.jpg" alt="LTX Director Trailer" width="400">
      </a>
    </td>
    <td>
      <p align="center">LTX Director Tutorial</p>
      <a href="https://www.youtube.com/watch?v=vM60pJJqqEI">
        <img src="https://img.youtube.com/vi/vM60pJJqqEI/0.jpg" alt="LTX Director Tutorial" width="400">
      </a>
    </td>
  </tr>
</table>

## How to Install

1. Navigate to your `ComfyUI/custom_nodes` folder.
2. Clone this repository:

```bash
git clone https://github.com/yg496/CS-WhatDreamsCost-ComfyUI.git
```

3. Restart ComfyUI.
4. Search for `CS-` in the ComfyUI node menu.

You can also install it through ComfyUI Manager after the package is available there.

**Important**

If you don't see the latest version (v1.4.0) yet in the manager then just downloaded the nightly version (or fetch the updates to update the list to see the latest version). 
Also you will need to update ComfyUI-LTXVideo and ComfyUI-KJNodes to the latest version as well. You cannot use this node without updating ComfyUI-LTXVideo!

# Recent Updates

**v1.4.0 CS fork**
  * **New node: CS-LTX Six-Grid Director / CS-LTX 六宫格导演台**
    - Adds an automatic six-grid storyboard workflow on top of the original LTX Director timeline.
    - Accepts a single 3x2 storyboard image or a batch of six images, then builds six editable timeline shots.
    - Connects LLM/GPT/Qwen shot text into the timeline so prompts can be reviewed and manually edited before generation.
    - Registers all public nodes under `CS-...` IDs to avoid overwriting the original WhatDreamsCost nodes on shared platforms.
    - Refreshes six-grid previews when the upstream storyboard image changes.
    - Adds a guide latent size alignment fix in `CS-LTXDirectorGuide` for more stable LTX guide insertion.

**v1.3.9**
  * **Fixed recent updates not showing in the manager**

It took like 5 tries but I finally got it working 🤦‍♂️

**v1.3.3**
  * **LTX Director Hotfix 2**
    - Fixed duration_seconds input issue.
    - Made both duration widgets visible at all times now
    - Implemented audio latent fix to improve compatibility


**v1.3.2**
  * **LTX Director Hotfix**
    - Fixed epsilon input overlapping custom_width input
    - Fixed invisible widgets in nodes 2.0 when toggling widget visibility through settings menu

If anyone finds anymore bugs or has idea for improvements please let me know! 


**v1.3.1**
  * **LTX Director Example Workflow Fix**
    - Minor fix to the example workflow (i forgot to set the clip loader type to ltxv lol)
    
 **v1.3.0**
  * **New nodes: LTX Director and LTX Director Guide**
    - A complete timeline editor that can do almost everything. It's my most ambitious node so far and the successor to LTX Sequencer/Multi Image Loader.

 **v1.2.9**
  * **Fixed every known issue with Multi Image Loader and added text output to Speech Length Calculator**
  
    - Removed the completely useless drag and drop animations (now it's snappy and no longer finicky)
    - Fixed the node resizing on nodes 2.0 
    - Updated grid logic to fit images better
    - Added ablity to right click images to copy/open/save images
    - Fixed the "invisible hitbox" underneath node issue (actually this time).

  Also added a text output to the Speech Length Calculator node (can't believe i didn't do this initially)

<details>
  <summary>Click to view older Updates</summary>

 **v1.2.8**
  * **Updated Load Video UI and Color Conversion**
    * Added crop mode, a simple interface to crop videos. It also include various aspect ratio presets.
    * Updated color conversion to ensure colors are as accurate as possible. Will first check metadata for colorspace, and if metadata is missing then it will guess the colorspace based on video dimensions.
    * Updated display mode toggle UI to be more understandable 

 **v1.2.7**
  * **New Node: Load Video UI**

Custom Node to Trim, Resize, and Preview Videos in Realtime
  
   **v1.2.6**
  * **Updated Speech Length Calculator UI**

Also added duration output to the Load Audio UI node

 **v1.2.5**
  * **Updated Load Audio UI Node**
    * Added Duration Setting
    * Made the whole selection bar draggable
    * Fixed Trimmed UI to show centiseconds
    
 **v1.2.4**
 * **New Node: Load Audio UI**

Overhaul of the load audio node. Features a simple interface to easily trim audio. Also allows dragging and dropping files (fixes the original node that doesn't allow dropping in videos). Also compatible with nodes 2.0.

 **v1.2.3**
  * **Workflow Update + Minor Bug Fix** 
    * Added new workflow that is compatible with the latest ComfyUI version (as of 4/27/26). The new workflow also included an option to include custom audio, and has minor improvements of the previous workflows.
    * Fixed minor bug with Multi Image Loader that blocked mouse input in a small area under the node 🤷‍♂️

**v1.2.0**
  * **New Node: Speech Length Calculator** 
  
  Automatically output in realtime how long a video should be based on the dialouge. 

**v1.1.0**
  * Added resize_method to the Multi Image Loader node for more resize options
  * Added insert_mode which allows you to enter in seconds instead of frames on the LTX Sequencer node
  * Updated workflows with more notes
  * Re-added tiny vae to workflows
  * Fixed various bugs
  * more things i can't rememeber
  
**This update will change the node layouts, so be sure to update your workflows or else they won't work properly.**

❗❗❗ **New Tutorial on using these nodes available: https://www.youtube.com/watch?v=aXDIr8eNovI**  ❗❗❗
</details>

# ⚙️ Custom Nodes

## CS-LTX Six-Grid Director / CS-LTX 六宫格导演台

`CS-LTX 六宫格导演台` 是这个分支的核心新增节点。它保留了原版 LTX Director 的时间线编辑能力，同时把六宫格分镜图、LLM/GPT/Qwen 分镜文本、LTX 引导图生成流程接到一起，让“六宫格图像 -> 六段分镜 -> 可编辑时间线 -> LTX 生成”尽量自动化。

它适合这样的工作流：先由上游节点生成一张 3x2 六宫格分镜图，再让反推模型或 GPT 输出 6 段分镜描述，导演台节点会自动把六宫格拆成 6 个分镜块，并把对应文本写入时间线。运行前你仍然可以在前端手动修改每段分镜的提示词、时长和引导强度。

**ComfyUI 节点名称：**

| Name | Meaning |
| --- | --- |
| `CS-LTX 六宫格导演台` | ComfyUI 里看到的节点显示名。 |
| `CS-LTXSixGridDirector` | 新的节点内部 ID。 |
| `CS-...` | 这个分支的所有公开节点都使用 `CS-` 前缀，避免覆盖原作者插件。 |

**基础流程：**

1. 用上游节点生成或加载一张 3x2 六宫格分镜图。
2. 把六宫格图片接到 `六宫格拆分图` / `storyboard_images`。
3. 把 LLM/GPT/Qwen 输出的分镜文本接到 `GPT 分镜文本` / `llm_response`。
4. 把 LTX 模型和 CLIP 接到 `模型` / `model` 与 `文本编码器` / `clip`。
5. 如果工作流需要音频潜空间，可以额外接入 Audio VAE。
6. 打开节点前端时间线，检查 6 个图像分镜块，并按需要调整每段时长和提示词。
7. 把 `引导数据` / `guide_data` 接到 `CS-LTXDirectorGuide`，把 `视频潜空间` / `video_latent` 接入 LTX 采样链路。

**六宫格读取顺序：**

六宫格按标准 3x2 顺序读取，从左到右、从上到下：

```text
1  2  3
4  5  6
```

也就是说，第 1 段是左上角，第 3 段是右上角，第 4 段是左下角，第 6 段是右下角。

**推荐的分镜文本格式：**

推荐让 GPT/Qwen 输出 JSON，因为它能同时保存分镜序号、提示词和每段帧数，最适合全自动工作流：

```json
[
  {"shot": 1, "prompt": "Wide shot, character enters the room...", "frames": 20},
  {"shot": 2, "prompt": "Medium shot, character reports to the boss...", "frames": 20},
  {"shot": 3, "prompt": "Close-up, boss listens and thinks...", "frames": 20}
]
```

节点也会尝试解析编号文本或普通文本，但如果你希望工作流稳定自动运行，JSON 是最稳的格式。

**前端可手动编辑：**

自动填充之后，6 个分镜块不是锁死的。你仍然可以在导演台里手动调整：

- 拖动或缩放分镜块，修改每段起止时间；
- 选中分镜后，在文本框里修改该段提示词；
- 修改每段图像引导强度；
- 继续手动添加图像、文本或音频片段；
- 使用原版 LTX Director 的自定义音频和时间线播放控制。

这些手动修改会写入 `时间线数据` / `timeline_data`。真正运行时，节点会优先使用当前前端时间线里的最终内容。

**LTX 引导尺寸修复：**

有些 LTX 工作流里，引导图经过 VAE 编码后会得到和主视频 latent 不一致的空间尺寸，例如 `Expected size 33 but got size 17`。这个分支在 `CS-LTXDirectorGuide` 中加入了尺寸对齐步骤，会在插入 keyframe 前把 guide latent 自动对齐到当前视频 latent 的尺寸，减少这类报错。


## CS-LTX Director
<img width="1481" height="833" alt="Clipboard Image (2)" src="https://github.com/user-attachments/assets/08f3fe53-9393-4f5d-9de5-58b229fbed47" />

A Complete Timeline Editor For LTX 2.3. This is the sucessor of my previous nodes, and has loads of features in it. It was originally based off of [Kijai's Prompt Relay node](https://github.com/kijai/ComfyUI-PromptRelay) and my LTX Sequencer/Multi Image Loader nodes.

**Main Features:**
- **Fully Functional Timeline Editor:** I spent hours studying various video editors and ended up with this design. If anyone has ideas for improvements let me know! I will adding documentation on all the functions soon.
- **Prompt Relay integrated:** This unlocks the ability to have granular control over video generation. For more information on Prompt Relay go here, https://gordonchen19.github.io/Prompt-Relay/
- **First, Middle, Last Frame Support:** This has by far the easiest method of creating first/last frames videos. It supports any number of keyframes, and will be the successor of my previous nodes.
- **Custom Audio Support:** Import, trim, and combine your own audio clips in this node. Enabling custom audio is as simple as clicking 1 button. It is also compatible with every other feature in the node, include first/last frames, t2v, i2v, and prompt relay.
- **Image to Video:** Part of the goal of this node was to make it easier to do everything, including Image to Video. It has built in resize functionality, and of course all the benifits of the prompt relay and custom audio integration.
- **Text to Video:** Use text segments to create T2V videos. Compatible with all other features of the node.

Download workflows here: https://github.com/yg496/CS-WhatDreamsCost-ComfyUI/tree/main/example_workflows

**Tutorial videos and documentation coming soon**


## CS-Multi Image Loader
<img width="1280" height="720" alt="Multi_Image_Loader_Wide_Gif" src="https://github.com/user-attachments/assets/99b6afd8-5197-4e6c-81da-a7bd156c42c7" />

An Image loader that features a built in gallery, allowing your to easily rearrange images and output them seperately or batched together. It also combines the image resize node and LTXVPreprocess node to reduce clutter in LTX workflows.

## CS-LTX Sequencer
![LTX_Sequencer_GIF](https://github.com/user-attachments/assets/88f27155-f50e-4cb2-b937-ab173e6bdf0b)

An overhaul of the LTXVAddGuideMulti node. It allows you to quickly create FFLF (First Frame Last Frame) videos, shot sequences, supports any number of middle frames.

Connect the `CS-MultiImageLoader` node's `multi_output` to automatically update the node's widgets.

It also has a sync feature that syncs all LTX Sequencer nodes together in realtime, removing the need to edit every single node manually every time you want to make a change to something. 


## CS-LTX Keyframer
<img width="1082" height="608" alt="LTX Keyframer Wide" src="https://github.com/user-attachments/assets/850ba4a2-dbca-4e5a-a580-1c271e9f0c41" />

An overhaul of the LTXVImgToVideoInplaceKJ node. It allows you to quickly create FFLF (First Frame Last Frame) videos and shot sequences. Also upports any number of middle frames.

Connect the `CS-MultiImageLoader` node's `multi_output` to automatically update the node's widgets.

It also has a sync feature that syncs all LTX Keyframer nodes together in realtime, removing the need to edit every single node manually every time you want to make a change to something. 

**I would recommend using the LTX Sequencer Node over this node, after further testing it seems superior in at pretty much everything. I'll leave it in just in case more people want to test it**

## CS-Speech Length Calculator
<img width="1280" height="720" alt="Speech Length Calculator v2 Gif" src="https://github.com/user-attachments/assets/04b9a1cf-20e4-4b7b-a9c6-4a5a0825995b" />
<br>
<br>
This node calculates in realtime how long a video should be based on the dialogue. Any words in quotations will be considered as speech. The node updates in realtime without having to run the workflow, and outputs the length depending on how fast the speech is.

If you connect another string/text node to the text_input, it will still update in the length in realtime.

I kept having to play the guessing game on my own generations so I made this node to make it easier :man_shrugging:

## CS-Load Video UI  
<table width="100%">
  <tr>
    <td width="50%" align="center">
      <p>Simple Controls</p>
      <img src="https://github.com/user-attachments/assets/fb76ff03-a6ff-4837-bd63-7e429f5f3d37" width="100%" />
    </td>
    <td width="50%" align="center">
      <p>New Crop Mode!</p>
      <img src="https://github.com/user-attachments/assets/28cfb4ca-e42a-44da-9afb-f20cb01b9722" width="100%" />
    </td>
  </tr>
</table>

<br>
<br>
An upgraded Load Video node. It has the following features:

* Simple interface to quickly trim videos and preview them in realtime.
* Ability to load any length of video into the node (the default load video node was limited to 100MB files)
* Easily switch between showing seconds and frames with a toggle button. This will change the widgets as well as the interface.
* Multiple options for resizing the video (maintain aspect ratio, crop, stretch to fit, pad)
* Allows dragging and dropping files into the node
* Progress bar
* Optimized to use less RAM (still very limited due to ComfyUI limitations, but at least a little more efficient)

Please note that due to ComfyUI limitations (and the fact that this node doesn't use any addtional libraries), this node will not work well for outputting large videos. You can trim any length of video without a problem, but if the output is still large it will end up using a lot of RAM. I have implemented various optimizations though to make it use less memory.

## CS-Load Audio UI  
<img width="1280" height="720" alt="Load_Audio_UI_V2" src="https://github.com/user-attachments/assets/e3dc5c8d-d0b9-4336-8196-944204719239" />
<br>
<br>
An upgraded Load Audio node. Features a simple interface to easily trim audio. Also allows dragging and dropping files (fixes the original node that doesn't allow dropping in videos). Also compatible with nodes 2.0.

# 💡 Workflows
Download workflows here: https://github.com/yg496/CS-WhatDreamsCost-ComfyUI/tree/main/example_workflows

# ❗ Known Issues

Fixed everything so far. If there are any other issue or bugs you find please let me know!

# 💡 Additional Info

Feel free to suggest improvements, and if you run into any bugs let me know!

For those asking, I mainly used gemini to create these nodes.
