"""
app/core/config.py
==================
Centralised application configuration loaded from environment variables.

Uses Pydantic BaseSettings so every variable is type-validated at startup.
Missing required variables raise a clear ValidationError before the app binds
any port — no silent misconfiguration.
"""

from __future__ import annotations

import secrets
from functools import lru_cache
from typing import List, Literal, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings sourced from environment variables / .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env vars silently
    )

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    app_env: Literal["development", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    db_host: str = Field(default="localhost", description="Hostname/IP of the PostgreSQL server")
    db_port: int = 5432
    db_name: str = Field(default="borsa_db", description="Database name")
    db_user: str = Field(default="app_readonly", description="DB role for the application")
    db_password: str = Field(default="", description="Password for db_user")
    db_sslmode: Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"] = "prefer"

    # ------------------------------------------------------------------ #
    # Session / JWT
    # ------------------------------------------------------------------ #
    session_secret: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        description="Secret key used for JWT signing. MUST be set explicitly in production.",
    )
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    access_token_expire_minutes: int = 30

    # ------------------------------------------------------------------ #
    # CORS
    # ------------------------------------------------------------------ #
    cors_origins: Union[List[AnyHttpUrl], str] = Field(
        default=["http://localhost:5173"],
        description="Comma-separated list of allowed frontend origins.",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Allow a comma-separated string or JSON array in the env file."""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ------------------------------------------------------------------ #
    # Computed properties
    # ------------------------------------------------------------------ #
    @property
    def secure_db_url(self) -> str:
        """Async DSN for the SQLAlchemy engine (psycopg3 driver)."""
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    Using lru_cache means environment is parsed once at startup.
    Call get_settings.cache_clear() in tests to reload settings.
    """
    return Settings()
