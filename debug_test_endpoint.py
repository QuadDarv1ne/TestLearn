from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded

# Test the exact scenario from the test
app = FastAPI()

@app.get("/test")
async def test_endpoint(request: Request):
    # Manually raise RateLimitExceeded
    class MockLimit:
        def __init__(self):
            self.error_message = "Too many requests"
            self.limit = "1/minute"
    print("Creating RateLimitExceeded...")
    exc = RateLimitExceeded(MockLimit())
    print(f"Created exc: {exc}")
    print(f"exc.detail: {exc.detail}")
    exc.retry_after = 10
    print(f"About to raise exc: {exc}")
    raise exc

client = TestClient(app)
print("Making request...")
try:
    response = client.get("/test")
    print(f"Response status: {response.status_code}")
    print(f"Response json: {response.json()}")
except Exception as e:
    print(f"Exception during request: {e}")
    import traceback
    traceback.print_exc()