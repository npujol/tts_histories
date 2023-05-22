import pytest

from pathlib import Path


REAL_AO3_URL = "https://archiveofourown.org/downloads/41826891/Complicidad.html?updated_at=1677757090"
REAL_WATTPAD_URL = "https://www.wattpad.com/story/157495653-el-tren"
REAL_WATTPAD_CHAPTER_URL = "https://www.wattpad.com/613460718-el-tren"
TEST_AO3_URL = "https://archiveofourown.org/works/123456"
SIZE = 30
RETRY_ATTEMPTS = 10


@pytest.fixture
def tts_file(tmp_path: Path ):
    file_path = tmp_path / "hello.txt"
    file_path.write_text("hello")
    return file_path