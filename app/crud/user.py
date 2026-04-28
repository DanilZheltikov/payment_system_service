from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.utils import get_password_hash, or_404
from app.crud.base import CRUDBase
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate


class UserCRUD(CRUDBase[User, UserCreate, UserUpdate]):
    """СRUD-класс пользователя."""

    async def create(
        self,
        user_in: UserCreate,
        session: AsyncSession
    ) -> UserRead:
        """Метод создания нового пользователя."""

        user_in_data = user_in.model_dump()
        user_in_data['hashed_password'] = get_password_hash(
            user_in_data.pop('password')
        )
        user_db = self.model(**user_in_data)
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        return user_db

    async def get_user_by_email(
        self,
        email: str,
        session: AsyncSession,
    ) -> Optional[User]:
        """Метод получения пользователя по email."""

        stmt = select(self.model).where(email == self.model.email)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_all_users_with_accounts(
        self,
        limit: int,
        offset: int,
        session: AsyncSession
    ) -> List[User]:
        """Метод получения всех пользователей вместе со всеми их счетами."""

        stmt = (
            select(self.model)
            .options(selectinload(self.model.accounts))
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @or_404
    async def get_user_with_accounts(
        self,
        user_id: int,
        session: AsyncSession
    ) -> User:
        """Метод получения одного пользователя вместе со всеми его счетами."""

        stmt = (
            select(self.model)
            .where(self.model.id == user_id)
            .options(selectinload(self.model.accounts))
        )
        result = await session.execute(stmt)

        return result.scalar_one_or_none()


user_crud = UserCRUD(User)
