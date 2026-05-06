import traceback

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

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
try:
    response = client.get("/test")
    print(f"Second request status: {response.status_code}")
    print(f"Second request response: {response.json()}")
    print(f"Second request headers: {dict(response.headers)}")
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
