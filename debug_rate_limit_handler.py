from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import traceback

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/test")
@limiter.limit("1/minute")
async def test_endpoint(request: Request):
    return {"message": "ok"}

# First request should work
client = TestClient(app)
print("Making first request...")
response = client.get("/test")
print(f"First request status: {response.status_code}")
print(f"First request response: {response.json()}")

# Second request should trigger rate limit
print("Making second request (should trigger rate limit)...")
response = client.get("/test")
print(f"Second request status: {response.status_code}")
print(f"Second request response: {response.json()}")
print(f"Second request headers: {dict(response.headers)}")

# Let's also test what happens if we manually raise RateLimitExceeded
print("\nTesting manual RateLimitExceeded raise...")
@app.get("/test2")
async def test_endpoint2(request: Request):
    # Manually raise RateLimitExceeded to see what the handler does
    # We need to create a proper Limit object
    from slowapi import Limit
    limit = Limit("1/minute")
    exc = RateLimitExceeded(limit)
    exc.retry_after = 10
    raise exc

print("Making request to /test2...")
response = client.get("/test2")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")