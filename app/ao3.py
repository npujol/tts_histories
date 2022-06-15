import html
import logging
import os
import re
import uuid
from pathlib import Path

from app.models import AO3Story, Language
from app.tts_stories import get_content

CURRENT_TEMP_PATH = Path(__file__).parent.parent.joinpath("temp")

URL_BASE = "https://archiveofourown.org"
WATTPAD_BASE_DIR = os.getcwd()
RE_CLEAN = re.compile(r"\/")
RE_SPACES = re.compile(r"\s+")

logger = logging.getLogger(__file__)


class AO3:
    """Class to download a story from Wattpad
    Params:
        url: str
        language: Language(Default: Language.SPANISH)
    Attributes:
        story: WattpadStory
    """

    def __init__(self, url: str, language: Language = Language.SPANISH):
        id = uuid.uuid1()
        filename = CURRENT_TEMP_PATH.joinpath(f"{id}.txt")
        logger.info(f"Creating file {filename}")
        # Create the file
        open(filename, mode="w").close()
        self.story = AO3Story(
            id=id, url=url, language=language, text_path=filename
        )

    def save(self) -> Path:
        logger.info(f"Starting the download from {self.story.url}")
        html_story = get_content(self.story.url)
        for li in html_story.find(
            "li", attrs={"class": "download"}
        ).find_all(  # type: ignore
            "li"
        ):
            if li.a.string != "HTML":
                continue
            url = (
                URL_BASE
                + html.unescape(li.a.get("href"))
                .replace("\u2022" * 3, "")
                .strip()
            )
            content = get_content(url)
            self.story.title = content.title.string or ""  # type: ignore
            if self.story.title:
                self.rename(
                    self.story.text_path, f"{self.story.title}-{self.story.id}"
                )

            text = "\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in content.findAll("p")
            )
            self.write(
                self.story.text_path,
                text,
            )
        return self.story.text_path

    def write(self, file_path: Path, content: str):
        logger.info(f"Writing to file {file_path} {len(content)} characters")
        with open(file_path, "a") as f:
            f.write(content)

    def rename(self, path: Path, new_name: str):
        new_path = Path(path.parent, f"{new_name}{path.suffix}")
        logger.info(f"Renaming file {path} -> {new_path}")
        path.rename(new_path)
        self.story.text_path = new_path
