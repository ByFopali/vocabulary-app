from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import db_helper
from auth.schemas import UserCreate, User
from auth.crud import (
    create_users,
)
from auth.dependencies import user_by_id


router = APIRouter(prefix="/auth/user", tags=["auth"])


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
    return await create_users(session=session, user=user)


@router.get("/{user_id}/", response_model=User)
async def get_user(
    user: User = Depends(user_by_id),
):
    return user
