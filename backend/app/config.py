from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://aichat:aichat@db:5432/aichat"

    # Redis
    redis_url: str = "redis://redis:6379"

    # Security
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # LLM Providers
    deepseek_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # App
    debug: bool = True
    app_name: str = "AI-Chat"
    api_v1_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
