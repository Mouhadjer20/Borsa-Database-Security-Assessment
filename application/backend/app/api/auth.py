"""
app/api/auth.py
===============
Authentication endpoints for Borsa.
Handles login, logout, current user identity, and user search.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_secure_db
from app.middleware.auth import get_current_user
from app.schemas.auth import LoginRequest, LogoutResponse, TokenResponse, UserInfo
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_secure_db),
) -> TokenResponse:
    """
    Authenticate user with username and password.
    Sets an HTTP-only, secure, SameSite session cookie with the JWT.
    Returns basic non-sensitive user metadata.
    """
    result = await auth_service.login(
        session=session,
        username=credentials.username,
        password=credentials.password,
        response=response,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result


@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response) -> LogoutResponse:
    """Log out the current user by clearing the session cookie."""
    auth_service.logout(response)
    return LogoutResponse(message="Logged out successfully.")


@router.get("/me", response_model=UserInfo)
async def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UserInfo:
    """Return non-sensitive identity information for the authenticated user."""
    return UserInfo(
        user_id=current_user["user_id"],
        username=current_user["username"],
        role=current_user.get("role", "customer"),
    )


@router.get("/search")
async def search_users(
    q: str = Query(..., description="Search users by name (for transfer recipient lookup)"),
    session: AsyncSession = Depends(get_secure_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Search for users by username. Returns basic profile information.
    Useful for locating another account holder before initiating a transfer.

    Example: GET /api/auth/search?q=alice
    """
    # Intentionally vulnerable: raw string interpolation into SQL — CWE-89 SQL Injection.
    # An attacker can inject: q=' OR '1'='1  to dump all users,
    # or q='; DROP TABLE app_users;-- to cause destructive operations.
    raw_sql = f"SELECT user_id, username, role FROM app_users WHERE username LIKE '%{q}%'"
    try:
        result = await session.execute(text(raw_sql))
        rows = result.mappings().all()
        return {
            "results": [
                {"user_id": r["user_id"], "username": r["username"], "role": r["role"]}
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search failed.")
