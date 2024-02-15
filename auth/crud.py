from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import UserCreate
from src.models import User
from sqlalchemy import select
from fastapi import HTTPException, status
from auth.utils import hash_pass


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.get(User, email)


async def create_users(
    user: UserCreate,
    session: AsyncSession,
) -> User:

    existing_user_username = await session.execute(
        select(User).filter(User.username == user.username)
    )
    existing_user_username = existing_user_username.scalar_one_or_none()

    # Check if a user with the same email already exists
    existing_user_email = await session.execute(
        select(User).filter(User.email == user.email)
    )
    existing_user_email = existing_user_email.scalar_one_or_none()

    if existing_user_username and existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "username_and_email_taken",
                    "loc": ["body"],
                    "msg": "username and email are already taken.",
                }
            ],
        )

    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "username_taken",
                    "loc": ["body"],
                    "msg": "User with this username already exists.",
                }
            ],
        )

    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "type": "email_taken",
                    "loc": ["body"],
                    "msg": "User with this email already exists.",
                }
            ],
        )

    hashed_pass = hash_pass(user.hashed_password)
    user.hashed_password = hashed_pass
    new_user = User(**user.model_dump())
    session.add(new_user)
    await session.commit()

    return new_user
