from typing import Annotated

from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.security import oauth2_scheme, authenticate_user_from_token
from app.models import User


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> User:
    user = await authenticate_user_from_token(token, session)
    return user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения действия'
        )
    return current_user
