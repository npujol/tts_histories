import logging

from pathlib import Path
from app.serializers import Language, RawStory, TTSType
from app.tts_processors._base import Base
from TTS.api import TTS  # type: ignore


MAP_LANGUAGE_MODEL = {Language.SPANISH: "tts_models/es/css10/vits"}
SENTENCE_COUNT = 200


logger = logging.getLogger(__file__)


class CoquiTTS(Base):
    tts_type = TTSType.C0QUI

    def __init__(self, story: RawStory):
        super().__init__(story)
        self.tts_handler: TTS = self._init_tts_handler()
        self.sentence_count = SENTENCE_COUNT

    def _init_tts_handler(self):
        if not isinstance(self.story.language, Language):
            raise ValueError(
                "Error in the tts handler creation. "
                "Story doesn't have a valid language."
            )

        if not self.story.content:
            raise ValueError(
                "Error in the tts handler creation. "
                "Story doesn't have a valid content."
            )

        model = MAP_LANGUAGE_MODEL.get(self.story.language, None)
        if model is None:
            list_models: list[str] = [
                m
                for m in TTS.list_models()  # type: ignore
                if f"/{self.story.language}/" in m
            ]
            if not list_models:
                raise ValueError(
                    "Error in the tts handler creation. There's not available "
                    f"model for language: {self.story.language}."
                )
            model = list_models[0]

        return TTS(
            model_name=model,
            progress_bar=False,
            gpu=False,
        )

    def _make_tts(self, text: str, path: Path):
        self.tts_handler.tts_to_file(
            text,
            file_path=f"{path}",
        )
