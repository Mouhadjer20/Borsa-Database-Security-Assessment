"""
app/repositories/accounts.py
=============================
Data-access layer for `bank_accounts`.

Security rules:
  - Every query filters by BOTH account_id AND customer_id.
  - Filtering only on account_id would create a BOLA (Broken Object-Level
    Authorization) vulnerability — a user could access any account by ID.
  - All queries are parameterized.
"""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.bank_accounts import BankAccount

logger = get_logger(__name__)


async def get_accounts_for_customer(
    session: AsyncSession,
    customer_id: int,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[BankAccount], int]:
    """
    Return all accounts belonging to *customer_id*.

    The WHERE customer_id = :customer_id clause is essential — without it any
    authenticated user could enumerate all accounts (BOLA).

    Returns (accounts, total_count).
    """
    # Count query
    count_stmt = (
        select(func.count())
        .select_from(BankAccount)
        .where(BankAccount.customer_id == customer_id)
    )
    total: int = (await session.execute(count_stmt)).scalar_one()

    # Data query
    stmt = (
        select(BankAccount)
        .where(BankAccount.customer_id == customer_id)
        .order_by(BankAccount.account_id)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    accounts = list(result.scalars().all())

    return accounts, total


async def get_account_by_id(
    session: AsyncSession,
    account_id: int,
    customer_id: int,
) -> BankAccount | None:
    """
    Retrieve a specific account IFF it belongs to *customer_id*.

    SECURITY: Both account_id AND customer_id are required predicates.
    Omitting the customer_id check would allow any authenticated user to
    read any account by guessing its numeric ID (BOLA/IDOR).
    """
    stmt = (
        select(BankAccount)
        .where(
            BankAccount.account_id == account_id,
            BankAccount.customer_id == customer_id,
        )
    )
    result = await session.execute(stmt)
    account = result.scalar_one_or_none()

    if account is None:
        logger.warning(
            "account_not_found_or_unauthorized",
            account_id=account_id,
            customer_id=customer_id,
        )

    return account
