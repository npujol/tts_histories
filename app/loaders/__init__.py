# from ao3 import AO3Loader
# from wattpad import WTFLoader
from typing import Optional
from urllib.parse import urlparse

from app.serializers import RawStory
from app.loaders._base import AO3Loader

_loaders = [AO3Loader()]


def load_story(url: str) -> Optional[RawStory]:
    parsed_url = urlparse(url)
    for loader in _loaders:  # type: ignore
        if loader.can_handle(parsed_url):  # type: ignore
            return loader.load(url)  # type: ignore
