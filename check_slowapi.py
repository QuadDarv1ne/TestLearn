from slowapi.util import get_remote_address
import slowapi
print("Available in slowapi:", dir(slowapi))

from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
print("Limiter attributes:", [attr for attr in dir(limiter) if not attr.startswith('_')])

# Check what the RateLimitExceeded expects
from slowapi.errors import RateLimitExceeded
print("RateLimitExceeded init:", RateLimitExceeded.__init__.__doc__)

# Let's see what the _rate_limit_exceeded_handler expects
from slowapi.extension import _rate_limit_exceeded_handler
print("_rate_limit_exceeded_handler:", _rate_limit_exceeded_handler)