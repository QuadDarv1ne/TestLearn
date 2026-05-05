from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.rate_limit import RateLimitMiddleware
from slowapi.errors import RateLimitExceeded

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get('/test')
async def test_endpoint(request: Request):
    class MockLimit:
        def __init__(self):
            self.error_message = 'Too many requests'
            self.limit = '1/minute'
    exc = RateLimitExceeded(MockLimit())
    exc.retry_after = 10
    raise exc

client = TestClient(app)
response = client.get('/test')
print('Status:', response.status_code)
print('Response:', response.json())