"""
app/lab/scenarios/bola.py
========================
Scenario 3: Broken Authorization / BOLA / IDOR (CWE-284)
Research objective:
Determine whether one customer can access another customer's financial resources.
"""

from __future__ import annotations

from typing import Any, Dict, List
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger, log_security_event
from app.models.bank_accounts import BankAccount
from app.schemas.lab import ExperimentResult
from app.security.rls import with_rls_context

logger = get_logger(__name__)


async def run_bola_experiment(
    session: AsyncSession,
    variant: str,
    target_account_id: int = 2,
    authenticated_customer_id: int = 1,
) -> ExperimentResult:
    """
    Execute Broken Object-Level Authorization test scenario.
    Target account 2 belongs to Customer B. Authenticated customer is Customer A (ID 1).

    Variant A: Missing ownership check (IDOR/BOLA vulnerability)
    Variant B: Correct application-level authorization check
    Variant C: PostgreSQL Row-Level Security (database-level policy)
    """
    audit_ids: List[int] = []

    if variant == "A":
        # Missing check: directly selects bank_accounts by account_id only!
        log_security_event(
            "lab_bola_attempt",
            variant="A",
            target_account=target_account_id,
            requesting_customer=authenticated_customer_id,
        )
        stmt = select(BankAccount).where(BankAccount.account_id == target_account_id)
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()

        if account:
            # Did Customer 1 get Customer 2's account?
            is_cross_customer = account.customer_id != authenticated_customer_id
            sample = [{
                "account_id": account.account_id,
                "customer_id": account.customer_id,
                "account_type": account.account_type,
                "balance": str(account.balance),
                "currency": account.currency,
                "status": account.status,
            }]
            return ExperimentResult(
                scenario="bola",
                variant="A",
                executed=True,
                vulnerability_demonstrated=is_cross_customer,
                rows_affected=1,
                data_sample=sample,
                explanation=(
                    f"Variant A fetched account {target_account_id} without verifying ownership. "
                    + (f"BOLA demonstrated: Customer {authenticated_customer_id} successfully viewed account belonging to Customer {account.customer_id}."
                       if is_cross_customer else "Account belongs to the same customer.")
                ),
                audit_event_ids=audit_ids,
            )
        else:
            return ExperimentResult(
                scenario="bola",
                variant="A",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=0,
                data_sample=[],
                explanation=f"Account {target_account_id} not found in database.",
                audit_event_ids=audit_ids,
            )

    elif variant == "B":
        # Correct application-level server-side check
        log_security_event(
            "lab_bola_attempt",
            variant="B",
            target_account=target_account_id,
            requesting_customer=authenticated_customer_id,
        )
        stmt = select(BankAccount).where(
            BankAccount.account_id == target_account_id,
            BankAccount.customer_id == authenticated_customer_id,
        )
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()

        if account:
            sample = [{"account_id": account.account_id, "customer_id": account.customer_id}]
            return ExperimentResult(
                scenario="bola",
                variant="B",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=1,
                data_sample=sample,
                explanation="Account belongs to the authenticated customer; access permitted.",
                audit_event_ids=audit_ids,
            )
        else:
            return ExperimentResult(
                scenario="bola",
                variant="B",
                executed=True,
                vulnerability_demonstrated=False,
                rows_affected=0,
                data_sample=[],
                explanation=(
                    f"Defense succeeded: Application-level check filtered query by both account_id={target_account_id} "
                    f"AND customer_id={authenticated_customer_id}. Cross-customer access was denied (0 records returned)."
                ),
                audit_event_ids=audit_ids,
            )

    elif variant == "C":
        # PostgreSQL Row-Level Security (RLS) check
        log_security_event(
            "lab_bola_attempt",
            variant="C",
            target_account=target_account_id,
            requesting_customer=authenticated_customer_id,
        )
        try:
            # Set RLS session context for customer
            ctx = with_rls_context(session, customer_id=authenticated_customer_id)
            async with ctx:
                # Query without customer_id in WHERE clause — relying strictly on PostgreSQL RLS
                stmt = select(BankAccount).where(BankAccount.account_id == target_account_id)
                result = await session.execute(stmt)
                account = result.scalar_one_or_none()

            if account:
                is_cross = account.customer_id != authenticated_customer_id
                sample = [{"account_id": account.account_id, "customer_id": account.customer_id}]
                return ExperimentResult(
                    scenario="bola",
                    variant="C",
                    executed=True,
                    vulnerability_demonstrated=is_cross,
                    rows_affected=1,
                    data_sample=sample,
                    explanation=(
                        "Database RLS allowed access. "
                        + ("RLS policy not active or bypassed." if is_cross else "Account owned by customer.")
                    ),
                    audit_event_ids=audit_ids,
                )
            else:
                return ExperimentResult(
                    scenario="bola",
                    variant="C",
                    executed=True,
                    vulnerability_demonstrated=False,
                    rows_affected=0,
                    data_sample=[],
                    explanation=(
                        f"Defense succeeded: PostgreSQL Row-Level Security (RLS) policy filtered out "
                        f"account {target_account_id} at the database engine layer for customer {authenticated_customer_id}."
                    ),
                    audit_event_ids=audit_ids,
                )
        except SQLAlchemyError as exc:
            return ExperimentResult(
                scenario="bola",
                variant="C",
                executed=False,
                vulnerability_demonstrated=False,
                rows_affected=0,
                data_sample=[],
                explanation=f"Database error during RLS execution: {type(exc).__name__}",
                audit_event_ids=audit_ids,
                error=str(exc),
            )

    raise ValueError(f"Unknown variant '{variant}' for BOLA scenario.")

