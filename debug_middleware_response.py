from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.rate_limit import RateLimitMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import traceback

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.add_middleware(RateLimitMiddleware)
# Configure like in main.py
from app.middleware.rate_limit import configure_rate_limiting
configure_rate_limiting(app)
from slowapi.errors import RateLimitExceeded
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/test")
@limiter.limit("1/minute")
async def test_endpoint(request: Request):
    return {"message": "ok"}

client = TestClient(app)
# First request should work
print("Making first request...")
response = client.get("/test")
print(f"First request status: {response.status_code}")
print(f"First request response: {response.json()}")

# Second request should hit rate limit and be caught by middleware
print("Making second request (should be caught by middleware)...")
response = client.get("/test")
print(f"Second request status: {response.status_code}")
print(f"Second request response: {response.json()}")
print(f"Second request headers: {dict(response.headers)}")