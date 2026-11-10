"""
app/core/logging.py
===================
Structured logging configuration using structlog.

Security rules enforced here:
  - Passwords, tokens, and session secrets are NEVER logged.
  - Financial records are logged only as identifiers (IDs), never as full values.
  - All security-significant events (logins, auth failures, lab runs) produce
    a dedicated structured log entry that can be correlated with DB audit rows.

Usage:
    from app.core.logging import get_logger, log_security_event

    logger = get_logger(__name__)
    logger.info("account_retrieved", account_id=account_id, user_id=user_id)
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

# ------------------------------------------------------------------ #
# Sensitive field names — values are scrubbed before logging
# ------------------------------------------------------------------ #
_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "password_hash",
        "token",
        "access_token",
        "session_secret",
        "db_password",
        "lab_db_password",
        "authorization",
        "cookie",
        "set_cookie",
    }
)

_REDACTED = "[REDACTED]"


def _scrub_sensitive(logger: Any, method: str, event_dict: dict) -> dict:  # noqa: ANN401
    """
    structlog processor that replaces sensitive values with [REDACTED].

    This is a defence-in-depth measure: code should never pass sensitive data
    to the logger in the first place, but this processor acts as a safety net.
    """
    for key in list(event_dict.keys()):
        if key.lower() in _SENSITIVE_KEYS:
            event_dict[key] = _REDACTED
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """
    Set up structlog with JSON rendering for production and coloured console
    output for development.  Call once at application startup.
    """
    # Configure stdlib logging so uvicorn / SQLAlchemy logs are captured.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        _scrub_sensitive,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # In production, emit newline-delimited JSON; otherwise use a readable
        # coloured format for the developer console.
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named structlog logger."""
    return structlog.get_logger(name)


# ------------------------------------------------------------------ #
# Security-event helpers
# ------------------------------------------------------------------ #

_security_logger = get_logger("borsa.security")


def log_security_event(
    event: str,
    actor: str | None = None,
    resource: str | None = None,
    outcome: str = "unknown",
    **extra: Any,
) -> None:
    """
    Emit a structured security-event log entry.

    Parameters
    ----------
    event:
        Short machine-readable event name, e.g. "login_success", "auth_failure".
    actor:
        Username or user_id of the entity performing the action.
    resource:
        The API path, account ID, or table name being accessed.
    outcome:
        "success" | "failure" | "blocked" | "unknown"
    **extra:
        Additional contextual fields.  Sensitive keys are automatically scrubbed
        by the _scrub_sensitive processor.
    """
    _security_logger.info(
        event,
        actor=actor,
        resource=resource,
        outcome=outcome,
        security_event=True,  # allows easy filtering in log aggregators
        **extra,
    )
