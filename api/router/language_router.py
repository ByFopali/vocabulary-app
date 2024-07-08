from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.language_crud import (
    create_language,
    update_language,
    get_all_languages,
)
from api.dependencies import language_by_id, if_language_exists
from api.schemas.language_schemas import (
    Language,
    LanguageCreate,
    LanguageUpdatePartial,
)
from src.models import db_helper

router = APIRouter(prefix="/language", tags=["Languages"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new language",
    response_model=Language,
)
async def create_a_language(
    language: LanguageCreate = Depends(if_language_exists),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await create_language(
        language=language,
        session=session,
    )


@router.get(
    "/all-languages/",
    summary="Get all languages",
    response_model=list[Language],
)
async def get_all_languages_list(
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await get_all_languages(session=session)


@router.get(
    "/{language_id}/",
    summary="Get language by id",
    response_model=Language,
)
async def get_language_by_id(
    language: Language = Depends(language_by_id),
):
    return language


@router.patch(
    "/{language_id}/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update language by id",
    response_model=Language,
)
async def update_the_language(
    language_update: LanguageUpdatePartial = Depends(if_language_exists),
    language: Language = Depends(language_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await update_language(
        language_update,
        language,
        session,
    )


@router.delete(
    "/{language_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete language by id",
)
async def delete_language(
    session: AsyncSession = Depends(db_helper.session_dependency),
    language: Language = Depends(language_by_id),
) -> None:
    await session.delete(language)
    await session.commit()
