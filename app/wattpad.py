import html
import logging
import re
import uuid
from pathlib import Path

from bs4 import BeautifulSoup

from app.serializers import Chapter, Language, WattpadStory
from app.tts_stories import get_content

CURRENT_TEMP_PATH = Path(__file__).parent.parent.joinpath("temp")

URL_BASE_WATTPAD = "https://www.wattpad.com"
RE_CLEAN = re.compile(r"\/")

logger = logging.getLogger(__file__)


class Wattpad:
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
        self.story = WattpadStory(
            id=id,
            url=url,
            language=language,
            text_path=filename,
        )

    def save(self) -> Path:
        logger.info(f"Starting the content download from {self.story.url}")
        html_story = get_content(self.story.url)
        title = (  # type: ignore
            (
                html_story.find(
                    "div", attrs={"class": "story-info__title"}
                ).string  # type: ignore
                or ""
            )
            .encode("ascii", "ignore")  # type: ignore
            .decode("utf-8")
        )
        self.story.title = RE_CLEAN.sub("", title)  # type: ignore
        if self.story.title:
            self.rename(
                self.story.text_path, f"{self.story.title}-{self.story.id}"
            )
        author = (  # type: ignore
            html_story.find(
                "div", attrs={"class": "author-info__username"}
            ).string  # type: ignore
            or ""
        )
        summary = (  # type: ignore
            html_story.find(
                "pre", attrs={"class": "description-text"}
            ).string  # type: ignore
            or ""
        )
        logger.info(f"Saving story info {self.story.title}, {author}")

        self.write(
            self.story.text_path,
            f"{self.story.title}, {author} \n {summary} \n",
        )

        chapters = html_story.find(  # type: ignore
            "div", attrs={"class": "story-parts"}
        ).find_all(  # type: ignore
            "a", attrs={"class": "story-parts__part"}
        )

        logger.info(f"There are {len(chapters)}")  # type: ignore

        for k, ch in enumerate(chapters):  # type: ignore
            logger.info(f"Processing chapter {k}")

            url_chapter = (
                URL_BASE_WATTPAD
                + html.unescape(ch.get("href"))
                .replace("\u2022" * 3, "")
                .strip()
            )
            self.story.chapters.append(
                Chapter(
                    id=uuid.uuid1(),
                    url=url_chapter,
                    text=self.extract_info(url_chapter),
                )
            )
        return self.story.text_path

    def extract_info(self, url: str) -> str:
        chapter_html = get_content(url)
        title = (  # type: ignore
            chapter_html.find(
                "h1",
                attrs={"class": "h2"},
            ).string  # type: ignore
            or ""
        )
        text = self.get_chapter_text(url, chapter_html)
        self.write(
            self.story.text_path,
            f"\n {title}\n {text}",
        )
        return f"\n {title}\n {text}"

    def get_chapter_text(self, url: str, chapter_html: BeautifulSoup) -> str:
        text = ""
        i = 1
        while i == 1 or (str(i) in chapter_html.title.string):  # type: ignore
            logger.info(f"Processing page {i}")

            chapter_parts = chapter_html.findAll(attrs={"data-p-id": True})
            part = "\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in chapter_parts
            )
            text += part
            i += 1
            new_page_url = url + f"/page/{i}"
            chapter_html = get_content(new_page_url)
        return text

    def write(self, file_path: Path, content: str):
        logger.info(f"Writing to file {file_path} {len(content)} characters")
        with open(file_path, "a") as f:
            f.write(content)

    def rename(self, path: Path, new_name: str):
        new_path = Path(path.parent, f"{new_name}{path.suffix}")
        logger.info(f"Renaming file {path} -> {new_path}")
        path.rename(new_path)
        self.story.text_path = new_path
