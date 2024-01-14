import uuid
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from langdetect import detect  # type: ignore
from pydantic import BaseModel, root_validator

MIN_SIZE = 5000


class StrEnumBase(str, Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def available_str_values(cls):
        return "\n".join(v for v in list(cls))


class Language(StrEnumBase):
    SPANISH = "es"
    ENGLISH = "en"
    GERMAN = "de"
    DEFAULT = "es"


class TTSType(StrEnumBase):
    GOOGlE = "google"
    C0QUI = "coqui"


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


class RawStory(BaseModel):
    url: str
    title: str = ""
    language: Optional[Language] = None
    content: str = ""

    @root_validator(pre=True)
    def extract_language(cls, values: dict[str, Any]):
        language = values.get("language", None)
        content = values.get("content", None)

        if language is None and content is not None:
            to_check = content[:MIN_SIZE] if len(content) >= MIN_SIZE else content
            values["language"] = detect(to_check)

        return values


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
