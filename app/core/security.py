from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated

import jwt
from fastapi import Cookie
from fastapi.security import OAuth2PasswordBearer
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
    Token
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def create_jwt(token_type: str, token_data: dict) -> str:
    jwt_payload = {
        'token_type': token_type,
    }
    jwt_payload.update(token_data)
    return jwt.encode(
        payload=jwt_payload,
        key=settings.secret_key,
        algorithm=settings.algorithm
    )


def create_access_token(
    subject: int,
    expires_minutes: int = settings.access_token_expire_minutes
) -> str:
    expire = (
        datetime.now(tz=timezone.utc)
        + timedelta(minutes=expires_minutes)
    )
    jwt_payload = {
        'exp': expire,
        'sub': subject
    }

    return create_jwt(token_type='access', token_data=jwt_payload)


async def create_refresh_token(
    user: User,
    session: AsyncSession,
    expires_minutes: int = settings.refresh_token_expire_minutes
) -> str:
    await session.refresh(user, ['refresh_token'])

    expire = (
        datetime.now(tz=timezone.utc)
        + timedelta(minutes=expires_minutes)
    )
    jwt_payload = {
        'exp': expire,
        'sub': user.id
    }
    refresh_token = create_jwt(token_type='refresh', token_data=jwt_payload)

    if user.refresh_token:
        await refresh_token_crud.remove(user.refresh_token, session)
        await session.flush()

    await refresh_token_crud.create(
        obj_in=RefreshTokenCreate(
            user_id=user.id,
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

    user = await user_crud.get_user_by_email(email=email, session=session)

    if not verify_password(password, user.hashed_password):
        raise exceptions.CredentialsException()

    access_token = create_access_token(str(user.id))
    refresh_token = await create_refresh_token(user, session)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


async def check_refresh_token(token: str, session: AsyncSession):
    try:
        token_data = RefreshTokenPayload(
            **jwt.decode(
                jwt=token,
                key=settings.secret_key,
                algorithms=[settings.algorithm]
            )
        )
        await user_crud.get(token_data.sub, session)

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException()

    except (
        jwt.InvalidTokenError,
        ValidationError,
        exceptions.NotFoundException
    ):
        raise exceptions.InvalidTokenException()


def get_refresh_token_from_cookie(
        token: Annotated[str | None, Cookie()] = None
) -> str:
    if not token:
        raise exceptions.MissingTokenException()
    return token
