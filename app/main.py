from pathlib import Path
import tempfile
from typing import Optional
from app.loaders import load_story


from app.serializers import Language, TTSType
from app.tts_stories import create_TTS


def make_tts(
    url: str,
    tts_type: TTSType = TTSType.C0QUI,
    language: Optional[Language] = None,
    to_save_path: Optional[Path] = None,
):
    story = load_story(url)
    if story:
        path = to_save_path or Path(
            tempfile.NamedTemporaryFile(delete=False).name
        )

        return create_TTS(
            tts_type,
            story.content,
            language or story.language or Language.DEFAULT,
            path,
        )
