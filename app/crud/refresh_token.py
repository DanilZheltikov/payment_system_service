from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import or_404
from app.crud.base import UserRelatedBaseCRUD
from app.models import RefreshToken
from app.schemas import RefreshTokenCreate


class RefreshTokenCRUD(UserRelatedBaseCRUD[RefreshToken, RefreshTokenCreate]):
    """CRUD-класс refresh token'а."""

    @or_404
    async def get_token_by_hash(
        self,
        token_hash: str,
        session: AsyncSession
    ) -> RefreshToken | None:
        """Метод получения refresh token'а по его хешу."""

        stmt = (
            select(self.model)
            .where(self.model.hashed_token == token_hash)
        )
        refresh_token = await session.execute(stmt)
        return refresh_token.scalar_one_or_none()


refresh_token_crud = RefreshTokenCRUD(RefreshToken)
