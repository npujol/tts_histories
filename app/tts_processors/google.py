import logging
from pathlib import Path
import time
from gtts import gTTS  # type: ignore
from app.tts_processors._base import Base

from app.serializers import RawStory, TTSType

SENTENCE_COUNT = 10

logger = logging.getLogger(__file__)


class GoogleTTS(Base):
    tts_type = TTSType.GOOGlE

    def __init__(self, story: RawStory):
        super().__init__(story)
        self.sentence_count = SENTENCE_COUNT

    def _make_tts(self, text: str, path: Path):
        time.sleep(2)
        attempts = 5
        while attempts:
            try:
                tts = gTTS(text, lang=self.story.language)  # type: ignore
                tts.save(str(path))  # type: ignore
            except Exception as e:
                logger.warning(f"Error creating TTS audio: {e}")
                time.sleep(3)
                attempts -= 1
