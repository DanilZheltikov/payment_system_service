from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.payment import PaymentBase


class Account(BaseModel):
    name: str
    balance: Decimal
    payments: List[PaymentBase] | None

    model_config = ConfigDict(from_attributes=True)
