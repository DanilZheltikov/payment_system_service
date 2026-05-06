from decimal import Decimal
from http import HTTPStatus
from typing import Any, Callable

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import Account


WEBHOOK_URL = '/webhook/payment'
WEBHOOK_SUCCESS_RESPONSE = {'status': 'success'}
NON_EXISTENT_ID = 999_999_999
NEGATIVE_AMOUNT = -1500


async def test_webhook_work(
    client: AsyncClient,
    webhook_payload_factory: Callable[..., dict[str, Any]],
    get_test_async_session: AsyncSession
):
    payload = webhook_payload_factory()
    result_before = await get_test_async_session.execute(
        select(Account).where(Account.user_id == payload['user_id'])
    )
    balance_before = result_before.scalar_one().balance

    response = await client.post(WEBHOOK_URL, json=payload)
    assert response.status_code == HTTPStatus.OK
    assert WEBHOOK_SUCCESS_RESPONSE == response.json()

    get_test_async_session.expire_all()

    result_after = await get_test_async_session.execute(
        select(Account).where(Account.user_id == payload['user_id'])
    )
    balance_after = result_after.scalar_one().balance

    assert balance_after == balance_before + Decimal(str(payload['amount']))


async def test_webhook_create_new_account(
    client: AsyncClient,
    webhook_payload_factory: Callable[..., dict[str, Any]],
    get_test_async_session: AsyncSession
):
    payload = webhook_payload_factory(account_id=NON_EXISTENT_ID)
    result_before = await get_test_async_session.execute(
        select(Account)
        .where(
            Account.id == payload['account_id']
        )
    )

    assert result_before.scalar_one_or_none() is None

    response = await client.post(
        WEBHOOK_URL,
        json=payload
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == WEBHOOK_SUCCESS_RESPONSE

    get_test_async_session.expire_all()

    result_after = await get_test_async_session.execute(
        select(Account)
        .where(
            Account.id == payload['account_id']
        )
    )
    account = result_after.scalar_one_or_none()
    assert account is not None
    assert account.balance == Decimal(str(payload['amount']))


@pytest.mark.parametrize(
    'payload_kwargs, expected_status',
    [
        ({'user_id': None}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'user_id': NON_EXISTENT_ID}, HTTPStatus.NOT_FOUND),
        ({'amount': NEGATIVE_AMOUNT}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({'secret': 'itsnotsuchabigsecret'}, HTTPStatus.BAD_REQUEST),
    ]
)
async def test_webhook_invalid_payload(
    client: AsyncClient,
    webhook_payload_factory: Callable[..., dict[str, Any]],
    payload_kwargs: dict[str, Any],
    expected_status: int
):
    response = await client.post(
        WEBHOOK_URL,
        json=webhook_payload_factory(**payload_kwargs)
    )
    assert response.status_code == expected_status
    assert 'detail' in response.json()


async def test_webhook_double_request(
    client: AsyncClient,
    webhook_payload_factory: Callable[..., dict[str, Any]]
):
    webhookpayload = webhook_payload_factory()
    first_response = await client.post(WEBHOOK_URL, json=webhookpayload)
    assert first_response.status_code == HTTPStatus.OK
    assert first_response.json() == WEBHOOK_SUCCESS_RESPONSE

    second_response = await client.post(WEBHOOK_URL, json=webhookpayload)

    assert second_response.status_code == HTTPStatus.OK
    assert 'detail' in second_response.json()
    assert first_response.json() != second_response.json()
