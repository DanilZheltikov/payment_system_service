from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account


class Payment(Base):
    transaction_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=15, scale=2),
        CheckConstraint('amount > 0', name='check_amount_non_negative'),
        nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey('account.id'),
        nullable=False
    )
    account: Mapped['Account'] = relationship(back_populates='payment')
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=False
    )
    user: Mapped['User'] = relationship(back_populates='payments')
