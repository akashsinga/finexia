# api/websockets/auth.py
from fastapi import WebSocket, status
from jose import jwt, JWTError
import logging
from typing import Tuple, Optional
from api.config import settings

logger = logging.getLogger("finexia-api")

async def verify_token(websocket: WebSocket) -> Tuple[bool, Optional[str]]:
    """Verify token from query parameters or cookies"""
    try:
        # Try to get token from query parameters
        token = websocket.query_params.get("token")

        # If not in query params, try to get from cookies
        if not token:
            token = websocket.cookies.get("token")

        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False, None

        # Verify token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")

        if not username:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False, None

        return True, username

    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False, None
