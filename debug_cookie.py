from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.csrf import CSRFMiddleware

app = FastAPI()
app.add_middleware(CSRFMiddleware)

@app.get("/test")
async def test_endpoint():
    return {"message": "ok"}

client = TestClient(app)
print("Making GET request...")
response = client.get("/test")
print(f"Status: {response.status_code}")
print(f"Cookies: {response.cookies}")
print(f"Client cookies: {client.cookies}")

# Try to get the cookie from response
cookie = response.cookies.get("csrf_token")
print(f"Cookie from response: {cookie}")

# Try to get the cookie from client
cookie = client.cookies.get("csrf_token")
print(f"Cookie from client: {cookie}")