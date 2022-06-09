import uuid
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Language(str, Enum):
    SPANISH = "es"
    ENGLISH = "en"
    GERMAN = "de"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Sentence(BaseModel):
    content: str
    audio_path: str = ""


class Paragraph(BaseModel):
    audio_path: Optional[Path] = None
    sentences: list[Sentence] = []


class Story(BaseModel):
    title: str = "None"
    id: uuid.UUID
    saved_text_path: Path
    language: Language = Language.SPANISH
    content: list[Paragraph] = []


class Chapter(BaseModel):
    id: uuid.UUID
    url: str
    text: str = ""
    text_path: Optional[Path] = None


class WattpadStory(BaseModel):
    id: uuid.UUID
    url: str
    title: str = "None"
    text_path: Path
    language: Language = Language.SPANISH
    chapters: list[Chapter] = []
