import html

from bs4 import BeautifulSoup
from app.serializers import RawStory
import logging
from app.loaders._base import Base
from app.tts_stories import get_content, get_raw_content
import re
from urllib.parse import urlparse

WATTPAD_STORY_URL_REGEX = re.compile(r"^\/story\/\d+-[a-zA-Z0-9%-]+$")
WATTPAD_CHAPTER_URL_REGEX = re.compile(r"^\/\d+-[a-zA-Z0-9%-]+$")
WATTPAD_HOSTNAME = "www.wattpad.com"
URL_BASE_WATTPAD = "https://www.wattpad.com"


logger = logging.getLogger(__file__)


class WattpadLoader(Base):
    def can_handle(self, source: str) -> bool:
        try:
            parsed_url = urlparse(source)
            return parsed_url.hostname == WATTPAD_HOSTNAME and (
                bool(WATTPAD_STORY_URL_REGEX.match(parsed_url.path))
            )
        except Exception:
            return False

    def load(self, source: str) -> RawStory:
        logger.info(f"Starting the download from {source}")
        response = get_raw_content(source)
        content = "\n"
        title = ""
        if response:
            content_soup = BeautifulSoup(response.content, "html.parser")
            title_soup = content_soup.find(
                "div", attrs={"class": "story-info__title"}  # type: ignore
            )
            if title is not None:
                title = title_soup.text  # type: ignore
                content += f"\n{title}"

            author_soup = content_soup.find(
                "div", attrs={"class": "author-info__username"}
            )  # type: ignore

            if author_soup is not None:
                content += f"\n{author_soup.text}"

            summary_soup = content_soup.find(  # type: ignore
                "pre", attrs={"class": "description-text"}
            )
            if summary_soup is not None:
                content += f"\n{summary_soup.text}"

            chapters = content_soup.find(  # type: ignore
                "div",
                attrs={
                    "class": "story-parts",
                },
            ).find_all(  # type: ignore
                "a",
                attrs={
                    "class": "story-parts__part",
                },
            )
            for ch in chapters:  # type: ignore
                href = ch.get("href")  # type: ignore
                url_chapter = URL_BASE_WATTPAD + href  # type: ignore
                if url_chapter is not None and isinstance(url_chapter, str):
                    content += extract_info_from_wattpad_chapter(url_chapter)
        return RawStory(
            title=title,
            url=source,
            content=content,
        )


class WattpadChapterLoader(Base):
    def can_handle(self, source: str) -> bool:
        try:
            parsed_url = urlparse(source)
            return parsed_url.hostname == WATTPAD_HOSTNAME and (
                bool(WATTPAD_CHAPTER_URL_REGEX.match(parsed_url.path))
            )
        except Exception:
            return False

    def load(self, source: str) -> RawStory:
        logger.info(f"Starting the download from {source}")
        response = get_raw_content(source)
        if response:
            content = BeautifulSoup(response.content, "html.parser")

        return RawStory(
            title=content.title.text if content else "",  # type: ignore
            url=source,
            content=extract_info_from_wattpad_chapter(source),
        )


def extract_info_from_wattpad_chapter(url: str) -> str:
    """Extracts the chapter title and content from a Wattpad chapter URL.

    Args:
        url (str): The URL of the Wattpad chapter to extract information from.

    Returns:
        str: A string containing the chapter title and content.
    """
    text = "\n"
    chapter_html = get_content(url)
    if chapter_html is not None:
        title_element = chapter_html.find(
            "h1",
            attrs={"class": "h2"},
        )
        text += title_element.text if title_element is not None else ""
        if chapter_html:
            i = 1
            while i == 1 or (str(i) in chapter_html.title.string):  # type: ignore
                if chapter_html is None:
                    break
                chapter_parts = chapter_html.findAll(attrs={"data-p-id": True})
                part = "\n".join(
                    html.unescape(p.text).replace("\u2022" * 3, "").strip()
                    for p in chapter_parts
                )
                text += part

                i += 1
                new_page_url = url + f"/page/{i}"
                chapter_html = get_content(new_page_url)
    return text
