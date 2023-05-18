from pathlib import Path
from tests.app.conftest import REAL_AO3_URL
from app.main import make_tts

import pytest


@pytest.mark.vcr()
def test_make_tts(
    tmp_path: Path,
):
    file_path = tmp_path.joinpath("out.mp3")
    result = make_tts(source=REAL_AO3_URL, out_path=file_path)
    assert result
