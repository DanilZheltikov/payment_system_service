from datetime import datetime, timedelta, timezone
from hashlib import sha256

import jwt
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
    Token,
    TokenCreatePayload
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def create_jwt(payload: TokenCreatePayload) -> str:

    return jwt.encode(
        payload=payload.model_dump(),
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
    return create_jwt(
        TokenCreatePayload(sub=subject, exp=expire, token_type='access')
    )


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
    refresh_token = create_jwt(
        TokenCreatePayload(sub=user.id, exp=expire, token_type='refresh')
    )
    await refresh_token_crud.remove_by_user_id(user.id, session)

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
