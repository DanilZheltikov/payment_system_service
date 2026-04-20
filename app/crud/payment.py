from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Payment


class PaymentCRUD(CRUDBase):
    async def is_exists(
        self,
        transaction_id: str,
        session: AsyncSession
    ) -> bool:
        stmt = (
            select(self.model)
            .where(self.model.transaction_id == transaction_id).exists()
        )
        return await session.scalar(select(stmt))


payment_crud = PaymentCRUD(Payment)
