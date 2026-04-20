from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class Token(AccessToken):
    refresh_token: Optional[str] = None


class RefreshTokenCreate(BaseModel):
    hashed_token: str
    user_id: int
    expires: datetime


class AccessTokenPayload(BaseModel):
    sub: int
    token_type: Literal['access']
    exp: datetime


class RefreshTokenPayload(BaseModel):
    sub: int
    token_type: Literal['refresh']
    exp: datetime
