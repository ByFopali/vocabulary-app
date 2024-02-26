from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.grammar_element_crud import (
    create_grammar_element,
    get_all_speech_parts,
    update_grammar_element,
)
from api.schemas.grammar_element_schemas import (
    GrammarElement,
    GrammarElementCreate,
    GrammarElementUpdatePartial,
)
from src.models import db_helper
from api.dependencies import grammar_element_by_id

router = APIRouter(prefix="/grammar_element", tags=["GrammarElements"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a speech part",
    response_model=GrammarElement,
)
async def create_a_grammar_element(
    grammar_element: GrammarElementCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await create_grammar_element(
        grammar_element=grammar_element,
        session=session,
    )


@router.get(
    "/all-speech-parts/",
    summary="Get all speech parts",
    response_model=list[GrammarElement],
)
async def get_all_speech_parts_list(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await get_all_speech_parts(session=session)


@router.get(
    "/{grammar_element_id}/",
    summary="Get speech part by id",
    response_model=GrammarElement,
)
async def get_user_by_id(
    grammar_element: GrammarElement = Depends(grammar_element_by_id),
):
    return grammar_element


@router.patch(
    "/{grammar_element_id}/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update speech part by id",
    response_model=GrammarElement,
)
async def update_user(
    grammar_element_update: GrammarElementUpdatePartial,
    grammar_element: GrammarElement = Depends(grammar_element_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await update_grammar_element(
        grammar_element_update, grammar_element, session
    )


@router.delete(
    "/{grammar_element_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete speech part by id",
)
async def delete_grammar_element(
    session: AsyncSession = Depends(db_helper.session_dependency),
    grammar_element: GrammarElement = Depends(grammar_element_by_id),
) -> None:
    await session.delete(grammar_element)
    await session.commit()
