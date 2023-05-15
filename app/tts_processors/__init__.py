from pathlib import Path
from typing import Optional
from app.serializers import RawStory, TTSType

_tta_processors = []


def process_story(
    story: RawStory,
    tts_type: TTSType = TTSType.C0QUI,
) -> Optional[Path]:
    for processor in _tta_processors:  # type: ignore
        if processor.can_handle(story):  # type: ignore
            return processor.make(story)  # type: ignore
