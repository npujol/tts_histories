import os
import tempfile
from pathlib import Path
from tts.tts_stories import save_text, get_content, read_text, create_TTS
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import pytest


# Test save_text function
def test_save_text():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        # Prepare test data
        title = "test_title"
        text = "This is a test text."
        expected_file = temp_dir / f"{title}.txt"
        expected_content = f"{text}"

        # Call the function to save the text
        file_path = save_text(title, text, temp_dir)

        # Assert that the file is created with the correct path and content
        assert file_path == expected_file
        assert expected_file.exists()
        assert expected_file.read_text() == expected_content

        # Clean up the temporary file
        os.remove(expected_file)


def test_get_content_successful():
    url = "https://example.com"

    # Mock successful response
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

    # Mock HTTPError response
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

    # Mock RequestException response
    def requests_get(*args, **kwargs):  # type: ignore
        return raise_exception(RequestException("Connection error"))

    requests.get = requests_get

    result = get_content(url)
    expected = None
    assert result == expected


def test_read_text():
    # Create a temporary file with some text
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("hello\nworld\n")

    # Call the read_text function to read the temporary file
    filename = Path(f.name)
    content = read_text(filename)

    # Check that the function returned the expected content
    assert content == "hello\nworld"

    # Clean up the temporary file
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


@pytest.fixture
def tts_file():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        yield Path(f.name)
    # Clean up the temporary file


def test_create_TTS(tts_file: Path):
    # Test that TTS file is created successfully
    text = "Hello, world!"
    language = "en"
    create_TTS(tts_file, text, language)
    assert os.path.exists(tts_file)


# Helper function to raise an exception
def raise_exception(exception: Exception):
    raise exception
