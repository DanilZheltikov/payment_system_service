from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from uuid import uuid4

import pytest_asyncio

from app.models import Account, Payment, RefreshToken, User
from app.core.security import create_jwt
from app.schemas import TokenCreatePayload
from app.core.utils import get_password_hash


@pytest_asyncio.fixture
def user_factory(get_test_async_session):
    async def create_user(**kwargs):
        user = User(
            email=kwargs.get('email', 'test@test.com'),
            first_name=kwargs.get('first_name', 'test_name'),
            last_name=kwargs.get('last_name', 'test_last_name'),
            hashed_password=get_password_hash(
                kwargs.get('password', 'test_password')
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
def account_factory(get_test_async_session):
    async def create_account(user, **kwargs):
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
def payment_factory(get_test_async_session):
    async def create_payment(account, user, **kwargs):
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


@pytest_asyncio.fixture
def refresh_token_factory(get_async_session):
    async def create_refresh_token(user, **kwargs):
        expire = kwargs.pop(
            'expires',
            datetime.now(timezone.utc) + timedelta(days=7)
        )
        raw_jwt = create_jwt(
            TokenCreatePayload(sub=user.id, exp=expire, token_type='refresh')
        )
        token = RefreshToken(
            expires=expire,
            revoked=kwargs.pop('revoked', False),
            hashed_token=sha256(raw_jwt.encode()).hexdigest(),
            user_id=user.id,
            **kwargs
        )

        get_async_session.add(token)
        await get_async_session.flush()

        token.raw_token = raw_jwt

        return token
    return create_refresh_token
