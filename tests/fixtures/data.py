import pytest_asyncio


@pytest_asyncio.fixture
async def user_accounts(user, account_factory):
    return [await account_factory(user=user) for _ in range(5)]


@pytest_asyncio.fixture
async def other_user_accounts(admin, account_factory):
    return [await account_factory(user=admin) for _ in range(5)]


@pytest_asyncio.fixture
async def user_payments(user, payment_factory, user_accounts):
    return [
        await payment_factory(user=user, account=account)
        for account in user_accounts
    ]


@pytest_asyncio.fixture
async def other_user_payments(admin, payment_factory, other_user_accounts):
    return [
        await payment_factory(user=admin, account=account)
        for account in other_user_accounts
    ]
