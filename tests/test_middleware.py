import pytest
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

from app.middleware.csrf import CSRFMiddleware, get_csrf_token
from app.middleware.rate_limit import RateLimitMiddleware, configure_rate_limiting, limiter
from slowapi.errors import RateLimitExceeded


# Test CSRF Middleware
def test_csrf_middleware_safe_methods():
    """Test that safe methods (GET, HEAD, OPTIONS) bypass CSRF check."""
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}

    @app.head("/test")
    async def test_endpoint_head():
        return {"message": "ok"}

    @app.options("/test")
    async def test_endpoint_options():
        return {"message": "ok"}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}

    response = client.head("/test")
    assert response.status_code == 200

    response = client.options("/test")
    assert response.status_code == 200


def test_csrf_middleware_auth_routes_skipped():
    """Test that API routes under /api/auth are skipped."""
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)

    @app.post("/api/auth/login")
    async def login():
        return {"message": "logged in"}

    client = TestClient(app)
    # No CSRF token provided, but should pass because it's under /api/auth
    response = client.post("/api/auth/login", json={"username": "test", "password": "test"})
    assert response.status_code == 200
    assert response.json() == {"message": "logged in"}


def test_csrf_middleware_missing_token():
    """Test that POST without CSRF token returns 403."""
    app = FastAPI()
    app.add_exception_handler(HTTPException, lambda request, exc: JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    ))
    app.add_middleware(CSRFMiddleware)

    @app.post("/test")
    async def test_endpoint():
        return {"message": "ok"}

    client = TestClient(app)
    # Explicitly clear cookies to ensure clean state
    client.cookies.clear()
    # Now make POST without CSRF token (no header, no form, no cookie)
    response = client.post("/test", json={})
    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF token missing"


def test_csrf_middleware_valid_token_header():
    """Test that POST with valid CSRF token in header passes."""
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)
    app.add_exception_handler(HTTPException, lambda request, exc: JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    ))

    @app.get("/test")
    async def test_endpoint_get():
        return {"message": "ok"}

    @app.post("/test")
    async def test_endpoint_post():
        return {"message": "ok"}

    client = TestClient(app)
    # First, get a token by making a safe request (which sets cookie in client's cookie jar)
    response = client.get("/test")
    assert response.status_code == 200

    # Get the token from the response cookie
    csrf_token = response.cookies.get("csrf_token")
    assert csrf_token is not None

    # Now make a POST request with the token in header (must match cookie)
    try:
        response = client.post(
            "/test",
            json={},
            headers={"X-CSRF-Token": csrf_token}
        )
        # If we get a response, check it
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}
    except ExceptionGroup as exc_group:
        # We expect exactly one exception in the group
        assert len(exc_group.exceptions) == 1
        exc = exc_group.exceptions[0]
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 200
        assert exc.detail == "ok"


def test_csrf_middleware_valid_token_form():
    """Test that POST with valid CSRF token in form data passes."""
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)

    @app.get("/test")
    async def test_endpoint_get():
        return {"message": "ok"}

    @app.post("/test")
    async def test_endpoint_post():
        return {"message": "ok"}

    client = TestClient(app)
    # Get a token via cookie
    response = client.get("/test")
    assert response.status_code == 200
    cookie = response.cookies.get("csrf_token")
    assert cookie is not None

    # Send token in JSON body (as per middleware, it checks JSON body for csrf_token)
    # Need to pass the cookie along with the request
    response = client.post(
        "/test",
        json={"csrf_token": cookie},
        cookies={"csrf_token": cookie}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_csrf_middleware_invalid_token():
    """Test that POST with CSRF token in header that doesn't match cookie returns 403 (mismatch)."""
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)
    app.add_exception_handler(HTTPException, lambda request, exc: JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    ))

    @app.get("/test")
    async def test_endpoint_get():
        return {"message": "ok"}

    @app.post("/test")
    async def test_endpoint_post():
        return {"message": "ok"}

    client = TestClient(app)
    # First, get a token by making a safe request (which sets cookie in client's cookie jar)
    response = client.get("/test")
    assert response.status_code == 200

    # Get the token from cookie
    csrf_token = client.cookies.get("csrf_token")
    assert csrf_token is not None

    # Now make a POST request with a different token in header (must not match cookie)
    try:
        response = client.post(
            "/test",
            json={},
            headers={"X-CSRF-Token": "different_token"}
        )
        # If we get a response, check it
        assert response.status_code == 403
        assert response.json()["detail"] == "CSRF token mismatch"
    except ExceptionGroup as exc_group:
        # We expect exactly one exception in the group
        assert len(exc_group.exceptions) == 1
        exc = exc_group.exceptions[0]
        assert isinstance(exc, HTTPException)
        assert exc.status_code == 403
        assert exc.detail == "CSRF token mismatch"


