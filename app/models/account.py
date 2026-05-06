from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DEFAULT_AMOUNT, MIN_AMOUNT, PRECISION, SCALE
from app.core.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.payment import Payment


class Account(Base):
    """Модель счета."""

    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=PRECISION, scale=SCALE),
        CheckConstraint(
            f'balance >= {MIN_AMOUNT}',
            name='check_balance_non_negative'
        ),
        default=Decimal(DEFAULT_AMOUNT),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    user: Mapped['User'] = relationship(back_populates='accounts')
    payments: Mapped[List['Payment']] = relationship(back_populates='account')
