from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import get_password_hash
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserRead


class UserCRUD(CRUDBase):
    async def create(
        self,
        user_in: UserCreate,
        session: AsyncSession
    ) -> UserRead:
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
        stmt = select(User).where(email == User.email)
        user = await session.execute(stmt)
        return user.scalars().first()


user_crud = UserCRUD(User)
