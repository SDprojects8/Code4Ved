"""Application settings configuration."""

import os
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""

    # Application Settings
    APP_NAME: str = Field(default="lcm-automation", env="APP_NAME")
    APP_VERSION: str = Field(default="0.1.0", env="APP_VERSION")
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")

    # API Configuration
    API_HOST: str = Field(default="localhost", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_SECRET_KEY: str = Field(default="dev-secret-key", env="API_SECRET_KEY")
    API_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"], env="API_CORS_ORIGINS"
    )

    # Database Configuration
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis Configuration
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")

    # Security
    JWT_SECRET_KEY: str = Field(default="jwt-secret-key", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Feature Flags
    ENABLE_ASYNC_PROCESSING: bool = Field(
        default=True, env="ENABLE_ASYNC_PROCESSING"
    )
    ENABLE_MONITORING: bool = Field(default=True, env="ENABLE_MONITORING")
    ENABLE_CACHE: bool = Field(default=False, env="ENABLE_CACHE")

    # Development Settings
    DEV_RELOAD: bool = Field(default=True, env="DEV_RELOAD")
    DEV_PROFILER: bool = Field(default=False, env="DEV_PROFILER")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.APP_ENV == "test"


# Global settings instance
settings = Settings()