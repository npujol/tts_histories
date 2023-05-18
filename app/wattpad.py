import html
import logging
import re
from typing import Optional
import uuid
from pathlib import Path

from bs4 import BeautifulSoup
from app.serializers import Chapter, Language, WattpadStory
from app.tts_stories import get_content
import tempfile

CURRENT_TEMP_PATH = Path(__file__).parent.parent.joinpath("temp")

URL_BASE_WATTPAD = "https://www.wattpad.com"
RE_CLEAN = re.compile(r"\/")

logger = logging.getLogger(__file__)


class Wattpad:
    """Class to download a story from Wattpad.
    Params:
        url (str): The URL of the story on Wattpad.
    Attributes:
        story (WattpadStory): A WattpadStory object containing the information
        about the downloaded story.
    """

    def __init__(self, url: str, language: Language = Language.SPANISH):
        id = uuid.uuid1()
        filename = CURRENT_TEMP_PATH.joinpath(f"{id}.txt")
        logger.info(f"Creating file {filename}")
        # Create the file
        open(filename, mode="w").close()
        self.story = WattpadStory(
            id=uuid.uuid1(),
            url=url,
            language=language,
            text_path=tempfile.NamedTemporaryFile(mode="w", delete=False).name,
        )

    def save(self) -> Optional[Path]:
        logger.info(f"Starting the content download from {self.story.url}")
        html_story = get_content(self.story.url)
        if html_story is None:
            return
        title = (  # type: ignore
            (
                html_story.find(  # type: ignore
                    "div", attrs={"class": "story-info__title"}
                ).string  # type: ignore
                or ""
            )
            .encode("ascii", "ignore")  # type: ignore
            .decode("utf-8")
        )
        self.story.title = RE_CLEAN.sub("", title)  # type: ignore
        if self.story.title:
            self._rename(
                self.story.text_path, f"{self.story.title}-{self.story.id}"
            )
        author = (  # type: ignore
            html_story.find(  # type: ignore
                "div", attrs={"class": "author-info__username"}
            ).string  # type: ignore
            or ""
        )
        summary = (  # type: ignore
            html_story.find(  # type: ignore
                "pre", attrs={"class": "description-text"}
            ).string  # type: ignore
            or ""
        )
        logger.info(f"Saving story info {self.story.title}, {author}")

        self._write(
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

    def extract_info(self, url: str) -> Optional[str]:
        """Extracts the title and text of a chapter from the chapter's HTML.
        Args:
            url (str): The URL of the chapter on Wattpad.
        Returns:
            Optional[str]: The title and text of the chapter, separated by a
            newline character, or None if the chapter HTML is empty.
        """
        chapter_html = get_content(url)
        title_element = chapter_html.find("h1", attrs={"class": "h2"})  # type: ignore
        title = title_element.string if title_element else ""  # type: ignore
        if chapter_html:
            text = self._get_chapter_text(url, chapter_html)
            self._write(self.story.text_path, f"\n {title}\n {text}")
            return f"\n {title}\n {text}"

    @staticmethod
    def _get_chapter_text(url: str, chapter_html: BeautifulSoup) -> str:
        """Scrapes and combines the text from multiple web pages containing a chapter.

        Args:
            url (str): The URL of the first page of the chapter.
            chapter_html (BeautifulSoup): The HTML content of the first page of the
            chapter.

        Returns:
            str: The combined text of the chapter from all the pages.
        """
        # Initialize variables
        text = ""
        i = 1

        # Loop until there are no more pages to process
        while i == 1 or (str(i) in chapter_html.title.string):  # type: ignore
            logger.info(f"Processing page {i}")

            # Extract the content of the chapter parts from the current page
            chapter_parts = chapter_html.findAll(attrs={"data-p-id": True})
            part = "\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in chapter_parts
            )
            text += part

            # Move to the next page
            i += 1
            new_page_url = url + f"/page/{i}"
            chapter_html = get_content(new_page_url)  # type: ignore

        return text

    def _write(self, file_path: Path, content: str):
        logger.debug(f"Writing to file {file_path} {len(content)} characters")
        with open(file_path, "a") as f:
            f.write(content)

    def _rename(self, path: Path, new_name: str):
        new_path = Path(path.parent, f"{new_name}{path.suffix}")
        logger.info(f"Renaming file {path} -> {new_path}")
        path.rename(new_path)
        self.story.text_path = new_path
