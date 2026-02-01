"""
═══════════════════════════════════════════════════════════════════════════════
WEBSOCKET ROUTES
Real-time WebSocket connections for live features.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging

from services.realtime.websocket_manager import (
    get_websocket_manager,
    MessageType,
    Connection
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    user_id: str = Query(...),
    token: Optional[str] = Query(None)
):
    """
    Main WebSocket connection endpoint.

    Features:
    - Real-time presence updates
    - Watch party synchronization
    - Direct messaging
    - Notifications

    Message format:
    {
        "type": "message_type",
        "data": { ... }
    }
    """
    manager = get_websocket_manager()

    # Accept connection
    await websocket.accept()

    # Register connection
    connection = await manager.connect(
        websocket=websocket,
        user_id=user_id,
        metadata={"token": token}
    )

    # Send welcome message
    await manager.send_to_connection(connection, {
        "type": "connected",
        "user_id": user_id,
        "message": "Welcome to dopamine.watch real-time!"
    })

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)

                # Handle the message
                await manager.handle_message(connection, message)

            except json.JSONDecodeError:
                await manager.send_to_connection(connection, {
                    "type": MessageType.ERROR.value,
                    "error": "Invalid JSON message"
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: {user_id}")

    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
        await manager.disconnect(websocket, user_id)


@router.websocket("/party/{party_id}")
async def websocket_party(
    websocket: WebSocket,
    party_id: str,
    user_id: str = Query(...)
):
    """
    WebSocket connection for watch party.

    Handles:
    - Playback sync (play, pause, seek)
    - Chat messages
    - Reactions
    - Member presence
    """
    from services.realtime.watch_party import get_watch_party_service

    manager = get_websocket_manager()
    party_service = get_watch_party_service()

    # Check if party exists
    party = party_service.get_party(party_id)
    if not party:
        await websocket.close(code=4004, reason="Party not found")
        return

    # Accept and register
    await websocket.accept()

    connection = await manager.connect(
        websocket=websocket,
        user_id=user_id,
        metadata={"party_id": party_id}
    )

    # Join party room
    await manager.join_room(user_id, party_id)

    # Send party state
    await party_service._send_party_state(party, user_id)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message["party_id"] = party_id  # Ensure party context

                await manager.handle_message(connection, message)

            except json.JSONDecodeError:
                await manager.send_to_connection(connection, {
                    "type": MessageType.ERROR.value,
                    "error": "Invalid JSON"
                })

    except WebSocketDisconnect:
        await party_service.leave_party(user_id)
        await manager.disconnect(websocket, user_id)

    except Exception as e:
        logger.error(f"Party WebSocket error: {e}")
        await manager.disconnect(websocket, user_id)


@router.websocket("/dm/{conversation_id}")
async def websocket_dm(
    websocket: WebSocket,
    conversation_id: str,
    user_id: str = Query(...)
):
    """
    WebSocket connection for direct messaging.

    Handles:
    - Message sending/receiving
    - Typing indicators
    - Read receipts
    """
    from services.social.messaging import get_messaging_service

    manager = get_websocket_manager()
    dm_service = get_messaging_service()

    # Check if conversation exists and user is participant
    conversation = dm_service.get_conversation(conversation_id)
    if not conversation or user_id not in conversation.participants:
        await websocket.close(code=4004, reason="Conversation not found or access denied")
        return

    # Accept and register
    await websocket.accept()

    connection = await manager.connect(
        websocket=websocket,
        user_id=user_id,
        metadata={"conversation_id": conversation_id}
    )

    # Send conversation state
    messages = conversation.messages[-50:]  # Last 50 messages
    await manager.send_to_connection(connection, {
        "type": "conversation_state",
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    })

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message["conversation_id"] = conversation_id

                await manager.handle_message(connection, message)

            except json.JSONDecodeError:
                await manager.send_to_connection(connection, {
                    "type": MessageType.ERROR.value,
                    "error": "Invalid JSON"
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user_id)

    except Exception as e:
        logger.error(f"DM WebSocket error: {e}")
        await manager.disconnect(websocket, user_id)


@router.get("/status")
async def websocket_status():
    """Get WebSocket service status."""
    manager = get_websocket_manager()
    stats = manager.get_stats()

    return {
        "status": "running",
        "stats": stats,
        "endpoints": [
            "/ws/connect - Main connection",
            "/ws/party/{party_id} - Watch party",
            "/ws/dm/{conversation_id} - Direct messages"
        ]
    }
