"""
app/database/engine.py
======================
Async SQLAlchemy engine factory for the Borsa application.

Security architecture:
  - Engine uses the least-privileged DB role (app_readonly / app_writer).
  - SSL/TLS enforced via the connect_args sslmode setting.
  - DB credentials are never exposed in log output or exception messages.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level engine reference — initialised in startup, torn down in shutdown.
_secure_engine: AsyncEngine | None = None
_SecureSessionFactory: async_sessionmaker[AsyncSession] | None = None


def _build_engine(dsn: str, sslmode: str, pool_label: str) -> AsyncEngine:
    """
    Create an async SQLAlchemy engine with psycopg3 driver.

    Parameters
    ----------
    dsn:
        Full async DSN including credentials (never logged).
    sslmode:
        PostgreSQL sslmode value: "require", "verify-full", etc.
    pool_label:
        Human-readable label for log messages (never includes credentials).
    """
    connect_args: dict = {"sslmode": sslmode}

    engine = create_async_engine(
        dsn,
        connect_args=connect_args,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=False,  # NEVER set echo=True in production (logs SQL)
    )
    logger.info("db_engine_created", pool=pool_label, sslmode=sslmode)
    return engine


async def init_engines() -> None:
    """
    Initialise the database engine at application startup.
    Called from the FastAPI lifespan handler. Attempts a simple connectivity
    check and logs the outcome. On failure the app starts but endpoints that
    require DB access will return HTTP 503.
    """
    global _secure_engine, _SecureSessionFactory
    settings = get_settings()

    _secure_engine = _build_engine(
        dsn=settings.secure_db_url,
        sslmode=settings.db_sslmode,
        pool_label="secure",
    )
    _SecureSessionFactory = async_sessionmaker(
        bind=_secure_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    await _ping_engine(_secure_engine, "secure")


async def close_engines() -> None:
    """Dispose the engine at application shutdown."""
    global _secure_engine
    if _secure_engine:
        await _secure_engine.dispose()
        logger.info("db_engine_disposed", pool="secure")


async def _ping_engine(engine: AsyncEngine, label: str) -> None:
    """
    Attempt a cheap SELECT 1 to verify connectivity.

    Logs the result but does NOT raise — the app continues to start even when
    the DB is momentarily unreachable.
    """
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("db_ping_success", pool=label)
    except OperationalError as exc:
        logger.error(
            "db_ping_failure",
            pool=label,
            error_type=type(exc).__name__,
            detail="Connection refused or credentials incorrect — check .env",
        )
    except SQLAlchemyError as exc:
        logger.error("db_ping_failure", pool=label, error_type=type(exc).__name__)


def get_secure_engine() -> AsyncEngine:
    """Return the secure engine. Raises RuntimeError if not initialised."""
    if _secure_engine is None:
        raise RuntimeError("Secure engine has not been initialised. Call init_engines() first.")
    return _secure_engine


def get_secure_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the secure session factory. Raises RuntimeError if not initialised."""
    if _SecureSessionFactory is None:
        raise RuntimeError("Session factory has not been initialised. Call init_engines() first.")
    return _SecureSessionFactory
