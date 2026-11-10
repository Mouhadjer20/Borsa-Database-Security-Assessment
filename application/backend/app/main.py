"""
app/main.py
===========
Main entry point for the Borsa FastAPI application.

Configures:
  - Application lifespan (DB engine startup and shutdown)
  - CORS middleware
  - Security headers middleware
  - API routers (health, auth, accounts, transactions, lab)
  - Structured logging
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import accounts, auth, health, lab, transactions
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.database.engine import close_engines, init_engines
from app.middleware.security_headers import SecurityHeadersMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Initializes DB engines on startup and closes them on shutdown.
    """
    settings = get_settings()
    configure_logging(log_level="DEBUG" if settings.app_env == "development" else "INFO")
    logger.info(
        "app_startup",
        app_env=settings.app_env,
        security_mode=settings.app_security_mode,
        lab_enabled=settings.lab_enabled,
    )

    # Initialize database connection engines
    await init_engines()

    yield

    # Clean up database connections
    logger.info("app_shutdown")
    await close_engines()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title="Borsa — Financial Platform & Security Lab",
        description="Educational financial application and database security assessment platform.",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS Middleware
    origins = [str(o).rstrip("/") for o in settings.cors_origins]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register API Routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(accounts.router)
    app.include_router(transactions.router)
    app.include_router(lab.router)

    return app


app = create_app()

