"""
WebSocket connection manager for real-time features
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.max_connections = 100
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_type: str = "general"):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Initialize user's connection list if needed
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        # Add connection
        self.active_connections[user_id].append(websocket)
        
        # Store metadata
        connection_id = f"{user_id}_{len(self.active_connections[user_id])}"
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "type": connection_type,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ WebSocket connected: {user_id} ({connection_type})")
        return connection_id
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            
            # Clean up empty lists
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"❌ WebSocket disconnected: {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send message to {user_id}: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)
    
    async def send_text(self, text: str, user_id: str):
        """Send text message to specific user"""
        await self.send_personal_message({"type": "text", "content": text}, user_id)
    
    async def broadcast(self, message: dict, exclude_user: Optional[str] = None):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            if exclude_user and user_id == exclude_user:
                continue
            await self.send_personal_message(message, user_id)
    
    async def send_to_group(self, message: dict, user_ids: List[str]):
        """Send message to specific group of users"""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_active_connections_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_active_users_count(self) -> int:
        """Get number of unique connected users"""
        return len(self.active_connections)
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if user has active connection"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0
    
    async def heartbeat(self, websocket: WebSocket, user_id: str, interval: int = 30):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(interval)
                await websocket.send_json({"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()})
        except WebSocketDisconnect:
            self.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"Heartbeat error for {user_id}: {e}")
            self.disconnect(websocket, user_id)

# Global connection manager instance
manager = ConnectionManager()

def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager"""
    return manager
