from __future__ import annotations

from collections import defaultdict
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class RateLimiter:
    """Sliding window rate limiter per user/key."""

    def __init__(self, max_requests: int = 16, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> tuple[bool, int, float]:
        now = time.time()
        cutoff = now - self.window_seconds
        timestamps = [ts for ts in self.requests[key] if ts > cutoff]
        self.requests[key] = timestamps

        if len(timestamps) < self.max_requests:
            timestamps.append(now)
            remaining = self.max_requests - len(timestamps)
            return True, remaining, 0.0
        else:
            oldest = timestamps[0]
            reset_in = max(0.0, round(oldest + self.window_seconds - now, 2))
            return False, 0, reset_in


rate_limiter = RateLimiter(max_requests=16, window_seconds=60.0)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()

        raw_id = request.headers.get("x-request-id") or request.headers.get("x-correlation-id")
        if raw_id and raw_id.strip():
            correlation_id = raw_id.strip()
        else:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)

        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(elapsed_ms)

        return response
