"""
app/models/security_audit.py
=============================
ORM mapping for the `security_audit` table.

Schema (expected — do not modify):
  event_id   SERIAL PRIMARY KEY
  actor      VARCHAR              -- username or system identifier
  action     VARCHAR NOT NULL     -- e.g. 'login', 'account_read', 'experiment_run'
  resource   VARCHAR              -- target resource: table name, endpoint, account_id
  timestamp  TIMESTAMPTZ NOT NULL DEFAULT now()
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SecurityAudit(Base):
    __tablename__ = "security_audit"
    __table_args__ = {"extend_existing": True}

    event_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    resource: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
