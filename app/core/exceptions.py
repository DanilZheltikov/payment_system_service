from fastapi import HTTPException, status


class BaseException(HTTPException):
    """Базовое исключение."""

    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Базовое исключение'

    def __init__(self):
        super().__init__(self.status_code, self.detail)


class BaseAuthException(HTTPException):
    """Базовое исключение аутентификации."""

    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Ошибка аутентификации'
    headers = {'WWW-Authenticate': 'Bearer'}

    def __init__(self):
        super().__init__(self.status_code, self.detail, self.headers)


class AuthException(BaseAuthException):
    detail = 'Неверный логин или пароль'
    headers = None


class CredentialsException(BaseAuthException):
    """Исключение неверных учетных данных пришедших через токен."""

    detail = 'Неверные учетные данные'


class TokenExpiredException(BaseAuthException):
    """Исключение просроченного токена."""

    detail = 'Токен просрочен'


class TokenRevokedException(BaseAuthException):
    """Исключение отозванного токена."""

    detail = 'Токен отозван, залогиньтесь заново'


class MissingTokenException(BaseAuthException):
    """Исключение ненайденного токена в Cookie."""

    detail = 'Refresh Token не найден в куках'


class InvalidTokenException (BaseException):
    """Исключение невалидного токена."""

    detail = 'Невалидный токен'


class InvalidSignatureException(BaseException):
    """Исключение неверной сигнатуры webhook'а."""

    detail = 'Неверная сигнатура вебхука'


class NotFoundException(BaseException):
    """Исключение не существующего объекта."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Объекта не существует'


class UserExistsException(BaseException):
    """
    Исключение для конфликта создаваемого с уже существующим пользователем.
    """

    status_code = status.HTTP_409_CONFLICT
    detail = 'Такой пользователь уже существует.'


class PermissionDeniedException(BaseException):
    """Исключение ограничения прав на действие."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Недостаточно прав для выполнения действия'


class UserInactiveException(BaseException):
    """Исключение деактивированного аккаунта."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Аккаунт деактивирован'


class PaymentAlreadyProcessedException(BaseException):
    """
    Исключение уже существующего платежа, при попытки отправить два одинаковых.
    """

    status_code = status.HTTP_200_OK
    detail = 'Платеж уже зачислен'
