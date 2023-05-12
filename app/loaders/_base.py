from abc import ABC, abstractmethod
import logging
from pathlib import Path

from app.serializers import RawStory


logger = logging.getLogger(__file__)



class Base(ABC):
    @abstractmethod
    def can_handle(self, source: str) -> bool:
        ...

    @abstractmethod
    def load(self, source: str) -> RawStory:
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

