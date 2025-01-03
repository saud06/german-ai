from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    )
    MONGODB_URI: str
    MONGODB_DB_NAME: str | None = None
    JWT_SECRET: str
    OPENAI_API_KEY: str | None = None
    ALLOW_SPEECH_FEATURE: bool = True
    ENABLE_AI_QUIZ_TOPUP: bool = False
    DEV_MODE: bool = False
    ALLOW_DEV_ROUTES: bool = False
    FRONTEND_ORIGIN: str | None = None  # e.g., https://your-frontend.onrender.com

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

def reload_settings() -> Settings:
    """Dev-only: clear cache and reinitialize module-level settings."""
    get_settings.cache_clear()  # type: ignore[attr-defined]
    global settings
    settings = get_settings()
    return settings
