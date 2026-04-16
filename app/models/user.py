from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.refresh_token import RefreshToken
    from app.models.account import Account
    from app.models.payment import Payment


class User(Base):
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_token: Mapped['RefreshToken'] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        uselist=False
    )
    accounts: Mapped[List['Account']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )
    payments: Mapped[List['Payment']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.title()
