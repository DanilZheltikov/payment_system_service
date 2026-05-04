from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import UserRelatedBaseCRUD
from app.models import Account
from app.schemas import AccountCreate


class AccountCRUD(UserRelatedBaseCRUD[Account, AccountCreate]):
    """CRUD класс счета."""

    async def get_or_create_with_lock(
        self,
        account_id: int,
        user_id: int,
        session: AsyncSession
    ) -> Account:
        """Создает или получает счет с блокировкой."""
        try:
            async with session.begin_nested():
                return await self.create(
                    obj_in=AccountCreate(id=account_id, user_id=user_id),
                    session=session,
                    commit=False,
                    refresh=False
                )

        except IntegrityError:
            pass

        result = await session.execute(
            select(self.model)
            .where(self.model.id == account_id)
            .with_for_update()
        )
        return result.scalar_one()

    async def update_balance_atomic(
        self,
        account_id: int,
        amount: Decimal,
        session: AsyncSession
    ):
        """Атомарное обновление баланса."""
        stmt = (
            update(self.model)
            .where(self.model.id == account_id)
            .values(balance=self.model.balance + amount)
        )
        await session.execute(stmt)


account_crud = AccountCRUD(Account)
