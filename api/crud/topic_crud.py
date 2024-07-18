from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, Result, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.schemas.topic_schemas import (
    TopicCreate,
    TopicUpdatePartial,
    Topic as PydanticTopic,
)
from src.models import Topic, User, TopicWordAssociation
from auth.utils import get_current_user


async def get_topic_by_id(
    session: AsyncSession,
    topic_id: int,
) -> Topic | None:
    return await session.get(Topic, topic_id)


# async def create_topic(
#     topic: TopicCreate,
#     session: AsyncSession,
#     user: User,
# ) -> Topic:
#
#     new_topic = Topic(**topic.model_dump(), user_id=user.id)
#     session.add(new_topic)
#     await session.commit()
#
#     return new_topic

async def create_topic(
    topic: TopicCreate,
    session: AsyncSession,
    user: Annotated[dict, Depends(get_current_user)],
) -> Topic:

    new_topic = Topic(**topic.model_dump(), user_id=user["id"])
    session.add(new_topic)
    await session.commit()

    return new_topic


async def update_topic(
    topic_update: TopicUpdatePartial,
    topic: PydanticTopic,
    session: AsyncSession,
    partial: bool = True,
) -> Topic:
    for name, value in topic_update.model_dump(exclude_unset=partial).items():
        setattr(
            topic,
            name,
            value,
        )
    await session.commit()
    return topic


async def get_all_topics(
    session: AsyncSession,
) -> list[Topic]:
    stmt = select(Topic).order_by(Topic.id)
    result: Result = await session.execute(stmt)
    topics = result.scalars().all()
    return list(topics)


async def get_all_topics_for_auth_user(
    user: Annotated[dict, Depends(get_current_user)],
    session: AsyncSession,
) -> list[Topic]:
    stmt = select(Topic).where(Topic.user_id == user["id"]).order_by(Topic.id)
    result: Result = await session.execute(stmt)
    topics = result.scalars().all()
    return list(topics)


async def delete_the_topic(
    user: Annotated[dict, Depends(get_current_user)],
    topic_id: int,
    session: AsyncSession,
) -> None:

    topic = await get_topic_by_id(
        session=session,
        topic_id=topic_id,
    )

    result = await session.execute(
        select(Topic)
        .where(
            Topic.id == topic.id,
            Topic.user_id == user["id"],
        )
    )
    topic = result.scalars().first()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "type": "topic_id_taken",
                    "loc": ["body"],
                    "msg": f"You do not have permission to delete this topic.",
                }
            ],
        )

    result = await session.execute(
        select(TopicWordAssociation)
        .options(
            joinedload(TopicWordAssociation.word))
        .where(
            TopicWordAssociation.topic_id == topic.id,
        )
    )
    associations = result.scalars().all()

    for association in associations:
        await session.delete(association.word)

    await session.delete(topic)
    await session.commit()
