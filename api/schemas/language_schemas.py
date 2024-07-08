from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict


class LanguageBase(BaseModel):
    name: Annotated[str, MinLen(4), MaxLen(20)]


class Language(LanguageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LanguageCreate(LanguageBase):
    pass


class LanguageUpdatePartial(LanguageCreate):
    name: str | None = None
