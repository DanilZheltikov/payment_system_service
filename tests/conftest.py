import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from app.core.db import Base, get_async_session
from app.main import app
from app.models import Account, Payment, RefreshToken, User  # noqa

pytest_plugins = [
    'tests.fixtures.factories',
    'tests.fixtures.clients',
    'tests.fixtures.data',
    'tests.fixtures.users'
]


@pytest.fixture(scope='session')
def event_loop():
    """Создает экземпляр цикла событий для каждой тестовой сессии."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
def postgres_container():
    with PostgresContainer('postgres:15-alpine') as postgres:
        yield postgres


@pytest_asyncio.fixture(scope='session')
async def engine(postgres_container):
    url = (
        'postgresql+asyncpg://'
        f'{postgres_container.username}:'
        f'{postgres_container.password}@'
        f'{postgres_container.get_container_host_ip()}:'
        f'{postgres_container.get_exposed_port(5432)}/'
        f'{postgres_container.dbname}'
    )
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def get_test_async_session(engine):
    async with engine.connect() as conn:
        await conn.begin()

        session_maker = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint"
        )
        async with session_maker() as session:
            yield session

        await conn.rollback()


@pytest_asyncio.fixture
async def client(get_test_async_session):
    async def override_test_async_session():
        yield get_test_async_session

    app.dependency_overrides[get_async_session] = override_test_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as async_client:

        yield async_client

    app.dependency_overrides.clear()
