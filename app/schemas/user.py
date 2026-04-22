from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas import AccountSchema


class UserCreate(BaseModel):
    """Схема создания юзера."""

    email: EmailStr
    first_name: str
    last_name: str
    password: str


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

    accounts: List[AccountSchema] = []
