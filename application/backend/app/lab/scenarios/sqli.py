"""
app/lab/scenarios/sqli.py
=========================
Scenario 1: SQL Injection (CWE-89)
Research objective:
Determine whether unsafe SQL query construction allows manipulation of database operations.
"""

from __future__ import annotations

from typing import Any, Dict, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger, log_security_event
from app.schemas.lab import ExperimentResult

logger = get_logger(__name__)


async def run_sqli_experiment(
    session: AsyncSession,
    variant: str,
    payload: str | None = None,
) -> ExperimentResult:
    """
    Execute SQL Injection test scenario.
    Variant A: Unsafe SQL string construction (vulnerable)
    Variant B: Parameterized SQL query (secure)
    """
    input_val = payload if payload is not None else "' OR '1'='1"
    audit_ids: List[int] = []

    if variant == "A":
        # Unsafe string formatting — intentionally vulnerable for lab demonstration
        raw_query = f"SELECT user_id, username, role FROM app_users WHERE username = '{input_val}'"
        log_security_event("lab_sqli_executed", variant="A", raw_query=raw_query)

        try:
            result = await session.execute(text(raw_query))
            rows = result.mappings().all()
            sample = [
                {"user_id": r["user_id"], "username": r["username"], "role": r["role"]}
                for r in rows
            ]
            # If multiple users or unauthorized records returned, injection succeeded
            vulnerable = len(sample) > 1 or any(s["username"] != input_val for s in sample)

            return ExperimentResult(
                scenario="sqli",
                variant="A",
                executed=True,
                vulnerability_demonstrated=vulnerable,
                rows_affected=len(sample),
                data_sample=sample[:10],
                explanation=(
                    f"Variant A executed an unparameterized string concatenation query: [{raw_query}]. "
                    f"Returned {len(sample)} record(s). "
                    + ("SQL Injection succeeded: query logic was manipulated to bypass authentication or extract multiple records."
                       if vulnerable else "Query executed without returning additional rows.")
                ),
                audit_event_ids=audit_ids,
            )
        except SQLAlchemyError as exc:
            logger.warning("lab_sqli_syntax_error", error=str(exc))
            return ExperimentResult(
                scenario="sqli",
                variant="A",
                executed=True,
                vulnerability_demonstrated=True,  # Syntax error provoked by injection syntax
                rows_affected=0,
                data_sample=[],
                explanation=f"SQL query syntax error triggered by injection payload: {type(exc).__name__}",
                audit_event_ids=audit_ids,
                error=str(exc),
            )

    elif variant == "B":
        # Parameterized query — secure implementation
        param_query = "SELECT user_id, username, role FROM app_users WHERE username = :username"
        log_security_event("lab_sqli_executed", variant="B", query="parameterized")

        try:
            result = await session.execute(text(param_query), {"username": input_val})
            rows = result.mappings().all()
            sample = [
                {"user_id": r["user_id"], "username": r["username"], "role": r["role"]}
                for r in rows
            ]
            return ExperimentResult(
                scenario="sqli",
                variant="B",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=len(sample),
                data_sample=sample,
                explanation=(
                    f"Variant B executed a safe parameterized query with bind parameter :username. "
                    f"The injection payload was treated strictly as a literal string. Returned {len(sample)} records. "
                    "Defense succeeded: SQL semantics remained unmanipulated."
                ),
                audit_event_ids=audit_ids,
            )
        except SQLAlchemyError as exc:
            return ExperimentResult(
                scenario="sqli",
                variant="B",
                executed=False,
                vulnerability_demonstrated=False,
                rows_affected=0,
                data_sample=[],
                explanation="Database error executing parameterized query.",
                audit_event_ids=audit_ids,
                error=str(exc),
            )

    raise ValueError(f"Unknown variant '{variant}' for SQLi scenario.")

