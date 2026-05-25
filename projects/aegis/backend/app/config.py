from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://aegis:aegis@localhost:5432/aegis"
    redis_url: str = "redis://localhost:6379"
    kafka_bootstrap_servers: str = "localhost:9092"

    class Config:
        env_file = ".env"
