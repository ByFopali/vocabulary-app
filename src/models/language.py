from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .topic import Topic
    from .language_user_association import LanguageUserAssociation


class Language(Base):

    name: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
    )

    topics: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="language",
    )

    users_details: Mapped[list["LanguageUserAssociation"]] = relationship(
        back_populates="language",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __repr__(self):
        return str(self)
