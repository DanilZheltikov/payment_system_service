from fastapi import HTTPException, status

CredentialsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Неверные учетные данные',
    headers={'WWW-Authenticate': 'Bearer'}
)
TokenExpiredException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Токен просрочен',
    headers={'WWW-Authenticate': 'Bearer'}
)
UserNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Пользователя не существует',
)
TokenRevokedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Токен отозван, залогиньтесь заново'
)
InvalidTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Невалидный токен'
)
UserExistsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Такой пользователь уже существует.'
)
MissingTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Refresh Token не найден в куках'
)
