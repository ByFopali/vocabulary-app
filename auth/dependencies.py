from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import db_helper, User

from auth.crud import get_user_by_id


async def user_by_id(
    user_id: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> User:
    user = await get_user_by_id(session=session, user_id=user_id)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=[
            {
                "type": "user_id_taken",
                "loc": ["body"],
                "msg": f"User with id {user_id} not found!",
            }
        ],
    )


# async def user_by_email(
#     email: str,
#     session: AsyncSession = Depends(db_helper.session_dependency),
# ) -> User:
#     user = await crud.get_user_by_email(session=session, email=email)
#     if user is not None:
#         return user
#
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=[
#             {
#                 "type": "user_email_taken",
#                 "loc": ["body"],
#                 "msg": f"User with email {email} not found!",
#             }
#         ],
#     )
