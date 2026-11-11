from collections import deque
from threading import Lock
from time import monotonic

from app.identity.domain import RateLimited


class LoginRateLimiter:
    """Single-process throttling for the local, single-worker demo API."""

    def __init__(self, limit: int = 10, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._failures: dict[str, deque[float]] = {}
        self._lock = Lock()

    def check(self, address: str) -> None:
        now = monotonic()
        with self._lock:
            failures = self._failures.setdefault(address, deque())
            self._discard_expired(failures, now)
            if len(failures) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - failures[0])))
                raise RateLimited(retry_after)

    def record_failure(self, address: str) -> None:
        now = monotonic()
        with self._lock:
            failures = self._failures.setdefault(address, deque())
            self._discard_expired(failures, now)
            failures.append(now)
            if len(self._failures) > 10_000:
                expired = [
                    key
                    for key, values in self._failures.items()
                    if not values or now - values[-1] >= self.window_seconds
                ]
                for key in expired:
                    self._failures.pop(key, None)

    def clear(self, address: str) -> None:
        with self._lock:
            self._failures.pop(address, None)

    def _discard_expired(self, failures: deque[float], now: float) -> None:
        while failures and now - failures[0] >= self.window_seconds:
            failures.popleft()
