from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.datastructures import Headers

limiter = Limiter(key_func=get_remote_address)

# Create a mock request with app.state.limiter
class MockApp:
    class state:
        limiter = limiter

class MockRequest:
    def __init__(self):
        self.app = MockApp()

# Let's see what the _rate_limit_exceeded_handler does
print("_rate_limit_exceeded_handler:", _rate_limit_exceeded_handler)
print("_rate_limit_exceeded_handler.__doc__:", _rate_limit_exceeded_handler.__doc__)

# Create a mock request and exception
class MockLimit:
    def __init__(self):
        self.error_message = "Too many requests"
        self.limit = "1/minute"

request = MockRequest()
exc = RateLimitExceeded(MockLimit())
exc.retry_after = 10

print(f"exc: {exc}")
print(f"exc.detail: {exc.detail}")

# Call the handler
try:
    response = _rate_limit_exceeded_handler(request, exc)
    print(f"Response: {response}")
    print(f"Response status_code: {response.status_code}")
    print(f"Response body: {response.body}")
    print(f"Response headers: {dict(response.headers)}")
except Exception as e:
    print(f"Exception during handler call: {e}")
    import traceback
    traceback.print_exc()