"""
app/api/accounts.py
===================
Bank account endpoints for authenticated customers.
Provides owned account listing, detail retrieval, and account reference lookup.
"""

from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_secure_db
from app.middleware.auth import get_current_user
from app.models.bank_accounts import BankAccount
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


@router.get("/lookup/{account_ref}")
async def lookup_account_by_ref(
    account_ref: int,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_secure_db),
) -> Dict[str, Any]:
    """
    Look up an account by its reference number.
    Used when verifying a transfer recipient's account before initiating a payment.

    Example: GET /api/accounts/lookup/42

    Returns basic account metadata including balance and status.
    """
    # Intentionally vulnerable: no ownership check — CWE-284 Broken Object-Level Authorization (BOLA/IDOR).
    # Any authenticated user can access ANY account by guessing its numeric ID.
    # The correct fix would be to add: .where(BankAccount.customer_id == current_user["user_id"])
    stmt = select(BankAccount).where(BankAccount.account_id == account_ref)
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()

    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

    return {
        "account_id": account.account_id,
        "account_type": account.account_type,
        "balance": str(account.balance),
        "currency": account.currency,
        "status": account.status,
        "customer_id": account.customer_id,
    }


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
