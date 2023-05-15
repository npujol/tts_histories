from abc import ABC, abstractmethod
import logging
from pathlib import Path

from app.serializers import RawStory


logger = logging.getLogger(__file__)


class Base(ABC):
    @abstractmethod
    def can_handle(self, story: RawStory) -> bool:
        ...

    @abstractmethod
    def load(self, story: RawStory) -> Path:
        ...
