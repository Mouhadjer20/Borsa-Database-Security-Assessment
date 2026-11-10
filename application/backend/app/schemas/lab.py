"""
app/schemas/lab.py
==================
Pydantic schemas for the Security Lab API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LabStatus(BaseModel):
    """
    Current lab configuration status returned by GET /api/lab/status.
    DB credentials and internal DSNs are NEVER included.
    """

    lab_enabled: bool
    app_security_mode: str
    # Only safe metadata — never expose credentials or internal host details
    # beyond what an authenticated researcher needs to understand the config.
    lab_db_connected: bool = False
    active_scenario: Optional[str] = None
    message: str = ""


class ExperimentRequest(BaseModel):
    """Request body for POST /api/lab/experiments/{scenario}."""

    variant: str = Field(
        ...,
        description="Experiment variant identifier, e.g. 'A' (vulnerable) or 'B' (secure).",
        pattern=r"^[A-C]$",
    )
    # Optional payload that specific scenarios may consume (e.g. user-supplied
    # input for the SQL injection scenario).  Validated per-scenario.
    payload: Optional[str] = Field(
        None,
        max_length=512,
        description="Optional scenario-specific payload (e.g. a username to inject).",
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional scenario parameters.",
    )


class ExperimentResult(BaseModel):
    """Result of a completed lab experiment."""

    scenario: str
    variant: str
    # Whether the experiment ran without an unexpected error
    executed: bool
    # Did the vulnerable behaviour manifest (e.g. injection succeeded)?
    vulnerability_demonstrated: Optional[bool] = None
    # Number of rows affected / returned by the lab query
    rows_affected: Optional[int] = None
    # Safe excerpt of data accessed — stripped of any PII beyond synthetic IDs
    data_sample: Optional[List[Dict[str, Any]]] = None
    # Human-readable explanation of what happened
    explanation: str = ""
    # Corresponding application log event IDs for correlation
    audit_event_ids: List[int] = []
    error: Optional[str] = None
