from app.core.config import settings
from app.core.db import get_session
from app.core.utils import get_password_hash
from app.crud import user_crud
from app.models import User


async def create_first_users() -> None:
    async with get_session() as session:
        if not await user_crud.get_user_by_email(settings.user_email, session):
            session.add(
                User(
                    email=settings.user_email,
                    hashed_password=get_password_hash(settings.user_password),
                    first_name='user',
                    last_name='notadmin',
                    is_admin=False
                )
            )
        if not await user_crud.get_user_by_email(
            settings.admin_email,
            session
        ):
            session.add(
                User(
                    email=settings.admin_email,
                    hashed_password=get_password_hash(settings.admin_password),
                    first_name='admin',
                    last_name='isadmin',
                    is_admin=True
                )
            )
