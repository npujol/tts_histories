from abc import ABC, abstractmethod
import logging
from pathlib import Path

from typing import Generator, Iterable, Optional
from app.serializers import RawStory
from tempfile import TemporaryDirectory

import ffmpeg  # type: ignore
from itertools import zip_longest
import pysbd  # type: ignore


logger = logging.getLogger(__file__)


class Base(ABC):
    sentence_count = 1

    def __init__(self, story: RawStory) -> None:
        self.story = story
        super().__init__()

    def clean_paragraphs(self) -> Generator[str, None, None]:
        cleaner = pysbd.Segmenter(language=self.story.language, clean=True)
        sentences: list[Iterable[str]] = [
            iter(cleaner.segment(self.story.content))  # type: ignore
        ] * self.sentence_count
        return (
            " ".join(v for v in part if v).strip()
            for part in zip_longest(*sentences, fillvalue="")
        )

    def make(self, out_path: Path) -> Optional[Path]:
        temp_files: list[str] = []
        paragraphs = self.clean_paragraphs()
        with TemporaryDirectory(dir=out_path.parent) as tmpdir:
            for pos, text in enumerate(paragraphs):  # type: ignore
                temp_name = f"{pos:04d}"
                temp_path = Path(tmpdir) / temp_name
                temp_files.append(str(temp_path))
                self._make_tts(text, temp_path)

            inputs = [ffmpeg.input(str(f)) for f in temp_files]  # type: ignore
            ffmpeg.concat(*inputs, a=1, v=0).output(str(out_path)).run(  # type: ignore
                overwrite_output=True
            )
        return out_path

    @abstractmethod
    def _make_tts(self, text: str, path: Path): ...
