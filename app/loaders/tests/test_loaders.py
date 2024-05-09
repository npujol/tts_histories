from app.loaders import load_story
from pytest_insta.fixture import SnapshotFixture

import pytest

REAL_AO3_URL = (
    "https://archiveofourown.org/downloads/55724413/Video.html?updated_at=1715002036"
)
REAL_WATTPAD_URL = "https://www.wattpad.com/story/57740438-el-caminante-y-la-verdad"
REAL_WATTPAD_CHAPTER_URL = "https://www.wattpad.com/198877707-el-caminante-y-la-verdad"


@pytest.mark.vcr()
def test_ao3_load(
    snapshot: SnapshotFixture,
):
    result = load_story(REAL_AO3_URL)
    assert result
    assert snapshot("json") == result.json(exclude={"content": True})


@pytest.mark.vcr()
def test_wattpad_load(snapshot: SnapshotFixture):
    result = load_story(REAL_WATTPAD_URL)
    assert result
    assert snapshot("json") == result.json(exclude={"content": True})


@pytest.mark.vcr()
def test_wattpad_chapter_load(snapshot: SnapshotFixture):
    result = load_story(REAL_WATTPAD_CHAPTER_URL)
    assert result
    assert snapshot("json") == result.json(exclude={"content": True})
