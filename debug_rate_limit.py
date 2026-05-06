from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Try to create a RateLimitExceeded exception like the middleware does
try:
    # This is how it's done in the _rate_limit_exceeded_handler
    # Let's see what the actual exception looks like
    print("Creating RateLimitExceeded...")
    # We need to trigger it through the limiter to see the real structure
    @limiter.limit("1/minute")
    async def test_endpoint():
        return "ok"

    # We can't easily test without making a request, but let's see what the exception expects
    print("RateLimitExceeded.__init__:", RateLimitExceeded.__init__.__doc__)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
