from abc import ABC, abstractmethod
from serializers import Story
from urllib.parse import ParseResult

class Base(ABC):
    @abstractmethod
    def can_handle(self, parsed_url: ParseResult) -> bool:
        ...

    @abstractmethod
    def load(self, url: str) -> Story:
        ...


