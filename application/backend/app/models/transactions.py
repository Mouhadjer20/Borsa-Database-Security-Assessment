"""
app/models/transactions.py
==========================
ORM mapping for the `transactions` table.

Schema (expected — do not modify):
  transaction_id       SERIAL PRIMARY KEY
  source_account       INTEGER REFERENCES bank_accounts(account_id)
  destination_account  INTEGER REFERENCES bank_accounts(account_id)
  amount               NUMERIC(15,2) NOT NULL
  timestamp            TIMESTAMPTZ NOT NULL DEFAULT now()
  status               VARCHAR NOT NULL   -- 'completed', 'pending', 'failed'
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_account: Mapped[int | None] = mapped_column(
        ForeignKey("bank_accounts.account_id"), nullable=True
    )
    destination_account: Mapped[int | None] = mapped_column(
        ForeignKey("bank_accounts.account_id"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
