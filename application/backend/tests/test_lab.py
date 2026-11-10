"""
application/backend/tests/test_lab.py
=====================================
Tests for Security Lab schemas and scenario validation logic.
"""

import pytest
from app.schemas.lab import ExperimentRequest, ExperimentResult, LabStatus


def test_experiment_request_validation():
    req = ExperimentRequest(variant="A", payload="' OR '1'='1")
    assert req.variant == "A"
    assert req.payload == "' OR '1'='1'"

    # Variant must match ^[A-C]$
    with pytest.raises(Exception):
        ExperimentRequest(variant="Z")


def test_experiment_result_model():
    res = ExperimentResult(
        scenario="sqli",
        variant="A",
        executed=True,
        vulnerability_demonstrated=True,
        rows_affected=5,
        explanation="SQL injection succeeded in lab environment.",
    )
    assert res.executed is True
    assert res.vulnerability_demonstrated is True
    assert res.rows_affected == 5


def test_lab_status_model():
    status = LabStatus(
        lab_enabled=False,
        app_security_mode="secure",
        lab_db_connected=False,
        message="Strict secure mode active.",
    )
    assert status.lab_enabled is False
    assert status.app_security_mode == "secure"

