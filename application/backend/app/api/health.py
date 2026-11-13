"""
app/api/health.py
=================
Health check endpoint for Borsa.
Reports server status and database connectivity.
Credentials and internal configuration details are never exposed.
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
    db_status = "unavailable"

    try:
        engine = get_secure_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception:
        db_status = "unavailable"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "app_env": settings.app_env,
        "database_status": db_status,
    }
