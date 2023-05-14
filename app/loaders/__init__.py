from typing import Optional

from app.serializers import RawStory
from app.loaders.ao3_loader import AO3Loader
from app.loaders.wattpad_loader import WattpadLoader, WattpadChapterLoader
from app.loaders.file_loader import FileLoader

_loaders = [AO3Loader(), FileLoader(), WattpadLoader(), WattpadChapterLoader()]


def load_story(source: str) -> Optional[RawStory]:
    for loader in _loaders:  # type: ignore
        if loader.can_handle(source):  # type: ignore
            return loader.load(source)  # type: ignore
