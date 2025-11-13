from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ntal.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis for USSD session state and rate limiting
    REDIS_URL: str = "redis://localhost:6379"
    
    # USSD configuration
    HASH_PEPPER: str = "dev-hash-pepper-change-in-production"
    CONSENT_VERSION: str = "v0.1-EN-USSD"
    RATE_LIMIT_MAX: int = 10
    
    class Config:
        env_file = ".env"


settings = Settings()
