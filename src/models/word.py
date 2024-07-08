from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .grammar_element import GrammarElement
    from .topic_word_association import TopicWordAssociation
    from .topic import Topic


class Word(Base):

    learnt_word: Mapped[str] = mapped_column(
        String(20),
        unique=False,
        nullable=False,
    )

    definition: Mapped[str] = mapped_column(
        String(100),
        unique=False,
        nullable=False,
    )

    example: Mapped[str] = mapped_column(
        Text,
        unique=False,
        nullable=True,
        default="",
        server_default="",
    )

    grammar_element_id: Mapped[int] = mapped_column(
        ForeignKey("grammar_elements.id"),
    )

    grammar_element: Mapped["GrammarElement"] = relationship(
        back_populates="words",
    )

    topics_details: Mapped[list["TopicWordAssociation"]] = relationship(
        back_populates="word",
        cascade="all, delete, delete-orphan",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(learnt_word={self.learnt_word}, definition={self.definition!r})"

    def __repr__(self):
        return str(self)
