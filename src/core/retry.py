import time
import random
from functools import wraps

def retry(max_retry=3, base_delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retry + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retry:
                        raise
                    delay = base_delay * attempt + random.uniform(0.5, 2)
                    print(f"🔁 Retry {attempt}/{max_retry} sau {delay:.1f}s")
                    time.sleep(delay)
        return wrapper
    return decorator
