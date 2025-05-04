# api/middleware/auth.py - JWT Authentication middleware
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from datetime import datetime
from api.config import settings
import logging

logger = logging.getLogger("finexia-api")

# Public endpoints that don't require authentication
PUBLIC_PATHS = ["/", "/docs", "/redoc", "/openapi.json", "/api/v1/auth/token"]

# Admin-only endpoints
ADMIN_PATHS = ["/api/v1/system/run-pipeline", "/api/v1/system/status"]


class JWTAuthMiddleware(BaseHTTPMiddleware):
    # Replace your dispatch method with this updated version
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process each request and verify JWT token if required
        """
        path = request.url.path
        logger.info(f"Processing request for path: {path}")
        
        if request.method == "OPTIONS":
            return await call_next(request)

        # Check if path is public
        is_public = any(path.startswith(public_path) for public_path in PUBLIC_PATHS) or request.method == "OPTIONS"
        logger.info(f"Path is public: {is_public}")

        # Check if path is admin-only
        is_admin_path = any(path.startswith(admin_path) for admin_path in ADMIN_PATHS)
        logger.info(f"Path is admin-only: {is_admin_path}")
        
        # If path is in ADMIN_PATHs, it should not be considered as public
        if is_admin_path:
            is_public = False
            logger.info("Path is admin-only, so setting is_public to False")

        # Allow access to public endpoints without auth
        if is_public:
            logger.info(f"Skipping auth for public path: {path}")
            return await call_next(request)

        # Check for token in header
        auth_header = request.headers.get("Authorization")
        logger.info(f"Auth header: {auth_header}")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.error(f"Missing or invalid Authorization header: {auth_header}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})

        # Extract token
        token = auth_header.split("Bearer ")[1]
        logger.info(f"Token length: {len(token)}")

        try:
            # Verify token
            logger.info(f"Decoding token with SECRET_KEY: {settings.SECRET_KEY[:3]}***")
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            logger.info(f"Token payload: {payload}")

            # Extract user info
            username = payload.get("sub")
            if username is None:
                logger.error("No 'sub' in token payload")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token", headers={"WWW-Authenticate": "Bearer"})

            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.fromtimestamp(exp) < datetime.now():
                logger.error(f"Token expired. Exp: {exp}, Now: {datetime.now()}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})

            # Check permissions for admin-only paths
            if any(path.startswith(admin_path) for admin_path in ADMIN_PATHS):
                is_admin = payload.get("is_admin", False)
                if not is_admin:
                    logger.error("User is not admin")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

            # Store user info in request state
            request.state.user = payload
            logger.info(f"Authentication successful for user: {username}")

        except JWTError as e:
            logger.error(f"JWT Error: {str(e)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token", headers={"WWW-Authenticate": "Bearer"})

        # Continue processing the request
        return await call_next(request)
