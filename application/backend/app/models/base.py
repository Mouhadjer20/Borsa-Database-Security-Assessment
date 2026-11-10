"""
app/models/base.py
==================
Shared SQLAlchemy DeclarativeBase for all ORM models.

The application DOES NOT create or modify the schema (alembic / DDL is out of
scope).  Models here are purely for read/write operations against an existing
database that the DBA has already provisioned.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all Borsa ORM models."""
    pass
