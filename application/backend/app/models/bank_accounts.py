"""
app/models/bank_accounts.py
============================
ORM mapping for the `bank_accounts` table.

Schema (expected — do not modify):
  account_id    SERIAL PRIMARY KEY
  customer_id   INTEGER NOT NULL REFERENCES customers(customer_id)
  account_type  VARCHAR NOT NULL   -- e.g. 'checking', 'savings'
  balance       NUMERIC(15,2) NOT NULL
  currency      CHAR(3) NOT NULL   -- ISO 4217, e.g. 'EUR'
  status        VARCHAR NOT NULL
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    __table_args__ = {"extend_existing": True}

    account_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)
    account_type: Mapped[str] = mapped_column(String, nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
