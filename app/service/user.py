from sqlalchemy.ext.asyncio import AsyncSession

from app.core import exceptions
from app.crud.user import user_crud
from app.models import User
from app.schemas.user import UserCreate


async def user_create_service(
    user_in: UserCreate,
    session: AsyncSession
) -> User:
    """Сервис создания юзера."""
    if await user_crud.is_exists(user_in.email, session):
        raise exceptions.UserExistsException()
    return await user_crud.create(user_in=user_in, session=session)
