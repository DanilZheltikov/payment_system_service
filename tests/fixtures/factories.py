from decimal import Decimal
from typing import Any, Awaitable, Callable
from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account, Payment, User
from app.core.utils import get_password_hash


@pytest_asyncio.fixture
def user_factory(
    get_test_async_session: AsyncSession,
    user_password: str
) -> Callable[[Any], Awaitable[User]]:
    async def create_user(**kwargs) -> User:
        user = User(
            email=kwargs.get('email', 'test@test.com'),
            first_name=kwargs.get('first_name', 'test_name'),
            last_name=kwargs.get('last_name', 'test_last_name'),
            hashed_password=get_password_hash(
                kwargs.get('password', user_password)
            ),
            is_active=kwargs.get('is_active', True),
            is_admin=kwargs.get('is_admin', False)
        )
        get_test_async_session.add(user)
        await get_test_async_session.flush()
        await get_test_async_session.refresh(user)

        return user

    return create_user


@pytest_asyncio.fixture
def account_factory(
    get_test_async_session: AsyncSession
) -> Callable[[User], Awaitable[Account]]:
    async def create_account(user: User, **kwargs) -> Account:
        account = Account(
            balance=kwargs.get('balance', Decimal('0.00')),
            user_id=user.id
        )
        get_test_async_session.add(account)
        await get_test_async_session.flush()
        await get_test_async_session.refresh(account)
        return account

    return create_account


@pytest_asyncio.fixture
def payment_factory(
    get_test_async_session: AsyncSession
) -> Callable[[Account, User], Awaitable[Payment]]:

    async def create_payment(
        account: Account,
        user: User,
        **kwargs
    ) -> Payment:
        payment = Payment(
            transaction_id=kwargs.get('transaction_id', str(uuid4())),
            amount=kwargs.get('amount', Decimal('10.00')),
            account_id=account.id,
            user_id=user.id
        )
        get_test_async_session.add(payment)
        await get_test_async_session.flush()
        await get_test_async_session.refresh(payment)

        return payment

    return create_payment
