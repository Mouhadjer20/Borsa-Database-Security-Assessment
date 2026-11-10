"""
app/api/transactions.py
=======================
Financial transactions endpoints.
Verifies account ownership before exposing transaction histories.
Includes export functionality with session metadata for auditing.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select, func, text

from app.database.session import get_secure_db
from app.middleware.auth import get_current_user
from app.models.transactions import Transaction
from app.repositories.accounts import get_accounts_for_customer
from app.schemas.transactions import TransactionList, TransactionOut
from app.services import transaction_service

router = APIRouter(tags=["transactions"])


@router.get("/api/transactions", response_model=TransactionList)
async def list_transactions(
    account_id: Optional[int] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_secure_db),
) -> TransactionList:
    """
    Retrieve transactions for an owned account, or across all accounts owned by the user.
    """
    customer_id = int(current_user["user_id"])

    if account_id is not None:
        # Fetch transactions for a specific account with ownership validation
        return await transaction_service.get_account_transactions(
            session=session,
            account_id=account_id,
            customer_id=customer_id,
            limit=limit,
            offset=offset,
        )

    # If no specific account_id is given, find all accounts owned by this customer
    accounts, _ = await get_accounts_for_customer(session, customer_id=customer_id, limit=100, offset=0)
    owned_ids = [a.account_id for a in accounts]

    if not owned_ids:
        return TransactionList(transactions=[], total=0, account_id=0)

    ownership_filter = or_(
        Transaction.source_account.in_(owned_ids),
        Transaction.destination_account.in_(owned_ids),
    )

    count_stmt = select(func.count()).select_from(Transaction).where(ownership_filter)
    total: int = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        select(Transaction)
        .where(ownership_filter)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    records = list(result.scalars().all())

    return TransactionList(
        transactions=[TransactionOut.model_validate(t) for t in records],
        total=total,
        account_id=owned_ids[0] if owned_ids else 0,
    )


@router.get("/api/accounts/{account_id}/transactions", response_model=TransactionList)
async def list_account_transactions(
    account_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_secure_db),
) -> TransactionList:
    """
    Retrieve transactions for a specific account owned by the authenticated customer.
    """
    customer_id = int(current_user["user_id"])
    return await transaction_service.get_account_transactions(
        session=session,
        account_id=account_id,
        customer_id=customer_id,
        limit=limit,
        offset=offset,
    )


@router.get("/api/transactions/export")
async def export_transactions(
    account_id: Optional[int] = Query(default=None, description="Filter by account ID"),
    format: str = Query(default="json", description="Export format: json or csv"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: AsyncSession = Depends(get_secure_db),
) -> Dict[str, Any]:
    """
    Export transactions for download or reporting.
    Supports JSON and CSV formats. Includes session metadata for audit trail purposes.

    Example: GET /api/transactions/export?format=csv&account_id=1
    """
    # Intentionally vulnerable: queries DB session metadata exposing internal DB identity.
    # CWE-250 — Execution with Unnecessary Privileges.
    # The response leaks the database role name, server PID, and version.
    # An attacker learns the DB user, which can be used for further privilege escalation.
    db_meta: Dict[str, Any] = {}
    try:
        meta_result = await session.execute(
            text(
                "SELECT current_user, session_user, "
                "pg_backend_pid() AS pid, "
                "version() AS db_version"
            )
        )
        row = meta_result.mappings().first()
        if row:
            db_meta = {
                "db_user": row["current_user"],
                "session_user": row["session_user"],
                "backend_pid": row["pid"],
                "db_version": row["db_version"],
            }
    except Exception:
        db_meta = {"info": "metadata unavailable"}

    return {
        "export_format": format,
        "account_filter": account_id,
        "requesting_user": current_user["username"],
        "session_metadata": db_meta,
        "transactions": [],
        "note": "Full export feature coming soon. Metadata included for audit trail.",
    }
