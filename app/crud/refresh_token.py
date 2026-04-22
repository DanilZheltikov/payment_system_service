from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models import RefreshToken


class RefreshTokenCRUD(CRUDBase):
    async def get_token_by_hash(
        self,
        token_hash: str,
        session: AsyncSession
    ) -> RefreshToken:
        stmt = (
            select(self.model)
            .where(self.model.hashed_token == token_hash)
            .options(joinedload(self.model.user))
        )
        refresh_token = await session.execute(stmt)
        return refresh_token.scalars().first()

    async def remove_by_user_id(self, user_id: int, session: AsyncSession):
        stmt = delete(self.model).where(self.model.user_id == user_id)
        await session.execute(stmt)
        await session.flush()


refresh_token_crud = RefreshTokenCRUD(RefreshToken)
