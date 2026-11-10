"""
app/models/customers.py
========================
ORM mapping for the `customers` table.

Schema (expected — do not modify):
  customer_id  SERIAL PRIMARY KEY
  full_name    VARCHAR NOT NULL
  email        VARCHAR UNIQUE NOT NULL
  status       VARCHAR NOT NULL   -- e.g. 'active', 'suspended'
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Customer(Base):
    __tablename__ = "customers"
    __table_args__ = {"extend_existing": True}

    customer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
