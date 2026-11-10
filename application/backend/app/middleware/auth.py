"""
app/middleware/auth.py
======================
JWT authentication dependency for FastAPI route protection.

Reads the JWT from the HTTP-only cookie set at login.
Provides two dependency flavours:
  - get_current_user  — returns user dict or raises HTTP 401.
  - get_current_user_optional — returns user dict or None (for public routes).

Security notes:
  - The token is read from the cookie, not the Authorization header.
    This prevents JavaScript from accessing the token (XSS mitigation).
  - Token validation failure always returns 401 with a generic message —
    no internal detail is exposed to the caller.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import Cookie, Depends, HTTPException, status

from app.core.logging import get_logger, log_security_event
from app.core.security import extract_user_from_token

logger = get_logger(__name__)

# Must match the name used in auth_service.py
_AUTH_COOKIE_NAME = "borsa_access_token"

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required.",
    headers={"WWW-Authenticate": "Bearer"},
)


def _read_cookie(borsa_access_token: Optional[str] = Cookie(default=None)) -> Optional[str]:
    """Extract the raw JWT value from the cookie jar."""
    return borsa_access_token


async def get_current_user(
    token: Optional[str] = Depends(_read_cookie),
) -> Dict[str, Any]:
    """
    FastAPI dependency: return the authenticated user payload.

    Raises HTTP 401 when:
      - The cookie is absent.
      - The token is expired.
      - The token signature is invalid.
    """
    if token is None:
        log_security_event("missing_auth_token", outcome="failure")
        raise _CREDENTIALS_EXCEPTION

    user = extract_user_from_token(token)
    if user is None:
        log_security_event("invalid_auth_token", outcome="failure")
        raise _CREDENTIALS_EXCEPTION

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(_read_cookie),
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency: return the user payload or None for unauthenticated requests.
    Use for endpoints that behave differently for authenticated vs anonymous users.
    """
    if token is None:
        return None
    return extract_user_from_token(token)


def require_role(*allowed_roles: str):
    """
    Dependency factory that enforces role-based access control.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])

    Raises HTTP 403 when the authenticated user's role is not in allowed_roles.
    """
    async def _check(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("role") not in allowed_roles:
            log_security_event(
                "authorization_failure",
                actor=user.get("username"),
                outcome="blocked",
                required_roles=list(allowed_roles),
                user_role=user.get("role"),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return user

    return _check
