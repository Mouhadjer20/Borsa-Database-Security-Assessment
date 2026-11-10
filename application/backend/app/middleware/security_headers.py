"""
app/middleware/security_headers.py
===================================
ASGI middleware that appends security-relevant HTTP response headers.

Applied globally to all responses.  These headers are a defence-in-depth
measure; they do not replace proper server-side security controls.

Headers set:
  X-Content-Type-Options    — prevents MIME sniffing
  X-Frame-Options           — clickjacking protection
  X-XSS-Protection          — legacy XSS filter (belt-and-suspenders)
  Referrer-Policy           — limits referrer information leakage
  Content-Security-Policy   — restricts resource loading origins
  Strict-Transport-Security — enforces HTTPS (only sent in production)
  Permissions-Policy        — opt-out of browser features not needed here
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every HTTP response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        # Prevent MIME-type confusion attacks
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent this app from being embedded in an iframe (clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

        # Legacy XSS filter — belt-and-suspenders; modern CSP is the real guard
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Limit referrer to same origin to avoid leaking URL paths
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Basic CSP — tighten per deployment.
        # 'self' allows same-origin resources only; adjust if CDN assets are used.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Disable unnecessary browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )

        # HSTS — only add in production to avoid breaking local dev
        settings = get_settings()
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )

        return response
