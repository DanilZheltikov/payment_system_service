from hashlib import sha256

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TokenRevokedException
from app.core.security import (
    check_refresh_token,
    create_access_token,
    create_refresh_token
)
from app.crud import refresh_token_crud
from app.schemas import Token


async def rotate_refresh_token_service(
    token: str,
    session: AsyncSession
) -> Token:
    """Сервис ротации refresh token'а."""
    check_refresh_token(token)
    refresh_token = await refresh_token_crud.get_token_by_hash(
        token_hash=sha256(token.encode()).hexdigest(),
        session=session
    )
    if refresh_token.revoked:
        raise TokenRevokedException()

    return Token(
        access_token=create_access_token(refresh_token.user_id),
        refresh_token=await create_refresh_token(
            user_id=refresh_token.user_id,
            session=session
        )
    )
