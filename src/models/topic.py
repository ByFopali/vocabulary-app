from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .topic_word_association import TopicWordAssociation
    from .language import Language
    from .user import User


class Topic(Base):

    name: Mapped[str] = mapped_column(
        String(50),
        unique=False,
        nullable=False,
    )

    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    words_details: Mapped[list["TopicWordAssociation"]] = relationship(
        back_populates="topic",
        cascade="all, delete, delete-orphan",
    )

    language: Mapped["Language"] = relationship(
        # "Language",
        back_populates="topics",
    )

    user: Mapped["User"] = relationship(
        # "Language",
        back_populates="topics",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __repr__(self):
        return str(self)
