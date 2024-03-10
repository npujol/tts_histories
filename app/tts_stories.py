import logging
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from gtts import gTTS  # type: ignore
from requests.adapters import HTTPAdapter, Response
from requests.sessions import Session
from urllib3.util.retry import Retry  # type: ignore
from TTS.api import TTS  # type: ignore
import ffmpeg  # type: ignore
from app.serializers import Language, TTSType  # type: ignore

logger = logging.getLogger(__file__)

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
)

adapter = HTTPAdapter(max_retries=retry_strategy)  # type: ignore

http_requests = Session()
http_requests.mount("https://", adapter)
http_requests.mount("http://", adapter)


def get_raw_content(url: str) -> Optional[Response]:
    """
    Retrieve HTML content from a URL.

    Args:
        url (str): The URL to fetch the HTML content from.

    Returns:
        bytes: A HTML content.

    Raises:
        requests.exceptions.HTTPError: If the HTTP response status code
        indicates an error.
        requests.exceptions.RequestException: If an error occurs while making
        the HTTP request.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error retrieving content from {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error making request to {url}: {e}")
        return None
    if response.status_code == 200:
        return response


def get_content(url: str) -> Optional[BeautifulSoup]:
    """
    Retrieve HTML content from a URL and parse it using BeautifulSoup.

    Args:
        url (str): The URL to fetch the HTML content from.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML
        content.
    """
    response = get_raw_content(url)
    if response:
        return BeautifulSoup(response.content, "html.parser")


def read_text(filename: Path) -> Optional[str]:
    """
    Read text from a file and return its content as a string.

    Args:
        filename (Path): The path of the file to read.

    Returns:
        str: The content of the file as a string.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the specified file cannot be opened due to
        insufficient permissions.
        UnicodeDecodeError: If the file contains non-UTF-8 encoded characters.
        OSError: If any other I/O error occurs while reading the file.
    """
    try:
        with open(filename, "r", encoding="utf8") as f:
            content = f.readlines()
        content = "\n".join([x.strip() for x in content])
        return content
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None
    except PermissionError as e:
        logger.error(f"Permission error: {e}")
        return None
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decoding error: {e}")
        return None
    except OSError as e:
        logger.error(f"Error reading file: {e}")
        return None


def create_TTS(
    type: TTSType,
    text: str,
    language: Language,
    filename: Path,
) -> bool:
    """
    Create a Text-to-Speech (TTS) audio file from the given text in
    the specified language and save it to a file.

    Args:
        filename (Path): The path of the file to save the TTS audio.
        text (str): The text to convert to speech.
        language (str): The language of the text.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the TTS conversion or
        saving the audio file.
    """
    attempts = 5
    while attempts:
        try:
            if type == TTSType.GOOGlE:
                tts = gTTS(text, lang=language)  # type: ignore
                tts.save(f"{filename}.mp3")  # type: ignore
            elif type == TTSType.C0QUI:
                tts = create_coqui_tts(filename, text, language)

            return True
        except Exception as e:
            logger.warning(f"Error creating TTS audio: {e}")
            attempts -= 1
    return False


def save_text(title: str, text: str, path: Path) -> Path:
    """
    Save the given text to a file with the specified title at the
    specified path.

    Args:
        title (str): The title of the text.
        text (str): The text to be saved.
        path (Path): The path where the text file will be saved.

    Returns:
        Path: The path of the saved text file.

    Raises:
        None
    """
    with open(path.joinpath(f"{title}.txt"), "w", encoding="utf8") as outfile:
        logger.debug(f"Init save story: {title}")
        outfile.write(text)
        logger.debug(f"Complete save story: {title}")
    return path.joinpath(f"{title}.txt")


def merge_audio_files(filename: str, path: Path) -> Path:
    """
    Merge multiple audio files from the specified path into a single
    audio file.

    Args:
        filename (str): The desired filename of the merged audio file.
        path (Path): The path containing the audio files to be merged.

    Returns:
        Path: The path of the merged audio file.
    """
    logger.debug(f"Merge audio from folder {path}")
    filepath = path.parent / f"{filename}.mp3"

    files = [path / f for f in sorted(path.glob("*.mp3"))]
    inputs = [ffmpeg.input(str(f)) for f in files]  # type: ignore
    ffmpeg.concat(*inputs, a=1, v=0).output(str(filepath)).run(  # type: ignore
        overwrite_output=True
    )

    logger.debug(f"Saved {filepath}")

    for f in files:
        f.unlink()

    return filepath


MAP_LANGUAGE_MODEL = {Language.SPANISH: "tts_models/es/css10/vits"}


def create_coqui_tts(filename: Path, text: str, language: Language):
    model = MAP_LANGUAGE_MODEL.get(language, None)
    if model is None:
        list_models: list[str] = [
            m for m in TTS.list_models() if f"/{language}/" in m  # type: ignore
        ]
        if not list_models:
            return
        model = list_models[0]
    tts = TTS(
        model_name=model,
        progress_bar=False,
        gpu=False,
    )
    tts.tts_to_file(  # type: ignore
        text,
        file_path=f"{filename}",
    )
    return f"{filename}"
