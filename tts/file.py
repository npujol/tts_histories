import logging
import shutil
import time
import uuid
from pathlib import Path

from nltk.tokenize import sent_tokenize  # type: ignore

from tts.serializers import Language, Paragraph, Sentence, Story, TTSType
from tts.telegram_handler import send_to_telegram
from tts.tts_stories import merge_audio_files, create_TTS, read_text

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
        self.tokenize()
        logger.info("Creating audio")
        file_path = self.create_audio()
        logger.info("Audio completed")

        logger.info("Sending to telegram")
        send_to_telegram(self.story.saved_text_path, self.story.title)
        send_to_telegram(file_path, self.story.title)
        logger.info("Finished sending to telegram")
        self.story.saved_text_path.unlink()
        file_path.unlink()

    def tokenize(self):
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

    def create_audio(self) -> Path:
        parent_path = (self.story.saved_text_path.parent / "temp").absolute()
        parent_path.mkdir(exist_ok=True)

        for paragraph_idx, paragraph in enumerate(self.story.content):
            paragraph_path = parent_path / f"paragraph_{paragraph_idx}"
            paragraph_path.mkdir(exist_ok=True)

            for sentence_idx, sentence in enumerate(paragraph.sentences):
                sentence_path = paragraph_path / f"sentence_{sentence_idx}"
                logger.debug(f"Saving audio to {sentence_path}")

                for _ in range(RETRY_ATTEMPTS):
                    try:
                        time.sleep(3)
                        create_TTS(
                            TTSType.GOOGlE,
                            sentence_path,
                            sentence.content,
                            self.story.language,
                        )
                        break
                    except Exception as e:
                        logger.exception(
                            f"TTS failed due to {e}", exc_info=True
                        )
                else:
                    logger.error(
                        f"Failed to create audio for sentence {sentence_idx} in "
                        f"paragraph {paragraph_idx}"
                    )
                    continue

            merge_audio_files(f"paragraph_{paragraph_idx}", paragraph_path)
            shutil.rmtree(paragraph_path)

        return merge_audio_files(
            f"{self.story.title}-{self.story.id}", parent_path
        )
