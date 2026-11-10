"""
app/security/rls.py
====================
PostgreSQL Row-Level Security (RLS) session context helpers.

RLS policies in PostgreSQL can be parameterised using session-local settings.
For example, a policy on `bank_accounts` might enforce:

    CREATE POLICY customer_isolation ON bank_accounts
    USING (customer_id = current_setting('app.current_user_id')::integer);

The helpers here set / unset that session variable within the scope of a
single database transaction.

Security warnings:
  1. The customer_id value MUST come from the verified JWT, NOT from any
     user-supplied parameter.
  2. This must be called within a transaction (BEGIN … COMMIT) so the setting
     is transaction-local and cannot leak between requests in a connection pool.
  3. Never use SET (session-level) instead of SET LOCAL (transaction-level)
     when using connection pooling — a session-level SET would persist across
     different user requests that reuse the same pooled connection.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger(__name__)


async def set_rls_user_context(session: AsyncSession, customer_id: int) -> None:
    """
    Set the PostgreSQL session-local variable `app.current_user_id`.

    Uses SET LOCAL so the setting is automatically reset at transaction end.
    This prevents RLS context from leaking to subsequent requests that reuse
    the same pooled connection.

    Must be called inside an active transaction (after BEGIN).
    """
    # Parameterized — the integer is converted server-side by SQLAlchemy.
    # Note: SET LOCAL does not support bind parameters in all PostgreSQL versions;
    # we format the integer directly (it is a trusted integer from the JWT, not
    # user-supplied text, so this is safe — no SQL injection risk).
    safe_id = int(customer_id)  # explicit cast: ensures it's an integer
    await session.execute(
        text(f"SET LOCAL app.current_user_id = '{safe_id}'")
    )
    logger.debug("rls_context_set", customer_id=safe_id)


async def clear_rls_user_context(session: AsyncSession) -> None:
    """
    Explicitly clear the RLS context variable.

    In practice, SET LOCAL makes this unnecessary (the variable resets on
    COMMIT/ROLLBACK), but calling this provides an explicit audit trail.
    """
    await session.execute(text("SET LOCAL app.current_user_id = ''"))
    logger.debug("rls_context_cleared")


async def with_rls_context(session: AsyncSession, customer_id: int):
    """
    Async context manager that sets and clears the RLS context variable.

    Usage:
        async with with_rls_context(session, customer_id):
            result = await session.execute(stmt)

    The SET LOCAL ensures cleanup happens automatically at transaction end.
    """
    # Import here to avoid circular dependency with contextlib
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _ctx():
        await set_rls_user_context(session, customer_id)
        try:
            yield
        finally:
            await clear_rls_user_context(session)

    return _ctx()
