"""
tests/test_auth.py
==================
Unit tests for authentication and security functions.
"""

import pytest
from app.core.security import (
    create_access_token,
    decode_access_token,
    extract_user_from_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    raw = "P@ssword1234!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_creation_and_decoding():
    token = create_access_token(
        user_id=1,
        username="alice",
        role="customer",
        expires_minutes=15,
    )
    assert token is not None

    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == "alice"
    assert payload.get("user_id") == 1
    assert payload.get("role") == "customer"

    extracted = extract_user_from_token(token)
    assert extracted is not None
    assert extracted["username"] == "alice"
    assert extracted["user_id"] == 1


def test_invalid_token_handling():
    assert extract_user_from_token("invalid.token.signature") is None
    assert decode_access_token("garbage_token") is None
