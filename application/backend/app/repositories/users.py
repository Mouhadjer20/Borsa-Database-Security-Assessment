"""
app/repositories/users.py
==========================
Data-access layer for `app_users`.

Security rules:
  - All queries use parameterized statements — no string interpolation.
  - password_hash is loaded only for the duration of authentication;
    it is never returned to callers as a string in a response.
  - A timing-safe dummy verify is performed when no user is found to
    prevent user-enumeration via response-time differences.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.security import verify_password
from app.models.app_users import AppUser

logger = get_logger(__name__)


async def get_user_by_username(
    session: AsyncSession, username: str
) -> AppUser | None:
    """
    Retrieve an AppUser by username using a parameterized query.

    Returns None when no user exists (do NOT raise — let the service layer
    produce a uniform 401 for both "not found" and "wrong password").
    """
    stmt = select(AppUser).where(AppUser.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> AppUser | None:
    """
    Look up a user and verify the supplied password.

    Returns the AppUser on success, None on failure.

    Timing-safe: a dummy bcrypt verify is performed even when the user is not
    found so that response time does not reveal whether the username exists.
    """
    user = await get_user_by_username(session, username)

    if user is None:
        # Perform a dummy verify to equalise response time (anti-enumeration).
        # The hash below is a valid but un-matchable bcrypt digest.
        _DUMMY_HASH = "$2b$12$iW4ePjChLoXMhsO.TXrBUuWLvfLSSOSWqYvXkbScI0xJwUHBCKEaa"
        verify_password(password, _DUMMY_HASH)
        logger.info("user_not_found", username=username)
        return None

    if not verify_password(password, user.password_hash):
        logger.info("password_mismatch", username=username)
        return None

    return user
