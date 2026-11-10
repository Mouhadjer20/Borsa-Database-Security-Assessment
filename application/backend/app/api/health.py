"""
app/api/health.py
=================
Health check endpoint for Borsa.
Reports server status, security mode, and database connectivity.
Credentials and database connection details are never exposed.
"""

from __future__ import annotations

from typing import Dict, Any
from fastapi import APIRouter, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.database.engine import get_secure_engine

router = APIRouter(tags=["health"])


@router.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Check the operational status of the backend API and database.
    """
    settings = get_settings()
    db_status = "unhealthy"

    try:
        engine = get_secure_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "healthy"
    except (RuntimeError, SQLAlchemyError):
        db_status = "unavailable"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_env": settings.app_env,
        "app_security_mode": settings.app_security_mode,
        "lab_enabled": settings.lab_enabled,
        "database_status": db_status,
    }

