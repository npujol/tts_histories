import uuid
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Language(str, Enum):
    SPANISH = "es"
    ENGLISH = "en"
    GERMAN = "de"
    DEFAULT = "es"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class TTSType(str, Enum):
    GOOGlE = "google"
    C0QUI = "coqui"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Sentence(BaseModel):
    content: str
    audio_path: str = ""


class Paragraph(BaseModel):
    audio_path: Optional[Path] = None
    sentences: list[Sentence] = []


# TODO Should we exclude the fields that are not extracted from the site??


class Story(BaseModel):
    title: str = "None"
    id: uuid.UUID
    saved_text_path: Path
    language: Language = Language.SPANISH
    content: list[Paragraph] = []


class RawStory(BaseModel):
    url: str
    title: str = ""
    language: Optional[Language] = None
    content: str = ""


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


class AO3Story(BaseModel):
    id: uuid.UUID
    url: str
    title: str = "None"
    text_path: Path
    language: Language = Language.SPANISH
    chapters: list[Chapter] = []
