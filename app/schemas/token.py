from datetime import datetime
from typing import Annotated, Optional, Literal

from pydantic import BaseModel, BeforeValidator

ForceStr = Annotated[str, BeforeValidator(lambda value: str(value))]


class AccessToken(BaseModel):
    """Схема для представления access token'а."""

    access_token: str
    token_type: str = 'bearer'


class Token(AccessToken):
    """Cхема для передачи пары токенов."""

    refresh_token: Optional[str] = None


class RefreshTokenCreate(BaseModel):
    """Схема для создания refresh token'а."""

    hashed_token: str
    user_id: int
    expires: datetime


class AccessTokenPayload(BaseModel):
    """Схема для валидации access token'а."""

    sub: int
    exp: datetime
    token_type: Literal['access'] = 'access'


class TokenCreatePayload(BaseModel):
    """Схема для кодирования токенов."""

    sub: ForceStr
    exp: datetime
    token_type: Literal['access', 'refresh']
