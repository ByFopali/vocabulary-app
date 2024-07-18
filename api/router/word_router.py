from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.word_crud import (
    create_word,
    get_all_words,
    update_word,
    delete_the_word,
    get_all_words_for_specific_topic,
)
from api.dependencies import (
    if_word_exists_and_auth_for_specific_topic,
    word_by_id,
)
from api.schemas.word_schemas import WordCreate, Word, WordUpdatePartial
from auth.utils import get_current_user
from src.models import db_helper

router = APIRouter(prefix="/word", tags=["Words"])


@router.post(
    "/",
    response_model=Word,
)
async def create_word_for_topic(
    topic_id: int,
    word: WordCreate = Depends(if_word_exists_and_auth_for_specific_topic),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await create_word(
        topic_id=topic_id,
        word=word,
        session=session,
    )


@router.get(
    "/all-words/",
    summary="Get all words",
    response_model=list[Word],
)
async def get_all_words_list(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await get_all_words(session=session)


@router.get(
    "/all-user-words/",
    summary="Get all words for specific user",
    response_model=list[Word],
)
async def get_all_user_words_list(
    topic_id: int,
    user: Annotated[dict, Depends(get_current_user)],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await get_all_words_for_specific_topic(
        topic_id=topic_id,
        session=session,
        user=user,
    )


@router.get(
    "/{word_id}/",
    summary="Get word by id",
    response_model=Word,
)
async def get_word_by_id(
    word: Word = Depends(word_by_id),
):
    return word


@router.delete(
    "/{word_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete word by id",
)
async def delete_word(
    user: Annotated[dict, Depends(get_current_user)],
    session: AsyncSession = Depends(db_helper.session_dependency),
    word: Word = Depends(word_by_id),
) -> None:

    return await delete_the_word(
        session=session,
        word_id=word.id,
        user=user,
    )


@router.patch(
    "/{word_id}/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update word by id",
    response_model=Word,
)
async def update_the_topic(
    word_update: WordCreate | WordUpdatePartial = Depends(
        if_word_exists_and_auth_for_specific_topic
    ),
    word: Word = Depends(word_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await update_word(
        word_update,
        word,
        session,
    )
