"""
app/database/session.py
=======================
FastAPI dependency providers for async database sessions.

Two separate dependency functions are provided:
  get_secure_db  — yields a session bound to the secure engine.
  get_lab_db     — yields a session bound to the lab engine.

Security rule: routes MUST NOT mix sessions.  A route that imports
get_secure_db will never accidentally use the vulnerable lab connection.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.database.engine import get_lab_session_factory, get_secure_session_factory

logger = get_logger(__name__)


async def get_secure_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields an async SQLAlchemy session for the secure DB.

    The session is automatically rolled back on exception and closed in the
    finally block to return the connection to the pool.
    """
    factory = get_secure_session_factory()
    async with factory() as session:
        try:
            yield session
        except OperationalError as exc:
            await session.rollback()
            logger.error(
                "db_session_error",
                pool="secure",
                error_type=type(exc).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is temporarily unavailable. Please try again later.",
            ) from None  # suppress credential details from leaking up the chain
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.error(
                "db_session_error",
                pool="secure",
                error_type=type(exc).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A database error occurred.",
            ) from None


async def get_lab_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields an async SQLAlchemy session for the lab DB.

    Only available when LAB_ENABLED=true.  Returns HTTP 503 when the lab
    engine has not been initialised, preventing silent fallback to the secure DB.
    """
    try:
        factory = get_lab_session_factory()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Lab mode is not enabled on this server.",
        ) from exc

    async with factory() as session:
        try:
            yield session
        except OperationalError as exc:
            await session.rollback()
            logger.error(
                "db_session_error",
                pool="lab",
                error_type=type(exc).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Lab database is temporarily unavailable.",
            ) from None
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.error(
                "db_session_error",
                pool="lab",
                error_type=type(exc).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="A lab database error occurred.",
            ) from None
