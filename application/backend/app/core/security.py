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

import bcrypt
# Passlib compatibility shim for bcrypt >= 4.0.0
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")})()

import passlib.handlers.bcrypt as _pb
_orig_calc_checksum = getattr(_pb._BcryptBackend, "_calc_checksum", None)
def _patched_calc_checksum(self, secret):
    secret, ident = self._prepare_digest_args(secret)
    config = self._get_config(ident)
    if isinstance(config, str):
        config = config.encode("ascii")
    # bcrypt >= 4.1.0 raises if secret > 72 bytes; truncate safely to 72 bytes
    h = bcrypt.hashpw(secret[:72], config)
    return h[-31:].decode("ascii")
_pb._BcryptBackend._calc_checksum = _patched_calc_checksum

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
    expires_minutes: int | None = None,
) -> str:
    """
    Create a signed JWT access token.

    The payload contains only the minimum necessary claims:
      sub   — username / user identifier
      user_id — numeric identifier
      uname — username (for display)
      role  — user role for coarse route-level guards
      exp   — expiry timestamp

    Sensitive data (passwords, full account records) is NEVER embedded in tokens.
    """
    settings = get_settings()
    if expires_minutes is not None:
        delta = timedelta(minutes=expires_minutes)
    elif expires_delta is not None:
        delta = expires_delta
    else:
        delta = timedelta(minutes=settings.access_token_expire_minutes)

    expire = datetime.now(timezone.utc) + delta
    payload: dict[str, Any] = {
        "sub": username,
        "user_id": user_id,
        "uname": username,
        "username": username,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _secret(), algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decode and verify a JWT token.

    Returns the payload dictionary if valid, or None if invalid/expired.
    """
    try:
        return jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
    except JWTError:
        return None


def extract_user_from_token(token: str) -> dict[str, Any] | None:
    """
    Convenience wrapper: returns a dict with user_id, username, role or None.

    Returns None (rather than raising) so middleware can produce a clean 401.
    """
    try:
        payload = decode_access_token(token)
        if not payload:
            log_security_event(
                "token_decode_failure",
                outcome="failure",
                reason="invalid_or_expired_token",
            )
            return None

        user_id = payload.get("user_id")
        if user_id is None:
            sub = payload.get("sub")
            if sub is not None and str(sub).isdigit():
                user_id = int(sub)

        username = payload.get("username") or payload.get("uname") or payload.get("sub", "")
        return {
            "user_id": user_id,
            "username": username,
            "role": payload.get("role", "customer"),
        }
    except (JWTError, ValueError, TypeError):
        log_security_event(
            "token_decode_failure",
            outcome="failure",
            reason="invalid_or_expired_token",
        )
        return None
