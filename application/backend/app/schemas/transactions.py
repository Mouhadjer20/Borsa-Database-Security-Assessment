"""
app/schemas/transactions.py
===========================
Pydantic schemas for transaction endpoints.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, field_serializer


class TransactionOut(BaseModel):
    """Public representation of a single financial transaction."""

    transaction_id: int
    source_account: int | None
    destination_account: int | None
    amount: Decimal
    timestamp: datetime
    status: str

    model_config = {"from_attributes": True}

    @field_serializer("amount")
    def _serialize_amount(self, v: Decimal) -> str:
        return str(v)


class TransactionList(BaseModel):
    """Paginated transaction list for a specific account."""

    transactions: List[TransactionOut]
    total: int
    account_id: int
