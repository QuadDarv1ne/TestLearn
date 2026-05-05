from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.rate_limit import RateLimitMiddleware
from slowapi.errors import RateLimitExceeded

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get("/test")
async def test_endpoint(request: Request):
    # Manually raise RateLimitExceeded to simulate hitting the limit
    # Create a mock limit object with required attributes
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