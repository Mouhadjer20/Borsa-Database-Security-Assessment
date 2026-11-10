"""
app/security/authorization.py
==============================
Server-side ownership and authorization checks.

NEVER trust account IDs or customer IDs supplied directly by the client.
Always derive the customer_id from the validated JWT and verify ownership
against the database.

This module provides the canonical ownership-check function used by all
secure-mode endpoints.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger, log_security_event
from app.repositories.accounts import get_account_by_id

logger = get_logger(__name__)


async def check_account_ownership(
    user_id: int,
    account_id: int,
    session: AsyncSession,
    customer_id: int,
) -> bool:
    """
    Verify that *account_id* belongs to the customer associated with *user_id*.

    Parameters
    ----------
    user_id:
        Authenticated user's ID from the verified JWT (not from the request body).
    account_id:
        The account the user is attempting to access.
    session:
        Active database session.
    customer_id:
        The customer_id linked to the authenticated user.  Must be derived from
        the JWT or a trusted DB lookup — never from user-supplied input.

    Returns
    -------
    True if the account belongs to the customer; False otherwise.

    Security note:
        This function does NOT raise on failure — it returns a boolean so the
        caller can decide the appropriate HTTP status (403 vs 404 depending on
        whether we want to reveal existence of the account).
    """
    account = await get_account_by_id(
        session=session,
        account_id=account_id,
        customer_id=customer_id,
    )

    if account is None:
        log_security_event(
            "authorization_failure",
            actor=str(user_id),
            resource=f"account:{account_id}",
            outcome="blocked",
        )
        return False

    return True


async def require_account_ownership(
    user_id: int,
    account_id: int,
    session: AsyncSession,
    customer_id: int,
) -> None:
    """
    Like check_account_ownership but raises HTTP 404 on failure.

    HTTP 404 is used (rather than 403) to avoid confirming that the account
    exists when the requesting user does not own it (prevents enumeration).
    """
    owned = await check_account_ownership(
        user_id=user_id,
        account_id=account_id,
        session=session,
        customer_id=customer_id,
    )
    if not owned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )
