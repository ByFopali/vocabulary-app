from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict, Field


class TopicBase(BaseModel):
    name: Annotated[str, MinLen(4), MaxLen(20)]
    language_id: Annotated[int, Field(gt=0)]
    # user_id: Annotated[int, Field(gt=0)]


class Topic(TopicBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


class TopicCreate(TopicBase):
    pass


class TopicUpdatePartial(TopicCreate):
    name: str | None = None
    language_id: int | None = None
    # user_id: int | None = None
