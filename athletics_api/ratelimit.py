"""Rate limiting i minnet per klient-IP, glidende vindu (B-4).

Nullstilles ved omstart og deles ikke mellom instanser. Det holder med én instans i v1.
"""

import math
import time
from collections import deque
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from athletics_api.errors import error_response

WINDOW_SECONDS = 60.0
EXEMPT_PATHS = frozenset({"/api/v1/health"})
_SWEEP_THRESHOLD = 10_000


class SlidingWindowLimiter:
    def __init__(
        self,
        limit: int,
        window: float = WINDOW_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window = window
        self.clock = clock
        self._hits: dict[str, deque[float]] = {}

    def hit(self, key: str) -> int | None:
        """Registrer et kall. ``None`` hvis det er innenfor grensen, ellers sekunder å vente."""
        now = self.clock()
        if len(self._hits) > _SWEEP_THRESHOLD:
            self._sweep(now)
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] <= now - self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return max(1, math.ceil(hits[0] + self.window - now))
        hits.append(now)
        return None

    def _sweep(self, now: float) -> None:
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= now - self.window]:
            del self._hits[key]


def client_ip(request: Request, trust_proxy: bool) -> str:
    """Klient-IP. Bak proxy er det siste leddet i ``X-Forwarded-For`` det proxyen selv la til."""
    if trust_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, limiter: SlidingWindowLimiter, trust_proxy: bool) -> None:
        super().__init__(app)
        self.limiter = limiter
        self.trust_proxy = trust_proxy

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS" or request.url.path in EXEMPT_PATHS:
            return await call_next(request)
        retry_after = self.limiter.hit(client_ip(request, self.trust_proxy))
        if retry_after is not None:
            return error_response(
                429,
                "rate_limited",
                "For mange forespørsler. Prøv igjen om litt.",
                {"retry_after_seconds": retry_after},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)
