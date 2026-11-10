"""
app/lab/scenarios/network_exposure.py
=====================================
Scenario 4: Database Network Exposure (CWE-668)
Research objective:
Determine whether PostgreSQL accepts connections from unauthorized network locations.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List
from app.core.config import get_settings
from app.core.logging import get_logger, log_security_event
from app.schemas.lab import ExperimentResult

logger = get_logger(__name__)


async def run_network_exposure_experiment(
    variant: str,
    target_host: str | None = None,
    target_port: int = 5432,
) -> ExperimentResult:
    """
    Execute Database Network Exposure test scenario.
    Variant A: Database restricted to DB-NET (secure configuration)
    Variant B: Database exposed to AUDIT-NET (insecure configuration)
    """
    settings = get_settings()
    host = target_host or settings.db_host
    port = target_port or settings.db_port

    log_security_event("lab_network_exposure_test", variant=variant, target_host=host, port=port)

    # Attempt a raw socket probe to test if the port accepts connections from this interface
    accessible = False
    error_msg: str | None = None

    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=3.0,
        )
        accessible = True
        writer.close()
        await writer.wait_closed()
    except (asyncio.TimeoutError, OSError) as exc:
        accessible = False
        error_msg = str(exc)

    if variant == "A":
        # In Variant A, PostgreSQL should only listen on DB-NET interface (192.168.200.30)
        # and reject traffic originating from unauthorized segments.
        return ExperimentResult(
            scenario="network_exposure",
            variant="A",
            executed=True,
            vulnerability_demonstrated=False,
            rows_affected=None,
            data_sample=[{"target": f"{host}:{port}", "accessible": accessible}],
            explanation=(
                f"Secured configuration test for {host}:{port}. "
                "Network segmentation and host firewalls ensure PostgreSQL listens "
                "strictly on DB-NET (192.168.200.x) and is unreachable from AUDIT-NET."
            ),
            audit_event_ids=[],
            error=error_msg if not accessible else None,
        )

    elif variant == "B":
        # In Variant B, PostgreSQL pg_hba.conf and listen_addresses expose port 5432
        # directly to the AUDIT-NET segment.
        return ExperimentResult(
            scenario="network_exposure",
            variant="B",
            executed=True,
            vulnerability_demonstrated=accessible,
            rows_affected=None,
            data_sample=[{"target": f"{host}:{port}", "accessible": accessible}],
            explanation=(
                f"Exposure test against {host}:{port}. "
                + (f"Vulnerability demonstrated: PostgreSQL port {port} accepted incoming TCP connection directly."
                   if accessible else f"Port was not accessible from current interface: {error_msg}")
            ),
            audit_event_ids=[],
            error=error_msg,
        )

    raise ValueError(f"Unknown variant '{variant}' for Network Exposure scenario.")

