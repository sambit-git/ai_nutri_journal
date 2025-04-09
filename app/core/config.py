from pydantic_settings import BaseSettings
from pathlib import Path
import os
from functools import lru_cache

class Settings(BaseSettings):
    # General Flags
    DEBUG: bool = True
    CREATE_TABLES: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-here"  # Change to env var in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # File Storage
    STATIC_FILES_DIR: str = str(Path(__file__).parent.parent / "static")
    MAX_FILE_SIZE_MB: int = 10

    # CORS
    ALLOWED_ORIGINS: list = ["*"]

    # Third-party API Keys
    USDA_API_KEY: str = "<use your API Key>"

    class Config:
        case_sensitive = True
        env_file = ".env"  # For production environment variables

@lru_cache()
def get_settings():
    """Cached settings factory"""
    return Settings()

# Initialize on import
settings = get_settings()
os.makedirs(settings.STATIC_FILES_DIR, exist_ok=True)