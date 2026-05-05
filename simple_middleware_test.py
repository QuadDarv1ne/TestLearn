from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.rate_limit import RateLimitMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create a very simple test
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

# Add a route that will definitely trigger rate limit
@app.get("/test")
@limiter.limit("1/minute")
async def test_endpoint(request: Request):
    return {"message": "ok"}

client = TestClient(app)

print("First request:")
response = client.get("/test")
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")

print("\nSecond request (should trigger rate limit):")
response = client.get("/test")
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")
print(f"  Response text: {response.text}")