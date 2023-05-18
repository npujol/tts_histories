from pathlib import Path
from typing import Optional
from app.serializers import RawStory, TTSType
from app.tts_processors.coqui import CoquiTTS
from app.tts_processors.google import GoogleTTS


def process_story(
    story: RawStory,
    out_path: Path,
    tts_type: TTSType = TTSType.C0QUI,
) -> Optional[Path]:
    if tts_type == TTSType.C0QUI:
        return CoquiTTS(story=story).make(out_path)
    elif tts_type == TTSType.GOOGlE:
        return GoogleTTS(story=story).make(out_path)
