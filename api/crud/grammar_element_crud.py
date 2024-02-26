from fastapi import HTTPException, status
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.grammar_element_schemas import (
    GrammarElementCreate,
    GrammarElementUpdatePartial,
    GrammarElement as PydanticGrammarElement,
)
from src.models import GrammarElement


async def get_grammar_element_by_id(
    session: AsyncSession, grammar_element_id: int
) -> GrammarElement | None:
    return await session.get(GrammarElement, grammar_element_id)


async def create_grammar_element(
    grammar_element: GrammarElementCreate,
    session: AsyncSession,
) -> GrammarElement:

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
                    "msg": "this part of speech are created",
                }
            ],
        )

    new_grammar_element = GrammarElement(**grammar_element.model_dump())
    session.add(new_grammar_element)
    await session.commit()

    return new_grammar_element


async def update_grammar_element(
    grammar_element_update: GrammarElementUpdatePartial,
    grammar_element: PydanticGrammarElement,
    session: AsyncSession,
    partial: bool = True,
) -> PydanticGrammarElement:
    for name, value in grammar_element_update.model_dump(exclude_unset=partial).items():
        setattr(
            grammar_element,
            name,
            value,
        )
    await session.commit()
    return grammar_element


#
#
async def get_all_speech_parts(session: AsyncSession) -> list[GrammarElement]:
    stmt = select(GrammarElement).order_by(GrammarElement.id)
    result: Result = await session.execute(stmt)
    speech_parts = result.scalars().all()
    return list(speech_parts)
