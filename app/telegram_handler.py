import logging
from json import loads
from pathlib import Path

from telethon.sync import TelegramClient  # type: ignore
from environs import Env

logger = logging.getLogger(__file__)

env = Env()
env.read_env()
channel_id = env.int("CHANNEL_ID", 0)  # type: ignore
config = loads((Path.home() / ".config/telegram-upload.json").read_text())


def send_to_telegram(path: Path, name: str):
    logger.info("Starting to send file to telegram.")
    if not channel_id:
        logger.error(f"Error sending file: {name} to telegram, missing channel id.")
        return
    with TelegramClient("tts_stories", **config) as client:  # type: ignore
        message = client.send_file(  # type: ignore
            channel_id,
            path,
            caption=name,
        )
        logger.info(f"{message}")
