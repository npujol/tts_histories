import glob
import logging
import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from gtts import gTTS  # type: ignore
from pydub import AudioSegment  # type: ignore
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__file__)

retry_strategy: Retry = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http_requests = requests.Session()
http_requests.mount("https://", adapter)
http_requests.mount("http://", adapter)


def get_content(url: str) -> BeautifulSoup:
    MOZILLA = {"User-Agent": "Mozilla/5.0"}
    response = http_requests.get(url, headers=MOZILLA)
    response.raise_for_status()

    html_content = response.content
    return BeautifulSoup(html_content, "html.parser")


def read_text(filename: Path) -> str:
    with open(filename, "r", encoding="utf8") as f:
        content = f.readlines()
    content = "\n".join([x.strip() for x in content])
    return content


def create_TTS(filename: Path, text: str, language: str) -> None:
    attempts = 5
    while attempts:
        try:
            tts = gTTS(text, lang=language)  # type: ignore
            break
        except Exception:
            attempts = attempts - 1
    tts.save(f"{filename}.mp3")  # type: ignore


def save_text(title: str, text: str, path: Path):
    with open(path.joinpath(f"{title}.txt"), "w", encoding="utf8") as outfile:
        logger.debug(f"Init save story: {title}")
        outfile.write(text)
        logger.debug(f"Complete save story: {title}")
    return path.joinpath(f"{title}.txt")


def combine_audio(path: Path, filename: str) -> Path:
    logger.debug(f"Merge audio from folder {path}")
    combined = AudioSegment.empty()
    files = [f for f in glob.glob("*.mp3", root_dir=path)]
    for a in sorted(files, key=lambda f: int(f.split("_")[1].split(".")[0])):
        try:
            combined += AudioSegment.from_file(path / a, "mp3")  # type: ignore
        except Exception as e:
            logger.exception(
                f"Failed merging file {a}, due to {e}",
                exc_info=True,
            )
    logger.debug(f"Saving {f'{filename}.mp3'}")
    filepath = path.parent / f"{filename}.mp3"
    combined.export(  # type: ignore
        path.parent / f"{filename}.mp3",
        format="mp3",
    )

    for a in files:
        os.remove(path / a)

    return filepath
