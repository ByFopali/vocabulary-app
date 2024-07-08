from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.grammar_element_crud import get_grammar_element_by_id
from api.crud.language_crud import get_language_by_id
from api.crud.topic_crud import get_topic_by_id
from api.crud.word_crud import get_word_by_id
from api.schemas.grammar_element_schemas import GrammarElementCreate
from api.schemas.language_schemas import LanguageCreate, LanguageUpdatePartial
from api.schemas.topic_schemas import TopicCreate, TopicUpdatePartial
from api.schemas.word_schemas import WordCreate, WordUpdatePartial
from auth.utils import get_current_user
from src.models import (
    db_helper,
    GrammarElement,
    Language,
    Topic,
    Word,
    TopicWordAssociation,
)


async def grammar_element_by_id(
    grammar_element_id: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> GrammarElement:
    grammar_element = await get_grammar_element_by_id(
        session=session,
        grammar_element_id=grammar_element_id,
    )
    if grammar_element is not None:
        return grammar_element

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "type": "grammar_element_id_taken",
                "loc": ["body"],
                "msg": f"Speech part with id {grammar_element_id} not found!",
            }
        ],
    )


async def if_grammar_element_exists(
    grammar_element: GrammarElementCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    existing_name = await session.execute(
        select(GrammarElement).filter(GrammarElement.name == grammar_element.name)
    )
    existing_name = existing_name.scalar_one_or_none()

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "grammar_element_exists",
                    "loc": ["body"],
                    "msg": f'This part of speech "{grammar_element.name}" is created',
                }
            ],
        )

    return grammar_element


async def language_by_id(
    language_id: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Language:
    language = await get_language_by_id(
        session=session,
        language_id=language_id,
    )
    if language is not None:
        return language

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "type": "language_id_taken",
                "loc": ["body"],
                "msg": f"Language with id {language_id} not found!",
            }
        ],
    )


async def if_language_exists(
    language: LanguageCreate | LanguageUpdatePartial,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    existing_name = await session.execute(
        select(Language).filter(Language.name == language.name)
    )
    existing_name = existing_name.scalar_one_or_none()

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "language_exists",
                    "loc": ["body"],
                    "msg": f'this language "{language.name}" is created',
                }
            ],
        )

    return language


async def topic_by_id(
    topic_id: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Topic:
    topic = await get_topic_by_id(
        session=session,
        topic_id=topic_id,
    )
    if topic is not None:
        return topic

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "type": "topic_id_taken",
                "loc": ["body"],
                "msg": f"Topic with id {topic_id} not found!",
            }
        ],
    )


async def if_topic_exists_for_specific_user(
    topic: TopicCreate | TopicUpdatePartial,
    user: Annotated[dict, Depends(get_current_user)],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    existing_name = await session.execute(
        select(Topic).filter(Topic.name == topic.name, Topic.user_id == user["id"])
    )

    existing_name = existing_name.scalar_one_or_none()

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "topic_duplicate",
                    "loc": ["body"],
                    "msg": f'This topic name "{topic.name}" is created now',
                }
            ],
        )

    return topic


async def if_word_exists_and_auth_for_specific_topic(
    topic_id: int,
    user: Annotated[dict, Depends(get_current_user)],
    word: WordCreate | WordUpdatePartial,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    result = await session.execute(
        select(Topic).filter(
            Topic.id == topic_id,
            Topic.user_id == user["id"],
        )
    )
    topic = result.scalar_one_or_none()

    existing_name = await session.execute(
        select(Word)
        .join(TopicWordAssociation)
        .filter(
            TopicWordAssociation.topic_id == topic_id,
            Word.learnt_word == word.learnt_word,
        )
    )
    existing_name = existing_name.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "type": "topic_id_taken",
                    "loc": ["body"],
                    "msg": f"You do not have permission to create a word in this topic.",
                }
            ],
        )

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "word_duplicate",
                    "loc": ["body"],
                    "msg": f'This word "{word.learnt_word}" is created in this topic now',
                }
            ],
        )

    return word


async def word_by_id(
    word_id: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Word:
    word = await get_word_by_id(
        session=session,
        word_id=word_id,
    )
    if word is not None:
        return word

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "type": "topic_id_taken",
                "loc": ["body"],
                "msg": f"Topic with id {word_id} not found!",
            }
        ],
    )


async def verify_topic_ownership(
    topic_id: int,
    user_id: int,
    session: AsyncSession,
) -> None:
    result = await session.execute(
        select(Topic).filter(
            Topic.id == topic_id,
            Topic.user_id == user_id,
        )
    )
    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[
                {
                    "type": "topic_id_taken",
                    "loc": ["body"],
                    "msg": f"You do not have permission to create a word in this topic.",
                }
            ],
        )
