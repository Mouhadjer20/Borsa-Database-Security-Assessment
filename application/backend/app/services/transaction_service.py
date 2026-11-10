"""
app/services/transaction_service.py
=====================================
Business logic for transaction retrieval.

The service verifies account ownership before fetching transactions to ensure
no cross-customer data leakage.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.repositories.accounts import get_account_by_id
from app.repositories.transactions import get_transactions_for_account
from app.schemas.transactions import TransactionList, TransactionOut

logger = get_logger(__name__)


async def get_account_transactions(
    session: AsyncSession,
    account_id: int,
    customer_id: int,
    limit: int = 50,
    offset: int = 0,
) -> TransactionList:
    """
    Return transactions for *account_id*, enforcing ownership by *customer_id*.

    Steps:
    1. Verify that account_id belongs to customer_id (authorization gate).
    2. Fetch matching transactions.

    Raises HTTP 404 when the account doesn't exist or isn't owned by the caller.
    """
    # Step 1 — ownership gate (also validates account existence)
    account = await get_account_by_id(
        session=session,
        account_id=account_id,
        customer_id=customer_id,
    )
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )

    # Step 2 — fetch transactions
    transactions, total = await get_transactions_for_account(
        session=session,
        account_id=account_id,
        limit=limit,
        offset=offset,
    )

    return TransactionList(
        transactions=[TransactionOut.model_validate(t) for t in transactions],
        total=total,
        account_id=account_id,
    )
