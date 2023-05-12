from pathlib import Path
from tests.app.conftest import REAL_AO3_URL
from app.main import make_tts

import pytest


@pytest.mark.vcr()
def test_make_tts(
    tmp_path: Path,
):
    result = make_tts(source=REAL_AO3_URL, to_save_path=tmp_path)
    assert result
