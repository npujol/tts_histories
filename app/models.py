
from enum import Enum
from lib2to3.pgen2.token import OP
from pathlib import Path
from typing import Optional
import uuid
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
