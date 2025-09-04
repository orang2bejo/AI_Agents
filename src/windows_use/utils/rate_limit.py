from __future__ import annotations

import time
from functools import wraps
from typing import Callable


def rate_limit(max_calls: int, period: float) -> Callable:
    tokens = max_calls
    last = time.monotonic()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal tokens, last
            now = time.monotonic()
            tokens += (now - last) * (max_calls / period)
            if tokens > max_calls:
                tokens = max_calls
            if tokens < 1:
                sleep_for = (1 - tokens) * (period / max_calls)
                time.sleep(sleep_for)
                now = time.monotonic()
                tokens += (now - last) * (max_calls / period)
            tokens -= 1
            last = now
            return func(*args, **kwargs)

        return wrapper

    return decorator
