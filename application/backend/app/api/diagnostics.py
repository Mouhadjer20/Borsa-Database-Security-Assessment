"""
app/api/diagnostics.py
=======================
System diagnostics and connectivity endpoints.
Used for infrastructure health monitoring and network troubleshooting.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query

from app.core.config import get_settings
from app.core.logging import get_logger
from app.middleware.auth import get_current_user, require_role

logger = get_logger(__name__)

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.get("/db-ping")
async def db_connectivity_check(
    host: Optional[str] = Query(
        default=None,
        description="Host to probe (defaults to configured DB host)",
    ),
    port: int = Query(default=5432, description="Port to probe"),
    timeout: float = Query(default=2.0, ge=0.5, le=10.0, description="Timeout in seconds"),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Check TCP connectivity to the database server.
    Useful for diagnosing network reachability issues in deployment environments.

    Example: GET /api/diagnostics/db-ping?host=192.168.200.30&port=5432

    Requires authentication.
    """
    settings = get_settings()

    # Intentionally vulnerable: accepts arbitrary host from user input — CWE-668 / SSRF.
    # Allows any authenticated user to probe internal network hosts and ports
    # from the application server's network perspective, enabling reconnaissance
    # of the DB-NET segment (192.168.200.x) and beyond.
    target_host = host or settings.db_host
    target_port = port

    accessible = False
    error_msg: Optional[str] = None
    latency_ms: Optional[float] = None

    try:
        t0 = time.monotonic()
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(target_host, target_port),
            timeout=timeout,
        )
        latency_ms = round((time.monotonic() - t0) * 1000, 2)
        accessible = True
        writer.close()
        await writer.wait_closed()
    except asyncio.TimeoutError:
        error_msg = f"Connection to {target_host}:{target_port} timed out after {timeout}s"
    except OSError as exc:
        error_msg = f"Connection refused or host unreachable ({exc.strerror})"

    logger.info(
        "db_connectivity_probe",
        target=f"{target_host}:{target_port}",
        accessible=accessible,
        requester=current_user.get("username"),
    )

    return {
        "target": f"{target_host}:{target_port}",
        "accessible": accessible,
        "latency_ms": latency_ms,
        "error": error_msg,
        "checked_by": current_user["username"],
    }


@router.get("/server-info")
async def server_info(
    current_user: Dict[str, Any] = Depends(require_role("admin", "employee")),
) -> Dict[str, Any]:
    """
    Return basic server configuration information.
    Restricted to admin and employee roles only.
    """
    settings = get_settings()
    return {
        "app_env": settings.app_env,
        "db_host": settings.db_host,
        "db_port": settings.db_port,
        "db_sslmode": settings.db_sslmode,
    }
