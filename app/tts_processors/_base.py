from abc import ABC, abstractmethod
import logging
from pathlib import Path

from app.serializers import RawStory, TTSType


logger = logging.getLogger(__file__)


class Base(ABC):
    @abstractmethod
    def can_handle(self, story: RawStory, tts_type: TTSType) -> bool:
        ...

    @abstractmethod
    def clean(self, story: RawStory) -> Path:
        ...

    @abstractmethod
    def make(self, story: RawStory, file_path: Path) -> Path | None:
        ...
