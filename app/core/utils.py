from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

from fastapi import Response
from pwdlib import PasswordHash

from app.core.exceptions import NotFoundException

P = ParamSpec('P')
T = TypeVar('T')

password_hash = PasswordHash.recommended()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key='refresh_token',
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )


def or_404(
    func: Callable[P, Coroutine[Any, Any, T | None]]
) -> Callable[P, Coroutine[Any, Any, T | None]]:
    """
    Проверяет, что объект существует, иначе выбрасывает NotFoundException.
    """
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        obj = await func(*args, **kwargs)
        if not obj:
            raise NotFoundException()
        return obj
    return wrapper
