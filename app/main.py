import logging
from pathlib import Path
import tempfile
from typing import Optional
from app.loaders import load_story
from app.tts_processors import process_story


from app.serializers import TTSType

logger = logging.getLogger(__name__)


def make_tts(
    source: str,
    tts_type: TTSType = TTSType.C0QUI,
    out_path: Optional[Path] = None,
):
    story = load_story(source)
    if story is None:
        logger.error("The content couldn't be processed.")
        return
    path = out_path or Path(tempfile.NamedTemporaryFile(delete=False).name)
    name = story.title.replace(" ", "_") or "out"
    file_path = path.joinpath(f"{name}.mp3") if path.is_dir() else path

    return process_story(story=story, out_path=file_path, tts_type=tts_type)
