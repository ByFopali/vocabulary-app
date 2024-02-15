from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


def create_access_token(
    username: str,
    user_id: int,
    email: str,
    expires_delta: timedelta,
):
    encode = {
        "username": username,
        "id": user_id,
        "email": email,
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(
        encode,
        settings.jwt.secret_key,
        settings.jwt.algorithm,
    )


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
    token = create_access_token(
        user.username,
        user.id,
        user.email,
        timedelta(minutes=settings.jwt.access_token_expire_minutes),
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


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
