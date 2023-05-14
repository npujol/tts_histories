

from pathlib import Path
from app.serializers import RawStory
import logging
from app.loaders._base import Base
from app.tts_stories import read_text



logger = logging.getLogger(__file__)

class FileLoader(Base):
    def can_handle(self, source: str) -> bool:
        try:
            path = Path(source)
            return path.exists() and path.is_file()
        except Exception:
            return False

    def load(self, source: str) -> RawStory:
        logger.info(f"Starting to load content from {source}")
        return RawStory(
            title=str(source).split(".")[0],  # type: ignore
            url=source,
            content=read_text(Path(source))
        )
