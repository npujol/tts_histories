from pytest_insta.fixture import SnapshotFixture
from app.serializers import Language, RawStory, TTSType
from app.tts_processors import process_story
from pathlib import Path
import pytest

from app.tts_processors.coqui import CoquiTTS


@pytest.fixture(scope="function")
def raw_story():
    return RawStory(
        url="http://example.com",
        title="un título válido",
        language=Language.SPANISH,
        content="Este es un ejemplo de contenido, con caracteres de español.",
    )


@pytest.mark.vcr()
def test_default_tts_coqui_process(
    tmp_path: Path,
    raw_story: RawStory,
):
    out_path = tmp_path.joinpath("out.wav")
    result = process_story(story=raw_story, out_path=out_path)
    assert result
    assert out_path.is_file()
    out_path.unlink()


@pytest.mark.vcr()
@pytest.mark.parametrize(
    ("content", "language"),
    [
        ("   Ejemplo con espacios    ", Language.SPANISH),
        (
            "   Ejemplo con espacios. Dos oraciones.    ",
            Language.SPANISH,
        ),
        (
            "Un ejemplo limpio. Dos oraciones. Tres oraciones.",
            Language.SPANISH,
        ),
        (
            "Un ejemplo limpio. Dos oraciones. . ... Tres oraciones.",
            Language.SPANISH,
        ),
    ],
)
def test_clean_paragraph(
    raw_story: RawStory,
    content: str,
    language: Language,
    snapshot: SnapshotFixture,
):
    raw_story.content = content
    raw_story.language = language
    handler = CoquiTTS(story=raw_story)

    assert snapshot("json") == sorted(handler.clean_paragraphs())


@pytest.mark.skip("TODO wait to unlock google api")
@pytest.mark.vcr()
def test_default_tts_google_process(
    tmp_path: Path,
    raw_story: RawStory,
):
    out_path = tmp_path.joinpath("out.mp3")
    result = process_story(
        story=raw_story, out_path=out_path, tts_type=TTSType.GOOGlE
    )
    assert result
    assert out_path.is_file()
    out_path.unlink()
