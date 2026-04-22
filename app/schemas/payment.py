from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentRead(BaseModel):
    """Схема для представления платежа."""

    id: int
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhook(BaseModel):
    """Схема для валидации webhook'а."""

    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    signature: str

    model_config = ConfigDict(from_attributes=True)
