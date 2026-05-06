from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limit import RateLimitMiddleware

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
    raise exc

client = TestClient(app)
response = client.get("/test")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Assertions
assert response.status_code == 429
assert response.json()["detail"] == "Too many requests. Please try again later."
assert response.json()["status"] == 429
assert response.json()["retry_after"] == 10
print("Test passed!")
