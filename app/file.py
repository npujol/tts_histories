import logging
import shutil
import glob
import re
import os
from urllib.request import Request, urlopen
import uuid
from bs4 import BeautifulSoup
from urllib3 import Retry
from gtts import gTTS
from app.tts_stories import read_text, combine_audio, create_TTS
from app.models import Language, Story, Sentence, Paragraph
from nltk.tokenize import sent_tokenize
from pathlib import Path
from pydub import AudioSegment

SIZE = 10
RETRY_ATTEMPTS = 10
URL_BASE_WATTPAD = "https://www.wattpad.com"
WATTPAD_BASE_DIR = os.getcwd()
RE_CLEAN = re.compile(r"\/")
RE_SPACES = re.compile(r"\s+")

logger = logging.getLogger(__file__)


class FileStory:
    def __init__(self, path: Path, language: Language = Language.SPANISH):
        self.story = Story(id=uuid.uuid1(), language=language, saved_text_path=path)
        self.story.title = str(path).split(".")[0]

    def run(self):
        self.extract_content()
        logger.info(f"Init tts story: {self.story.id}")
        self.create_audio()
        logger.info(f"Complete tts story: {self.story.id}")

    def extract_content(self):
        # Convert the text into paragraphs
        sentences = list(Sentence(content=s) for s in sent_tokenize(read_text(self.story.saved_text_path)))
        self.story.content = [Paragraph(sentences=sentences[s:s+SIZE]) for s in range(0, len(sentences), SIZE)]

    def create_audio(self):
        parent_path = self.story.saved_text_path.parent / "temp"
        for x, p in enumerate(self.story.content):
            for k, s in enumerate(p.sentences):
                temp_path = parent_path / f"{x}"
                temp_path.mkdir(exist_ok=True)
                part = temp_path / str(k)
                retry_attempts = RETRY_ATTEMPTS
                while retry_attempts:
                    try:
                        create_TTS(part, s.content, self.story.language)
                    except Exception as e:
                        logger.exception(f"Retrying {retry_attempts}, TTS failed due to {e}", exc_info=True)
                        retry_attempts -= 1
                combine_audio(temp_path, f"{x}")

        combine_audio(parent_path, f"{self.story.title}-{self.story.id}")
