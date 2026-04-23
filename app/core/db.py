from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    Mapped,
    mapped_column,
    sessionmaker
)

from app.core.config import settings


class Base(DeclarativeBase):
    """Базовый класс моделей."""

    @declared_attr
    @classmethod
    def __tablename__(cls):
        """Задает название таблиц по названию класса модели."""
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_async_engine(settings.database_url, echo=True)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_session():
    """Отдает асинхронное соединение с базой данных."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
