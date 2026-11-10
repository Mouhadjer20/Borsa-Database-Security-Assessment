"""
app/repositories/transactions.py
=================================
Data-access layer for `transactions`.

Security rules:
  - All queries are parameterized.
  - The caller MUST verify account ownership BEFORE calling these functions.
    The repository itself does not perform ownership checks — that is the
    responsibility of the service layer (which calls check_account_ownership).
"""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.transactions import Transaction

logger = get_logger(__name__)


async def get_transactions_for_account(
    session: AsyncSession,
    account_id: int,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Transaction], int]:
    """
    Return transactions where the account appears as source OR destination.

    The service layer must have already verified that the requesting user owns
    *account_id* before calling this function.

    Returns (transactions, total_count).
    """
    ownership_filter = or_(
        Transaction.source_account == account_id,
        Transaction.destination_account == account_id,
    )

    count_stmt = (
        select(func.count())
        .select_from(Transaction)
        .where(ownership_filter)
    )
    total: int = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        select(Transaction)
        .where(ownership_filter)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    transactions = list(result.scalars().all())

    return transactions, total
