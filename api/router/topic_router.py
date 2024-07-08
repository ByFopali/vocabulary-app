from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.topic_crud import (
    create_topic,
    update_topic,
    get_all_topics,
    delete_the_topic
)
from api.dependencies import topic_by_id, if_topic_exists_for_specific_user
from api.schemas.topic_schemas import (
    Topic as TopicPydantic,
    TopicCreate,
    TopicUpdatePartial,
)
from auth.utils import get_current_auth_user_model, get_current_user
from src.models import db_helper, User, Topic

router = APIRouter(prefix="/topic", tags=["Topics"])


@router.post(
    "/",
    response_model=TopicPydantic,
)
async def create_topic_for_user(
    user: Annotated[dict, Depends(get_current_user)],
    topic: TopicCreate = Depends(if_topic_exists_for_specific_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await create_topic(
        user=user,
        topic=topic,
        session=session,
    )


@router.get(
    "/all-topics/",
    summary="Get all topics",
    response_model=list[TopicPydantic],
)
async def get_all_topics_list(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await get_all_topics(session=session)


@router.get(
    "/{topic_id}/",
    summary="Get topic by id",
    response_model=TopicPydantic,
)
async def get_topic_by_id(
    topic: Topic = Depends(topic_by_id),
):
    return topic


@router.delete(
    "/{topic_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete topic by id",
)
async def delete_topic(
    user: Annotated[dict, Depends(get_current_user)],
    session: AsyncSession = Depends(db_helper.session_dependency),
    topic: Topic = Depends(topic_by_id),
) -> None:

    return await delete_the_topic(
        user=user,
        session=session,
        topic_id=topic.id
    )


@router.patch(
    "/{topic_id}/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update topic by id",
    response_model=TopicPydantic,
)
async def update_the_topic(
    topic_update: TopicUpdatePartial = Depends(if_topic_exists_for_specific_user),
    topic: Topic = Depends(topic_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await update_topic(
        topic_update,
        topic,
        session,
    )
