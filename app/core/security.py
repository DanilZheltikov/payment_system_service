from datetime import datetime, timedelta, timezone
from hashlib import sha256

import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.config import settings
from app.core.utils import verify_password
from app.crud import refresh_token_crud, user_crud
from app.models import User
from app.schemas import (
    AccessTokenPayload,
    RefreshTokenCreate,
    Token,
    TokenCreatePayload
)


def create_jwt(payload: TokenCreatePayload) -> str:
    """Универсальная функция создания JWT."""
    return jwt.encode(
        payload=payload.model_dump(),
        key=settings.secret_key,
        algorithm=settings.algorithm
    )


def create_access_token(
    subject: int,
    expires_minutes: int = settings.access_token_expire_minutes
) -> str:
    """Создает access token."""
    expire = (
        datetime.now(tz=timezone.utc)
        + timedelta(minutes=expires_minutes)
    )
    return create_jwt(
        TokenCreatePayload(sub=subject, exp=expire, token_type='access')
    )


async def create_refresh_token(
    user_id: int,
    session: AsyncSession,
    expires_minutes: int = settings.refresh_token_expire_minutes
) -> str:
    """Создает, удаляет старый и добавляет новый refresh token в базу."""

    expire = (
        datetime.now(tz=timezone.utc)
        + timedelta(minutes=expires_minutes)
    )
    refresh_token = create_jwt(
        TokenCreatePayload(sub=user_id, exp=expire, token_type='refresh')
    )
    await refresh_token_crud.remove_by_user_id(user_id, session)

    await refresh_token_crud.create(
        obj_in=RefreshTokenCreate(
            user_id=user_id,
            hashed_token=sha256(refresh_token.encode()).hexdigest(),
            expires=expire
        ),
        session=session
    )
    return refresh_token


async def authenticate_user_from_token(
    token: str,
    session: AsyncSession
) -> User:
    """Аутентификация пользователя по access token."""

    try:
        token_data = AccessTokenPayload(
            **jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
        )

        return await user_crud.get(token_data.sub, session)

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException()

    except (
        jwt.InvalidTokenError,
        ValidationError,
        exceptions.NotFoundException
    ):
        raise exceptions.CredentialsException()


async def authenticate_user(
    email: str,
    password: str,
    session: AsyncSession
) -> Token:
    """Аутентификация пользователя по email'у и паролю."""

    user = await user_crud.get_user_by_email(email=email, session=session)

    if not verify_password(password, user.hashed_password):
        raise exceptions.CredentialsException()

    access_token = create_access_token(user.id)
    refresh_token = await create_refresh_token(user.id, session)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


def check_refresh_token(token: str):
    """Проверяет refresh token."""
    try:
        token_data = jwt.decode(
            jwt=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm]
        )
        if token_data.get('token_type') != 'refresh':
            raise exceptions.InvalidTokenException()

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException()

    except jwt.InvalidTokenError:
        raise exceptions.InvalidTokenException()
