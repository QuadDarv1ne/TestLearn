from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded

from app.middleware.rate_limit import RateLimitMiddleware

print("Creating app...")
app = FastAPI()
print("Adding middleware...")
app.add_middleware(RateLimitMiddleware)

@app.get('/test')
async def test_endpoint(request: Request):
    print("In endpoint, about to raise RateLimitExceeded")
    class MockLimit:
        def __init__(self):
            self.error_message = 'Too many requests'
            self.limit = '1/minute'
    exc = RateLimitExceeded(MockLimit())
    exc.retry_after = 10
    print(f"Raising exception: {exc}")
    raise exc

print("Creating test client...")
client = TestClient(app)
print("Making request...")
response = client.get('/test')
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
print('Done.')
