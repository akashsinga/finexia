# api/middleware/auth.py - JWT Authentication middleware
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from datetime import datetime

from api.config import settings

# Public endpoints that don't require authentication
PUBLIC_PATHS = ["/", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/token"]

# Admin-only endpoints
ADMIN_PATHS = ["/api/v1/system/run-pipeline", "/api/v1/system/status"]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process each request and verify JWT token if required
        """
        path = request.url.path

        # Allow access to public endpoints without auth
        if any(path.startswith(public_path) for public_path in PUBLIC_PATHS) or request.method == "OPTIONS":
            return await call_next(request)

        # Check for token in header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})

        # Extract token
        token = auth_header.split("Bearer ")[1]

        try:
            # Verify token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            # Extract user info
            username = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token", headers={"WWW-Authenticate": "Bearer"})

            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.fromtimestamp(exp) < datetime.now():
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})

            # Check permissions for admin-only paths
            if any(path.startswith(admin_path) for admin_path in ADMIN_PATHS):
                is_admin = payload.get("is_admin", False)
                if not is_admin:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

            # Store user info in request state
            request.state.user = payload

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token", headers={"WWW-Authenticate": "Bearer"})

        # Continue processing the request
        return await call_next(request)