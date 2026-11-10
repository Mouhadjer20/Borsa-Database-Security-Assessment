"""
app/models/app_users.py
=======================
ORM mapping for the `app_users` table.

Schema (expected — do not modify):
  user_id       SERIAL PRIMARY KEY
  username      VARCHAR UNIQUE NOT NULL
  password_hash VARCHAR NOT NULL
  role          VARCHAR NOT NULL   -- 'customer', 'employee', 'admin'

Security notes:
  - password_hash is NEVER serialised into API responses.
  - The column is loaded here only so the repository layer can verify
    passwords during authentication.
"""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = {"extend_existing": True}

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    # password_hash must NEVER appear in API responses.
    # Pydantic response models deliberately exclude this field.
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="customer")
