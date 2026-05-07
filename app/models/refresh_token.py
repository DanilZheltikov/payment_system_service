from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.mixins import UserRelationMixin


class RefreshToken(UserRelationMixin, Base):
    """Модель refresh token'а."""

    _user_id_unique = True
    _user_back_populates = 'refresh_token'

    hashed_token: Mapped[str] = mapped_column(String(), unique=True)
    expires: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
