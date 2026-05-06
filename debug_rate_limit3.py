from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

# Also add the exception handler as in configure_rate_limiting
from slowapi import _rate_limit_exceeded_handler

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/test")
async def test_endpoint(request: Request):
    # Manually raise RateLimitExceeded to simulate hitting the limit
    class MockLimit:
        def __init__(self):
            self.error_message = "Too many requests"
    exc = RateLimitExceeded(MockLimit())
    exc.retry_after = 10
    raise exc

client = TestClient(app)
response = client.get("/test")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print(f"Response headers: {response.headers}")
