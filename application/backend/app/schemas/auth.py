"""
app/schemas/auth.py
===================
Pydantic schemas for authentication endpoints.

Security note: password_hash is NEVER included in any response schema.
Tokens are returned only once (at login) and stored in an HTTP-only cookie;
the client JS cannot read them.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request body for POST /api/auth/login."""

    username: str = Field(..., min_length=1, max_length=150)
    # min_length=1 prevents empty-string bypasses; real validation is in the service.
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    """
    Response body for a successful login.

    The actual JWT is delivered via Set-Cookie (HTTP-only) so it is not
    accessible from JavaScript.  This body carries only non-sensitive metadata
    for the frontend to store in React state.
    """

    token_type: str = "bearer"
    # Expose enough for the UI to personalise the experience without
    # embedding sensitive session data in localStorage.
    user_id: int
    username: str
    role: str


class UserInfo(BaseModel):
    """
    Response body for GET /api/auth/me.

    Returns the authenticated user's public identity.  No financial data,
    no password hash, no raw token.
    """

    user_id: int
    username: str
    role: str


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully."
