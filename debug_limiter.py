from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

@app.get("/test")
@limiter.limit("1/minute")
async def test_endpoint(request: Request):
    return {"message": "ok"}

client = TestClient(app)

print("First request:")
response = client.get("/test")
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")

print("\nSecond request:")
response = client.get("/test")
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")
