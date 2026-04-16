from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated

import jwt

from fastapi import Cookie
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.core.config import settings
from app.core.utils import verify_password
from app.crud.refresh_token import refresh_token_crud
from app.crud.user import user_crud
from app.models import User
from app.schemas.token import RefreshTokenCreate, Token

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
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id = payload.get('sub')

        if not user_id:
            raise exceptions.CredentialsException
        if payload.get('token_type') != 'access':
            raise exceptions.CredentialsException
        user = await user_crud.get(int(user_id), session)
        if not user:
            raise exceptions.CredentialsException
        return user

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException

    except jwt.InvalidTokenError:
        raise exceptions.CredentialsException


async def authenticate_user(
    email: str,
    password: str,
    session: AsyncSession
) -> Token:

    user = await user_crud.get_user_by_email(email=email, session=session)

    if not user or not verify_password(password, user.hashed_password):
        raise exceptions.CredentialsException

    access_token = create_access_token(str(user.id))
    refresh_token = await create_refresh_token(user, session)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


async def check_refresh_token(
    token: str,
    session: AsyncSession
) -> None:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm]
        )

        if not (user_id := payload.get('sub')):
            raise exceptions.CredentialsException
        if payload.get('token_type') != 'refresh':
            raise exceptions.CredentialsException
        if not await user_crud.get(int(user_id), session):
            raise exceptions.UserNotExists

    except jwt.ExpiredSignatureError:
        raise exceptions.TokenExpiredException

    except jwt.InvalidTokenError:
        raise exceptions.InvalidTokenException


def get_refresh_token_from_cookie(
        token: Annotated[str | None, Cookie()] = None
) -> str:
    if not token:
        raise exceptions.MissingTokenException
    return token
