from datetime import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: Annotated[str, MinLen(5), MaxLen(50)]
    hashed_password: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(UserCreate):
    pass


class UserUpdatePartial(UserCreate):
    username: str | None = None
    hashed_password: str | None = None
    email: EmailStr | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


# class TokenSchema(BaseModel):
#     access_token: str
#     refresh_token: str
