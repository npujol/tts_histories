from pathlib import Path
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from gtts import gTTS


def get_content(url: str) -> BeautifulSoup:
    MOZILLA = {"User-Agent": "Mozilla/5.0"}
    req = Request(url, headers=MOZILLA)
    html_content = urlopen(req).read()
    return BeautifulSoup(html_content, "html.parser")


def read_text(filename: Path) -> str:
    with open(filename, "r", encoding="utf8") as f:
        content = f.readlines()
    content = "\n".join([x.strip() for x in content])
    return content


def create_TTS(filename, text, language):
    tts = gTTS(text, lang=language)
    tts.save(f"{filename}.mp3")


def save_text(title: str, text: str, path: Path):
    with open(path.joinpath(f"{title}.txt"), "w", encoding="utf8") as outfile:
        print(f"Init save story: {title}")
        outfile.write(text)
        print(f"Complete save story: {title}")
    return path.joinpath(f"{title}.txt")


def spanish_correction(text):
    PAUSE_CORRECTIONS = [
        [" y ", ", y "],
        [" o ", ", o "],
        [" pero ", ", pero "],
        [" *** ", ""],
    ]
    for val in PAUSE_CORRECTIONS:
        text = text.replace(val[0], val[1])
    return text
