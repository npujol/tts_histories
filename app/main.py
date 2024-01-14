import logging
from pathlib import Path
import tempfile
from typing import Optional
from app.loaders import load_story
from app.tts_processors import process_story
from app.telegram_handler import send_to_telegram


from app.serializers import TTSType

logger = logging.getLogger(__name__)


def make_tts(
    source: str,
    tts_type: TTSType = TTSType.C0QUI,
    out_path: Optional[Path] = None,
    shall_save_text: bool = False,
    shall_send_to_telegram: bool = False,
):
    story = load_story(source)
    if story is None:
        logger.error("The content couldn't be processed.")
        return
    path = out_path or Path(tempfile.NamedTemporaryFile(delete=False).name)
    name = story.title or "out"
    file_path = path.joinpath(f"{name}.mp3") if path.is_dir() else path

    tts_path = process_story(
        story=story,
        out_path=file_path,
        tts_type=tts_type,
    )
    if shall_send_to_telegram and tts_path is not None:
        send_to_telegram(path=tts_path, name=story.title)

    if shall_save_text:
        text_path = path.joinpath(f"{name}.txt") if path.is_dir() else path
        text_path.write_text(story.content)
        if shall_send_to_telegram:
            send_to_telegram(path=text_path, name=story.title)

    return tts_path
