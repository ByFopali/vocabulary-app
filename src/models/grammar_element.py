from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .word import Word


class GrammarElement(Base):
    __tablename__ = "grammar_elements"

    name: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    words: Mapped["Word"] = relationship(
        "Word",
        back_populates="grammar_element",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __repr__(self):
        return str(self)
