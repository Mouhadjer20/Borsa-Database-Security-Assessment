"""
app/database/engine.py
======================
Async SQLAlchemy engine factory for both secure and lab modes.

Security architecture:
  - Secure engine uses the least-privileged DB role (app_readonly / app_writer).
  - Lab engine uses the overprivileged role (app_vulnerable) and is ONLY created
    when LAB_ENABLED=true.
  - SSL/TLS is enforced via the connect_args sslmode setting.
  - Neither engine is ever swapped silently — the caller must explicitly request
    the lab engine.
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
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level engine references — initialised in startup, torn down in shutdown.
_secure_engine: AsyncEngine | None = None
_lab_engine: AsyncEngine | None = None

_SecureSessionFactory: async_sessionmaker[AsyncSession] | None = None
_LabSessionFactory: async_sessionmaker[AsyncSession] | None = None


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
        # psycopg3 connection arguments
        connect_args=connect_args,
        # Pool configuration — tune per deployment
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,          # seconds to wait for a connection
        pool_recycle=1800,        # recycle connections every 30 min
        pool_pre_ping=True,       # health-check connections before use
        echo=False,               # NEVER set echo=True in production (logs SQL)
    )
    logger.info("db_engine_created", pool=pool_label, sslmode=sslmode)
    return engine


def _build_lab_engine(dsn: str) -> AsyncEngine:
    """
    Create the lab engine.

    The lab engine uses NullPool to avoid connection leaks between experiments
    and to ensure each lab request opens a fresh, isolated connection.
    This is intentional: lab sessions are transient and must not carry over
    any RLS or session-variable state from a previous experiment.
    """
    connect_args: dict = {"sslmode": "prefer"}  # lab may run without TLS in isolated VM

    engine = create_async_engine(
        dsn,
        connect_args=connect_args,
        # NullPool: no pooling — each connection is opened and closed explicitly.
        # This prevents session-variable leakage between experiments.
        poolclass=NullPool,
        echo=False,
    )
    logger.info("lab_engine_created", pool="NullPool")
    return engine


async def init_engines() -> None:
    """
    Initialise database engines at application startup.

    Called from the FastAPI lifespan handler.  Attempts a simple connectivity
    check and logs the outcome.  On failure the app starts but endpoints that
    require DB access will return HTTP 503.
    """
    global _secure_engine, _lab_engine, _SecureSessionFactory, _LabSessionFactory
    settings = get_settings()

    # -- Secure engine --------------------------------------------------------
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

    # -- Lab engine (only when explicitly enabled) ----------------------------
    if settings.lab_enabled:
        _lab_engine = _build_lab_engine(dsn=settings.lab_db_url)
        _LabSessionFactory = async_sessionmaker(
            bind=_lab_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        await _ping_engine(_lab_engine, "lab")


async def close_engines() -> None:
    """Dispose all engines at application shutdown."""
    global _secure_engine, _lab_engine
    if _secure_engine:
        await _secure_engine.dispose()
        logger.info("db_engine_disposed", pool="secure")
    if _lab_engine:
        await _lab_engine.dispose()
        logger.info("db_engine_disposed", pool="lab")


async def _ping_engine(engine: AsyncEngine, label: str) -> None:
    """
    Attempt a cheap SELECT 1 to verify connectivity.

    Logs the result but does NOT raise — the app continues to start even when
    the DB is momentarily unreachable.  Endpoints will return 503 on actual
    queries if the pool is exhausted or the DB is down.
    """
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        logger.info("db_ping_success", pool=label)
    except OperationalError as exc:
        # Log the exception type and a sanitised message — never the DSN.
        logger.error(
            "db_ping_failure",
            pool=label,
            error_type=type(exc).__name__,
            detail="Connection refused or credentials incorrect — check .env",
        )
    except SQLAlchemyError as exc:
        logger.error("db_ping_failure", pool=label, error_type=type(exc).__name__)


def get_secure_engine() -> AsyncEngine:
    """Return the secure-mode engine; raises RuntimeError if not initialised."""
    if _secure_engine is None:
        raise RuntimeError("Secure DB engine has not been initialised.")
    return _secure_engine


def get_lab_engine() -> AsyncEngine:
    """
    Return the lab engine.

    Raises
    ------
    RuntimeError
        When LAB_ENABLED=false or the engine was not initialised.
    """
    if _lab_engine is None:
        raise RuntimeError(
            "Lab DB engine is not available. "
            "Set LAB_ENABLED=true and provide all LAB_DB_* variables."
        )
    return _lab_engine


def get_secure_session_factory() -> async_sessionmaker[AsyncSession]:
    if _SecureSessionFactory is None:
        raise RuntimeError("Secure session factory not initialised.")
    return _SecureSessionFactory


def get_lab_session_factory() -> async_sessionmaker[AsyncSession]:
    if _LabSessionFactory is None:
        raise RuntimeError(
            "Lab session factory not initialised. "
            "Set LAB_ENABLED=true and provide all LAB_DB_* variables."
        )
    return _LabSessionFactory
