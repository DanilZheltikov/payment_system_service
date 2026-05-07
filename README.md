# Payment System Service

**Payment System Service** - Сервис обработки платежей с JWT-аутентификацией и ротацией refresh-токенов.<br>
Сервис родился из [тестового задания](https://example.com), которое я немного перевыполнил.

## Стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** (async) -ORM
- **Alembic** - миграции
- **PostgreSQL** - база данных
- **Pydantic v2** - валидация
- **Docker / Docker Compose** - контейнеризаци
- **pytest + pytest-asyncio** - тестирование
- **Testcontainers** - изолированная тестовая БД

## Возможности

- регистрация и логин пользователей
- аутентификация через access token
- безопасная ротация refresh token
- хранение refresh token в HTTP-only cookie
- просмотр профиля текущего пользователя
- получение списка собственных счетов и платежей
- административное управление пользователями
- webhook-прием платежей с проверкой подписи
- idempotent-процессинг платежей по `transaction_id`
- асинхронная работа с базой данных

## Архитектура

- `app/main.py` - точка запуска FastAPI
- `app/api/routers.py` - маршрутизация
- `app/api/v1/` - API-эндпоинты
- `app/core/` - конфигурация, безопасность, база данных, исключения
- `app/models/` - SQLAlchemy-модели
- `app/schemas/` - Pydantic-схемы
- `app/crud/` - базовые операции CRUD
- `app/service/` - бизнес-логика
- `tests/` - автотесты

## API

### Аутентификация

- `POST /auth/register` - регистрация пользователя
- `POST /auth/login` - логин, получает access token и refresh token cookie
- `POST /auth/refresh` - ротация refresh token, возвращает новый access token

### Пользователь

- `GET /me/` - информация о текущем пользователе
- `GET /me/accounts` - счета текущего пользователя
- `GET /me/payments` - платежи текущего пользователя

### Админ

> Доступно только для пользователей с `is_admin=true`

- `GET /admin/users/` - список пользователей с их счетами
- `GET /admin/users/{user_id}` - данные пользователя и счета
- `POST /admin/users/create` - создание пользователя
- `PATCH /admin/users/{user_id}` - обновление пользователя
- `DELETE /admin/users/{user_id}` - удаление пользователя

### Webhook

- `POST /webhook/payment` - прием платежа от внешнего сервиса
  - включает проверку цифровой подписи
  - создает платеж и обновляет баланс счета

## Установка и запуск

1. Создать `.env` файл.
2. Установить и запустить `PostgreSQL`
3. Заполнить переменные:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `SECRET_KEY_TO_WEBHOOK`
   - `ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `REFRESH_TOKEN_EXPIRE_MINUTES`
   - ***Для автоматического создания админа и обычного пользователя заполнить:***
      - `USER_EMAIL`
      - `USER_PASSWORD`
      - `ADMIN_EMAIL`
      - `ADMIN_PASSWORD`
  
4. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Применить миграции:
   ```bash
   alembic upgrade head
   ```
6. Запустить:
   ```bash
    uvicorn app.main:app --reload
   ```
---

Документация будет доступна по адресу: 
- [Swagger UI](http://127.0.0.1:8000/docs)

--- 

### Запуск через Docker
```bash
docker compose up --build
```
Документация будет доступна по адресу: 
- [Swagger UI](http://localhost:80/docs)


## Тестирование

*Для запуска тестов необходимо установить Docker*
```bash
pytest
```

### Автор :man_technologist::

[Danil Zheltikov](https://github.com/DanilZheltikov)