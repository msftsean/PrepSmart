"""Configuration management for PrepSmart."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Claude API
    claude_api_key: str

    # Flask
    flask_env: str = "development"
    flask_debug: bool = True
    flask_secret_key: str

    # Database
    database_url: str = "sqlite:///prepsmart.db"

    # Agent Configuration
    agent_timeout: int = 30
    max_concurrent_tasks: int = 10

    # Logging
    log_level: str = "INFO"

    # CORS (Optional)
    allowed_origins: Optional[str] = None

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
