from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Let's see what the _rate_limit_exceeded_handler does
print("_rate_limit_exceeded_handler:", _rate_limit_exceeded_handler)
print("_rate_limit_exceeded_handler.__doc__:", _rate_limit_exceeded_handler.__doc__)

# Create a mock request and exception
class MockRequest:
    pass

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
response = _rate_limit_exceeded_handler(request, exc)
print(f"Response: {response}")
print(f"Response body: {response.body}")
