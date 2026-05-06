from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import MAX_LEN_TRANSACTION_ID, MIN_AMOUNT, SCALE


class PaymentRead(BaseModel):
    """Схема для представления платежа."""

    id: int
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    """Схема для создания платежа в базе."""

    transaction_id: str = Field(..., max_length=MAX_LEN_TRANSACTION_ID)
    account_id: int
    user_id: int
    amount: Decimal = Field(..., gt=MIN_AMOUNT, decimal_places=SCALE)

    model_config = ConfigDict(from_attributes=True)


class PaymentWebhook(PaymentCreate):
    """Схема для валидации webhook'а."""

    signature: str
