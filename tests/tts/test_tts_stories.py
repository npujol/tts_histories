import os
import tempfile
from pathlib import Path
from tts.serializers import Language, TTSType
from tts.tts_stories import (
    create_coqui_tts,
    save_text,
    get_content,
    read_text,
    create_TTS,
)
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import pytest
from tests.tts.conftest import raise_exception


def test_save_text():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        title = "test_title"
        text = "This is a test text."
        expected_file = temp_dir / f"{title}.txt"
        expected_content = f"{text}"

        file_path = save_text(title, text, temp_dir)

        assert file_path == expected_file
        assert expected_file.exists()
        assert expected_file.read_text() == expected_content

        os.remove(expected_file)


def test_get_content_successful():
    url = "https://example.com"
    response_content = (
        "<html><head></head><body><h1>Hello World</h1></body></html>"
    )
    response = requests.Response()
    response._content = response_content.encode("utf-8")
    response.status_code = 200
    response.raise_for_status = lambda: None

    def requests_get(*args, **kwargs):  # type: ignore
        return response

    original_get = requests.get
    requests.get = requests_get

    result = get_content(url)
    expected = BeautifulSoup(response_content, "html.parser")
    assert result == expected

    # Cleanup
    requests.get = original_get


def test_get_content_http_error():
    url = "https://example.com"
    response = requests.Response()
    response.status_code = 404
    response.raise_for_status = lambda: None

    def requests_get(*args, **kwargs):  # type: ignore
        return response

    requests.get = requests_get

    result = get_content(url)
    expected = None
    assert result == expected


def test_get_content_request_exception():
    url = "https://example.com"

    def requests_get(*args, **kwargs):  # type: ignore
        return raise_exception(RequestException("Connection error"))

    requests.get = requests_get

    result = get_content(url)
    expected = None
    assert result == expected


def test_read_text():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("hello\nworld\n")

    filename = Path(f.name)
    content = read_text(filename)

    assert content == "hello\nworld"

    filename.unlink()


def test_read_text_file_not_found():
    assert read_text(Path("non_existing_file.txt")) is None


def test_read_text_permission_error():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        os.chmod(temp_file.name, 0o000)
        assert read_text(Path(temp_file.name)) is None


def test_read_text_unicode_error():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("Some non-UTF-8 encoded text: \x80")
        assert read_text(Path(temp_file.name)) == ""


def test_read_text_io_error():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("Some text")
        os.chmod(temp_file.name, 0o000)
        assert read_text(Path(temp_file.name)) is None


def test_read_text_empty_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file_path = Path(temp_file.name)
        assert read_text(temp_file_path) == ""


def test_create_TTS(tts_file: Path):
    text = "Hello, world!"
    language = Language.ENGLISH
    create_TTS(TTSType.GOOGlE, tts_file, text, language)
    assert tts_file.exists()


@pytest.mark.vcr()
def test_create_coqui_TTS(tts_file: Path):
    text = "Hola, mundo!"
    language = Language.SPANISH
    create_coqui_tts(tts_file, text, language)
    assert tts_file.exists()
