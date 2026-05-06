from hashlib import sha256
from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.models import RefreshToken, User
from app.schemas import Token
from tests.test_me import PROFILE_URL, USERS_ACCOUNTS_URL, USERS_PAYMENTS_URL

LOGIN_URL = '/auth/login'
REFRESH_URL = '/auth/refresh'
REGISTER_URL = '/auth/register'


async def test_user_can_register(
    client: AsyncClient,
    new_user_payload: dict,
    get_test_async_session: AsyncSession
):
    response = await client.post(REGISTER_URL, json=new_user_payload)

    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert data['email'] == new_user_payload['email']

    query = select(User).where(User.email == new_user_payload['email'])
    result = await get_test_async_session.execute(query)

    user_in_db = result.scalars().one_or_none()

    assert user_in_db is not None
    assert user_in_db.email == new_user_payload['email']
    assert user_in_db.first_name == new_user_payload['first_name']
    assert user_in_db.last_name == new_user_payload['last_name']
    assert user_in_db.hashed_password != new_user_payload['password']


@pytest.mark.parametrize(
    'field, value',
    [
        ('email', 'l' * 150 + '@email.com'),
        ('first_name', 'a' * 121),
        ('last_name', 'm' * 121)
    ]
)
async def test_user_cant_register_invalid_long_fields(
    field: str,
    value: str,
    new_user_payload: dict,
    client: AsyncClient
):
    new_user_payload[field] = value

    response = await client.post(REGISTER_URL, json=new_user_payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert 'detail' in response.json()


async def test_register_duplicate_email(
    client: AsyncClient,
    user: User,
    new_user_payload: dict
):
    new_user_payload['email'] = user.email

    response = await client.post(REGISTER_URL, json=new_user_payload)
    assert response.status_code == HTTPStatus.CONFLICT
    assert 'detail' in response.json()


async def test_user_can_login(
    client: AsyncClient,
    user: User,
    user_password: str
):
    response = await client.post(
        LOGIN_URL,
        data={'username': user.email, 'password': user_password}
    )
    assert response.status_code == HTTPStatus.OK

    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.parametrize(
    'email, password, expected_status',
    [
        ('wrong@email.com', 'correct_password', HTTPStatus.UNAUTHORIZED),
        ('correct@email.com', 'wrong_password', HTTPStatus.UNAUTHORIZED),
        ('', '', HTTPStatus.UNPROCESSABLE_ENTITY),
    ]
)
async def test_login_fail(
    email: str,
    password: str,
    expected_status: int,
    client: AsyncClient
):
    response = await client.post(
        LOGIN_URL,
        data={'username': email, 'password': password}
    )
    assert response.status_code == expected_status
    assert 'detail' in response.json()


async def test_access_token_is_work(
    user: User,
    user_password: str,
    client: AsyncClient
):
    response = await client.post(
        LOGIN_URL,
        data={'username': user.email, 'password': user_password}
    )
    assert response.status_code == HTTPStatus.OK

    token = response.json()['access_token']
    auth_headers = {'Authorization': f'Bearer {token}'}

    response_with_token = await client.get(PROFILE_URL, headers=auth_headers)

    assert response_with_token.status_code == HTTPStatus.OK

    data = response_with_token.json()
    assert data['id'] == user.id
    assert data['email'] == user.email
    assert data['full_name'] == user.full_name


@pytest.mark.parametrize(
    'url',
    [PROFILE_URL, USERS_ACCOUNTS_URL, USERS_PAYMENTS_URL]
)
async def test_get_me_without_invalid_access_token(
    url: str,
    client: AsyncClient
):
    invalid_auth_headers = {'Authorization': 'Bearer ' + 'abrakadabra' * 5}
    response = await client.get(url, headers=invalid_auth_headers)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response.json()


async def test_access_token_expired(client: AsyncClient, user: User):
    normal_token = create_access_token(user.id)
    expired_token = create_access_token(user.id, expires_minutes=0)

    response = await client.get(
        PROFILE_URL,
        headers={'Authorization': f'Bearer {normal_token}'}
    )
    assert response.status_code == HTTPStatus.OK

    response_with_expired_token = await client.get(
        PROFILE_URL,
        headers={'Authorization': f'Bearer {expired_token}'}
    )
    assert response_with_expired_token.status_code == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response_with_expired_token.json()


async def test_refresh_is_work(client_with_refresh: AsyncClient):

    response = await client_with_refresh.post(REFRESH_URL)

    assert response.status_code == HTTPStatus.OK

    token = Token.model_validate(response.json())

    auth_response = await client_with_refresh.get(
        PROFILE_URL,
        headers={'Authorization': f'Bearer {token.access_token}'}
    )
    assert auth_response.status_code == HTTPStatus.OK


async def test_refresh_token_rotation(
    client_with_refresh: AsyncClient,
    get_test_async_session: AsyncSession
):
    old_refresh_token = client_with_refresh.cookies['refresh_token']
    old_hash = sha256(old_refresh_token.encode()).hexdigest()

    old_record = await get_test_async_session.execute(
        select(RefreshToken).where(RefreshToken.hashed_token == old_hash)
    )

    old_refresh_from_db = old_record.scalar_one_or_none()
    assert old_refresh_from_db is not None

    response = await client_with_refresh.post(REFRESH_URL)
    assert response.status_code == HTTPStatus.OK

    get_test_async_session.expire_all()

    old_check = await get_test_async_session.execute(
        select(RefreshToken).where(RefreshToken.id == old_refresh_from_db.id)
    )
    assert old_check.scalar_one_or_none() is None

    new_refresh_token = response.cookies['refresh_token']
    new_hash = sha256(new_refresh_token.encode()).hexdigest()

    new_record = await get_test_async_session.execute(
        select(RefreshToken).where(RefreshToken.hashed_token == new_hash)
    )

    new_refresh_from_db = new_record.scalar_one_or_none()
    assert new_refresh_from_db is not None

    assert old_refresh_from_db.id != new_refresh_from_db.id
    assert old_hash != new_hash
    assert old_refresh_token != new_refresh_token


async def test_refresh_token_expired(
        client: AsyncClient,
        user: User,
        get_test_async_session: AsyncSession
):
    expired_token = await create_refresh_token(
        subject=user.id,
        session=get_test_async_session,
        expires_minutes=0
    )

    client.cookies.set('refresh_token', expired_token)

    response = await client.post(REFRESH_URL)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response.json()


async def test_refresh_token_revoked(client_with_revoked_refresh: AsyncClient):
    response = await client_with_revoked_refresh.post(REFRESH_URL)

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert 'detail' in response.json()


async def test_invalid_refresh_token(client: AsyncClient):
    invalid_token = 'abrakadabra'
    client.cookies.set('refresh_token', invalid_token)

    response = await client.post(REFRESH_URL)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'detail' in response.json()
