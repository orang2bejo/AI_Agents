from __future__ import annotations

import random
import time
from functools import wraps
from typing import Callable, Iterable, Tuple, Type


def retry(
    exceptions: Iterable[Type[BaseException]],
    tries: int = 3,
    backoff: float = 0.5,
    jitter: bool = True,
) -> Callable:
    exceptions_tuple: Tuple[Type[BaseException], ...] = tuple(exceptions)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = backoff
            for attempt in range(tries - 1):
                try:
                    return func(*args, **kwargs)
                except exceptions_tuple:
                    sleep = delay + (random.uniform(0, delay) if jitter else 0)
                    time.sleep(sleep)
                    delay *= 2
            return func(*args, **kwargs)

        return wrapper

    return decorator
