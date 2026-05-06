from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Let's see what the RateLimitExceeded expects
print("RateLimitExceeded.__init__:", RateLimitExceeded.__init__.__doc__)

# Try to create one with a mock limit
class MockLimit:
    def __init__(self):
        self.error_message = "Too many requests"
        self.limit = "1/minute"

try:
    exc = RateLimitExceeded(MockLimit())
    print(f"exc: {exc}")
    print(f"exc.args: {exc.args}")
    print(f"type(exc): {type(exc)}")
    # Check if it has a detail attribute
    if hasattr(exc, 'detail'):
        print(f"exc.detail: {exc.detail}")
    else:
        print("exc has no detail attribute")
    # Check what's in the exception
    for attr in dir(exc):
        if not attr.startswith('_'):
            print(f"  {attr}: {getattr(exc, attr)}")
except Exception as e:
    print(f"Error creating RateLimitExceeded: {e}")
    import traceback
    traceback.print_exc()
