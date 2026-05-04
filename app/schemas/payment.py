from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentRead(BaseModel):
    """Схема для представления платежа."""

    id: int
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    """Схема для создания платежа в базе."""

    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal = Field(..., gt=0, decimal_places=2)

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhook(PaymentCreate):
    """Схема для валидации webhook'а."""

    signature: str
