# api/middleware/rate_limiter.py
import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from collections import defaultdict

from api.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits = defaultdict(list)  # IP address -> list of request timestamps

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Get client IP
        client_ip = request.client.host

        # Check if rate limit is exceeded
        now = time.time()
        window_start = now - settings.RATE_LIMIT_WINDOW

        # Clean up old requests
        self.rate_limits[client_ip] = [ts for ts in self.rate_limits[client_ip] if ts > window_start]

        # Check rate limit
        if len(self.rate_limits[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Rate limit exceeded. Try again in {settings.RATE_LIMIT_WINDOW} seconds.")

        # Add current request timestamp
        self.rate_limits[client_ip].append(now)

        # Process the request
        response = await call_next(request)

        # Add rate limit headers
        requests_left = settings.RATE_LIMIT_REQUESTS - len(self.rate_limits[client_ip])
        response.headers["X-Rate-Limit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-Rate-Limit-Remaining"] = str(max(0, requests_left))
        response.headers["X-Rate-Limit-Reset"] = str(int(window_start + settings.RATE_LIMIT_WINDOW))

        return response
