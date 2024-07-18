from typing import Annotated

from fastapi import Depends, status, HTTPException
from sqlalchemy import select, Result, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.topic_crud import get_topic_by_id
from api.schemas.word_schemas import (
    WordCreate,
    WordUpdatePartial,
    Word as PydanticWord,
)
from src.models import Word, TopicWordAssociation, Topic
from auth.utils import get_current_user


async def get_word_by_id(
    session: AsyncSession,
    word_id: int,
) -> Word | None:
    return await session.get(Word, word_id)


async def create_word(
    topic_id: int,
    word: WordCreate,
    session: AsyncSession,
    # user: Annotated[dict, Depends(get_current_user)],
) -> Word:

    current_topic = await get_topic_by_id(session, topic_id)

    new_word = Word(**word.model_dump())

    new_word.topics_details.append(
        TopicWordAssociation(topic=current_topic, word=new_word)
    )

    session.add(new_word)
    await session.commit()

    return new_word


async def update_word(
    word_update: WordUpdatePartial,
    word: PydanticWord,
    session: AsyncSession,
    partial: bool = True,
) -> Word:
    for name, value in word_update.model_dump(exclude_unset=partial).items():
        setattr(
            word,
            name,
            value,
        )
    await session.commit()
    return word


async def get_all_words(
    session: AsyncSession,
) -> list[Word]:
    stmt = select(Word).order_by(Word.id)
    result: Result = await session.execute(stmt)
    words = result.scalars().all()
    return list(words)


async def get_all_words_for_specific_topic(
    topic_id: int,
    session: AsyncSession,
    user: Annotated[dict, Depends(get_current_user)],
) -> list[Word]:

    stmt = select(Topic).where(Topic.id == topic_id, Topic.user_id == user["id"])
    result: Result = await session.execute(stmt)
    topic = result.scalars().first()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or does not belong to the authenticated user",
        )

    stmt = (
        select(Word)
        .join(TopicWordAssociation, TopicWordAssociation.word_id == Word.id)
        .where(TopicWordAssociation.topic_id == topic_id)
        .order_by(Word.id)
    )
    result: Result = await session.execute(stmt)
    words = result.scalars().all()
    return list(words)


async def delete_the_word(
    user: Annotated[dict, Depends(get_current_user)],
    word_id: int,
    session: AsyncSession,
) -> None:

    word = await get_word_by_id(
        session=session,
        word_id=word_id,
    )

    result = await session.execute(
        select(Topic)
        .join(TopicWordAssociation)
        .filter(
            TopicWordAssociation.word_id == word.id,
            Topic.user_id == user["id"],
        )
    )
    topic = result.scalars().first()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "type": "word_id_taken",
                    "loc": ["body"],
                    "msg": f"You do not have permission to delete this word.",
                }
            ],
        )

    await session.execute(
        delete(TopicWordAssociation).filter(
            TopicWordAssociation.word_id == word.id,
        )
    )

    await session.delete(word)
    await session.commit()
