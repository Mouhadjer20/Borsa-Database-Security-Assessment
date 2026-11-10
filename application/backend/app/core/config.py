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
from typing import List, Literal

from pydantic import AnyHttpUrl, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings sourced from environment variables / .env file.

    All fields with no default value are REQUIRED; the application will refuse
    to start when they are absent.
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
    app_security_mode: Literal["secure", "vulnerable"] = "secure"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ------------------------------------------------------------------ #
    # Secure-mode database (uses app_readonly / app_writer roles)
    # ------------------------------------------------------------------ #
    db_host: str = Field(..., description="Hostname/IP of the PostgreSQL server")
    db_port: int = 5432
    db_name: str = Field(..., description="Database name")
    db_user: str = Field(..., description="DB role for the application (app_readonly or app_writer)")
    db_password: str = Field(..., description="Password for db_user")
    db_sslmode: Literal["disable", "allow", "prefer", "require", "verify-ca", "verify-full"] = "require"

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
    cors_origins: List[AnyHttpUrl] = Field(
        default=["http://localhost:5173"],
        description="Comma-separated list of allowed frontend origins.",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Allow a comma-separated string in the env file."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ------------------------------------------------------------------ #
    # Vulnerable Lab
    # ------------------------------------------------------------------ #
    lab_enabled: bool = False
    lab_db_host: str | None = None
    lab_db_port: int = 5432
    lab_db_name: str | None = None
    lab_db_user: str | None = None
    lab_db_password: str | None = None

    # ------------------------------------------------------------------ #
    # Derived / computed helpers
    # ------------------------------------------------------------------ #
    @property
    def secure_db_url(self) -> str:
        """Async DSN for the secure-mode engine (psycopg3 driver)."""
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def lab_db_url(self) -> str:
        """Async DSN for the lab engine — only valid when lab is enabled."""
        if not self.lab_enabled:
            raise RuntimeError("Lab is not enabled; lab_db_url is unavailable.")
        return (
            f"postgresql+psycopg://{self.lab_db_user}:{self.lab_db_password}"
            f"@{self.lab_db_host}:{self.lab_db_port}/{self.lab_db_name}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    # ------------------------------------------------------------------ #
    # Startup validation
    # ------------------------------------------------------------------ #
    @model_validator(mode="after")
    def _validate_lab_config(self) -> "Settings":
        """
        Security rule: when LAB_ENABLED=true all lab DB variables must be
        present.  The app refuses to start rather than silently falling back
        to the secure DB or running lab experiments against production data.
        """
        if self.lab_enabled:
            missing = [
                name
                for name, value in {
                    "LAB_DB_HOST": self.lab_db_host,
                    "LAB_DB_NAME": self.lab_db_name,
                    "LAB_DB_USER": self.lab_db_user,
                    "LAB_DB_PASSWORD": self.lab_db_password,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(
                    f"LAB_ENABLED=true but the following required lab variables are missing: "
                    f"{', '.join(missing)}. "
                    "The application refuses to start the lab without a fully configured "
                    "isolated laboratory database."
                )

        if self.app_security_mode == "vulnerable" and not self.lab_enabled:
            raise ValueError(
                "APP_SECURITY_MODE=vulnerable requires LAB_ENABLED=true. "
                "Vulnerable mode must only run inside the isolated laboratory."
            )

        return self

    @model_validator(mode="after")
    def _warn_insecure_session_secret(self) -> "Settings":
        """Warn loudly when no explicit session secret is set in production."""
        if self.is_production and len(self.session_secret) < 32:
            raise ValueError(
                "SESSION_SECRET must be at least 32 characters in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    Using lru_cache means environment is parsed once at startup.
    Call get_settings.cache_clear() in tests to reload settings.
    """
    return Settings()
