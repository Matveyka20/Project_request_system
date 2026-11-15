"""
Configuration module for the Request System application.

Uses pydantic-settings with environment variables and .env file support.
Variables can be customized via:
1. Environment variables (highest priority)
2. .env file in project root
3. Default values in Settings class
"""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    
    All settings can be overridden via environment variables.
    Example: export APP_PORT=9000
    """

    # ============================================================================
    # Environment & Server
    # ============================================================================
    app_env: str = Field(
        "development",
        alias="APP_ENV",
        description="Application environment: development, staging, production"
    )
    app_debug: bool = Field(
        True,
        alias="APP_DEBUG",
        description="Enable debug mode (development only)"
    )
    app_port: int = Field(
        8000,
        alias="APP_PORT",
        ge=1,
        le=65535,
        description="Port for API server"
    )
    app_host: str = Field(
        "0.0.0.0",
        alias="APP_HOST",
        description="Host/IP to bind to"
    )
    app_workers: int = Field(
        4,
        alias="APP_WORKERS",
        ge=1,
        description="Number of Uvicorn workers (production only)"
    )
    app_name: str = Field(
        "Request System",
        alias="APP_NAME",
        description="Application name"
    )

    # ============================================================================
    # Database
    # ============================================================================
    database_url: str = Field(
        "sqlite:///./requests.db",
        alias="DATABASE_URL",
        description="Database connection URL (SQLite or PostgreSQL)"
    )
    database_pool_size: int = Field(
        10,
        alias="DATABASE_POOL_SIZE",
        ge=1,
        description="Database connection pool size"
    )
    database_echo_sql: bool = Field(
        False,
        alias="DATABASE_ECHO_SQL",
        description="Log SQL queries (development only)"
    )

    # ============================================================================
    # API Configuration
    # ============================================================================
    api_prefix: str = Field(
        "/api",
        alias="API_PREFIX",
        description="API endpoint prefix"
    )
    api_title: str = Field(
        "Request System API",
        alias="API_TITLE",
        description="API title for documentation"
    )
    api_version: str = Field(
        "1.1.0",
        alias="API_VERSION",
        description="API version"
    )
    api_cors_origins: str = Field(
        "*",
        alias="API_CORS_ORIGINS",
        description="CORS allowed origins (comma-separated or *)"
    )
    api_docs_url: str = Field(
        "/docs",
        alias="API_DOCS_URL",
        description="Swagger UI documentation path"
    )
    api_redoc_url: str = Field(
        "/redoc",
        alias="API_REDOC_URL",
        description="ReDoc documentation path"
    )
    api_openapi_url: str = Field(
        "/openapi.json",
        alias="API_OPENAPI_URL",
        description="OpenAPI schema path"
    )

    # ============================================================================
    # Logging
    # ============================================================================
    log_level: str = Field(
        "INFO",
        alias="LOG_LEVEL",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    class Config:
        """Pydantic configuration for settings loading."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    # ============================================================================
    # Computed Properties
    # ============================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env.lower() == "development"

    @property
    def is_staging(self) -> bool:
        """Check if running in staging mode."""
        return self.app_env.lower() == "staging"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env.lower() == "production"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.api_cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.api_cors_origins.split(",")]

    @property
    def workers(self) -> int:
        """Get number of workers (1 in development, configured in production)."""
        return 1 if self.is_development else self.app_workers

    def __str__(self) -> str:
        """String representation of settings."""
        return (
            f"Settings(env={self.app_env}, "
            f"host={self.app_host}, "
            f"port={self.app_port}, "
            f"db={self.database_url}, "
            f"debug={self.app_debug})"
        )


# Singleton instance
settings = Settings()
