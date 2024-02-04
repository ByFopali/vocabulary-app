import os

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class GetEnvValues(BaseSettings):
    load_dotenv()  # Дозволяє забрати з .env змінні

    DB_HOST: str = os.environ.get("DB_HOST")
    DB_PORT: int = os.environ.get("DB_PORT")
    DB_NAME: str = os.environ.get("DB_NAME")
    DB_USER: str = os.environ.get("DB_USER")
    DB_PASS: str = os.environ.get("DB_PASS")
    ACCESS_TOKEN_EXPIRE_MINUTES: str = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: str = os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES")
    ALGORITHM: str = os.environ.get("ALGORITHM")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = os.environ.get("JWT_REFRESH_SECRET_KEY")


class JWTSettings(BaseModel):
    env_values: GetEnvValues = GetEnvValues()

    access_token_expire_minutes: str = env_values.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_minutes: str = env_values.REFRESH_TOKEN_EXPIRE_MINUTES
    algorithm: str = env_values.ALGORITHM
    secret_key: str = env_values.JWT_SECRET_KEY
    refresh_secret_key: str = env_values.JWT_REFRESH_SECRET_KEY


class DbSettings(BaseModel):
    env_values: GetEnvValues = GetEnvValues()

    url: str = (
        f"postgresql+asyncpg://{env_values.DB_USER}:{env_values.DB_PASS}"
        f"@{env_values.DB_HOST}:{env_values.DB_PORT}/{env_values.DB_NAME}?async_fallback=True"
    )

    echo: bool = False


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"

    jwt: JWTSettings = JWTSettings()
    db: DbSettings = DbSettings()


settings = Settings()
