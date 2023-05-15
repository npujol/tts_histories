from abc import abstractmethod
import logging
from pathlib import Path
from typing import Optional

from app.serializers import Language, RawStory, TTSType
from app.tts_processors._base import Base
from TTS.api import TTS  # type: ignore


logger = logging.getLogger(__file__)
MAP_LANGUAGE_MODEL = {Language.SPANISH: "tts_models/es/css10/vits"}


class CoquiTTS(Base):
    tts_type = TTSType.C0QUI

    def can_handle(self, story: RawStory, tts_type: TTSType) -> bool:
        return (
            tts_type == self.tts_type
            and story.content != ""
            and story.language is not None
        )

    @abstractmethod
    def clean(self, story: RawStory) -> Path:
        ...

    def make(self, story: RawStory, file_path: Path) -> Optional[Path]:
        if isinstance(story.language, Language) and not story.content:
            model = MAP_LANGUAGE_MODEL.get(story.language, None)
            if model is None:
                list_models: list[str] = [
                    m
                    for m in TTS.list_models()  # type: ignore
                    if f"/{story.language}/" in m
                ]
                if not list_models:
                    return
                model = list_models[0]
            tts = TTS(
                model_name=model,
                progress_bar=False,
                gpu=False,
            )
            tts.tts_to_file(
                story.content,
                file_path=f"{file_path}",
            )
            return file_path
