# api/websockets/__init__.py
from fastapi import FastAPI
from api.websockets.router import router as ws_router


def init_websockets(app: FastAPI):
    """Initialize WebSocket routes"""
    app.include_router(ws_router)
