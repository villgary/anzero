from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "AppScan Pro"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql://appcheck:appcheck@localhost:5432/appcheck"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    REDIS_URL: str = "redis://localhost:6379/0"

    UPLOAD_DIR: str = "/data/uploads"
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
