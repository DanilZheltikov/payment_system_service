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

    async def get_or_create(
        self,
        user_id: int,
        account_id: int,
        session: AsyncSession
    ) -> Account:
        stmt = (
            select(self.model)
            .where(
                self.model.id == account_id,
                self.model.user_id == user_id
            )
        )
        result = await session.execute(stmt)
        if not (account := result.scalar_one_or_none()):
            session.add(account := self.model(id=account_id, user_id=user_id))

        return account


account_crud = AccountCRUD(Account)
