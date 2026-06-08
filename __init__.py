from .ltx_keyframer import LTXKeyframer
from .multi_image_loader import MultiImageLoader
from .ltx_sequencer import LTXSequencer
from .speech_length_calculator import SpeechLengthCalculator
from .load_audio_ui import LoadAudioUI
from .load_video_ui import LoadVideoUI
from .ltx_director import LTXDirector
from .ltx_auto_director import LTXAutoDirector
from .ltx_sixgrid_director import LTXGridDirector
from .ltx_director_guide import LTXDirectorGuide
from comfy_api.latest import ComfyExtension, io
from typing_extensions import override


class CSWhatDreamsCostExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [
            LTXDirector,
            LTXAutoDirector,
            LTXGridDirector,
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
    "CS-LTXGridDirector": LTXGridDirector,
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
    "CS-LTXGridDirector": "CS-LTX 宫格导演台",
    "CS-LTXDirectorGuide": "CS-LTX 导演台引导",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
