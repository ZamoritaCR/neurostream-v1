"""
═══════════════════════════════════════════════════════════════════════════════
WEBSOCKET MANAGER - Real-time Connection Handler
Manages WebSocket connections for live features like presence, watch parties,
and instant messaging.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    DISCONNECTED = "disconnected"


class MessageType(Enum):
    """Types of WebSocket messages."""
    # Presence
    PRESENCE_UPDATE = "presence_update"
    PRESENCE_SUBSCRIBE = "presence_subscribe"
    PRESENCE_UNSUBSCRIBE = "presence_unsubscribe"

    # Watch Party
    PARTY_JOIN = "party_join"
    PARTY_LEAVE = "party_leave"
    PARTY_SYNC = "party_sync"
    PARTY_CHAT = "party_chat"
    PARTY_REACTION = "party_reaction"

    # Direct Messages
    DM_SEND = "dm_send"
    DM_TYPING = "dm_typing"
    DM_READ = "dm_read"

    # Notifications
    NOTIFICATION = "notification"

    # System
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    ACK = "ack"


@dataclass
class Connection:
    """Represents a single WebSocket connection."""
    user_id: str
    websocket: Any  # WebSocket object
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)
    state: ConnectionState = ConnectionState.CONNECTED
    subscribed_rooms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Room:
    """Represents a room/channel for group communication."""
    room_id: str
    room_type: str  # "watch_party", "chat", "presence"
    created_at: datetime = field(default_factory=datetime.utcnow)
    members: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WebSocketManager:
    """
    Manages WebSocket connections and real-time communication.

    Features:
    - Connection pooling and management
    - Room-based messaging (watch parties, group chats)
    - Presence tracking
    - Automatic reconnection handling
    - Rate limiting and backpressure
    - Message queuing for offline users
    """

    def __init__(self,
                 ping_interval: int = 30,
                 ping_timeout: int = 10,
                 max_connections_per_user: int = 5,
                 message_queue_size: int = 100):
        # Active connections: user_id -> list of Connection objects
        self._connections: Dict[str, List[Connection]] = {}

        # Active rooms: room_id -> Room object
        self._rooms: Dict[str, Room] = {}

        # Presence state: user_id -> status info
        self._presence: Dict[str, Dict[str, Any]] = {}

        # Message queues for offline users
        self._offline_queues: Dict[str, List[Dict]] = {}

        # Configuration
        self._ping_interval = ping_interval
        self._ping_timeout = ping_timeout
        self._max_connections_per_user = max_connections_per_user
        self._message_queue_size = message_queue_size

        # Message handlers
        self._handlers: Dict[MessageType, List[Callable]] = {}

        # Background tasks
        self._ping_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        # Statistics
        self._stats = {
            "total_connections": 0,
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "active_rooms": 0
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # CONNECTION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    async def connect(self, websocket: Any, user_id: str, metadata: Dict = None) -> Connection:
        """
        Register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection object
            user_id: The user's unique identifier
            metadata: Optional connection metadata (device, platform, etc.)

        Returns:
            Connection object representing this connection
        """
        # Create connection object
        connection = Connection(
            user_id=user_id,
            websocket=websocket,
            metadata=metadata or {}
        )

        # Add to user's connections
        if user_id not in self._connections:
            self._connections[user_id] = []

        # Enforce max connections per user
        user_connections = self._connections[user_id]
        if len(user_connections) >= self._max_connections_per_user:
            # Disconnect oldest connection
            oldest = min(user_connections, key=lambda c: c.connected_at)
            await self._close_connection(oldest, "max_connections_exceeded")

        self._connections[user_id].append(connection)
        self._stats["total_connections"] += 1

        # Update presence
        await self._update_presence(user_id, "online")

        # Deliver queued messages
        await self._deliver_queued_messages(user_id)

        logger.info(f"User {user_id} connected. Total connections: {len(self._connections[user_id])}")

        return connection

    async def disconnect(self, websocket: Any, user_id: str) -> None:
        """
        Handle WebSocket disconnection.

        Args:
            websocket: The disconnected WebSocket
            user_id: The user's identifier
        """
        if user_id not in self._connections:
            return

        # Find and remove the specific connection
        connections = self._connections[user_id]
        for conn in connections:
            if conn.websocket == websocket:
                conn.state = ConnectionState.DISCONNECTED

                # Leave all rooms
                for room_id in list(conn.subscribed_rooms):
                    await self._leave_room(conn, room_id)

                connections.remove(conn)
                break

        # Clean up if no more connections
        if not connections:
            del self._connections[user_id]
            # Update presence to offline after a delay (to handle reconnects)
            asyncio.create_task(self._delayed_offline(user_id, delay=30))

        logger.info(f"User {user_id} disconnected")

    async def _delayed_offline(self, user_id: str, delay: int) -> None:
        """Mark user offline after delay if still disconnected."""
        await asyncio.sleep(delay)
        if user_id not in self._connections:
            await self._update_presence(user_id, "offline")

    async def _close_connection(self, connection: Connection, reason: str) -> None:
        """Force close a connection."""
        try:
            await self.send_to_connection(connection, {
                "type": MessageType.ERROR.value,
                "reason": reason
            })
            await connection.websocket.close()
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGE SENDING
    # ═══════════════════════════════════════════════════════════════════════════

    async def send_to_user(self, user_id: str, message: Dict, queue_if_offline: bool = True) -> bool:
        """
        Send a message to all connections of a specific user.

        Args:
            user_id: Target user's ID
            message: Message dictionary to send
            queue_if_offline: Whether to queue message if user is offline

        Returns:
            True if message was delivered to at least one connection
        """
        connections = self._connections.get(user_id, [])

        if not connections:
            if queue_if_offline:
                self._queue_message(user_id, message)
            return False

        # Send to all user's connections
        success = False
        for conn in connections:
            if await self.send_to_connection(conn, message):
                success = True

        return success

    async def send_to_connection(self, connection: Connection, message: Dict) -> bool:
        """Send message to a specific connection."""
        try:
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()

            await connection.websocket.send_json(message)
            self._stats["total_messages_sent"] += 1
            return True
        except Exception as e:
            logger.warning(f"Failed to send to {connection.user_id}: {e}")
            connection.state = ConnectionState.DISCONNECTED
            return False

    async def send_to_room(self, room_id: str, message: Dict, exclude_user: str = None) -> int:
        """
        Broadcast message to all members of a room.

        Args:
            room_id: The room to broadcast to
            message: Message to send
            exclude_user: Optional user to exclude (e.g., message sender)

        Returns:
            Number of users the message was delivered to
        """
        room = self._rooms.get(room_id)
        if not room:
            return 0

        # Add room context to message
        message["room_id"] = room_id

        delivered_count = 0
        for user_id in room.members:
            if user_id != exclude_user:
                if await self.send_to_user(user_id, message, queue_if_offline=False):
                    delivered_count += 1

        return delivered_count

    async def broadcast(self, message: Dict, exclude_users: Set[str] = None) -> int:
        """Broadcast message to all connected users."""
        exclude_users = exclude_users or set()
        delivered_count = 0

        for user_id in self._connections.keys():
            if user_id not in exclude_users:
                if await self.send_to_user(user_id, message):
                    delivered_count += 1

        return delivered_count

    def _queue_message(self, user_id: str, message: Dict) -> None:
        """Queue a message for offline user."""
        if user_id not in self._offline_queues:
            self._offline_queues[user_id] = []

        queue = self._offline_queues[user_id]

        # Enforce queue size limit
        while len(queue) >= self._message_queue_size:
            queue.pop(0)  # Remove oldest

        queue.append(message)

    async def _deliver_queued_messages(self, user_id: str) -> None:
        """Deliver queued messages when user connects."""
        if user_id not in self._offline_queues:
            return

        messages = self._offline_queues.pop(user_id, [])
        for message in messages:
            await self.send_to_user(user_id, message, queue_if_offline=False)

    # ═══════════════════════════════════════════════════════════════════════════
    # ROOM MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    async def create_room(self, room_id: str, room_type: str, metadata: Dict = None) -> Room:
        """Create a new room."""
        room = Room(
            room_id=room_id,
            room_type=room_type,
            metadata=metadata or {}
        )
        self._rooms[room_id] = room
        self._stats["active_rooms"] = len(self._rooms)

        logger.info(f"Room created: {room_id} ({room_type})")
        return room

    async def join_room(self, user_id: str, room_id: str) -> bool:
        """Add user to a room."""
        room = self._rooms.get(room_id)
        if not room:
            return False

        room.members.add(user_id)

        # Subscribe all user connections to room
        for conn in self._connections.get(user_id, []):
            conn.subscribed_rooms.add(room_id)

        # Notify room members
        await self.send_to_room(room_id, {
            "type": MessageType.PRESENCE_UPDATE.value,
            "user_id": user_id,
            "action": "joined",
            "room_id": room_id
        }, exclude_user=user_id)

        logger.info(f"User {user_id} joined room {room_id}")
        return True

    async def leave_room(self, user_id: str, room_id: str) -> bool:
        """Remove user from a room."""
        room = self._rooms.get(room_id)
        if not room or user_id not in room.members:
            return False

        room.members.discard(user_id)

        # Unsubscribe all user connections
        for conn in self._connections.get(user_id, []):
            await self._leave_room(conn, room_id)

        # Notify room members
        await self.send_to_room(room_id, {
            "type": MessageType.PRESENCE_UPDATE.value,
            "user_id": user_id,
            "action": "left",
            "room_id": room_id
        })

        # Clean up empty rooms (except persistent ones)
        if not room.members and not room.metadata.get("persistent"):
            await self.delete_room(room_id)

        return True

    async def _leave_room(self, connection: Connection, room_id: str) -> None:
        """Internal: Remove connection from room."""
        connection.subscribed_rooms.discard(room_id)

    async def delete_room(self, room_id: str) -> bool:
        """Delete a room."""
        if room_id not in self._rooms:
            return False

        room = self._rooms.pop(room_id)
        self._stats["active_rooms"] = len(self._rooms)

        # Notify all members
        for user_id in room.members:
            await self.send_to_user(user_id, {
                "type": "room_deleted",
                "room_id": room_id
            })

        logger.info(f"Room deleted: {room_id}")
        return True

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get room by ID."""
        return self._rooms.get(room_id)

    def get_room_members(self, room_id: str) -> Set[str]:
        """Get all members of a room."""
        room = self._rooms.get(room_id)
        return room.members if room else set()

    # ═══════════════════════════════════════════════════════════════════════════
    # PRESENCE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    async def _update_presence(self, user_id: str, status: str, activity: Dict = None) -> None:
        """Update user's presence status."""
        self._presence[user_id] = {
            "status": status,
            "activity": activity,
            "last_seen": datetime.utcnow().isoformat()
        }

        # Broadcast to friends/subscribers (would need friend list integration)
        # For now, broadcast to all rooms user is in
        for conn in self._connections.get(user_id, []):
            for room_id in conn.subscribed_rooms:
                await self.send_to_room(room_id, {
                    "type": MessageType.PRESENCE_UPDATE.value,
                    "user_id": user_id,
                    "status": status,
                    "activity": activity
                }, exclude_user=user_id)

    async def broadcast_presence(self, user_id: str, status: str, activity: Dict = None) -> None:
        """Public method to broadcast presence update."""
        await self._update_presence(user_id, status, activity)

    def get_presence(self, user_id: str) -> Optional[Dict]:
        """Get user's current presence."""
        return self._presence.get(user_id)

    def get_online_users(self) -> List[str]:
        """Get list of all online users."""
        return [
            user_id for user_id, presence in self._presence.items()
            if presence.get("status") == "online"
        ]

    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGE HANDLING
    # ═══════════════════════════════════════════════════════════════════════════

    async def handle_message(self, connection: Connection, message: Dict) -> None:
        """
        Handle an incoming WebSocket message.

        Args:
            connection: The connection that sent the message
            message: The parsed message dictionary
        """
        self._stats["total_messages_received"] += 1

        message_type = message.get("type")

        # Handle ping/pong
        if message_type == MessageType.PING.value:
            connection.last_ping = datetime.utcnow()
            await self.send_to_connection(connection, {"type": MessageType.PONG.value})
            return

        # Call registered handlers
        try:
            msg_type = MessageType(message_type)
            handlers = self._handlers.get(msg_type, [])
            for handler in handlers:
                await handler(connection, message)
        except ValueError:
            logger.warning(f"Unknown message type: {message_type}")
            await self.send_to_connection(connection, {
                "type": MessageType.ERROR.value,
                "error": f"Unknown message type: {message_type}"
            })

    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register a handler for a specific message type."""
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        self._handlers[message_type].append(handler)

    # ═══════════════════════════════════════════════════════════════════════════
    # BACKGROUND TASKS
    # ═══════════════════════════════════════════════════════════════════════════

    async def start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        self._ping_task = asyncio.create_task(self._ping_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_background_tasks(self) -> None:
        """Stop background tasks."""
        if self._ping_task:
            self._ping_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()

    async def _ping_loop(self) -> None:
        """Periodically ping connections to keep them alive."""
        while True:
            try:
                await asyncio.sleep(self._ping_interval)

                for user_id, connections in list(self._connections.items()):
                    for conn in connections:
                        if conn.state == ConnectionState.CONNECTED:
                            await self.send_to_connection(conn, {"type": MessageType.PING.value})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")

    async def _cleanup_loop(self) -> None:
        """Periodically clean up stale connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                now = datetime.utcnow()
                timeout = timedelta(seconds=self._ping_interval + self._ping_timeout)

                for user_id, connections in list(self._connections.items()):
                    for conn in list(connections):
                        if now - conn.last_ping > timeout:
                            logger.info(f"Cleaning up stale connection for {user_id}")
                            await self.disconnect(conn.websocket, user_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # STATISTICS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        return {
            **self._stats,
            "current_connections": sum(len(c) for c in self._connections.values()),
            "unique_users": len(self._connections),
            "online_users": len(self.get_online_users())
        }

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently online."""
        return user_id in self._connections and len(self._connections[user_id]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

# Singleton instance
_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create the global WebSocket manager instance."""
    global _manager
    if _manager is None:
        _manager = WebSocketManager()
    return _manager
