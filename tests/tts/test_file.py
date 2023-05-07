import logging
from tts.file import FileStory
import pytest
from unittest import mock

logging.basicConfig(level=logging.DEBUG)


def test_file_story_extract_content(file_story: FileStory):
    file_story.extract_content()
    assert len(file_story.story.content) == 1
    assert len(file_story.story.content[0].sentences) == 2


def test_file_story_create_audio(file_story: FileStory):
    file_story.extract_content()
    file_path = file_story.create_audio()
    assert file_path.exists()


@pytest.mark.vcr()
def test_file_story_send_to_telegram(
    file_story: FileStory,
    snapshot,  # type: ignore
    monkeypatch,  # type: ignore
):
    file_story.extract_content()
    assert snapshot() == file_story.story.language
    assert snapshot() == "|".join(
        sorted(p.model_dump_json() for p in file_story.story.content)
    )

    filename = file_story.create_audio()

    send_to_telegram_mock = mock.Mock()
    monkeypatch.setattr(  # type: ignore
        "tts.file.send_to_telegram",
        send_to_telegram_mock,
    )

    file_story.run()
    send_to_telegram_mock.assert_called_with(filename, file_story.story.title)
