from typing import Annotated

from fastapi import Cookie, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core import exceptions
from app.core.security import oauth2_scheme, authenticate_user_from_token
from app.models import User


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> User:
    user = await authenticate_user_from_token(token, session)
    if not user.is_active:
        raise exceptions.UserInactiveException()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_superuser(
    current_user: CurrentUserDep
) -> User:
    if not current_user.is_admin:
        raise exceptions.PermissionDeniedException()
    return current_user


CurrentSuperUserDep = Annotated[User, Depends(get_current_superuser)]
FormDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def get_refresh_token_from_cookie(
        token: Annotated[str | None, Cookie(alias='refresh_token')] = None
) -> str:
    if not token:
        raise exceptions.MissingTokenException()
    return token


RefreshTokenDep = Annotated[str, Depends(get_refresh_token_from_cookie)]
