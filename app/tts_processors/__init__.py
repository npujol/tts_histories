from pathlib import Path
from typing import Optional
from app.serializers import RawStory, TTSType
from app.tts_processors.coqui import CoquiTTS
from app.tts_processors.google import GoogleTTS

_tta_processors = [CoquiTTS(), GoogleTTS()]


def process_story(
    story: RawStory,
    out_path: Path,
    tts_type: TTSType = TTSType.C0QUI,
) -> Optional[Path]:
    for processor in _tta_processors:  # type: ignore
        if processor.can_handle(story, tts_type):  # type: ignore
            return processor.make(story, out_path)  # type: ignore
