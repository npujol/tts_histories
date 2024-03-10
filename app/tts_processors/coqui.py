from enum import Enum
import logging

from pathlib import Path


from app.serializers import Language, RawStory, TTSType
from app.tts_processors._base import Base
from TTS.api import TTS  # type: ignore
from collections import namedtuple


logger = logging.getLogger(__file__)


class TTSModelType(Enum):
    MULTI = "multi"
    SINGLE = "single"


TTSModelConfig = namedtuple(  # type: ignore
    "TTSModelConfig",
    [
        "model_name",
        "sentence_count",
        "type",
        "shall_add_speaker",
    ],
)

MAP_LANGUAGE_MODEL = {
    Language.SPANISH: TTSModelConfig(
        model_name="tts_models/es/css10/vits",
        sentence_count=10,
        type=TTSModelType.SINGLE,
        shall_add_speaker=True,
    ),
    Language.GERMAN: TTSModelConfig(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        sentence_count=1,
        type=TTSModelType.MULTI,
        shall_add_speaker=True,
    ),
    Language.ENGLISH: TTSModelConfig(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        sentence_count=1,
        type=TTSModelType.MULTI,
        shall_add_speaker=True,
    ),
}


class CoquiTTS(Base):
    tts_type = TTSType.C0QUI

    def __init__(self, story: RawStory):
        super().__init__(story)
        self.tts_handler, self.model_config = self._init_tts_handler()
        self.sentence_count = self.model_config.sentence_count or 1  # type: ignore

    def _init_tts_handler(self) -> tuple[TTS, TTSModelConfig]:
        if not self.story.language:
            raise ValueError(
                "Error in the tts handler creation. "
                "Story doesn't have a valid language."
            )

        if not self.story.content:
            raise ValueError(
                "Error in the tts handler creation. "
                "Story doesn't have a valid content."
            )

        model_config: TTSModelConfig | None = MAP_LANGUAGE_MODEL.get(
            self.story.language, None
        )
        if model_config is None:
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
            model_name = list_models[0]
        else:
            model_name = model_config.model_name  # type: ignore

        return (
            TTS(
                model_name=model_name,  # type: ignore
                progress_bar=False,
                gpu=False,
            ),
            model_config,
        )

    def _make_tts(self, text: str, path: Path):
        args = {
            "text": text,
            "file_path": f"{path}",
        }
        if self.model_config.type == TTSModelType.MULTI:  # type: ignore
            args["language"] = self.story.language
        if self.model_config.shall_add_speaker:  # type: ignore
            args["speaker_wav"] = str(Path(__file__).parent.parent / "speakers/me.wav")

        self.tts_handler.tts_with_vc_to_file(
            **args,
        )
