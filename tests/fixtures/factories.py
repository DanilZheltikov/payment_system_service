from decimal import Decimal
from hashlib import sha256
from typing import Any, Awaitable, Callable
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import MIN_AMOUNT
from app.core.utils import get_password_hash
from app.models import Account, Payment, User

DEFAULT_WEBHOOK_AMOUNT = '1550.55'
MIN_AMOUNT_PAYMENT = '10.00'


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
            balance=kwargs.get('balance', Decimal(MIN_AMOUNT)),
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
            amount=kwargs.get('amount', Decimal(MIN_AMOUNT_PAYMENT)),
            account_id=account.id,
            user_id=user.id
        )
        get_test_async_session.add(payment)
        await get_test_async_session.flush()
        await get_test_async_session.refresh(payment)

        return payment

    return create_payment


@pytest.fixture
def webhook_payload_factory(
    user: User,
    account: Account
) -> Callable[..., dict[str, Any]]:

    def create_webhook_payload(
        transaction_id: str | None = None,
        amount: float | int | str = DEFAULT_WEBHOOK_AMOUNT,
        secret: str = settings.secret_key_to_webhook,
        **kwargs: Any
    ) -> dict[str, Any]:
        formatted_amount = f'{Decimal(amount):.2f}'
        payload = {
            'account_id': account.id,
            'amount': formatted_amount,
            'transaction_id': transaction_id or str(uuid4()),
            'user_id': user.id
        }
        payload.update(kwargs)

        raw_str = (
            f"{payload['account_id']}"
            f"{payload['amount']}"
            f"{payload['transaction_id']}"
            f"{payload['user_id']}"
            f"{secret}"
        )

        payload['signature'] = sha256(raw_str.encode()).hexdigest()

        return payload

    return create_webhook_payload
