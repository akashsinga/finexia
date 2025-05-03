# api/middleware/db_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from db.database import SessionLocal
import logging

logger = logging.getLogger("finexia-api")

class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Create a new session for each request
        db = SessionLocal()
        
        # Store the session in request state for easy access
        request.state.db = db
        
        try:
            # Process the request
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error in request: {str(e)}")
            raise
        finally:
            # Always close the session
            db.close()