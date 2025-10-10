# app/config.py
import os
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import PostgresDsn, computed_field


class Settings(BaseSettings):
    OPEN_WEATHER_API_KEY: str

    # Database settings
    POSTGRES_USER: str

    POSTGRES_PASSWORD: str

    POSTGRES_SERVER: str

    POSTGRES_PORT: int

    POSTGRES_DB: str

    # Authentication settings
    SECRET_KEY: str
    JWT_ALGORITHM: str
    PASSWORD_HASHING_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Determine which .env file to load
    # This is the key change: we check an environment variable.
    if os.getenv("TESTING"):
        use_env_file: ClassVar = ".env.test"
    else:
        use_env_file: ClassVar = ".env"

    # This tells Pydantic to load variables from a .env file
    model_config = SettingsConfigDict(env_file=use_env_file)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field
    @property
    def ASYNC_SQL_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )


# Create a single, reusable instance of the settings
settings = Settings()
