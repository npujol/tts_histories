from pathlib import Path
from tts.wattpad import Wattpad, Language
from tests.tts.conftest import REAL_WATTPAD_URL
import pytest


def test_init(
    wattpad: Wattpad,
    snapshot,  # type: ignore
):
    # Check that the Wattpad object was created successfully
    assert wattpad.story.url == REAL_WATTPAD_URL
    assert wattpad.story.language == Language.ENGLISH
    assert isinstance(wattpad.story.text_path, Path)
    assert snapshot() == "|".join(
        sorted(p.json() for p in wattpad.story.chapters)
    )


@pytest.mark.vcr()
def test_save(
    snapshot,  # type: ignore
):
    wattpad = Wattpad(REAL_WATTPAD_URL, language=Language.ENGLISH)
    # Check that the save method works as expected
    path = wattpad.save()
    if path is not None:
        assert snapshot() == "|".join(
            sorted(ch.text for ch in wattpad.story.chapters)
        )
        assert isinstance(path, Path)


@pytest.mark.vcr()
def test_write(wattpad: Wattpad, tmp_path: Path):
    # Check that the _write method works as expected
    file_path = tmp_path / "test.txt"
    wattpad._write(file_path, "Test content")  # type: ignore
    assert file_path.read_text() == "Test content"


@pytest.mark.vcr()
def test_rename(wattpad: Wattpad, tmp_path: Path):
    # Check that the _rename method works as expected
    old_path = tmp_path / "old.txt"
    old_path.write_text("Old content")
    new_name = "new"
    wattpad._rename(old_path, new_name)  # type: ignore
    new_path = tmp_path / f"{new_name}.txt"
    assert not old_path.exists()
    assert new_path.exists()
    assert new_path.read_text() == "Old content"
