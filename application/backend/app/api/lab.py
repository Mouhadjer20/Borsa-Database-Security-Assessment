"""
app/api/lab.py
==============
Security Laboratory API endpoints.
Provides experiment status and execution endpoints for the 4 research scenarios.
All endpoints require explicit laboratory enablement (LAB_ENABLED=true).
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.config import get_settings
from app.core.logging import get_logger, log_security_event
from app.database.engine import get_lab_engine, get_secure_engine
from app.database.session import get_lab_db, get_secure_db
from app.lab.config import require_lab_enabled
from app.lab.scenarios.sqli import run_sqli_experiment
from app.lab.scenarios.privileges import run_privileges_experiment
from app.lab.scenarios.bola import run_bola_experiment
from app.lab.scenarios.network_exposure import run_network_exposure_experiment
from app.schemas.lab import ExperimentRequest, ExperimentResult, LabStatus

logger = get_logger(__name__)

router = APIRouter(prefix="/api/lab", tags=["security-lab"])


@router.get("/status", response_model=LabStatus)
async def get_lab_status() -> LabStatus:
    """
    Return current laboratory configuration status.
    Credentials and secret keys are NEVER exposed.
    """
    settings = get_settings()
    lab_connected = False

    if settings.lab_enabled:
        try:
            lab_engine = get_lab_engine()
            async with lab_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                lab_connected = True
        except Exception:
            lab_connected = False

    return LabStatus(
        lab_enabled=settings.lab_enabled,
        app_security_mode=settings.app_security_mode,
        lab_db_connected=lab_connected,
        active_scenario=None,
        message=(
            "Laboratory mode is ACTIVE for authorized security research."
            if settings.lab_enabled
            else "Security Lab is DISABLED. Running in strict secure mode."
        ),
    )


async def _execute_scenario(
    scenario: str,
    request: ExperimentRequest,
    lab_session: AsyncSession,
    secure_session: AsyncSession,
) -> ExperimentResult:
    """
    Dispatch experiment request to the appropriate scenario handler.
    """
    norm_scenario = scenario.lower().replace("-", "_")

    # For Variant B (secure defense verification), use the secure session
    # For Variant A (vulnerable research demonstration), use the lab session
    target_session = secure_session if request.variant == "B" else lab_session

    log_security_event(
        "lab_experiment_invoked",
        scenario=norm_scenario,
        variant=request.variant,
    )

    if norm_scenario in ("sqli", "sql_injection"):
        return await run_sqli_experiment(
            session=target_session,
            variant=request.variant,
            payload=request.payload,
        )

    elif norm_scenario in ("privileges", "excessive_privileges"):
        return await run_privileges_experiment(
            session=target_session,
            variant=request.variant,
            payload=request.payload,
        )

    elif norm_scenario in ("bola", "idor", "broken_authorization"):
        target_id = 2
        customer_id = 1
        if request.parameters:
            target_id = request.parameters.get("target_account_id", 2)
            customer_id = request.parameters.get("authenticated_customer_id", 1)

        return await run_bola_experiment(
            session=target_session,
            variant=request.variant,
            target_account_id=target_id,
            authenticated_customer_id=customer_id,
        )

    elif norm_scenario in ("network", "network_exposure"):
        host = request.parameters.get("target_host") if request.parameters else None
        port = request.parameters.get("target_port", 5432) if request.parameters else 5432
        return await run_network_exposure_experiment(
            variant=request.variant,
            target_host=host,
            target_port=port,
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Unknown scenario '{scenario}'. Valid options: sqli, privileges, bola, network.",
    )


@router.post("/experiments/{scenario}", response_model=ExperimentResult)
async def run_experiment_endpoint(
    scenario: str,
    request: ExperimentRequest,
    _: None = Depends(require_lab_enabled),
    lab_session: AsyncSession = Depends(get_lab_db),
    secure_session: AsyncSession = Depends(get_secure_db),
) -> ExperimentResult:
    """Execute an experiment by scenario name."""
    return await _execute_scenario(scenario, request, lab_session, secure_session)


@router.post("/experiments/{scenario}/run", response_model=ExperimentResult)
async def run_experiment_run_endpoint(
    scenario: str,
    request: ExperimentRequest,
    _: None = Depends(require_lab_enabled),
    lab_session: AsyncSession = Depends(get_lab_db),
    secure_session: AsyncSession = Depends(get_secure_db),
) -> ExperimentResult:
    """Frontend-compatible alias for executing an experiment."""
    return await _execute_scenario(scenario, request, lab_session, secure_session)

