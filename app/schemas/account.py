from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    """Схема для создания счета."""

    id: int
    user_id: int


class AccountRead(BaseModel):
    """Схема для представления счета."""

    id: int
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)
