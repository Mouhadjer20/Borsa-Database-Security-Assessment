"""
app/core/security.py
====================
Password hashing, JWT token creation/verification, and session utilities.

Security decisions documented inline:
  - bcrypt with a minimum cost factor of 12.
  - HS256 JWT signed with the SESSION_SECRET.
  - Tokens carry only the user_id (sub) and role — no PII.
  - Tokens are short-lived (default 30 min); refresh is not in scope here.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.logging import get_logger, log_security_event

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# Password hashing
# ------------------------------------------------------------------ #

# bcrypt cost factor 12 is the recommended minimum for 2024+.
# auto_schemes deprecated schemes are intentionally empty — only bcrypt.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash of *plaintext*. Never log the input."""
    return _pwd_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    """
    Constant-time comparison of *plaintext* against the stored *hashed* value.

    Returns False (not raises) on any verification error so callers receive a
    uniform boolean — no timing oracle, no internal detail leakage.
    """
    try:
        return _pwd_context.verify(plaintext, hashed)
    except Exception:
        # An exception here means the hash is malformed — treat as failure.
        logger.warning("password_verify_error", detail="malformed hash encountered")
        return False


# ------------------------------------------------------------------ #
# JWT
# ------------------------------------------------------------------ #

_ALGORITHM = "HS256"


def _secret() -> str:
    """Return the signing secret from settings."""
    return get_settings().session_secret


def create_access_token(
    user_id: int,
    username: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    The payload contains only the minimum necessary claims:
      sub   — user_id (string, as per JWT spec)
      uname — username (for display, not for auth lookups)
      role  — user role for coarse route-level guards
      exp   — expiry timestamp

    Sensitive data (passwords, full account records) is NEVER embedded in tokens.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "uname": username,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _secret(), algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Raises
    ------
    JWTError
        When the token is invalid, expired, or the signature does not match.
        Callers should catch JWTError and return HTTP 401.
    """
    return jwt.decode(token, _secret(), algorithms=[_ALGORITHM])


def extract_user_from_token(token: str) -> dict[str, Any] | None:
    """
    Convenience wrapper: returns a dict with user_id, username, role or None.

    Returns None (rather than raising) so middleware can produce a clean 401.
    """
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        return {
            "user_id": int(user_id_str),
            "username": payload.get("uname", ""),
            "role": payload.get("role", "customer"),
        }
    except (JWTError, ValueError, TypeError):
        log_security_event(
            "token_decode_failure",
            outcome="failure",
            reason="invalid_or_expired_token",
        )
        return None
