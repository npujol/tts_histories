from bs4 import BeautifulSoup
from app.serializers import RawStory
from urllib.parse import urlparse
import html
import logging
from app.loaders._base import Base

from app.tts_stories import get_raw_content
import re


logger = logging.getLogger(__file__)

AO3_HOSTNAME = "archiveofourown.org"
AO3_REGEX = re.compile(r"^\/downloads\/\d+/[a-zA-Z0-9%-]+\.html$")


class AO3Loader(Base):
    def can_handle(self, source: str) -> bool:
        try:
            parsed_url = urlparse(source)
            return parsed_url.hostname == AO3_HOSTNAME and bool(
                AO3_REGEX.match(parsed_url.path)
            )
        except Exception:
            return False

    def load(self, source: str) -> RawStory:
        logger.info(f"Starting the download from {source}")
        response = get_raw_content(source)
        if response:
            content = BeautifulSoup(response.content, "html.parser")

        return RawStory(
            title=content.title.string if content else "",  # type: ignore
            url=source,
            content="\n".join(
                html.unescape(t.text).replace("\u2022" * 3, "").strip()
                for t in content.findAll("p")  # type: ignore
            ),
        )
