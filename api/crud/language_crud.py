from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.language_schemas import (
    LanguageCreate,
    LanguageUpdatePartial,
    Language as PydanticLanguage,
)
from src.models import Language


async def get_language_by_id(
    session: AsyncSession,
    language_id: int,
) -> Language | None:
    return await session.get(Language, language_id)


async def create_language(
    language: LanguageCreate,
    session: AsyncSession,
) -> Language:

    new_language = Language(**language.model_dump())
    session.add(new_language)
    await session.commit()

    return new_language


async def update_language(
    language_update: LanguageUpdatePartial,
    language: PydanticLanguage,
    session: AsyncSession,
    partial: bool = True,
) -> Language:
    for name, value in language_update.model_dump(exclude_unset=partial).items():
        setattr(
            language,
            name,
            value,
        )
    await session.commit()
    return language


async def get_all_languages(
    session: AsyncSession,
) -> list[Language]:
    stmt = select(Language).order_by(Language.id)
    result: Result = await session.execute(stmt)
    languages = result.scalars().all()
    return list(languages)
