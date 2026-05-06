from typing import Awaitable, Callable

import pytest
import pytest_asyncio

from app.models import Account, Payment, User


@pytest_asyncio.fixture
async def user_accounts(
    user: User,
    account_factory: Callable
) -> list[Account]:
    return [await account_factory(user=user) for _ in range(5)]


@pytest_asyncio.fixture
async def other_user_accounts(
    admin: User,
    account_factory: Callable
) -> list[Account]:
    return [await account_factory(user=admin) for _ in range(5)]


@pytest_asyncio.fixture
async def user_payments(
    user: User,
    payment_factory: Callable,
    user_accounts: list[Account]
) -> list[Payment]:
    return [
        await payment_factory(user=user, account=account)
        for account in user_accounts
    ]


@pytest_asyncio.fixture
async def other_user_payments(
    admin: User,
    payment_factory: Callable,
    other_user_accounts: list[Account]
) -> list[Payment]:
    return [
        await payment_factory(user=admin, account=account)
        for account in other_user_accounts
    ]


@pytest_asyncio.fixture
async def account(
    user: User,
    account_factory: Callable[[User], Awaitable[Account]]
) -> Account:
    return await account_factory(user)


@pytest.fixture
def new_user_payload() -> dict:
    return {
        'email': 'created_user@email.com',
        'first_name': 'donatello',
        'last_name': 'turtle',
        'password': 'donatelospassword'
    }


@pytest.fixture
def user_update_payload() -> dict:
    return {
        'first_name': 'splinter',
        'last_name': 'rat',
        'is_active': True,
        'is_admin': False
    }


@pytest.fixture
def user_password() -> str:
    return 'supersecretpassword'
