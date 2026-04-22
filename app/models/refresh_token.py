from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User


class RefreshToken(Base):
    """Модель refresh token'а."""

    hashed_token: Mapped[str] = mapped_column(String, unique=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            'user.id',
            ondelete='CASCADE'
        ),
        unique=True
    )
    user: Mapped['User'] = relationship(back_populates='refresh_token')
    expires: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
