"""
═══════════════════════════════════════════════════════════════════════════════
WATCH PARTY SERVICE - Synchronized Viewing Experience
Enables friends to watch content together in real-time with chat and reactions.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

from .websocket_manager import get_websocket_manager, MessageType

logger = logging.getLogger(__name__)


class PartyState(Enum):
    """Watch party states."""
    LOBBY = "lobby"           # Waiting for members
    STARTING = "starting"     # Countdown before play
    PLAYING = "playing"       # Content is playing
    PAUSED = "paused"         # Content is paused
    ENDED = "ended"           # Party has ended


class SyncEvent(Enum):
    """Synchronization events."""
    PLAY = "play"
    PAUSE = "pause"
    SEEK = "seek"
    BUFFER = "buffer"
    READY = "ready"


@dataclass
class PartyMember:
    """Represents a member in a watch party."""
    user_id: str
    display_name: str
    avatar_url: Optional[str] = None
    joined_at: datetime = field(default_factory=datetime.utcnow)
    is_host: bool = False
    is_ready: bool = False
    playback_position: float = 0.0  # Seconds
    is_buffering: bool = False
    last_sync: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatMessage:
    """A chat message in a watch party."""
    id: str
    user_id: str
    display_name: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    is_system: bool = False


@dataclass
class Reaction:
    """A reaction in a watch party."""
    user_id: str
    emoji: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    position: float = 0.0  # Playback position when reacted


@dataclass
class WatchParty:
    """Represents a watch party session."""
    party_id: str
    host_id: str
    content_id: str
    content_type: str  # "movie", "tv_episode"
    content_title: str
    content_duration: int  # Total duration in seconds

    # State
    state: PartyState = PartyState.LOBBY
    current_position: float = 0.0  # Current playback position
    playback_rate: float = 1.0

    # Members
    members: Dict[str, PartyMember] = field(default_factory=dict)
    max_members: int = 10

    # Chat and reactions
    chat_history: List[ChatMessage] = field(default_factory=list)
    reactions: List[Reaction] = field(default_factory=list)

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    # Settings
    anyone_can_control: bool = False  # If False, only host can play/pause
    invite_code: Optional[str] = None
    is_private: bool = True


class WatchPartyService:
    """
    Manages synchronized watch parties.

    Features:
    - Real-time playback synchronization
    - Chat and reactions
    - Host controls with optional shared control
    - Automatic resync for late joiners
    - Buffer detection and handling
    """

    def __init__(self):
        self._parties: Dict[str, WatchParty] = {}
        self._user_party_map: Dict[str, str] = {}  # user_id -> party_id
        self._invite_codes: Dict[str, str] = {}  # invite_code -> party_id
        self._ws_manager = get_websocket_manager()

        # Register message handlers
        self._register_handlers()

        # Sync settings
        self._max_desync_seconds = 3.0  # Max allowed desync before force resync
        self._sync_interval = 5.0  # Seconds between sync checks

        # Statistics
        self._stats = {
            "total_parties_created": 0,
            "total_messages_sent": 0,
            "total_reactions": 0
        }

    def _register_handlers(self) -> None:
        """Register WebSocket message handlers."""
        self._ws_manager.register_handler(
            MessageType.PARTY_SYNC,
            self._handle_sync_message
        )
        self._ws_manager.register_handler(
            MessageType.PARTY_CHAT,
            self._handle_chat_message
        )
        self._ws_manager.register_handler(
            MessageType.PARTY_REACTION,
            self._handle_reaction
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # PARTY LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════════

    async def create_party(
        self,
        host_id: str,
        host_name: str,
        content_id: str,
        content_type: str,
        content_title: str,
        content_duration: int,
        is_private: bool = True,
        anyone_can_control: bool = False
    ) -> WatchParty:
        """
        Create a new watch party.

        Args:
            host_id: User ID of the party host
            host_name: Display name of the host
            content_id: ID of the content to watch
            content_type: Type of content (movie, tv_episode)
            content_title: Title for display
            content_duration: Total duration in seconds
            is_private: Whether party requires invite code
            anyone_can_control: Whether all members can control playback

        Returns:
            The created WatchParty object
        """
        party_id = f"party_{uuid.uuid4().hex[:12]}"
        invite_code = uuid.uuid4().hex[:8].upper() if is_private else None

        party = WatchParty(
            party_id=party_id,
            host_id=host_id,
            content_id=content_id,
            content_type=content_type,
            content_title=content_title,
            content_duration=content_duration,
            is_private=is_private,
            anyone_can_control=anyone_can_control,
            invite_code=invite_code
        )

        # Add host as first member
        host_member = PartyMember(
            user_id=host_id,
            display_name=host_name,
            is_host=True,
            is_ready=True
        )
        party.members[host_id] = host_member

        # Store party
        self._parties[party_id] = party
        self._user_party_map[host_id] = party_id
        if invite_code:
            self._invite_codes[invite_code] = party_id

        # Create WebSocket room
        await self._ws_manager.create_room(
            room_id=party_id,
            room_type="watch_party",
            metadata={"content_id": content_id, "content_title": content_title}
        )
        await self._ws_manager.join_room(host_id, party_id)

        # Add system message
        await self._add_system_message(party, f"{host_name} created the party")

        self._stats["total_parties_created"] += 1
        logger.info(f"Watch party created: {party_id} by {host_id}")

        return party

    async def join_party(
        self,
        party_id: str = None,
        invite_code: str = None,
        user_id: str = None,
        user_name: str = None,
        avatar_url: str = None
    ) -> Optional[WatchParty]:
        """
        Join an existing watch party.

        Args:
            party_id: Direct party ID (for public parties)
            invite_code: Invite code (for private parties)
            user_id: Joining user's ID
            user_name: Joining user's display name
            avatar_url: User's avatar URL

        Returns:
            The party if joined successfully, None otherwise
        """
        # Resolve party ID from invite code if needed
        if invite_code:
            party_id = self._invite_codes.get(invite_code.upper())

        if not party_id:
            return None

        party = self._parties.get(party_id)
        if not party:
            return None

        # Check if party can be joined
        if party.state == PartyState.ENDED:
            return None

        if len(party.members) >= party.max_members:
            return None

        if user_id in party.members:
            # Already a member, just return party
            return party

        # Add member
        member = PartyMember(
            user_id=user_id,
            display_name=user_name,
            avatar_url=avatar_url
        )
        party.members[user_id] = member
        self._user_party_map[user_id] = party_id

        # Join WebSocket room
        await self._ws_manager.join_room(user_id, party_id)

        # Notify party members
        await self._broadcast_to_party(party, {
            "type": MessageType.PARTY_JOIN.value,
            "user_id": user_id,
            "display_name": user_name,
            "member_count": len(party.members)
        })

        # Add system message
        await self._add_system_message(party, f"{user_name} joined the party")

        # Send current state to new member
        await self._send_party_state(party, user_id)

        logger.info(f"User {user_id} joined party {party_id}")
        return party

    async def leave_party(self, user_id: str) -> bool:
        """Leave the current party."""
        party_id = self._user_party_map.get(user_id)
        if not party_id:
            return False

        party = self._parties.get(party_id)
        if not party:
            return False

        member = party.members.pop(user_id, None)
        if not member:
            return False

        del self._user_party_map[user_id]

        # Leave WebSocket room
        await self._ws_manager.leave_room(user_id, party_id)

        # If host left, assign new host or end party
        if member.is_host:
            if party.members:
                # Assign first remaining member as host
                new_host_id = next(iter(party.members.keys()))
                party.members[new_host_id].is_host = True
                party.host_id = new_host_id
                await self._add_system_message(
                    party,
                    f"{party.members[new_host_id].display_name} is now the host"
                )
            else:
                # No members left, end party
                await self.end_party(party_id)
                return True

        # Notify remaining members
        await self._broadcast_to_party(party, {
            "type": MessageType.PARTY_LEAVE.value,
            "user_id": user_id,
            "display_name": member.display_name,
            "member_count": len(party.members)
        })

        await self._add_system_message(party, f"{member.display_name} left the party")

        logger.info(f"User {user_id} left party {party_id}")
        return True

    async def end_party(self, party_id: str) -> bool:
        """End a watch party."""
        party = self._parties.get(party_id)
        if not party:
            return False

        party.state = PartyState.ENDED
        party.ended_at = datetime.utcnow()

        # Notify all members
        await self._broadcast_to_party(party, {
            "type": "party_ended",
            "party_id": party_id
        })

        # Clean up
        for user_id in list(party.members.keys()):
            self._user_party_map.pop(user_id, None)

        if party.invite_code:
            self._invite_codes.pop(party.invite_code, None)

        await self._ws_manager.delete_room(party_id)
        del self._parties[party_id]

        logger.info(f"Party ended: {party_id}")
        return True

    # ═══════════════════════════════════════════════════════════════════════════
    # PLAYBACK CONTROL
    # ═══════════════════════════════════════════════════════════════════════════

    async def play(self, user_id: str) -> bool:
        """Start/resume playback."""
        party = self._get_user_party(user_id)
        if not party or not self._can_control(party, user_id):
            return False

        if party.state not in [PartyState.LOBBY, PartyState.PAUSED]:
            return False

        if party.state == PartyState.LOBBY:
            # Start from beginning
            party.started_at = datetime.utcnow()

        party.state = PartyState.PLAYING

        await self._broadcast_sync(party, SyncEvent.PLAY, user_id)
        return True

    async def pause(self, user_id: str) -> bool:
        """Pause playback."""
        party = self._get_user_party(user_id)
        if not party or not self._can_control(party, user_id):
            return False

        if party.state != PartyState.PLAYING:
            return False

        party.state = PartyState.PAUSED

        await self._broadcast_sync(party, SyncEvent.PAUSE, user_id)
        return True

    async def seek(self, user_id: str, position: float) -> bool:
        """Seek to a specific position."""
        party = self._get_user_party(user_id)
        if not party or not self._can_control(party, user_id):
            return False

        # Clamp position
        position = max(0, min(position, party.content_duration))
        party.current_position = position

        await self._broadcast_sync(party, SyncEvent.SEEK, user_id, position=position)
        return True

    async def report_position(self, user_id: str, position: float, is_buffering: bool = False) -> None:
        """Report current playback position (for sync tracking)."""
        party = self._get_user_party(user_id)
        if not party:
            return

        member = party.members.get(user_id)
        if not member:
            return

        member.playback_position = position
        member.is_buffering = is_buffering
        member.last_sync = datetime.utcnow()

        # Check if significantly desynced
        if party.state == PartyState.PLAYING:
            desync = abs(position - party.current_position)
            if desync > self._max_desync_seconds and not is_buffering:
                # Force resync
                await self._ws_manager.send_to_user(user_id, {
                    "type": MessageType.PARTY_SYNC.value,
                    "event": SyncEvent.SEEK.value,
                    "position": party.current_position,
                    "reason": "resync"
                })

    async def set_ready(self, user_id: str, is_ready: bool) -> bool:
        """Set member's ready status (for starting playback)."""
        party = self._get_user_party(user_id)
        if not party:
            return False

        member = party.members.get(user_id)
        if not member:
            return False

        member.is_ready = is_ready

        # Notify party
        await self._broadcast_to_party(party, {
            "type": "member_ready",
            "user_id": user_id,
            "is_ready": is_ready,
            "all_ready": all(m.is_ready for m in party.members.values())
        })

        return True

    def _can_control(self, party: WatchParty, user_id: str) -> bool:
        """Check if user can control playback."""
        if party.anyone_can_control:
            return user_id in party.members
        return user_id == party.host_id

    async def _broadcast_sync(
        self,
        party: WatchParty,
        event: SyncEvent,
        initiated_by: str,
        position: float = None
    ) -> None:
        """Broadcast a sync event to all party members."""
        message = {
            "type": MessageType.PARTY_SYNC.value,
            "event": event.value,
            "state": party.state.value,
            "position": position if position is not None else party.current_position,
            "initiated_by": initiated_by,
            "timestamp": datetime.utcnow().isoformat()
        }

        await self._broadcast_to_party(party, message)

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAT AND REACTIONS
    # ═══════════════════════════════════════════════════════════════════════════

    async def send_chat(self, user_id: str, content: str) -> Optional[ChatMessage]:
        """Send a chat message."""
        party = self._get_user_party(user_id)
        if not party:
            return None

        member = party.members.get(user_id)
        if not member:
            return None

        # Sanitize content
        content = content[:500]  # Max 500 chars

        message = ChatMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            display_name=member.display_name,
            content=content
        )

        party.chat_history.append(message)

        # Keep only last 100 messages
        if len(party.chat_history) > 100:
            party.chat_history = party.chat_history[-100:]

        # Broadcast to party
        await self._broadcast_to_party(party, {
            "type": MessageType.PARTY_CHAT.value,
            "message": {
                "id": message.id,
                "user_id": message.user_id,
                "display_name": message.display_name,
                "content": message.content,
                "timestamp": message.timestamp.isoformat()
            }
        })

        self._stats["total_messages_sent"] += 1
        return message

    async def send_reaction(self, user_id: str, emoji: str) -> Optional[Reaction]:
        """Send a reaction."""
        party = self._get_user_party(user_id)
        if not party:
            return None

        # Validate emoji (allow standard emojis)
        if len(emoji) > 4:  # Max 4 chars for emoji
            return None

        reaction = Reaction(
            user_id=user_id,
            emoji=emoji,
            position=party.current_position
        )

        party.reactions.append(reaction)

        # Broadcast to party
        await self._broadcast_to_party(party, {
            "type": MessageType.PARTY_REACTION.value,
            "reaction": {
                "user_id": user_id,
                "emoji": emoji,
                "position": reaction.position,
                "timestamp": reaction.timestamp.isoformat()
            }
        })

        self._stats["total_reactions"] += 1
        return reaction

    async def _add_system_message(self, party: WatchParty, content: str) -> None:
        """Add a system message to chat."""
        message = ChatMessage(
            id=f"sys_{uuid.uuid4().hex[:8]}",
            user_id="system",
            display_name="System",
            content=content,
            is_system=True
        )
        party.chat_history.append(message)

        await self._broadcast_to_party(party, {
            "type": MessageType.PARTY_CHAT.value,
            "message": {
                "id": message.id,
                "user_id": "system",
                "display_name": "System",
                "content": content,
                "is_system": True,
                "timestamp": message.timestamp.isoformat()
            }
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def _handle_sync_message(self, connection, message: Dict) -> None:
        """Handle sync messages from clients."""
        user_id = connection.user_id
        event = message.get("event")
        position = message.get("position", 0)

        if event == SyncEvent.PLAY.value:
            await self.play(user_id)
        elif event == SyncEvent.PAUSE.value:
            await self.pause(user_id)
        elif event == SyncEvent.SEEK.value:
            await self.seek(user_id, position)
        elif event == SyncEvent.READY.value:
            await self.set_ready(user_id, message.get("is_ready", True))
        elif event == SyncEvent.BUFFER.value:
            await self.report_position(user_id, position, is_buffering=True)

    async def _handle_chat_message(self, connection, message: Dict) -> None:
        """Handle chat messages from clients."""
        content = message.get("content", "")
        if content:
            await self.send_chat(connection.user_id, content)

    async def _handle_reaction(self, connection, message: Dict) -> None:
        """Handle reactions from clients."""
        emoji = message.get("emoji", "")
        if emoji:
            await self.send_reaction(connection.user_id, emoji)

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════════

    def _get_user_party(self, user_id: str) -> Optional[WatchParty]:
        """Get the party a user is currently in."""
        party_id = self._user_party_map.get(user_id)
        return self._parties.get(party_id) if party_id else None

    async def _broadcast_to_party(self, party: WatchParty, message: Dict) -> None:
        """Broadcast a message to all party members."""
        message["party_id"] = party.party_id
        await self._ws_manager.send_to_room(party.party_id, message)

    async def _send_party_state(self, party: WatchParty, user_id: str) -> None:
        """Send full party state to a specific user."""
        members_data = [
            {
                "user_id": m.user_id,
                "display_name": m.display_name,
                "avatar_url": m.avatar_url,
                "is_host": m.is_host,
                "is_ready": m.is_ready
            }
            for m in party.members.values()
        ]

        chat_data = [
            {
                "id": m.id,
                "user_id": m.user_id,
                "display_name": m.display_name,
                "content": m.content,
                "is_system": m.is_system,
                "timestamp": m.timestamp.isoformat()
            }
            for m in party.chat_history[-50:]  # Last 50 messages
        ]

        state_message = {
            "type": "party_state",
            "party": {
                "party_id": party.party_id,
                "content_id": party.content_id,
                "content_type": party.content_type,
                "content_title": party.content_title,
                "content_duration": party.content_duration,
                "state": party.state.value,
                "current_position": party.current_position,
                "host_id": party.host_id,
                "anyone_can_control": party.anyone_can_control,
                "members": members_data,
                "chat_history": chat_data,
                "invite_code": party.invite_code if party.host_id == user_id else None
            }
        }

        await self._ws_manager.send_to_user(user_id, state_message)

    def get_party(self, party_id: str) -> Optional[WatchParty]:
        """Get a party by ID."""
        return self._parties.get(party_id)

    def get_party_by_invite(self, invite_code: str) -> Optional[WatchParty]:
        """Get a party by invite code."""
        party_id = self._invite_codes.get(invite_code.upper())
        return self._parties.get(party_id) if party_id else None

    def get_user_current_party(self, user_id: str) -> Optional[WatchParty]:
        """Get the party a user is currently in."""
        return self._get_user_party(user_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self._stats,
            "active_parties": len(self._parties),
            "total_members": sum(len(p.members) for p in self._parties.values())
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_service: Optional[WatchPartyService] = None


def get_watch_party_service() -> WatchPartyService:
    """Get or create the global watch party service instance."""
    global _service
    if _service is None:
        _service = WatchPartyService()
    return _service
