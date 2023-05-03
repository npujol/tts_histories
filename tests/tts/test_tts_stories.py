import os
import tempfile
from pathlib import Path
from tts.tts_stories import save_text, get_content

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


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


# Helper function to raise an exception
def raise_exception(exception: Exception):
    raise exception
