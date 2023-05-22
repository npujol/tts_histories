from pathlib import Path
from app.main import make_tts

import pytest

from app.tests.conftest import REAL_AO3_URL


@pytest.mark.vcr()
def test_make_tts(
    tmp_path: Path,
):
    file_path = tmp_path.joinpath("out.mp3")
    result = make_tts(source=REAL_AO3_URL, out_path=file_path)
    assert result
