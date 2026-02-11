"""
Centralized configuration management for DevPulse.

Provides type-safe, validated configuration with environment-specific
settings and secrets management.
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, ValidationInfo
from backend.utils.exceptions import ConfigurationError


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="DevPulse", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=1, description="Number of API workers")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    
    # Database
    database_url: str = Field(
        default="sqlite:///./devpulse.db",
        description="Database connection URL"
    )
    database_pool_size: int = Field(default=5, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, description="Database max overflow connections")
    
    # AI Services
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    ai_model: str = Field(default="gpt-4o-mini", description="AI model to use")
    ai_timeout: int = Field(default=30, description="AI API timeout in seconds")
    ai_max_retries: int = Field(default=3, description="AI API max retries")
    
    # Docker/Sandbox
    docker_enabled: bool = Field(default=False, description="Enable Docker sandbox")
    sandbox_image: str = Field(default="devpulse-sandbox", description="Docker sandbox image")
    sandbox_timeout: int = Field(default=120, description="Sandbox execution timeout in seconds")
    sandbox_memory_limit: str = Field(default="512m", description="Sandbox memory limit")
    
    # Analysis Tools
    analysis_timeout: int = Field(default=300, description="Analysis timeout in seconds")
    max_repo_size_mb: int = Field(default=500, description="Maximum repository size in MB")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=10, description="Max requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # ML Model
    ml_model_path: str = Field(
        default="ml/historical_risk_model.joblib",
        description="Path to ML model file"
    )
    
    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for signing tokens"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ConfigurationError(
                f"Invalid environment: {v}. Must be one of {allowed}",
                config_key="environment"
            )
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ConfigurationError(
                f"Invalid log level: {v}. Must be one of {allowed}",
                config_key="log_level"
            )
        return v
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate secret key in production."""
        if info.data.get("environment") == "production" and v == "change-me-in-production":
            raise ConfigurationError(
                "SECRET_KEY must be changed in production environment",
                config_key="secret_key"
            )
        return v
    
    def has_ai_service(self) -> bool:
        """Check if any AI service is configured."""
        return bool(self.groq_api_key or self.openai_api_key)
    
    def get_ai_api_key(self) -> Optional[str]:
        """Get the configured AI API key (prefer Groq)."""
        return self.groq_api_key or self.openai_api_key
    
    def get_ai_api_url(self) -> str:
        """Get the AI API URL based on configured service."""
        if self.groq_api_key:
            return "https://api.groq.com/openai/v1/chat/completions"
        return "https://api.openai.com/v1/chat/completions"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton).
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment (useful for testing).
    
    Returns:
        New settings instance
    """
    global _settings
    _settings = Settings()
    return _settings
