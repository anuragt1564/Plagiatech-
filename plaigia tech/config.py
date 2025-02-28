import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    COPYLEAKS_API_KEY: str = os.getenv("COPYLEAKS_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Server Settings
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100/hour")
    RATE_LIMIT_FREE_TIER: str = os.getenv("RATE_LIMIT_FREE_TIER", "10/day")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ]
    
    # Text Processing Settings
    MAX_TEXT_LENGTH: int = 10000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Validate settings
def validate_settings():
    """Validate required settings."""
    missing = []
    
    # Check for production environment
    if settings.ENVIRONMENT == "production":
        # API keys required in production
        if not settings.COPYLEAKS_API_KEY:
            missing.append("COPYLEAKS_API_KEY")
        if not settings.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        
        # JWT secret key should be strong in production
        if settings.JWT_SECRET_KEY == "your_jwt_secret_key":
            print("WARNING: Using default JWT_SECRET_KEY in production is insecure!")
    
    if missing:
        print(f"WARNING: Missing required environment variables: {', '.join(missing)}")
        if settings.ENVIRONMENT == "production":
            raise ValueError(f"Missing required environment variables for production: {', '.join(missing)}")

# Validate settings on import
validate_settings()
