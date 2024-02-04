from typing import TYPE_CHECKING
from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import String, Boolean, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .language_user_association import LanguageUserAssociation


class User(Base):

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    email: Mapped[EmailStr] = mapped_column(
        String(length=56),
        unique=True,
        nullable=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    languages_details: Mapped[list["LanguageUserAssociation"]] = relationship(
        back_populates="user",
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, username={self.username}, email={self.email}, "
            f"created_at={self.created_at}, updated_at={self.updated_at!r})"
        )

    def __repr__(self):
        return str(self)
