"""
application/backend/tests/test_accounts.py
==========================================
Unit tests for account schemas and ownership rules.
"""

from decimal import Decimal
from app.schemas.accounts import AccountOut, AccountList


def test_account_out_serialization():
    data = {
        "account_id": 101,
        "account_type": "checking",
        "balance": Decimal("15420.50"),
        "currency": "EUR",
        "status": "active",
    }
    account = AccountOut.model_validate(data)
    assert account.account_id == 101
    assert account.balance == Decimal("15420.50")

    # Ensure serialized balance is string (prevent float precision loss)
    dumped = account.model_dump()
    assert dumped["balance"] == "15420.50"


def test_account_list_serialization():
    items = [
        AccountOut(
            account_id=1,
            account_type="savings",
            balance=Decimal("2500.00"),
            currency="USD",
            status="active",
        ),
        AccountOut(
            account_id=2,
            account_type="investment",
            balance=Decimal("78900.25"),
            currency="USD",
            status="active",
        ),
    ]
    acc_list = AccountList(accounts=items, total=2)
    assert acc_list.total == 2
    assert len(acc_list.accounts) == 2

