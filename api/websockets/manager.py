# api/websockets/manager.py
from fastapi import WebSocket
from typing import Dict, List, Optional
import logging

logger = logging.getLogger("finexia-api")


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, topic: Optional[str] = None):
        """Connect a client to a specific topic"""
        await websocket.accept()

        # Use topic name as a channel key, default to 'general' if none provided
        channel = topic or "general"

        if channel not in self.active_connections:
            self.active_connections[channel] = []

        # Store connection with client ID
        self.active_connections[channel].append((client_id, websocket))
        logger.info(f"Client {client_id} connected to {channel}. Total connections: {self.connection_count}")

    def disconnect(self, websocket: WebSocket, client_id: str):
        """Disconnect a client from all topics"""
        for channel in self.active_connections:
            self.active_connections[channel] = [conn for conn in self.active_connections[channel] if conn[1] is not websocket]
        logger.info(f"Client {client_id} disconnected. Total connections: {self.connection_count}")

    async def broadcast(self, message: dict, topic: Optional[str] = None):
        """Broadcast a message to all connections in a topic"""
        channel = topic or "general"

        if channel in self.active_connections:
            for client_id, connection in self.active_connections[channel]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to client {client_id}: {str(e)}")

    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client across all topics"""
        for channel in self.active_connections:
            for cid, connection in self.active_connections[channel]:
                if cid == client_id:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending to client {client_id}: {str(e)}")

    @property
    def connection_count(self) -> int:
        """Total number of active connections"""
        count = 0
        for channel in self.active_connections:
            count += len(self.active_connections[channel])
        return count


# Create a global instance of the manager
connection_manager = ConnectionManager()
