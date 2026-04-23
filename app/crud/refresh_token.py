from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import or_404
from app.crud.base import UserRelatedBaseCRUD
from app.models import RefreshToken


class RefreshTokenCRUD(UserRelatedBaseCRUD[RefreshToken]):
    """CRUD-класс refresh token'а."""

    @or_404
    async def get_token_by_hash(
        self,
        token_hash: str,
        session: AsyncSession
    ) -> RefreshToken:
        """Метод получения refresh token'а по его хешу."""

        stmt = (
            select(self.model)
            .where(self.model.hashed_token == token_hash)
        )
        refresh_token = await session.execute(stmt)
        return refresh_token.scalars().first()


refresh_token_crud = RefreshTokenCRUD(RefreshToken)
