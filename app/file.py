import logging
import shutil
import time
import uuid
from pathlib import Path

from nltk.tokenize import sent_tokenize  # type: ignore

from app.models import Language, Paragraph, Sentence, Story
from app.tts_stories import combine_audio, create_TTS, read_text

SIZE = 30
RETRY_ATTEMPTS = 10
logger = logging.getLogger(__file__)


class FileStory:
    """Class to create a audio file from a file
    Params:
        path: Path
        language: Language(Default: Language.SPANISH)
    Attributes:
        story: Story
    """

    def __init__(self, path: Path, language: Language = Language.SPANISH):
        self.story = Story(
            id=uuid.uuid1(), language=language, saved_text_path=path
        )
        self.story.title = str(path).split(".")[0]
        logger.info(
            f"Creating story({self.story.title} in {self.story.language} "
            f"from {self.story.saved_text_path})"
        )

    def run(self):
        self.extract_content()
        logger.info("Creating audio")
        self.create_audio()
        logger.info("Audio completed")

    def extract_content(self):
        # Convert the text into paragraphs
        sentences = list(
            Sentence(content=s)  # type: ignore
            for s in sent_tokenize(  # type: ignore
                read_text(self.story.saved_text_path)
            )
        )
        self.story.content = [
            Paragraph(sentences=sentences[s : s + SIZE])  # noqa
            for s in range(0, len(sentences), SIZE)
        ]

    def create_audio(self):
        parent_path = self.story.saved_text_path.parent.absolute() / "temp"
        parent_path.mkdir(exist_ok=True)
        for x, p in enumerate(self.story.content):
            temp_path = parent_path / f"{x}"
            temp_path.mkdir(exist_ok=True)
            for k, s in enumerate(p.sentences):
                part = temp_path / f"sentence_{k}"
                logger.debug(f"Saving audio to {part}")
                retry_attempts = RETRY_ATTEMPTS
                while retry_attempts:
                    try:
                        time.sleep(3)
                        create_TTS(part, s.content, self.story.language)
                        break
                    except Exception as e:
                        logger.exception(
                            f"Retrying {retry_attempts} TTS failed due to {e}",
                            exc_info=True,
                        )
                        retry_attempts -= 1
            combine_audio(temp_path, f"paragraph_{x}")
            shutil.rmtree(temp_path)

        combine_audio(parent_path, f"{self.story.title}-{self.story.id}")
