from datetime import datetime
from typing import Annotated, Optional, Literal

from pydantic import BaseModel, BeforeValidator

ForceStr = Annotated[str, BeforeValidator(lambda value: str(value))]


class AccessToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class Token(AccessToken):
    refresh_token: Optional[str] = None


class RefreshTokenCreate(BaseModel):
    hashed_token: str
    user_id: int
    expires: datetime


class BaseTokenPayload(BaseModel):
    sub: int
    exp: datetime


class AccessTokenPayload(BaseTokenPayload):
    token_type: Literal['access'] = 'access'


class RefreshTokenPayload(BaseTokenPayload):
    token_type: Literal['refresh'] = 'refresh'


class TokenCreatePayload(BaseModel):
    sub: ForceStr
    exp: datetime
    token_type: Literal['access', 'refresh']
