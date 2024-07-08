from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .word import Word
    from .topic import Topic


class TopicWordAssociation(Base):
    __tablename__ = "topic_word_association"
    __table_args__ = (
        UniqueConstraint(
            "topic_id",
            "word_id",
            name="idx_unique_topic_word",
        ),
    )

    word_id: Mapped[int] = mapped_column(
        ForeignKey(
            "words.id",
            ondelete="CASCADE",
        )
    )
    topic_id: Mapped[int] = mapped_column(
        ForeignKey(
            "topics.id",
            ondelete="CASCADE",
        )
    )

    # association between Assocation -> Word
    word: Mapped["Word"] = relationship(
        back_populates="topics_details",
    )
    # association between Assocation -> Topic
    topic: Mapped["Topic"] = relationship(
        back_populates="words_details",
    )
