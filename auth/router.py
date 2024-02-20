from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import db_helper
from auth.schemas import UserCreate, User, CurrentUserData, UserUpdatePartial
from auth.crud import create_users
from auth.utils import (
    login_for_access_token,
    get_current_auth_user,
    get_current_user,
    hash_pass,
)
from auth.dependencies import user_by_id
from auth.schemas import Token

router = APIRouter(prefix="/auth/user", tags=["Auth"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    response_model=User,
)
async def create_user(
    user: UserCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await create_users(
        session=session,
        user=user,
    )


@router.get(
    "/{user_id}/",
    summary="Get user by id",
    response_model=User,
)
async def get_user_by_id(
    user: User = Depends(user_by_id),
):
    return user


@router.post(
    "/token/",
    summary="Get user access token",
    response_model=Token,
)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await login_for_access_token(
        form_data=form_data,
        session=session,
    )


@router.get(
    "/",
    summary="Get current user",
    status_code=status.HTTP_200_OK,
    response_model=CurrentUserData,
)
async def get_current_user(
    user: Annotated[dict, Depends(get_current_user)],
):
    return await get_current_auth_user(user)


@router.patch(
    "/{user_id}/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update user",
    response_model=User,
)
async def update_user(
    user_update: UserUpdatePartial,
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
    current_user: dict = Depends(get_current_user),
    partial: bool = True,
):
    if current_user["id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user's data",
        )

    for name, value in user_update.model_dump(exclude_unset=partial).items():
        if name == "hashed_password" and value:
            value = hash_pass(value)
        setattr(
            user,
            name,
            value,
        )
    await session.commit()
    return user


@router.delete(
    "/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
)
async def delete_user(
    session: AsyncSession = Depends(db_helper.session_dependency),
    user: User = Depends(user_by_id),
    current_user: dict = Depends(get_current_user),
) -> None:
    if current_user["id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user's data",
        )
    await session.delete(user)
    await session.commit()
