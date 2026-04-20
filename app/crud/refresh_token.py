from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import or_404
from app.crud.base import CRUDBase
from app.models import RefreshToken


class RefreshTokenCRUD(CRUDBase):
    @or_404
    async def get_token_by_hash(
        self,
        token_hash: str,
        session: AsyncSession
    ) -> RefreshToken:
        stmt = (
            select(RefreshToken)
            .where(token_hash == RefreshToken.hashed_token)
            .options(selectinload(RefreshToken.user))
        )
        refresh_token = await session.execute(stmt)
        return refresh_token.scalars().first()


refresh_token_crud = RefreshTokenCRUD(RefreshToken)
