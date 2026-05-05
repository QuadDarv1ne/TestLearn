from slowapi.util import get_remote_address
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

limiter = Limiter(key_func=get_remote_address)

# Create a proper limit object
class MockLimit:
    def __init__(self):
        self.error_message = "Too many requests"
        self.limit = "1/minute"

# Create the exception
exc = RateLimitExceeded(MockLimit())
exc.retry_after = 10

print("Created RateLimitExceeded:")
print(f"  exc.limit: {exc.limit}")
print(f"  exc.limit.error_message: {exc.limit.error_message}")
print(f"  exc.status_code: {exc.status_code}")
print(f"  exc.detail: {exc.detail}")
print(f"  exc.retry_after: {getattr(exc, 'retry_after', 'NOT SET')}")

# Now let's see what the handler does
# We need to create a mock request and call the handler
class MockRequest:
    def __init__(self):
        self.app = type('MockApp', (), {'state': type('MockState', (), {'limiter': limiter})()})()
        self.client = type('MockClient', (), {'host': 'testclient'})()

try:
    request = MockRequest()
    # This is what the middleware calls
    print("\nCalling _rate_limit_exceeded_handler...")
    # The handler is async, so we need to run it properly
    import asyncio
    
    async def call_handler():
        response = await _rate_limit_exceeded_handler(request, exc)
        return response
    
    # Run the async function
    response = asyncio.run(call_handler())
    print(f"Handler response status: {response.status_code}")
    print(f"Handler response content: {response.body}")
    
except Exception as e:
    print(f"Error in handler: {e}")
    traceback.print_exc()