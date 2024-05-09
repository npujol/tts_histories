import pytest

from pathlib import Path


REAL_AO3_URL = (
    "https://archiveofourown.org/downloads/55724413/Video.html?updated_at=1715002036"
)
TEST_AO3_URL = "https://archiveofourown.org/works/123456"
SIZE = 30
RETRY_ATTEMPTS = 10


@pytest.fixture
def tts_file(tmp_path: Path):
    file_path = tmp_path / "hello.txt"
    file_path.write_text("hello")
    return file_path
