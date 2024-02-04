from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .word import Word
    from .topic_word_association import TopicWordAssociation
    from .language import Language


class Topic(Base):

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    language_id: Mapped[int] = mapped_column(
        ForeignKey("languages.id"),
    )

    # use or words or words_details!
    # words: Mapped[list["Word"]] = relationship(
    #     secondary="topic_word_association",
    #     back_populates="topics",
    # )

    words_details: Mapped[list["TopicWordAssociation"]] = relationship(
        back_populates="topic",
    )

    language: Mapped["Language"] = relationship(
        "Language",
        back_populates="topics",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __repr__(self):
        return str(self)
