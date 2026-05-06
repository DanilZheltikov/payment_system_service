from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.constants import (
    MAX_LEN_EMAIL,
    MAX_LEN_FIRST_NAME,
    MAX_LEN_LAST_NAME,
    MAX_LEN_PASSWORD
)
from app.schemas import AccountRead


class UserCreate(BaseModel):
    """Схема создания юзера."""

    email: EmailStr = Field(..., max_length=MAX_LEN_EMAIL)
    first_name: str = Field(..., max_length=MAX_LEN_FIRST_NAME)
    last_name: str = Field(..., max_length=MAX_LEN_LAST_NAME)
    password: str = Field(..., max_length=MAX_LEN_PASSWORD)


class UserLogin(BaseModel):
    """Схема для авторизации пользователя."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""

    first_name: str
    last_name: str
    is_active: bool
    is_admin: bool


class UserRead(BaseModel):
    """Схема для представления пользователя во вне."""

    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class UserWithAccountsRead(UserRead):
    """Схема представления пользователя вместе с его счетами."""

    accounts: List[AccountRead] = []
