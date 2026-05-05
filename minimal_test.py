from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from app.middleware.rate_limit import RateLimitMiddleware

# Create a minimal app with just our middleware
app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get("/test")
async def test_endpoint(request: Request):
    # Manually raise RateLimitExceeded
    class MockLimit:
        def __init__(self):
            self.error_message = "Too many requests"
            self.limit = "1/minute"
    print("About to raise RateLimitExceeded")
    exc = RateLimitExceeded(MockLimit())
    exc.retry_after = 10
    print(f"Raising: {exc}")
    raise exc

client = TestClient(app)
print("Making request...")
response = client.get("/test")
print(f"Status: {response.status_code}")
print(f"JSON: {response.json()}")