def test_csrf_middleware_token_cookie_fallback():
    """Test that CSRF token from cookie is used when header and form are missing."""
    app = FastAPI()
    app.add_middleware(CSRFMiddleware)

    @app.get("/test")
    async def test_endpoint_get():
        return {"message": "ok"}

    @app.post("/test")
    async def test_endpoint_post():
        return {"message": "ok"}

    client = TestClient(app)
    # Get a token via cookie by making a safe request
    response = client.get("/test")
    assert response.status_code == 200
    cookie = response.cookies.get("csrf_token")
    assert cookie is not None

    # Now make a POST request without header or form, but cookie should be sent automatically
    # The middleware checks for cookie if header and form token are missing
    response = client.post("/test", json={})
    # Since the cookie is sent with the request, it should be found and validated
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_get_csrf_token():
    """Test that get_csrf_token returns a secure random string."""
    token1 = get_csrf_token()
    token2 = get_csrf_token()
    assert token1 != token2
    assert len(token1) >= 32  # token_urlsafe(32) returns 43-char string
    # Check that it's URL-safe
    import string
    allowed = set(string.ascii_letters + string.digits + '-_')
    assert set(token1).issubset(allowed)


# Test Rate Limit Middleware
def test_rate_limit_middleware():
    """Test that RateLimitMiddleware catches RateLimitExceeded and returns 429."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/test")
    async def test_endpoint(request: Request):
        # Manually raise RateLimitExceeded
        class MockLimit:
            def __init__(self):
                self.error_message = "Too many requests"
                self.limit = "1/minute"
        exc = RateLimitExceeded(MockLimit())
        exc.retry_after = 10
        print(f"[TEST] About to raise exception: {exc}")
        print(f"[TEST] Exception detail: {exc.detail}")
        raise exc

    client = TestClient(app)
    response = client.get("/test")
    print(f"[TEST] Response: {response.json()}")
    assert response.status_code == 429
    # The middleware adds ". Please try again later." to the detail
    assert response.json()["detail"] == "Too many requests. Please try again later."
    assert response.json()["status"] == 429
    assert response.json()["retry_after"] == 10


def test_rate_limit_middleware_passthrough():
    """Test that RateLimitMiddleware lets normal requests through."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_configure_rate_limiting():
    """Test that configure_rate_limiting sets up the limiter and exception handler."""
    app = FastAPI()
    configure_rate_limiting(app)

    # Check that limiter is attached to app.state
    assert hasattr(app.state, 'limiter')
    assert app.state.limiter is not None

    # Check that the exception handler is added
    # We can't easily test the exception handler without making a request that triggers it,
    # but we can verify that the limiter is configured with the expected limits.
    from app.middleware.rate_limit import RATE_LIMITS
    # The limiter's limits are set via decorators, not directly on the limiter object.
    # So we just check that the limiter exists and the RATE_LIMITS dict is as expected.
    assert RATE_LIMITS["default"] == "100/minute"
    assert RATE_LIMITS["auth"] == "10/minute"