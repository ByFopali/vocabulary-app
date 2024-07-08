from typing import TYPE_CHECKING
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .topic import Topic


class Language(Base):

    name: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
    )

    topics: Mapped[list["Topic"]] = relationship(
        # "Topic",
        back_populates="language",
    )

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"

    def __repr__(self):
        return str(self)
