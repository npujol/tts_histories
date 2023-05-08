import pytest
from app.file import FileStory

import tempfile
from pathlib import Path
from app.serializers import Language

from app.wattpad import Wattpad

REAL_AO3_URL = "https://archiveofourown.org/downloads/41826891/Complicidad.html?updated_at=1677757090"
REAL_WATTPAD_URL = "https://www.wattpad.com/story/157495653-el-tren"
SIZE = 30
RETRY_ATTEMPTS = 10

# TODO replace by the builtin tmp_path  fixture

# @pytest.fixture(scope="function")
# def tmp_path():
#     with tempfile.TemporaryDirectory() as tmp_path:
#         yield Path(tmp_path)


@pytest.fixture(scope="function")
def file_story(tmp_path: Path):
    text = "This is a sample text for testing purposes. It contains multiple sentences."
    file_path = tmp_path / "test.txt"
    with open(file_path, "w") as f:
        f.write(text)
    story = FileStory(file_path)
    yield story


@pytest.fixture(scope="function")
def wattpad():
    # Create a new Wattpad object for testing
    wp = Wattpad(REAL_WATTPAD_URL, language=Language.ENGLISH)
    return wp


# TODO use the builtin tmp_path  fixture


@pytest.fixture
def tts_file():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        yield Path(f.name)
    # Clean up the temporary file


# TODO Seriously!
# Helper function to raise an exception
def raise_exception(exception: Exception):
    raise exception
