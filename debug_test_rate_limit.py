import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.rate_limit import RateLimitMiddleware
from slowapi.errors import RateLimitExceeded

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get("/test")
async def test_endpoint(request: Request):
    class MockLimit:
        def __init__(self):
            self.error_message = "Too many requests"
            self.limit = "1/minute"
    exc = RateLimitExceeded(MockLimit())
    exc.retry_after = 10
    raise exc

client = TestClient(app)
response = client.get("/test")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print(f"Response keys: {list(response.json().keys())}")

# Now, let's see what the test expects
expected_detail = "Too many requests. Please try again later."
actual_detail = response.json().get("detail")
print(f"Expected detail: {expected_detail}")
print(f"Actual detail: {actual_detail}")
print(f"Match: {expected_detail == actual_detail}")