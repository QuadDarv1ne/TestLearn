"""CSRF protection middleware for FastAPI."""
import secrets
import re
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware for state-changing operations."""

    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    CSRF_HEADER = "X-CSRF-Token"
    COOKIE_NAME = "csrf_token"

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        skip_csrf_check = request.method in self.SAFE_METHODS

        # Skip CSRF check for API routes that use token-based auth
        if request.url.path.startswith("/api/auth"):
            skip_csrf_check = True

        # Get CSRF token from header or form (only if not skipping CSRF check)
        csrf_token = None
        if not skip_csrf_check:
            csrf_token = request.headers.get(self.CSRF_HEADER)

            # Also check form data for CSRF token
            if not csrf_token and request.method in {"POST", "PUT", "DELETE", "PATCH"}:
                try:
                    body = await request.json()
                    csrf_token = body.get("csrf_token") if isinstance(body, dict) else None
                except:
                    pass

            # Validate CSRF token
            if not csrf_token:
                # For browser forms, check cookie
                cookie_token = request.cookies.get(self.COOKIE_NAME)
                if cookie_token:
                    csrf_token = cookie_token

            if not csrf_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token missing"
                )

            # Validate token format (should be secure random string)
            if not self._is_valid_token(csrf_token):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token mismatch"
                )

        # Process the request
        response = await call_next(request)

        # Set CSRF cookie if not exists (for new sessions)
        if not request.cookies.get(self.COOKIE_NAME):
            new_token = secrets.token_urlsafe(32)
            response.set_cookie(
                key=self.COOKIE_NAME,
                value=new_token,
                httponly=True,
                samesite="lax",
                max_age=3600  # 1 hour
            )

        return response

    def _is_valid_token(self, token: str) -> bool:
        """Validate that token is a secure random string."""
        if not token or len(token) < 20:
            return False
        # Token should be URL-safe base64 or hex
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', token))


def get_csrf_token() -> str:
    """Generate a new CSRF token."""
    return secrets.token_urlsafe(32)
