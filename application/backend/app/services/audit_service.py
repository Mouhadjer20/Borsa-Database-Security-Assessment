"""
app/services/audit_service.py
==============================
Application-level security event recording.

Writes to both:
  1. The application structured log (structlog).
  2. The `security_audit` database table (via the audit repository).

Non-critical: failures in audit recording are logged but do NOT block the
originating request.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger, log_security_event
from app.repositories.audit import log_event

logger = get_logger(__name__)


async def record_security_event(
    session: AsyncSession,
    action: str,
    actor: str | None = None,
    resource: str | None = None,
    outcome: str = "unknown",
    commit: bool = False,
) -> None:
    """
    Record a security event to both the structured log and the audit table.

    Parameters
    ----------
    session:
        Active AsyncSession.
    action:
        Machine-readable event name (e.g. "account_read", "login_failure").
    actor:
        Username or user_id (string form).
    resource:
        Target resource identifier.
    outcome:
        "success" | "failure" | "blocked" | "unknown"
    commit:
        When True, commits the session after the insert.  Set to False when
        the caller manages its own transaction boundary.
    """
    # 1. Structured application log
    log_security_event(event=action, actor=actor, resource=resource, outcome=outcome)

    # 2. Database audit row
    await log_event(session=session, action=action, actor=actor, resource=resource)

    if commit:
        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.error("audit_commit_failed", error_type=type(exc).__name__)
