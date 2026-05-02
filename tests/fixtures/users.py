from typing import Awaitable, Callable

import pytest_asyncio

from app.models import User


@pytest_asyncio.fixture
async def user(user_factory: Callable[..., Awaitable[User]]) -> User:
    return await user_factory()


@pytest_asyncio.fixture
async def admin(user_factory: Callable[..., Awaitable[User]]) -> User:
    return await user_factory(
        email='testadmin@admin.com',
        is_admin=True
    )
