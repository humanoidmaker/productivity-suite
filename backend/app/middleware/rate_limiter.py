from __future__ import annotations
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import get_settings


class InMemoryRateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, max_requests: int = 120, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._requests[key]
            # Remove expired entries
            cutoff = now - self.window
            self._requests[key] = [t for t in timestamps if t > cutoff]
            if len(self._requests[key]) >= self.max_requests:
                return False
            self._requests[key].append(now)
            return True

    def get_remaining(self, key: str) -> int:
        now = time.time()
        with self._lock:
            cutoff = now - self.window
            timestamps = [t for t in self._requests.get(key, []) if t > cutoff]
            return max(0, self.max_requests - len(timestamps))


_limiter: InMemoryRateLimiter | None = None


def get_rate_limiter() -> InMemoryRateLimiter:
    global _limiter
    if _limiter is None:
        settings = get_settings()
        _limiter = InMemoryRateLimiter(max_requests=settings.rate_limit_per_minute)
    return _limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/health", "/api/v1/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        limiter = get_rate_limiter()

        if not limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(limiter.get_remaining(client_ip))
        return response
