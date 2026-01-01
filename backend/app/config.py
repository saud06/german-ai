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
    
    # Redis Configuration
    REDIS_URL: str = "redis://redis:6379"
    REDIS_MAX_CONNECTIONS: int = 50
    
    # WebSocket Configuration
    WS_MAX_CONNECTIONS: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Ollama Configuration
    OLLAMA_HOST: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "mistral:7b"
    OLLAMA_MODEL_FAST: str = "llama3.2:3b"
    OLLAMA_MODEL_GRAMMAR: str = "mistral:7b"  # Fast enough for real-time grammar checking
    OLLAMA_TIMEOUT: int = 120
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_MAX_TOKENS: int = 2048
    
    # Voice Pipeline Configuration
    WHISPER_HOST: str = "http://whisper:9000"
    WHISPER_MODEL: str = "medium"
    WHISPER_LANGUAGE: str = "de"
    
    PIPER_HOST: str = "http://piper:10200"
    PIPER_VOICE: str = "de_DE-eva_k-x_low"  # Young female German voice
    PIPER_SAMPLE_RATE: int = 22050
    
    # Feature Flags
    ENABLE_AI_CONVERSATION: bool = False
    ENABLE_VOICE_FEATURES: bool = False
    ENABLE_LIFE_SIMULATION: bool = False
    
    # Stripe Configuration (Payment Processing)
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_PREMIUM_PRICE_ID: str | None = None
    STRIPE_PLUS_PRICE_ID: str | None = None

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
