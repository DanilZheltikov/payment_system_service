import uuid
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Literal, NewType, Optional

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
    RefreshTokenPayload,
    Token,
    TokenCreatePayload
)

UserId = NewType('UserId', int)


def create_jwt(payload: TokenCreatePayload) -> str:
    """Универсальная функция создания JWT."""
    return jwt.encode(
        payload=payload.model_dump(mode='json'),
        key=settings.secret_key,
        algorithm=settings.algorithm
    )


def _create_token_payload(
    subject: UserId,
    expires_delta: timedelta,
    token_type: Literal['access', 'refresh'],
    now: Optional[datetime] = None
) -> TokenCreatePayload:

    token_map = {
        'access': AccessTokenPayload,
        'refresh': RefreshTokenPayload
    }
    if not now:
        now = datetime.now(tz=timezone.utc)

    return token_map[token_type](
        sub=str(subject),
        iat=now,
        exp=now + expires_delta,
        jti=str(uuid.uuid4()),
        token_type=token_type
    )


def create_access_token(
    subject: UserId,
    expires_minutes: int = settings.access_token_expire_minutes
) -> str:
    """Создает access token."""

    return create_jwt(
        _create_token_payload(
            subject,
            timedelta(minutes=expires_minutes),
            'access'
        )
    )


async def create_refresh_token(
    subject: UserId,
    session: AsyncSession,
    expires_minutes: int = settings.refresh_token_expire_minutes
) -> str:
    """Создает, удаляет старый и добавляет новый refresh token в базу."""
    now = datetime.now(tz=timezone.utc)
    expires_delta = timedelta(minutes=expires_minutes)

    refresh_token = create_jwt(
        _create_token_payload(
            subject=subject,
            expires_delta=timedelta(minutes=expires_minutes),
            token_type='refresh',
            now=now
        )
    )
    await refresh_token_crud.remove_by_user_id(subject, session, commit=False)

    await refresh_token_crud.create(
        obj_in=RefreshTokenCreate(
            user_id=subject,
            hashed_token=sha256(refresh_token.encode()).hexdigest(),
            expires=now + expires_delta
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

        return await user_crud.get(int(token_data.sub), session)

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
    if not user:
        raise exceptions.AuthException()
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
        RefreshTokenPayload(
            **jwt.decode(
                jwt=token,
                key=settings.secret_key,
                algorithms=[settings.algorithm]
            )
        )

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException()

    except (jwt.InvalidTokenError, ValidationError):
        raise exceptions.InvalidTokenException()
