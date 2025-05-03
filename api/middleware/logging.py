# api/middleware/logging.py
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", handlers=[logging.FileHandler("api.log"), logging.StreamHandler()])

logger = logging.getLogger("finexia-api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        logger.info(f"Request {request_id} - {request.method} {request.url.path}")

        # Time the request
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            process_time = time.time() - start_time

            # Log response
            logger.info(f"Response {request_id} - {response.status_code} - {process_time:.4f}s")

            # Add custom headers for tracking
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response
        except Exception as e:
            # Log exceptions
            logger.error(f"Error {request_id} - {str(e)}")
            process_time = time.time() - start_time
            logger.info(f"Response {request_id} - 500 - {process_time:.4f}s")
            raise
