from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# Always resolve .env relative to this file, regardless of working directory
_ENV_FILE = str(Path(__file__).parent / ".env")


class Settings(BaseSettings):
    FIREWORKS_API_KEY: str
    TAVILY_API_KEY: str = ""  # Optional — set to enable live web search; mocked when empty
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    PORT: int = 8001
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5000,http://localhost:8000"

    class Config:
        env_file = _ENV_FILE
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
