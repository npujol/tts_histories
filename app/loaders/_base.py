from abc import ABC, abstractmethod
import logging
from pathlib import Path

from bs4 import BeautifulSoup
from app.serializers import RawStory
from urllib.parse import ParseResult
import re
import html

from app.tts_stories import get_raw_content

logger = logging.getLogger(__file__)


AO3_REGEX = re.compile(
    r"^https://archiveofourown\.org/downloads/\d+/.+\.html\?updated_at=\d+$"
)


class Base(ABC):
    @abstractmethod
    def can_handle(self, parsed_url: ParseResult) -> bool:
        ...

    @abstractmethod
    def load(self, url: str) -> RawStory:
        ...

    def write(self, file_path: Path, content: str):
        logger.info(f"Writing to file {file_path} {len(content)} characters")
        with open(file_path, "a") as f:
            f.write(content)

    def rename(self, path: Path, new_name: str):
        new_path = Path(path.parent, f"{new_name}{path.suffix}")
        logger.info(f"Renaming file {path} -> {new_path}")
        path.rename(new_path)
        return new_path


class AO3Loader(Base):
    def can_handle(self, parsed_url: ParseResult) -> bool:
        return True if AO3_REGEX.match(parsed_url.geturl()) else False

    def load(self, url: str) -> RawStory:
        logger.info(f"Starting the download from {url}")
        response = get_raw_content(url)
        if response:
            content = BeautifulSoup(response.content, "html.parser")

        return RawStory(
            title=content.title.string if content else "",  # type: ignore
            url=url,
            content="\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in content.findAll("p")  # type: ignore
            ),
        )
