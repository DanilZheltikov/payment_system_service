from typing import Generic, List, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.core.utils import or_404
from app.models.user import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый CRUD класс с основными операциями.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    @or_404
    async def get(
            self,
            obj_id: int,
            session: AsyncSession
    ) -> Optional[ModelType]:
        """Метод GET {obj_id}."""
        db_obj = await session.get(self.model, obj_id)
        return db_obj

    async def get_multi(self, session: AsyncSession) -> List[ModelType]:
        """Метод GET."""
        db_objects = await session.execute(select(self.model))
        return db_objects

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        user: Optional[User] = None,
        commit=True,
        refresh=True
    ) -> ModelType:
        """Метод POST."""
        obj_in_data = obj_in.model_dump()

        if user is not None:
            obj_in_data['user_id'] = user.id
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
        session: AsyncSession
    ) -> ModelType:
        """Метод UPDATE."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump()

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj: ModelType,
        session: AsyncSession
    ) -> ModelType:
        """Метод DELETE."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_multi_by_user(
        self,
        user_id: int,
        session: AsyncSession,
        limit: int,
        offset: int
    ) -> List[ModelType]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
