from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .language import Language


class LanguageUserAssociation(Base):
    __tablename__ = "language_user_association"
    __table_args__ = (
        UniqueConstraint(
            "language_id",
            "user_id",
            name="idx_unique_language_user",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
    )

    # association between Assocation -> Word
    user: Mapped["User"] = relationship(
        back_populates="languages_details",
    )
    # association between Assocation -> Topic
    language: Mapped["Language"] = relationship(
        back_populates="users_details",
    )
