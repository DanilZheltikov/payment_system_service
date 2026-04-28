from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


NEW_USER_PAYLOAD = {
    'email': 'created_user@email.com',
    'first_name': 'donatello',
    'last_name': 'turtle',
    'password': 'donatelospassword'
}
USER_UPDATE_PAYLOAD = {
    'first_name': 'splinter',
    'last_name': 'rat',
    'is_active': True,
    'is_admin': False
}


async def test_admin_can_create_user(admin_client, get_test_async_session):
    response = await admin_client.post(
        '/admin/users/create',
        json=NEW_USER_PAYLOAD
    )

    assert response.status_code == HTTPStatus.CREATED

    data = response.json()

    query = select(User).where(User.email == NEW_USER_PAYLOAD['email'])
    result = await get_test_async_session.execute(query)
    user_in_db = result.scalars().first()

    assert user_in_db is not None
    assert user_in_db.id == data['id']
    assert user_in_db.email == NEW_USER_PAYLOAD['email']
    assert user_in_db.full_name == data['full_name']


@pytest.mark.parametrize(
    'field, value',
    [
        ('email', 'l' * 150 + '@email.com'),
        ('first_name', 'a' * 121),
        ('last_name', 'm' * 121)
    ]
)
async def test_admin_create_user_invalid_long_fields(
    admin_client,
    field,
    value
):
    payload = {
        'email': 'lichking@frostmorn.com',
        'first_name': 'arthas',
        'last_name': 'menethil',
        'password': 'Iveinheritedapowerthatmyfathercouldneverdreamof'
    }
    payload[field] = value

    response = await admin_client.post(
        '/admin/users/create',
        json=payload
    )
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert 'detail' in response.json()
    print(response.json())


async def test_create_user_duplicate_email_fails(admin_client, user):
    response = await admin_client.post(
        '/admin/users/create',
        json={**NEW_USER_PAYLOAD, 'email': user.email}
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert 'detail' in response.json()


async def test_admin_can_update_user(
    admin_client: AsyncClient,
    user,
    get_test_async_session
):
    user_id = user.id
    response = await admin_client.patch(
        url=f'/admin/users/{user_id}',
        json=USER_UPDATE_PAYLOAD
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK

    get_test_async_session.expire_all()

    query = select(User).where(User.id == user_id)
    result = await get_test_async_session.execute(query)
    user_in_db = result.scalars().first()

    assert user_in_db is not None
    assert user_in_db.id == data['id']
    assert user_in_db.email == data['email']
    assert user_in_db.full_name == data['full_name']
    assert user_in_db.first_name == USER_UPDATE_PAYLOAD['first_name']
    assert user_in_db.last_name == USER_UPDATE_PAYLOAD['last_name']


async def test_admin_can_delete_user(
    admin_client: AsyncClient,
    user: User,
    get_test_async_session: AsyncSession
):
    user_id = user.id
    response = await admin_client.delete(f'/admin/users/{user_id}')

    assert response.status_code == HTTPStatus.OK

    get_test_async_session.expire_all()

    query = select(User).where(User.id == user_id)
    result = await get_test_async_session.execute(query)

    user_in_db = result.scalar_one_or_none()
    assert user_in_db is None


async def test_admin_can_get_user_with_accounts(
    admin_client: AsyncClient,
    user: User,
    user_accounts: list
):
    response = await admin_client.get(f'/admin/users/{user.id}')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert data['id'] == user.id
    assert data['email'] == user.email

    assert 'accounts' in data
    assert isinstance(data['accounts'], list)
    assert len(data['accounts']) == len(user_accounts)

    assert (
        {account['id'] for account in data['accounts']}
        == {account.id for account in user_accounts}
    )


async def test_admin_can_get_users_with_accounts(
    admin_client: AsyncClient,
    user,
    admin,
    user_accounts: list,
    other_user_accounts: list,
):
    response = await admin_client.get('/admin/users/')

    assert response.status_code == HTTPStatus.OK

    data = response.json()

    assert isinstance(data, list)

    user_row = next((u for u in data if u['id'] == user.id), None)
    assert user_row is not None
    assert len(user_row['accounts']) == len(user_accounts)

    other_user_row = next((u for u in data if u['id'] == admin.id), None)
    assert other_user_row is not None
    assert len(other_user_row['accounts']) == len(other_user_accounts)


@pytest.mark.parametrize(
    'url, method, payload',
    [
        ('/admin/users/create', 'POST', NEW_USER_PAYLOAD),
        ('/admin/users/300', 'PATCH', USER_UPDATE_PAYLOAD),
        ('/admin/users/300', 'DELETE', None),
        ('/admin/users/300', 'GET', None),
        ('/admin/users/', 'GET', None)
    ]
)
async def test_not_admin_cant_use_admins_endpoints(
    auth_client,
    url,
    method,
    payload
):
    response = await auth_client.request(method=method, url=url, json=payload)

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert 'detail' in response.json()
