from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import (
    MAX_LEN_TRANSACTION_ID,
    MIN_AMOUNT,
    PRECISION,
    SCALE
)
from app.core.db import Base
from app.models.mixins import UserRelationMixin

if TYPE_CHECKING:
    from app.models.account import Account


class Payment(UserRelationMixin, Base):
    """Модель платежа."""

    _user_back_populates = 'payments'

    transaction_id: Mapped[str] = mapped_column(
        String(MAX_LEN_TRANSACTION_ID),
        unique=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=PRECISION, scale=SCALE),
        CheckConstraint(
            f'amount > {MIN_AMOUNT}',
            name='check_amount_non_negative'
        ),
        nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey('account.id'),
        nullable=False
    )
    account: Mapped['Account'] = relationship(back_populates='payments')
