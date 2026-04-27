from http import HTTPStatus

import pytest
from pydantic import TypeAdapter
from pytest_lazy_fixtures.lazy_fixture import lf

from app.schemas import AccountRead, PaymentRead, UserRead


@pytest.mark.parametrize(
    'api_client, user_fixture, expected_status',
    [
        (lf('auth_client'), lf('user'), HTTPStatus.OK),
        (lf('admin_client'), lf('admin'), HTTPStatus.OK)
    ]
)
async def test_user_has_access_to_information_about_himself(
    api_client,
    user_fixture,
    expected_status
):
    response = await api_client.get('/me/')
    assert response.status_code == expected_status, (
        'При корректном запросе был получен не соответствующий ожидаемому '
        f'статус код - `{response.status_code}`'
    )
    api_user = UserRead.model_validate(response.json())
    db_user = UserRead.model_validate(user_fixture)

    assert api_user == db_user


@pytest.mark.parametrize(
    'api_client, accounts',
    [
        (lf('auth_client'), lf('user_accounts')),
        (lf('admin_client'), lf('other_user_accounts'))
    ]
)
async def test_the_user_has_access_to_his_accounts(api_client, accounts):
    response = await api_client.get('/me/accounts')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert isinstance(data, list)
    adapter = TypeAdapter(list[AccountRead])
    api_accounts = sorted(adapter.validate_python(data), key=lambda x: x.id)
    db_accounts = sorted(adapter.validate_python(accounts), key=lambda x: x.id)

    assert api_accounts == db_accounts


@pytest.mark.parametrize(
    'api_client, payments',
    [
        (lf('auth_client'), lf('user_payments')),
        (lf('admin_client'), lf('other_user_payments'))
    ]
)
async def test_the_user_has_access_to_his_payments(api_client, payments):

    response = await api_client.get('/me/payments')

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert isinstance(data, list)
    adapter = TypeAdapter(list[PaymentRead])
    api_payments = sorted(adapter.validate_python(data), key=lambda x: x.id)
    db_payments = sorted(adapter.validate_python(payments), key=lambda x: x.id)

    assert api_payments == db_payments


@pytest.mark.parametrize('url', ['/me/', '/me/accounts', '/me/payments'])
async def test_anonymous_user_should_not_access_me_endpoint(url, client):
    response = await client.get(url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response.json()


@pytest.mark.parametrize(
    'api_client, accounts, other_accounts',
    [
        (lf('auth_client'), lf('user_accounts'), lf('other_user_accounts')),
        (lf('admin_client'), lf('other_user_accounts'), lf('user_accounts'))
    ]
)
async def test_user_cannot_access_other_user_accounts(
    api_client,
    accounts,
    other_accounts
):

    response = await api_client.get('/me/accounts')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    api_ids = {item['id'] for item in data}
    user_db_ids = {account.id for account in accounts}
    other_user_db_ids = {account.id for account in other_accounts}

    assert api_ids == user_db_ids
    assert api_ids.isdisjoint(other_user_db_ids)


@pytest.mark.parametrize(
    'api_client, payments, other_payments',
    [
        (lf('auth_client'), lf('user_payments'), lf('other_user_payments')),
        (lf('admin_client'), lf('other_user_payments'), lf('user_payments'))
    ]
)
async def test_user_cannot_access_other_user_payments(
    api_client,
    payments,
    other_payments
):
    response = await api_client.get('/me/payments')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    api_ids = {item['id'] for item in data}
    user_db_ids = {account.id for account in payments}
    other_user_db_ids = {account.id for account in other_payments}

    assert api_ids == user_db_ids
    assert api_ids.isdisjoint(other_user_db_ids)
