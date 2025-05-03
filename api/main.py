# api/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.config import settings
from api.middleware.auth import JWTAuthMiddleware
from api.middleware.rate_limiter import RateLimiterMiddleware
from api.middleware.logging import RequestLoggingMiddleware
from api.routers import predictions, historical, models, system, auth, users, symbols
from api.dependencies.db import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize features, connections
    # Runs before the application starts

    print("Starting Finexia API Server")

    yield

    # Shutdown: Clean up resources
    # Runs when the application is shutting down
    print("Shutting down Finexia API Server")


# Initialize FastAPI app with lifespan
app = FastAPI(title="Finexia API", description="Stock Market Intelligence API", version="1.0.0", lifespan=lifespan)

# Adding CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(JWTAuthMiddleware)

# Include routers
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(historical.router, prefix="/api/v1/historical", tags=["historical"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(symbols.router, prefix="/api/v1/symbols", tags=["symbols"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint to check API status"""
    return {"status": "online", "api_version": "1.0.0", "system_name": "Finexia", "documentation": "/docs"}
