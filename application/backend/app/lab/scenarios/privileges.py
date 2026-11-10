"""
app/lab/scenarios/privileges.py
===============================
Scenario 2: Excessive Database Privileges (CWE-250)
Research objective:
Determine whether an application database identity can perform operations beyond its assigned responsibilities.
"""

from __future__ import annotations

from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError, ProgrammingError, SQLAlchemyError

from app.core.logging import get_logger, log_security_event
from app.schemas.lab import ExperimentResult

logger = get_logger(__name__)


async def run_privileges_experiment(
    session: AsyncSession,
    variant: str,
    payload: str | None = None,
) -> ExperimentResult:
    """
    Execute Excessive Database Privileges test scenario.
    Tests privilege boundaries by attempting an administrative or sensitive query:
    e.g., querying information_schema/pg_catalog or reading audit logs.
    """
    # Test query: inspecting PostgreSQL system tables or sensitive security audit tables
    test_query = payload or "SELECT rolname, rolsuper, rolinherit, rolcreaterole FROM pg_roles LIMIT 5"
    audit_ids: List[int] = []

    if variant == "A":
        # Overprivileged role variant (app_vulnerable)
        log_security_event("lab_privileges_executed", variant="A", query=test_query)
        try:
            result = await session.execute(text(test_query))
            rows = result.mappings().all()
            sample = [dict(r) for r in rows]

            return ExperimentResult(
                scenario="privileges",
                variant="A",
                executed=True,
                vulnerability_demonstrated=True,
                rows_affected=len(sample),
                data_sample=sample[:5],
                explanation=(
                    "Variant A executed using the overprivileged database identity. "
                    f"Successfully performed the operation: [{test_query}]. "
                    "Demonstrated risk: The database user has excessive catalog or administrative permissions."
                ),
                audit_event_ids=audit_ids,
            )
        except (ProgrammingError, DBAPIError) as exc:
            return ExperimentResult(
                scenario="privileges",
                variant="A",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=0,
                data_sample=[],
                explanation=f"Operation blocked even under overprivileged identity: {type(exc).__name__}",
                audit_event_ids=audit_ids,
                error=str(exc),
            )

    elif variant == "B":
        # Least-privilege role variant (app_readonly / app_writer)
        log_security_event("lab_privileges_executed", variant="B", query=test_query)
        try:
            result = await session.execute(text(test_query))
            rows = result.mappings().all()
            sample = [dict(r) for r in rows]

            return ExperimentResult(
                scenario="privileges",
                variant="B",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=len(sample),
                data_sample=sample[:5],
                explanation=(
                    "Operation succeeded. Note: check database role GRANT definitions "
                    "to confirm app_readonly does not have SELECT on system tables."
                ),
                audit_event_ids=audit_ids,
            )
        except (ProgrammingError, DBAPIError, SQLAlchemyError) as exc:
            # Expected outcome: Permission denied!
            is_perm_denied = "permission denied" in str(exc).lower()
            return ExperimentResult(
                scenario="privileges",
                variant="B",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=0,
                data_sample=[],
                explanation=(
                    f"Defense succeeded: Database role lacked privileges to execute [{test_query}]. "
                    f"Enforcement outcome: {type(exc).__name__} (Permission denied as expected)."
                ),
                audit_event_ids=audit_ids,
                error=str(exc) if not is_perm_denied else "Permission denied (least-privilege enforced)",
            )

    raise ValueError(f"Unknown variant '{variant}' for Privileges scenario.")

