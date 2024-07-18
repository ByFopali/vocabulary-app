from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_users, update_users, get_all_users
from auth.dependencies import user_by_id
from auth.schemas import Token
from auth.schemas import UserCreate, User, CurrentUserData, UserUpdatePartial, UserShow
from auth.utils import (
    login_for_access_token,
    get_current_auth_user,
    get_current_user,
    has_permission, refresh_access_token,
)
from src.models import db_helper

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
    "/all-users/",
    summary="Get all users",
    response_model=list[UserShow],
)
async def get_all_users_list(
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    return await get_all_users(session=session)


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


@router.post("/token/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    return await refresh_access_token(refresh_token, session)



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
    summary="Update user by id",
    response_model=User,
)
async def update_user(
    user_update: UserUpdatePartial,
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.session_dependency),
    dependencies: dict = Depends(has_permission),
):
    return await update_users(user_update, user, session)


@router.delete(
    "/{user_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by id",
)
async def delete_user(
    session: AsyncSession = Depends(db_helper.session_dependency),
    user: User = Depends(user_by_id),
    dependencies: dict = Depends(has_permission),
) -> None:
    await session.delete(user)
    await session.commit()
