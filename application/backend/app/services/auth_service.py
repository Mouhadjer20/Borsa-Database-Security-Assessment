"""
app/services/auth_service.py
=============================
Authentication business logic.

Responsibilities:
  - Coordinate user lookup + password verification.
  - Create JWT access tokens.
  - Record login/logout events in the audit log.
  - Set / clear the HTTP-only JWT cookie.

Security notes:
  - Tokens are delivered via Set-Cookie (HttpOnly, Secure, SameSite=Lax).
  - The raw token is never logged or included in response bodies beyond the
    initial TokenResponse (which the UI uses to populate React state).
  - Logout clears the cookie server-side — no client-side token deletion
    is required (though the frontend should clear its React state too).
"""

from __future__ import annotations

from fastapi import Response

from app.core.config import get_settings
from app.core.logging import get_logger, log_security_event
from app.core.security import create_access_token
from app.models.app_users import AppUser
from app.repositories.audit import log_event
from app.repositories.users import authenticate_user
from app.schemas.auth import TokenResponse
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

# Cookie name used for the JWT.  HttpOnly prevents JS from reading it.
AUTH_COOKIE_NAME = "borsa_access_token"


async def login(
    session: AsyncSession,
    username: str,
    password: str,
    response: Response,
) -> TokenResponse | None:
    """
    Authenticate a user and issue a JWT access token via HTTP-only cookie.

    Returns TokenResponse on success, None on authentication failure.
    The caller (API route) is responsible for raising HTTP 401 on None.
    """
    user: AppUser | None = await authenticate_user(session, username, password)

    if user is None:
        log_security_event("login_failure", actor=username, outcome="failure")
        await log_event(session, action="login_failure", actor=username, resource="/api/auth/login")
        await session.commit()
        return None

    token = create_access_token(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
    )

    settings = get_settings()
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        httponly=settings.session_cookie_httponly,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )

    log_security_event("login_success", actor=username, outcome="success")
    await log_event(session, action="login_success", actor=username, resource="/api/auth/login")
    await session.commit()

    logger.info("user_logged_in", user_id=user.user_id, username=username, role=user.role)

    return TokenResponse(user_id=user.user_id, username=user.username, role=user.role)


def logout(response: Response) -> None:
    """
    Invalidate the session by clearing the JWT cookie.

    Server-side: the cookie is deleted by setting max_age=0.
    Note: stateless JWTs cannot be truly revoked without a token blacklist or
    short expiry. For this application the short expiry (30 min default) plus
    cookie deletion provides adequate protection for the educational context.
    """
    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
    log_security_event("logout", outcome="success")
    logger.info("user_logged_out")
