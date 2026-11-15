"""Tests for the configuration system."""

import os
from pathlib import Path

import pytest

from request_system.config import Settings, settings


class TestSettingsDefaults:
    """Test default configuration values."""

    def test_default_environment(self):
        """Test default environment is development."""
        s = Settings()
        assert s.app_env == "development"

    def test_default_debug_enabled(self):
        """Test debug is enabled by default."""
        s = Settings()
        assert s.app_debug is True

    def test_default_port(self):
        """Test default port is 8000."""
        s = Settings()
        assert s.app_port == 8000

    def test_default_host(self):
        """Test default host is 0.0.0.0."""
        s = Settings()
        assert s.app_host == "0.0.0.0"

    def test_default_workers(self):
        """Test default workers is 4."""
        s = Settings()
        assert s.app_workers == 4

    def test_default_database_url(self):
        """Test default database is SQLite."""
        s = Settings()
        assert s.database_url == "sqlite:///./requests.db"

    def test_default_api_prefix(self):
        """Test default API prefix."""
        s = Settings()
        assert s.api_prefix == "/api"

    def test_default_api_version(self):
        """Test default API version."""
        s = Settings()
        assert s.api_version == "1.1.0"

    def test_default_log_level(self):
        """Test default log level is INFO."""
        s = Settings()
        assert s.log_level == "INFO"


class TestSettingsEnvironmentVariables:
    """Test loading settings from environment variables."""

    def test_env_override_port(self, monkeypatch):
        """Test port can be overridden via APP_PORT env var."""
        monkeypatch.setenv("APP_PORT", "9000")
        s = Settings()
        assert s.app_port == 9000

    def test_env_override_host(self, monkeypatch):
        """Test host can be overridden via APP_HOST env var."""
        monkeypatch.setenv("APP_HOST", "127.0.0.1")
        s = Settings()
        assert s.app_host == "127.0.0.1"

    def test_env_override_database_url(self, monkeypatch):
        """Test database URL can be overridden via DATABASE_URL env var."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
        s = Settings()
        assert s.database_url == "postgresql://user:pass@localhost/db"

    def test_env_override_environment(self, monkeypatch):
        """Test environment can be overridden via APP_ENV env var."""
        monkeypatch.setenv("APP_ENV", "production")
        s = Settings()
        assert s.app_env == "production"

    def test_env_override_debug(self, monkeypatch):
        """Test debug flag can be overridden via APP_DEBUG env var."""
        monkeypatch.setenv("APP_DEBUG", "false")
        s = Settings()
        assert s.app_debug is False

    def test_env_override_multiple(self, monkeypatch):
        """Test multiple environment variable overrides."""
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("APP_PORT", "8080")
        monkeypatch.setenv("APP_DEBUG", "false")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        s = Settings()
        assert s.app_env == "production"
        assert s.app_port == 8080
        assert s.app_debug is False
        assert s.log_level == "WARNING"


class TestSettingsProperties:
    """Test computed properties."""

    def test_is_development(self):
        """Test is_development property."""
        s = Settings(app_env="development")
        assert s.is_development is True
        assert s.is_staging is False
        assert s.is_production is False

    def test_is_staging(self):
        """Test is_staging property."""
        s = Settings(app_env="staging")
        assert s.is_staging is True
        assert s.is_development is False
        assert s.is_production is False

    def test_is_production(self):
        """Test is_production property."""
        s = Settings(app_env="production")
        assert s.is_production is True
        assert s.is_development is False
        assert s.is_staging is False

    def test_cors_origins_wildcard(self):
        """Test CORS origins parsing with wildcard."""
        s = Settings(api_cors_origins="*")
        assert s.cors_origins == ["*"]

    def test_cors_origins_single(self):
        """Test CORS origins parsing with single origin."""
        s = Settings(api_cors_origins="https://example.com")
        assert s.cors_origins == ["https://example.com"]

    def test_cors_origins_multiple(self):
        """Test CORS origins parsing with multiple origins."""
        s = Settings(api_cors_origins="https://example.com,https://app.example.com")
        assert s.cors_origins == ["https://example.com", "https://app.example.com"]

    def test_cors_origins_with_spaces(self):
        """Test CORS origins parsing with spaces."""
        s = Settings(api_cors_origins="https://example.com, https://app.example.com")
        assert s.cors_origins == ["https://example.com", "https://app.example.com"]

    def test_workers_development(self):
        """Test workers property in development (always 1)."""
        s = Settings(app_env="development", app_workers=8)
        assert s.workers == 1

    def test_workers_production(self):
        """Test workers property in production (uses configured value)."""
        s = Settings(app_env="production", app_workers=8)
        assert s.workers == 8


class TestSettingsValidation:
    """Test settings validation."""

    def test_port_valid_range(self):
        """Test port validation with valid values."""
        s = Settings(app_port=1)
        assert s.app_port == 1
        s = Settings(app_port=8000)
        assert s.app_port == 8000
        s = Settings(app_port=65535)
        assert s.app_port == 65535

    def test_port_invalid_range_too_low(self):
        """Test port validation rejects too low values."""
        with pytest.raises(ValueError):
            Settings(app_port=0)

    def test_port_invalid_range_too_high(self):
        """Test port validation rejects too high values."""
        with pytest.raises(ValueError):
            Settings(app_port=65536)

    def test_workers_minimum(self):
        """Test workers validation requires at least 1."""
        with pytest.raises(ValueError):
            Settings(app_workers=0)

    def test_database_pool_size_minimum(self):
        """Test database pool size requires at least 1."""
        with pytest.raises(ValueError):
            Settings(database_pool_size=0)


class TestSettingsStringRepresentation:
    """Test settings string representation."""

    def test_settings_str(self):
        """Test string representation of settings."""
        s = Settings(
            app_env="production",
            app_host="localhost",
            app_port=9000,
            database_url="postgresql://localhost/db",
            app_debug=False
        )
        str_repr = str(s)
        assert "env=production" in str_repr
        assert "host=localhost" in str_repr
        assert "port=9000" in str_repr
        assert "db=postgresql://localhost/db" in str_repr
        assert "debug=False" in str_repr


class TestSettingsSingleton:
    """Test singleton settings instance."""

    def test_singleton_exists(self):
        """Test that singleton settings instance is available."""
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_singleton_has_attributes(self):
        """Test singleton has all required attributes."""
        assert hasattr(settings, "app_port")
        assert hasattr(settings, "app_host")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "api_prefix")
        assert hasattr(settings, "is_development")
        assert hasattr(settings, "is_production")
