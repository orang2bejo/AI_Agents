import time

from windows_use.utils.rate_limit import rate_limit
from windows_use.utils.retry import retry


def test_rate_limit_sleep():
    calls = []

    @rate_limit(1, 0.2)
    def func():
        calls.append(time.time())

    func()
    func()
    assert calls[1] - calls[0] >= 0.2


def test_retry_eventually_succeeds():
    counter = {"n": 0}

    @retry((ValueError,), tries=3, backoff=0.01, jitter=False)
    def flaky():
        counter["n"] += 1
        if counter["n"] < 3:
            raise ValueError("fail")
        return True

    assert flaky() is True
    assert counter["n"] == 3
