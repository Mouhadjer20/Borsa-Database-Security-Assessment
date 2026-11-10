"""
app/lab/config.py
=================
Security validation for the Laboratory environment.
Ensures vulnerable experiments cannot be executed unless explicitly enabled
and pointed at an isolated lab database.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def require_lab_enabled() -> None:
    """
    Ensure the lab is explicitly enabled in application settings.
    Raises HTTP 403 / 503 if disabled.
    """
    settings = get_settings()
    if not settings.lab_enabled:
        logger.warning("lab_experiment_blocked_lab_disabled")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Security Lab is disabled on this server. "
                "Vulnerable experiments require explicit laboratory configuration "
                "(LAB_ENABLED=true) in an isolated environment."
            ),
        )

