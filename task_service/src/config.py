import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: str

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    RABBITMQ_URL: str
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


settings = Settings()


def get_db_url() -> str:
    return (f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@'
            f'{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}')


def get_rb_url() -> str:
    return settings.RABBITMQ_URL
