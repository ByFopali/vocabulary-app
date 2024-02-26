from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import db_helper, GrammarElement

from api.crud.grammar_element_crud import get_grammar_element_by_id


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
