from tts_histories import Story

import os

cwd = os.getcwd()
s = Story(os.path.join(cwd, "test/test.txt"))


def test_clean_text():
    result = s.text_story
    assert result == "Esto es una prueba y mucho más."
