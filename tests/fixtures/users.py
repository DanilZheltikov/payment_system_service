import pytest_asyncio


@pytest_asyncio.fixture
async def user(user_factory):
    return await user_factory(is_active=True)


@pytest_asyncio.fixture
async def admin(user_factory):
    return await user_factory(
        email='testadmin@admin.com',
        is_active=True,
        is_admin=True
    )
