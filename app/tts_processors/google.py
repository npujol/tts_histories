from abc import abstractmethod
import logging
from pathlib import Path
from gtts import gTTS  # type: ignore
from app.tts_processors._base import Base

from app.serializers import RawStory, TTSType


logger = logging.getLogger(__file__)


class GoogleTTS(Base):
    tts_type = TTSType.GOOGlE

    def can_handle(self, story: RawStory, tts_type: TTSType) -> bool:
        return (
            tts_type == self.tts_type
            and story.content != ""
            and story.language is not None
        )

    @abstractmethod
    def clean(self, story: RawStory) -> Path:
        ...

    def make(self, story: RawStory, file_path: Path) -> Path | None:
        attempts = 5
        while attempts:
            try:
                tts = gTTS(story.content, lang=story.language)  # type: ignore
                tts.save(f"{file_path}.mp3")  # type: ignore
                return file_path
            except Exception as e:
                logger.warning(f"Error creating TTS audio: {e}")
                attempts -= 1
