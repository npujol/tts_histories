from tests.app.conftest import (
    REAL_AO3_URL,
    REAL_WATTPAD_CHAPTER_URL,
    REAL_WATTPAD_URL,
)
from app.loaders import load_story

import pytest


@pytest.mark.vcr()
def test_ao3_load(
    snapshot,  # type: ignore
):
    result = load_story(REAL_AO3_URL)
    assert result
    assert snapshot("json") == result.json()


@pytest.mark.vcr()
def test_wattpad_load(
    snapshot,  # type: ignore
):
    result = load_story(REAL_WATTPAD_URL)
    assert result
    assert snapshot("json") == result.json()


@pytest.mark.vcr()
def test_wattpad_chapter_load(
    snapshot,  # type: ignore
):
    result = load_story(REAL_WATTPAD_CHAPTER_URL)
    assert result
    assert snapshot("json") == result.json()
