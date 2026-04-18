from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Payment, User


class PaymentCRUD(CRUDBase):
    async def get_payments_by_user(
        self,
        user: User,
        session: AsyncSession
    ) -> List[Payment]:
        stmt = select(self.model).where(self.model.user_id == user.id)
        result = await session.execute(stmt)
        return list(result.scalars().all())


payment_crud = PaymentCRUD(Payment)
