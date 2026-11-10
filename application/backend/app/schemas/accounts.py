"""
app/schemas/accounts.py
=======================
Pydantic schemas for bank account endpoints.

Balance is serialised as a string to preserve decimal precision across JSON
serialisation (avoid IEEE-754 floating-point rounding on the client side).
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from pydantic import BaseModel, field_serializer


class AccountOut(BaseModel):
    """Public representation of a single bank account."""

    account_id: int
    account_type: str
    # Returned as string to preserve exact decimal; frontend should parse with
    # a decimal library, never as a JS float.
    balance: Decimal
    currency: str
    status: str

    model_config = {"from_attributes": True}

    @field_serializer("balance")
    def _serialize_balance(self, v: Decimal) -> str:
        return str(v)


class AccountList(BaseModel):
    """Paginated list of accounts belonging to the authenticated customer."""

    accounts: List[AccountOut]
    total: int
