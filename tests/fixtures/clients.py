from hashlib import sha256
from typing import Callable

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.models import RefreshToken, User


@pytest_asyncio.fixture
def access_token():

    def _create(user: User):
        return create_access_token(subject=user.id)

    return _create


@pytest_asyncio.fixture
def auth_client(client: AsyncClient, user: User, access_token: Callable):
    token = access_token(user)

    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


@pytest_asyncio.fixture
def admin_client(client: AsyncClient, admin: User, access_token: Callable):
    token = access_token(admin)

    client.headers.update({"Authorization": f"Bearer {token}"})

    return client


@pytest_asyncio.fixture
async def client_with_refresh(
    client: AsyncClient,
    user: User,
    get_test_async_session: AsyncSession
):
    refresh_token = await create_refresh_token(
        subject=user.id,
        session=get_test_async_session
    )
    client.cookies.set('refresh_token', refresh_token)
    return client


@pytest_asyncio.fixture
async def client_with_revoked_refresh(
    client_with_refresh: AsyncClient,
    get_test_async_session: AsyncSession
):
    token = client_with_refresh.cookies.get('refresh_token')
    await get_test_async_session.execute(
        update(RefreshToken)
        .where(RefreshToken.hashed_token == sha256(token.encode()).hexdigest())
        .values(revoked=True)
    )
    await get_test_async_session.commit()

    return client_with_refresh
