from pydantic_settings import  BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config= SettingsConfigDict(env_file=".env",extra="ignore")
    PINECONE_API_KEY:str
    ENV:str
    GROQ_API_KEY:str
    DATABASE_URL:str
    SECRET_KEY:str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_MINUTES: int = 5
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_FROM: str | None = None
    MAIL_SERVER: str | None = None
    MAIL_PORT: int | None = None
    REDIS_URL:str
    SMTP_SERVER:str
    SMTP_PORT:int
    SMTP_LOGIN:str
    FROM_EMAIL:str
    BREVO_API_KEY:str
settings=Settings()