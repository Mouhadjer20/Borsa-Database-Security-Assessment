"""
app/database/session.py
=======================
FastAPI dependency provider for async database sessions.

Provides get_secure_db which yields a session bound to the application engine.
"""

from __future__ import annotations

from typing import AsyncGenerator

from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.database.engine import get_secure_session_factory

logger = get_logger(__name__)


async def get_secure_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yields an async SQLAlchemy session.

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
            ) from None
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
