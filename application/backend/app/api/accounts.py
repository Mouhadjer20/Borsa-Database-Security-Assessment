"""
app/api/accounts.py
===================
Bank account endpoints for authenticated customers.
Enforces strict server-side authorization and ownership checks.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_secure_db
from app.middleware.auth import get_current_user
from app.schemas.accounts import AccountList, AccountOut
from app.services import account_service

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=AccountList)
async def list_accounts(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_secure_db),
) -> AccountList:
    """
    Retrieve all accounts owned by the authenticated customer.
    The customer identity is extracted from the validated session token.
    """
    customer_id = int(current_user["user_id"])
    return await account_service.get_user_accounts(
        session=session,
        customer_id=customer_id,
        limit=limit,
        offset=offset,
    )


@router.get("/{account_id}", response_model=AccountOut)
async def get_account(
    account_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_secure_db),
) -> AccountOut:
    """
    Retrieve details for a specific bank account.
    Verifies that the account belongs to the authenticated customer.
    Returns 404 if the account does not exist or does not belong to the user.
    """
    customer_id = int(current_user["user_id"])
    return await account_service.get_account_detail(
        session=session,
        account_id=account_id,
        customer_id=customer_id,
    )

