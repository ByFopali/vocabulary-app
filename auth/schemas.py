from datetime import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: Annotated[str, MinLen(5), MaxLen(50)]
    hashed_password: Annotated[str, MinLen(8)]
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    pass


class UserUpdatePartial(UserCreate):
    username: str | None = None
    hashed_password: str | None = None
    email: str | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class CurrentUserData(BaseModel):
    id: int
    username: str
    email: str


class UserShow(BaseModel):
    id: int
    username: Annotated[str, MinLen(5), MaxLen(50)]
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
