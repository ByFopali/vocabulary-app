from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict


class GrammarElementBase(BaseModel):
    name: Annotated[str, MinLen(4), MaxLen(20)]


class GrammarElement(GrammarElementBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GrammarElementCreate(GrammarElementBase):
    pass


class GrammarElementUpdatePartial(GrammarElementCreate):
    name: str | None = None
