from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DEFAULT_AMOUNT, MIN_AMOUNT, PRECISION, SCALE
from app.core.db import Base
from app.models.mixins import UserRelationMixin

if TYPE_CHECKING:
    from app.models.payment import Payment


class Account(UserRelationMixin, Base):
    """Модель счета."""

    _user_back_populates = 'accounts'

    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=PRECISION, scale=SCALE),
        CheckConstraint(
            f'balance >= {MIN_AMOUNT}',
            name='check_balance_non_negative'
        ),
        default=Decimal(DEFAULT_AMOUNT),
        nullable=False
    )
    payments: Mapped[List['Payment']] = relationship(back_populates='account')
