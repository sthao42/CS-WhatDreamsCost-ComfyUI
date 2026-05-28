from .ltx_keyframer import LTXKeyframer
from .multi_image_loader import MultiImageLoader
from .ltx_sequencer import LTXSequencer
from .speech_length_calculator import SpeechLengthCalculator
from .load_audio_ui import LoadAudioUI
from .load_video_ui import LoadVideoUI
from .ltx_director import LTXDirector
from .ltx_auto_director import LTXAutoDirector
from .ltx_sixgrid_director import LTXSixGridDirector
from .ltx_director_guide import LTXDirectorGuide
from comfy_api.latest import ComfyExtension, io
from typing_extensions import override


class CSWhatDreamsCostExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            LTXDirector,
            LTXAutoDirector,
            LTXSixGridDirector,
            LTXDirectorGuide,
        ]


async def comfy_entrypoint() -> CSWhatDreamsCostExtension:
    return CSWhatDreamsCostExtension()


NODE_CLASS_MAPPINGS = {
    "CS-LTXKeyframer": LTXKeyframer,
    "CS-MultiImageLoader": MultiImageLoader,
    "CS-LTXSequencer": LTXSequencer,
    "CS-SpeechLengthCalculator": SpeechLengthCalculator,
    "CS-LoadAudioUI": LoadAudioUI,
    "CS-LoadVideoUI": LoadVideoUI,
    "CS-LTXDirector": LTXDirector,
    "CS-LTXAutoDirector": LTXAutoDirector,
    "CS-LTXSixGridDirector": LTXSixGridDirector,
    "CS-LTXDirectorGuide": LTXDirectorGuide,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CS-LTXKeyframer": "CS LTX Keyframer",
    "CS-MultiImageLoader": "CS Multi Image Loader",
    "CS-LTXSequencer": "CS LTX Sequencer",
    "CS-SpeechLengthCalculator": "CS Speech Length Calculator",
    "CS-LoadAudioUI": "CS Load Audio UI",
    "CS-LoadVideoUI": "CS Load Video UI",
    "CS-LTXDirector": "CS LTX Director",
    "CS-LTXAutoDirector": "CS LTX Auto Director",
    "CS-LTXSixGridDirector": "CS-LTX \u516d\u5bab\u683c\u5bfc\u6f14\u53f0",
    "CS-LTXDirectorGuide": "CS LTX Director Guide",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
