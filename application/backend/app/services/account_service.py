"""
app/services/account_service.py
================================
Business logic for account retrieval.

Bridges the authorization layer (security/authorization.py) with the
repository layer (repositories/accounts.py).
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.bank_accounts import BankAccount
from app.repositories.accounts import get_account_by_id, get_accounts_for_customer
from app.schemas.accounts import AccountList, AccountOut

logger = get_logger(__name__)


async def get_user_accounts(
    session: AsyncSession,
    customer_id: int,
    limit: int = 50,
    offset: int = 0,
) -> AccountList:
    """
    Return all accounts for the authenticated customer.

    The customer_id comes from the verified JWT — it is not user-supplied.
    """
    accounts, total = await get_accounts_for_customer(
        session=session,
        customer_id=customer_id,
        limit=limit,
        offset=offset,
    )
    return AccountList(
        accounts=[AccountOut.model_validate(a) for a in accounts],
        total=total,
    )


async def get_account_detail(
    session: AsyncSession,
    account_id: int,
    customer_id: int,
) -> AccountOut:
    """
    Return a single account, ensuring it belongs to *customer_id*.

    Raises HTTP 404 when the account does not exist or the customer does
    not own it — intentionally indistinguishable to prevent account enumeration.
    """
    account: BankAccount | None = await get_account_by_id(
        session=session,
        account_id=account_id,
        customer_id=customer_id,
    )
    if account is None:
        # Return 404, not 403 — do not confirm that an account with this ID
        # exists but belongs to someone else (account enumeration risk).
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )
    return AccountOut.model_validate(account)
