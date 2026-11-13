"""
app/repositories/audit.py
==========================
Data-access layer for `security_audit`.

Records security-significant events into the database audit table.
This complements the application-level structlog entries and provides
a database-visible audit trail that can be queried using the `auditor` role.

Security note: never log passwords, tokens, or complete financial records.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.security_audit import SecurityAudit

logger = get_logger(__name__)


async def log_event(
    session: AsyncSession,
    action: str,
    actor: str | None = None,
    resource: str | None = None,
) -> SecurityAudit | None:
    """
    Insert a row into `security_audit`.

    Parameters
    ----------
    session:
        An active AsyncSession.  The caller is responsible for committing.
    action:
        Short machine-readable event name, e.g. "login_success", "account_read".
    actor:
        Username or user_id of the person who triggered the event.
    resource:
        The resource being acted upon (endpoint path, account_id, table name).

    Returns the created SecurityAudit instance, or None if the insert failed
    (non-critical — audit failures must NOT block the main request).
    """
    safe_actor = actor or "anonymous"
    safe_resource = resource or "unknown"
    try:
        async with session.begin_nested():
            event = SecurityAudit(
                actor=safe_actor,
                action=action,
                resource=safe_resource,
                timestamp=datetime.now(timezone.utc),
            )
            session.add(event)
            await session.flush()  # get the generated event_id without a full commit
            return event
    except Exception as exc:  # noqa: BLE001
        # Audit failures are non-fatal. Savepoint rollback ensures the outer
        # session transaction is NOT poisoned, preventing PendingRollbackError.
        logger.error(
            "audit_insert_failed",
            action=action,
            actor=safe_actor,
            error_type=type(exc).__name__,
        )
        return None
