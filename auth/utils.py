from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.dependencies import user_by_id
from src.models import User
from src.config import settings
from jose import jwt, JWTError

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/user/token/",
)


def hash_pass(
    password: str,
):
    return pwd_context.hash(password)


def verify_password(
    password: str,
    hashed_pass: str,
) -> bool:
    return pwd_context.verify(password, hashed_pass)


async def authenticate_user(
    username: str,
    password: str,
    session: AsyncSession,
):
    user_query = await session.execute(select(User).filter(User.username == username))
    user = user_query.scalar_one_or_none()
    if not user:
        raise False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_and_refresh_tokens(
    username: str,
    user_id: int,
    email: str,
    access_expires_delta: timedelta,
    refresh_expires_delta: timedelta,
):
    access_encode = {
        "username": username,
        "id": user_id,
        "email": email,
    }
    refresh_encode = {
        "username": username,
        "id": user_id,
    }

    access_expires = datetime.utcnow() + access_expires_delta
    refresh_expires = datetime.utcnow() + refresh_expires_delta

    access_encode.update({"exp": access_expires})
    refresh_encode.update({"exp": refresh_expires})

    access_token = jwt.encode(
        access_encode,
        settings.jwt.secret_key,
        settings.jwt.algorithm,
    )
    refresh_token = jwt.encode(
        refresh_encode,
        settings.jwt.secret_key,
        settings.jwt.algorithm,
    )

    return access_token, refresh_token


async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession,
):
    user = await authenticate_user(
        form_data.username,
        form_data.password,
        session,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    access_token, refresh_token = create_access_and_refresh_tokens(
        user.username,
        user.id,
        user.email,
        timedelta(minutes=settings.jwt.access_token_expire_minutes),
        timedelta(days=settings.jwt.refresh_token_expire_days),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_access_token(
    refresh_token: str,
    session: AsyncSession,
):
    try:
        payload = jwt.decode(refresh_token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        username: str = payload.get("username")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Optionally verify user existence in the database
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        access_token, new_refresh_token = create_access_and_refresh_tokens(
            username,
            user_id,
            user.email,
            timedelta(minutes=settings.jwt.access_token_expire_minutes),
            timedelta(days=settings.jwt.refresh_token_expire_days),
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
):
    try:
        payload = jwt.decode(
            token,
            settings.jwt.secret_key,
            algorithms=[settings.jwt.algorithm],
        )
        username: str = payload.get("username")
        email: str = payload.get("email")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate",
            )
        return {
            "id": user_id,
            "username": username,
            "email": email,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_auth_user(
    user: Annotated[dict, Depends(get_current_user)],
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return user


def has_permission(
    user: User = Depends(user_by_id),
    current_user: dict = Depends(get_current_user),
):
    if current_user["id"] != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[
                {
                    "type": "user_id_taken",
                    "loc": ["body"],
                    "msg": f"You do not have permission to update this user's data",
                }
            ],
        )


async def get_current_auth_user_model(
    session: AsyncSession,
    user: Annotated[dict, Depends(get_current_user)],
):

    auth_user = await session.scalar(
        select(User)
        .where(User.id == user["id"])
    )

    if auth_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return auth_user
