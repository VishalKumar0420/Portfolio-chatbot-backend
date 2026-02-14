from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    ENV: str
    DATABASE_URL: str | None = None
    REDIS_URL: str | None = None
    SECRET_KEY: str | None = None
    PINECONE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_MINUTES: int = 5
    # MAIL_USERNAME: str | None = None
    # MAIL_PASSWORD: str | None = None
    # MAIL_FROM: str | None = None
    # MAIL_SERVER: str | None = None
    # MAIL_PORT: int | None = None
    REDIS_URL: str
    BREVO_API_KEY:str
    FROM_EMAIL:str


@lru_cache
def get_settings() -> Settings:
    return Settings()
