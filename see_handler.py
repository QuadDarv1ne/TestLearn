import inspect

from slowapi.extension import _rate_limit_exceeded_handler

print("_rate_limit_exceeded_handler source:")
try:
    print(inspect.getsource(_rate_limit_exceeded_handler))
except Exception as e:
    print(f"Could not get source: {e}")
    import traceback
    traceback.print_exc()
