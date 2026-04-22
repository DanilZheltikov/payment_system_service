from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    app_title: str = 'Payment System Service'
    database_url: str
    secret_key: str
    secret_key_to_webhook: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()
