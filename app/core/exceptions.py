from fastapi import HTTPException, status


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
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = 'Refresh Token не найден в куках'


class UserNotFound(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND,
    detail = 'Пользователя не существует',


class InvalidTokenException (HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST,
    detail = 'Невалидный токен'


class UserExistsException(HTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = 'Такой пользователь уже существует.'


class PermissionDeniedException(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Недостаточно прав для выполнения действия'


class UserInactiveException(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = 'Аккаунт деактивирован'
