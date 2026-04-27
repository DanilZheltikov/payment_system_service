import pytest_asyncio


@pytest_asyncio.fixture
def access_token():
    from app.core.security import create_access_token

    def _create(user):
        return create_access_token(subject=user.id)

    return _create


@pytest_asyncio.fixture
def auth_client(client, user, access_token):
    token = access_token(user)

    client.headers.update(
        {'Authorization': f'Bearer {token}'}
    )

    return client


@pytest_asyncio.fixture
def admin_client(client, admin, access_token):
    token = access_token(admin)

    client.headers.update(
        {'Authorization': f'Bearer {token}'}
    )

    return client
