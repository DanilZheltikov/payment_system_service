from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Account, User


class AccountCRUD(CRUDBase):
    async def get_accounts_by_user(
        self,
        user: User,
        session: AsyncSession
    ) -> List[Account]:
        stmt = select(self.model).where(self.model.user_id == user.id)
        result = await session.execute(stmt)

        return list(result.scalars().all())


account_crud = AccountCRUD(Account)
