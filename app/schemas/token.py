from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, field_serializer


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


class TokenCreatePayload(BaseModel):
    """Схема для кодирования токенов."""

    sub: str
    iat: datetime
    exp: datetime
    jti: str
    token_type: str

    @field_serializer('iat', 'exp')
    def serialize_dt(self, dt: datetime) -> int:
        return int(dt.timestamp())


class AccessTokenPayload(TokenCreatePayload):
    """Схема для валидации access token'а."""
    token_type: Literal['access'] = 'access'


class RefreshTokenPayload(TokenCreatePayload):
    """Схема для валидации refreh token'а."""
    token_type: Literal['refresh'] = 'refresh'
