from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict, Field


class WordBase(BaseModel):
    learnt_word: Annotated[str, MaxLen(20)]
    definition: Annotated[str, MaxLen(100)]
    example: Annotated[str, MaxLen(512)]
    grammar_element_id: Annotated[int, Field(gt=0)]


class Word(WordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class WordCreate(WordBase):
    pass


class WordUpdatePartial(WordCreate):
    learnt_word: str | None = None
    definition: str | None = None
    example: str | None = None
    grammar_element_id: int | None = None

