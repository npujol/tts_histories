import logging
from json import loads
from pathlib import Path

from telethon.sync import TelegramClient  # type: ignore

logger = logging.getLogger(__file__)

CHANNEL_ID = -1001567051258
config = loads((Path.home() / ".config/telegram-upload.json").read_text())


def send_to_telegram(path: Path, name: str):
    with TelegramClient("tts_stories", **config) as client:  # type: ignore
        message = client.send_file(  # type: ignore
            CHANNEL_ID,
            path,
            caption=name,
        )
        logger.info(f"{message}")
