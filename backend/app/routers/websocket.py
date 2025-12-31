"""
WebSocket endpoints for real-time communication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json
import logging
from ..websocket_manager import get_connection_manager, ConnectionManager
from ..security import decode_jwt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws")

@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    manager: ConnectionManager = Depends(get_connection_manager)
):
    """
    Main WebSocket endpoint for real-time communication
    
    Usage:
    ws://localhost:8000/api/v1/ws/connect?token=YOUR_JWT_TOKEN
    """
    
    # Authenticate user from token
    user_id = "anonymous"
    if token:
        try:
            payload = decode_jwt(token)
            user_id = payload.get("sub", "anonymous")
        except Exception as e:
            logger.error(f"WebSocket auth failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    # Connect
    connection_id = await manager.connect(websocket, user_id, "general")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "connection_id": connection_id,
            "message": "WebSocket connected successfully"
        })
        
        # Message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                # Handle different message types
                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                
                elif message_type == "echo":
                    # Echo message back
                    await websocket.send_json({
                        "type": "echo",
                        "content": message.get("content"),
                        "original": message
                    })
                
                elif message_type == "broadcast":
                    # Broadcast to all users
                    await manager.broadcast({
                        "type": "broadcast",
                        "from": user_id,
                        "content": message.get("content")
                    }, exclude_user=user_id)
                    
                    # Confirm to sender
                    await websocket.send_json({
                        "type": "broadcast_sent",
                        "status": "success"
                    })
                
                else:
                    # Unknown message type
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })
            
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Internal server error"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"Client {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        manager.disconnect(websocket, user_id)

@router.websocket("/test")
async def test_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Simple WebSocket test endpoint
    
    Usage:
    ws://localhost:8000/api/v1/ws/test?token=YOUR_JWT_TOKEN
    """
    
    # Authenticate
    user_id = "anonymous"
    if token:
        try:
            payload = decode_jwt(token)
            user_id = payload.get("sub", "anonymous")
        except Exception as e:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    # Accept connection
    await websocket.accept()
    
    try:
        # Send welcome message
        await websocket.send_text(f"✅ Connected! Your user ID: {user_id}")
        
        # Echo loop
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    
    except WebSocketDisconnect:
        logger.info(f"Test WebSocket client {user_id} disconnected")
    except Exception as e:
        logger.error(f"Test WebSocket error: {e}")

@router.websocket("/voice")
async def voice_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    manager: ConnectionManager = Depends(get_connection_manager)
):
    """
    WebSocket endpoint for voice streaming
    
    Usage:
    ws://localhost:8000/api/v1/ws/voice?token=YOUR_JWT_TOKEN
    """
    
    # Authenticate
    user_id = "anonymous"
    if token:
        try:
            payload = decode_jwt(token)
            user_id = payload.get("sub", "anonymous")
        except Exception as e:
            await websocket.close(code=1008, reason="Authentication failed")
            return
    
    # Connect
    connection_id = await manager.connect(websocket, user_id, "voice")
    
    try:
        await websocket.send_json({
            "type": "voice_connection",
            "status": "connected",
            "user_id": user_id,
            "message": "Voice WebSocket ready"
        })
        
        while True:
            # Receive audio data or control messages
            message = await websocket.receive()
            
            if "text" in message:
                # Control message
                data = json.loads(message["text"])
                
                if data.get("type") == "start_recording":
                    await websocket.send_json({
                        "type": "recording_started",
                        "status": "ready"
                    })
                
                elif data.get("type") == "stop_recording":
                    await websocket.send_json({
                        "type": "recording_stopped",
                        "status": "processing"
                    })
            
            elif "bytes" in message:
                audio_data = message["bytes"]
                await websocket.send_json({
                    "type": "audio_received",
                    "size": len(audio_data)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        manager.disconnect(websocket, user_id)
