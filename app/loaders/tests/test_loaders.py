from app.loaders import load_story
from pytest_insta.fixture import SnapshotFixture

import pytest

REAL_AO3_URL = "https://archiveofourown.org/downloads/41826891/Complicidad.html?updated_at=1677757090"
REAL_WATTPAD_URL = "https://www.wattpad.com/story/157495653-el-tren"
REAL_WATTPAD_CHAPTER_URL = "https://www.wattpad.com/613460718-el-tren"


@pytest.mark.vcr()
def test_ao3_load(
    snapshot: SnapshotFixture,
):
    result = load_story(REAL_AO3_URL)
    assert result
    assert snapshot("json") == result.json()


@pytest.mark.vcr()
def test_wattpad_load(snapshot: SnapshotFixture):
    result = load_story(REAL_WATTPAD_URL)
    assert result
    assert snapshot("json") == result.json()


@pytest.mark.vcr()
def test_wattpad_chapter_load(snapshot: SnapshotFixture):
    result = load_story(REAL_WATTPAD_CHAPTER_URL)
    assert result
    assert snapshot("json") == result.json()
