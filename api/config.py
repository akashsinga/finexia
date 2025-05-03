# api/config.py - Configuration for Finexia API

import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """API Settings loaded from environment variables with defaults"""
    
    # General settings
    APP_NAME: str = "Finexia API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000","http://localhost:8000","https://finexia.app"]
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database connection
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:password@localhost:5432/finexia")
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Model and prediction settings
    DEFAULT_MAX_DAYS: int = 5
    STRONG_MOVE_THRESHOLD: float = 3.0
    
    # Cache settings
    CACHE_TTL: int = 60 * 5  # 5 minutes
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    """Create cached settings instance"""
    return Settings()

# Export settings for use in other modules
settings = get_settings()