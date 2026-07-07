from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    DOMAIN: str = "http://localhost:8000"
    FRONTEND_DOMAIN: str = "http://localhost:5000"
    OAUTH_GITHUB_CLIENT_ID: str
    OAUTH_GITHUB_CLIENT_SECRET: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    JWT_SECRET: str
    SESSION_SECRET: str
    ENVIRONMENT: Literal["development", "production"] = "development"
    FireworksAPIKey: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = Settings()
