from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

limiter = Limiter(key_func=get_remote_address)

class TestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except RateLimitExceeded as exc:
            print(f"exc.detail: '{exc.detail}'")
            print(f"type(exc.detail): {type(exc.detail)}")
            result = f"{exc.detail}. Please try again later."
            print(f"f-string result: '{result}'")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": result,
                    "status": 429,
                    "retry_after": exc.retry_after,
                },
            )
        except Exception as exc:
            print(f"Other exception: {exc}")
            raise

# Test it
class MockLimit:
    def __init__(self):
        self.error_message = "Too many requests"
        self.limit = "1/minute"
        self.retry_after = 10

exc = RateLimitExceeded(MockLimit())
exc.retry_after = 10

print(f"Testing with exc: {exc}")
print(f"exc.detail: '{exc.detail}'")

# Simulate what the middleware does
result = f"{exc.detail}. Please try again later."
print(f"Result: '{result}'")