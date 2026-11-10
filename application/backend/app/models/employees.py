"""
app/models/employees.py
=======================
ORM mapping for the `employees` table.

Schema (expected — do not modify):
  employee_id  SERIAL PRIMARY KEY
  name         VARCHAR NOT NULL
  department   VARCHAR NOT NULL
  status       VARCHAR NOT NULL
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}

    employee_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
