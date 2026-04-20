from fastapi import HTTPException, status


class BaseException(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = 'Базовое исключение'

    def __init__(self):
        super().__init__(self.status_code, self.detail)


class BaseAuthException(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Ошибка аутентификации'
    headers = {'WWW-Authenticate': 'Bearer'}

    def __init__(self):
        super().__init__(self.status_code, self.detail, self.headers)


class CredentialsException(BaseAuthException):
    detail = 'Неверные учетные данные'


class TokenExpiredException(BaseAuthException):
    detail = 'Токен просрочен'


class TokenRevokedException(BaseAuthException):
    detail = 'Токен отозван, залогиньтесь заново'


class MissingTokenException(BaseAuthException):
    detail = 'Refresh Token не найден в куках'


class InvalidTokenException (BaseException):
    detail = 'Невалидный токен'


class InvalidSignatureException(BaseException):
    detail = 'Неверная сигнатура вебхука'


class NotFoundException(BaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = 'Объекта не существует'


class UserExistsException(BaseException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'Такой пользователь уже существует.'


class PermissionDeniedException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Недостаточно прав для выполнения действия'


class UserInactiveException(BaseException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Аккаунт деактивирован'


class PaymentAlreadyProcessedException(BaseException):
    status_code = status.HTTP_200_OK
    detail = 'Платеж уже зачислен'
