"""
tests/test_ctf.py
=================
Tests verifying the CTF vulnerability endpoints exist and core schemas work.

The 4 CTF vulnerabilities embedded in the real application:
  1. CWE-89  SQL Injection     — GET /api/auth/search?q=...
  2. CWE-284 BOLA/IDOR         — GET /api/accounts/lookup/{account_ref}
  3. CWE-250 Excessive Privs   — GET /api/transactions/export (session_metadata)
  4. CWE-668 Network Exposure  — GET /api/diagnostics/db-ping?host=...
"""

from __future__ import annotations

from decimal import Decimal
from datetime import datetime

import pytest


# ------------------------------------------------------------------ #
# Schema unit tests
# ------------------------------------------------------------------ #

def test_account_out_schema_serialises_balance_as_string():
    """AccountOut serialises Decimal balance as string to avoid JS float rounding."""
    from app.schemas.accounts import AccountOut
    acc = AccountOut(
        account_id=1,
        account_type="checking",
        balance=Decimal("15420.50"),
        currency="EUR",
        status="active",
    )
    dumped = acc.model_dump()
    assert dumped["balance"] == "15420.50"
    assert isinstance(dumped["balance"], str)


def test_account_list_schema():
    """AccountList wraps multiple AccountOut objects."""
    from app.schemas.accounts import AccountOut, AccountList
    items = [
        AccountOut(
            account_id=i,
            account_type="savings",
            balance=Decimal("1000.00"),
            currency="USD",
            status="active",
        )
        for i in range(1, 4)
    ]
    acc_list = AccountList(accounts=items, total=3)
    assert acc_list.total == 3
    assert len(acc_list.accounts) == 3


def test_transaction_out_schema_serialises_amount_as_string():
    """TransactionOut serialises Decimal amount as string."""
    from app.schemas.transactions import TransactionOut
    tx = TransactionOut(
        transaction_id=1,
        source_account=10,
        destination_account=20,
        amount=Decimal("250.75"),
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        status="completed",
    )
    dumped = tx.model_dump()
    assert dumped["amount"] == "250.75"
    assert isinstance(dumped["amount"], str)


def test_transaction_list_schema():
    """TransactionList wraps multiple TransactionOut objects."""
    from app.schemas.transactions import TransactionOut, TransactionList
    txs = [
        TransactionOut(
            transaction_id=i,
            source_account=1,
            destination_account=2,
            amount=Decimal("10.00"),
            timestamp=datetime.now(),
            status="completed",
        )
        for i in range(1, 4)
    ]
    tx_list = TransactionList(transactions=txs, total=3, account_id=1)
    assert tx_list.total == 3
    assert len(tx_list.transactions) == 3


# ------------------------------------------------------------------ #
# App route registration tests (CTF endpoints must exist, lab must not)
# ------------------------------------------------------------------ #

def test_app_loads_and_ctf_routes_registered():
    """
    FastAPI app loads correctly and all 4 CTF vulnerability routes are registered.
    No /api/lab routes should be present.
    """
    from app.main import app

    paths = [getattr(route, "path", "") for route in app.routes]

    # Normal auth routes
    assert "/api/auth/login" in paths
    assert "/api/auth/logout" in paths
    assert "/api/auth/me" in paths

    # CTF #1 — SQLi: user search endpoint
    assert "/api/auth/search" in paths, "Missing CTF SQLi endpoint: /api/auth/search"

    # Normal account routes
    assert "/api/accounts" in paths

    # CTF #2 — BOLA/IDOR: account lookup without ownership check
    assert "/api/accounts/lookup/{account_ref}" in paths, \
        "Missing CTF BOLA endpoint: /api/accounts/lookup/{account_ref}"

    # Normal transaction routes
    assert "/api/transactions" in paths

    # CTF #3 — Excessive Privileges: export with DB metadata leak
    assert "/api/transactions/export" in paths, \
        "Missing CTF privileges endpoint: /api/transactions/export"

    # CTF #4 — Network Exposure: arbitrary host probe
    assert "/api/diagnostics/db-ping" in paths, \
        "Missing CTF network exposure endpoint: /api/diagnostics/db-ping"

    # Lab routes MUST NOT exist (removed in CTF refactor)
    lab_routes = [p for p in paths if "lab" in p]
    assert not lab_routes, f"Lab routes still present (should be removed): {lab_routes}"


def test_no_lab_module_importable():
    """The old lab module must not be importable after CTF refactor."""
    import importlib
    import sys

    for mod in list(sys.modules.keys()):
        if "app.lab" in mod:
            del sys.modules[mod]

    with pytest.raises((ImportError, ModuleNotFoundError)):
        importlib.import_module("app.lab.config")


def test_settings_has_no_lab_fields():
    """Settings model must not expose any lab-related configuration fields."""
    from app.core.config import get_settings
    get_settings.cache_clear()
    settings = get_settings()

    assert not hasattr(settings, "lab_enabled"), "lab_enabled field still present in Settings"
    assert not hasattr(settings, "lab_db_host"), "lab_db_host field still present in Settings"
    assert not hasattr(settings, "lab_db_name"), "lab_db_name field still present in Settings"


def test_health_endpoint_no_lab_field():
    """Health endpoint returns 200 and must not leak lab_enabled field."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as client:
        resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "app_env" in data
    assert "lab_enabled" not in data
