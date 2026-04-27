from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.core.utils import or_404

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый CRUD класс с общими для всех операциями.
    """

    def __init__(self, model: Type[ModelType]):
        """Инициализация класса."""
        self.model = model

    @or_404
    async def get(
            self,
            obj_id: int,
            session: AsyncSession
    ) -> Optional[ModelType]:
        """Метод получения объекта из базы по его id."""
        db_obj = await session.get(self.model, obj_id)
        return db_obj

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        commit=True,
        refresh=True
    ) -> ModelType:
        """Метод создания объекта."""
        obj_in_data = obj_in.model_dump()

        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if commit:
            await session.commit()
            if refresh:
                await session.refresh(db_obj)
        else:
            await session.flush()
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        session: AsyncSession,
        commit=True,
        refresh=True
    ) -> ModelType:
        """Метод обновления объекта."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        if commit:
            await session.commit()
            if refresh:
                await session.refresh(db_obj)
        else:
            await session.flush()
        return db_obj

    async def remove(
        self,
        db_obj: ModelType,
        session: AsyncSession,
        commit=True
    ) -> ModelType:
        """Метод удаления объекта."""
        await session.delete(db_obj)
        if commit:
            await session.commit()
        else:
            await session.flush()

        return db_obj


class UserRelatedBaseCRUD(
    CRUDBase[ModelType, Any, Any],
    Generic[ModelType]
):
    """
    Базовый CRUD класс с операциями для связанных с пользователем моделей.
    """

    async def get_multi_by_user(
        self,
        user_id: int,
        session: AsyncSession,
        limit: int,
        offset: int,
    ) -> List[ModelType]:
        """Метод получения объектов по id пользователя."""
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def remove_by_user_id(
        self,
        user_id: int,
        session: AsyncSession,
        commit=True
    ):
        """Удаление объекта по id пользователя."""
        stmt = delete(self.model).where(self.model.user_id == user_id)
        await session.execute(stmt)

        if commit:
            await session.commit()
        else:
            await session.flush()
