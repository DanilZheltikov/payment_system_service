from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    id: int
    user_id: int


class AccountSchema(BaseModel):
    id: int
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)
