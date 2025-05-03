# api/websockets/router.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
import uuid

from api.websockets.manager import connection_manager
from api.websockets.auth import verify_token

logger = logging.getLogger("finexia-api")

router = APIRouter()


@router.websocket("/predictions/{symbol}")
async def prediction_updates(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for receiving predictions for a specific symbol"""
    # Verify client token
    is_authenticated, username = await verify_token(websocket)
    if not is_authenticated:
        return

    # Generate a unique client ID
    client_id = f"{username}_{uuid.uuid4()}"

    # Connect to the predictions channel for this symbol
    await connection_manager.connect(websocket, client_id, f"predictions_{symbol}")

    try:
        # Notify client of successful connection
        await websocket.send_json({"type": "connected", "message": f"Connected to prediction updates for {symbol}", "symbol": symbol})

        # Listen for client messages
        while True:
            data = await websocket.receive_text()
            try:
                json.loads(data)
                # Handle client commands here if needed
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, client_id)


@router.websocket("/system/status")
async def system_status_updates(websocket: WebSocket):
    """WebSocket endpoint for system status updates"""
    # Verify client token and admin privileges
    is_authenticated, username = await verify_token(websocket)
    if not is_authenticated:
        return

    # TODO: Check if user is admin

    # Generate a unique client ID
    client_id = f"{username}_{uuid.uuid4()}"

    # Connect to the system status channel
    await connection_manager.connect(websocket, client_id, "system_status")

    try:
        # Notify client of successful connection
        await websocket.send_json({"type": "connected", "message": "Connected to system status updates"})

        # Listen for client messages
        while True:
            await websocket.receive_text()
            # Just keep connection alive, no processing needed for client messages

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, client_id)
