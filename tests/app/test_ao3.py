from tests.app.conftest import REAL_AO3_URL
from app.ao3 import AO3
from pathlib import Path
from app.serializers import Language

import pytest


def test_init():
    url = "https://archiveofourown.org/works/123456"
    ao3 = AO3(url)
    assert ao3.story.url == url
    assert ao3.story.language == Language.SPANISH


def test_write(tmp_path: Path):
    file_path = tmp_path.joinpath("test.txt")
    ao3 = AO3("https://archiveofourown.org/works/123456")
    ao3.write(file_path, "test content")
    with open(file_path) as f:
        assert f.read() == "test content"


def test_rename(tmp_path: Path):
    file_path = tmp_path.joinpath("test.txt")
    file_path.touch()
    ao3 = AO3("https://archiveofourown.org/works/123456")
    new_name = "new_file_name"
    ao3.rename(file_path, new_name)
    new_path = tmp_path.joinpath(f"{new_name}.txt")
    assert not file_path.exists()
    assert new_path.exists()
    assert ao3.story.text_path == new_path


def test_init_creates_file():
    url = "https://archiveofourown.org/works/123456"
    ao3 = AO3(url)
    assert ao3.story.text_path.exists()


def test_init_unique_file():
    url1 = "https://archiveofourown.org/works/123456"
    url2 = "https://archiveofourown.org/works/654321"
    ao3_1 = AO3(url1)
    ao3_2 = AO3(url2)
    assert ao3_1.story.text_path.name != ao3_2.story.text_path.name


@pytest.mark.vcr()
def test_ao3_save(
    snapshot,  # type: ignore
    tmp_path: Path,
):
    temp_file = tmp_path / "temp.txt"
    temp_file.touch()

    ao3 = AO3(
        url=REAL_AO3_URL,
        language=Language.SPANISH,
    )
    filename = ao3.save()
    assert filename.is_file()
    assert snapshot() == temp_file.read_text()
    assert snapshot() == ao3.story.title
    assert filename.name.startswith(ao3.story.title)
