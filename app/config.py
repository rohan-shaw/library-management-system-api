from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI"
    LOG_FILE: str = "app.log"
    DATABASE_URL: str   
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = "your-email"
    EMAIL_PASSWORD: str  = "your-password"
    EMAIL_FROM: str = "your-email"

    class Config:
        env_file = ".env"


settings = Settings()