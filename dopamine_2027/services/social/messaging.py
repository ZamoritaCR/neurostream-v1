"""
═══════════════════════════════════════════════════════════════════════════════
DIRECT MESSAGING SERVICE
Real-time messaging between users with typing indicators and read receipts.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
import logging

from services.realtime.websocket_manager import get_websocket_manager, MessageType

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Message delivery status."""
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ConversationType(Enum):
    """Type of conversation."""
    DIRECT = "direct"       # 1-on-1 chat
    GROUP = "group"         # Group chat


@dataclass
class Message:
    """A direct message."""
    id: str
    conversation_id: str
    sender_id: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.SENT
    read_by: Set[str] = field(default_factory=set)
    reply_to_id: Optional[str] = None
    edited_at: Optional[datetime] = None
    attachments: List[Dict] = field(default_factory=list)
    reactions: Dict[str, List[str]] = field(default_factory=dict)  # emoji -> [user_ids]


@dataclass
class Conversation:
    """A conversation between users."""
    id: str
    type: ConversationType
    participants: Set[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_message: Optional[Message] = None
    messages: List[Message] = field(default_factory=list)
    typing_users: Dict[str, datetime] = field(default_factory=dict)  # user_id -> last_typing_time
    muted_by: Set[str] = field(default_factory=set)
    name: Optional[str] = None  # For group chats
    avatar_url: Optional[str] = None  # For group chats


class DirectMessagingService:
    """
    Manages direct messaging between users.

    Features:
    - 1-on-1 and group conversations
    - Real-time message delivery
    - Typing indicators
    - Read receipts
    - Message reactions
    - Reply threading
    """

    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}
        self._user_conversations: Dict[str, Set[str]] = {}  # user_id -> conversation_ids
        self._dm_lookup: Dict[str, str] = {}  # "user1:user2" -> conversation_id
        self._ws_manager = get_websocket_manager()

        # Register message handlers
        self._register_handlers()

        # Typing indicator timeout
        self._typing_timeout = 5  # seconds

        # Statistics
        self._stats = {
            "total_messages": 0,
            "total_conversations": 0
        }

    def _register_handlers(self) -> None:
        """Register WebSocket message handlers."""
        self._ws_manager.register_handler(
            MessageType.DM_SEND,
            self._handle_send_message
        )
        self._ws_manager.register_handler(
            MessageType.DM_TYPING,
            self._handle_typing
        )
        self._ws_manager.register_handler(
            MessageType.DM_READ,
            self._handle_read_receipt
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # CONVERSATION MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_or_create_dm(self, user1_id: str, user2_id: str) -> Conversation:
        """
        Get existing DM conversation or create new one.

        Args:
            user1_id: First user's ID
            user2_id: Second user's ID

        Returns:
            The DM conversation
        """
        # Create consistent lookup key
        key = ":".join(sorted([user1_id, user2_id]))

        if key in self._dm_lookup:
            return self._conversations[self._dm_lookup[key]]

        # Create new conversation
        conversation = Conversation(
            id=f"dm_{uuid.uuid4().hex[:12]}",
            type=ConversationType.DIRECT,
            participants={user1_id, user2_id}
        )

        self._conversations[conversation.id] = conversation
        self._dm_lookup[key] = conversation.id

        # Add to user's conversation lists
        for user_id in [user1_id, user2_id]:
            if user_id not in self._user_conversations:
                self._user_conversations[user_id] = set()
            self._user_conversations[user_id].add(conversation.id)

        self._stats["total_conversations"] += 1
        logger.info(f"Created DM conversation: {conversation.id}")

        return conversation

    async def create_group(
        self,
        creator_id: str,
        participant_ids: List[str],
        name: str = None,
        avatar_url: str = None
    ) -> Conversation:
        """
        Create a group conversation.

        Args:
            creator_id: User creating the group
            participant_ids: Other participants
            name: Group name
            avatar_url: Group avatar

        Returns:
            The group conversation
        """
        all_participants = set(participant_ids) | {creator_id}

        conversation = Conversation(
            id=f"group_{uuid.uuid4().hex[:12]}",
            type=ConversationType.GROUP,
            participants=all_participants,
            name=name or f"Group ({len(all_participants)})",
            avatar_url=avatar_url
        )

        self._conversations[conversation.id] = conversation

        # Add to participants' conversation lists
        for user_id in all_participants:
            if user_id not in self._user_conversations:
                self._user_conversations[user_id] = set()
            self._user_conversations[user_id].add(conversation.id)

        # Create WebSocket room
        await self._ws_manager.create_room(
            room_id=conversation.id,
            room_type="group_chat",
            metadata={"name": conversation.name}
        )

        # Join all participants
        for user_id in all_participants:
            await self._ws_manager.join_room(user_id, conversation.id)

        self._stats["total_conversations"] += 1
        logger.info(f"Created group conversation: {conversation.id}")

        return conversation

    async def add_to_group(
        self,
        conversation_id: str,
        user_id: str,
        added_by: str
    ) -> bool:
        """Add a user to a group conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or conversation.type != ConversationType.GROUP:
            return False

        if added_by not in conversation.participants:
            return False

        conversation.participants.add(user_id)

        if user_id not in self._user_conversations:
            self._user_conversations[user_id] = set()
        self._user_conversations[user_id].add(conversation_id)

        await self._ws_manager.join_room(user_id, conversation_id)

        # Send system message
        await self._send_system_message(
            conversation_id,
            f"User joined the group"
        )

        return True

    async def leave_group(self, conversation_id: str, user_id: str) -> bool:
        """Leave a group conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or conversation.type != ConversationType.GROUP:
            return False

        if user_id not in conversation.participants:
            return False

        conversation.participants.discard(user_id)
        self._user_conversations.get(user_id, set()).discard(conversation_id)

        await self._ws_manager.leave_room(user_id, conversation_id)

        # Send system message
        await self._send_system_message(
            conversation_id,
            f"User left the group"
        )

        return True

    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user."""
        conversation_ids = self._user_conversations.get(user_id, set())
        conversations = [
            self._conversations[cid]
            for cid in conversation_ids
            if cid in self._conversations
        ]

        # Sort by last message time
        conversations.sort(
            key=lambda c: c.updated_at,
            reverse=True
        )

        return conversations

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)

    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGING
    # ═══════════════════════════════════════════════════════════════════════════

    async def send_message(
        self,
        conversation_id: str,
        sender_id: str,
        content: str,
        reply_to_id: str = None,
        attachments: List[Dict] = None
    ) -> Optional[Message]:
        """
        Send a message to a conversation.

        Args:
            conversation_id: Target conversation
            sender_id: Sender's user ID
            content: Message content
            reply_to_id: Optional message ID to reply to
            attachments: Optional attachments

        Returns:
            The sent message, or None if failed
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return None

        if sender_id not in conversation.participants:
            return None

        # Sanitize content
        content = content[:4000]  # Max 4000 chars

        message = Message(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            reply_to_id=reply_to_id,
            attachments=attachments or []
        )

        # Add to conversation
        conversation.messages.append(message)
        conversation.last_message = message
        conversation.updated_at = datetime.utcnow()

        # Keep only last 1000 messages in memory
        if len(conversation.messages) > 1000:
            conversation.messages = conversation.messages[-1000:]

        # Clear typing indicator
        conversation.typing_users.pop(sender_id, None)

        # Broadcast to all participants
        await self._broadcast_message(conversation, message)

        self._stats["total_messages"] += 1
        return message

    async def edit_message(
        self,
        message_id: str,
        user_id: str,
        new_content: str
    ) -> Optional[Message]:
        """Edit a message (only by sender)."""
        message = self._find_message(message_id)
        if not message or message.sender_id != user_id:
            return None

        message.content = new_content[:4000]
        message.edited_at = datetime.utcnow()

        conversation = self._conversations.get(message.conversation_id)
        if conversation:
            await self._broadcast_to_conversation(
                conversation,
                {
                    "type": "message_edited",
                    "message_id": message_id,
                    "content": message.content,
                    "edited_at": message.edited_at.isoformat()
                }
            )

        return message

    async def delete_message(self, message_id: str, user_id: str) -> bool:
        """Delete a message (only by sender)."""
        message = self._find_message(message_id)
        if not message or message.sender_id != user_id:
            return False

        conversation = self._conversations.get(message.conversation_id)
        if conversation:
            conversation.messages = [
                m for m in conversation.messages
                if m.id != message_id
            ]

            await self._broadcast_to_conversation(
                conversation,
                {
                    "type": "message_deleted",
                    "message_id": message_id
                }
            )

        return True

    async def add_reaction(
        self,
        message_id: str,
        user_id: str,
        emoji: str
    ) -> bool:
        """Add a reaction to a message."""
        message = self._find_message(message_id)
        if not message:
            return False

        if len(emoji) > 4:  # Validate emoji length
            return False

        if emoji not in message.reactions:
            message.reactions[emoji] = []

        if user_id not in message.reactions[emoji]:
            message.reactions[emoji].append(user_id)

        conversation = self._conversations.get(message.conversation_id)
        if conversation:
            await self._broadcast_to_conversation(
                conversation,
                {
                    "type": "reaction_added",
                    "message_id": message_id,
                    "user_id": user_id,
                    "emoji": emoji
                }
            )

        return True

    async def remove_reaction(
        self,
        message_id: str,
        user_id: str,
        emoji: str
    ) -> bool:
        """Remove a reaction from a message."""
        message = self._find_message(message_id)
        if not message:
            return False

        if emoji in message.reactions and user_id in message.reactions[emoji]:
            message.reactions[emoji].remove(user_id)
            if not message.reactions[emoji]:
                del message.reactions[emoji]

            conversation = self._conversations.get(message.conversation_id)
            if conversation:
                await self._broadcast_to_conversation(
                    conversation,
                    {
                        "type": "reaction_removed",
                        "message_id": message_id,
                        "user_id": user_id,
                        "emoji": emoji
                    }
                )

            return True

        return False

    def _find_message(self, message_id: str) -> Optional[Message]:
        """Find a message by ID."""
        for conversation in self._conversations.values():
            for message in conversation.messages:
                if message.id == message_id:
                    return message
        return None

    # ═══════════════════════════════════════════════════════════════════════════
    # TYPING INDICATORS
    # ═══════════════════════════════════════════════════════════════════════════

    async def set_typing(self, conversation_id: str, user_id: str, is_typing: bool) -> None:
        """Set user's typing status."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or user_id not in conversation.participants:
            return

        if is_typing:
            conversation.typing_users[user_id] = datetime.utcnow()
        else:
            conversation.typing_users.pop(user_id, None)

        # Broadcast to other participants
        await self._broadcast_to_conversation(
            conversation,
            {
                "type": MessageType.DM_TYPING.value,
                "user_id": user_id,
                "is_typing": is_typing
            },
            exclude_user=user_id
        )

    def get_typing_users(self, conversation_id: str) -> List[str]:
        """Get list of currently typing users."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return []

        now = datetime.utcnow()
        timeout = timedelta(seconds=self._typing_timeout)

        # Filter out stale typing indicators
        typing = [
            user_id
            for user_id, last_time in conversation.typing_users.items()
            if now - last_time < timeout
        ]

        return typing

    # ═══════════════════════════════════════════════════════════════════════════
    # READ RECEIPTS
    # ═══════════════════════════════════════════════════════════════════════════

    async def mark_as_read(
        self,
        conversation_id: str,
        user_id: str,
        up_to_message_id: str = None
    ) -> int:
        """
        Mark messages as read.

        Args:
            conversation_id: Conversation to mark
            user_id: User marking as read
            up_to_message_id: Mark all messages up to this ID (or all if None)

        Returns:
            Number of messages marked as read
        """
        conversation = self._conversations.get(conversation_id)
        if not conversation or user_id not in conversation.participants:
            return 0

        marked_count = 0
        found_target = up_to_message_id is None

        for message in conversation.messages:
            if message.id == up_to_message_id:
                found_target = True

            if found_target or not up_to_message_id:
                if message.sender_id != user_id and user_id not in message.read_by:
                    message.read_by.add(user_id)
                    marked_count += 1

                    # Check if all participants have read
                    if message.read_by >= (conversation.participants - {message.sender_id}):
                        message.status = MessageStatus.READ

            if message.id == up_to_message_id:
                break

        # Broadcast read receipt
        if marked_count > 0:
            await self._broadcast_to_conversation(
                conversation,
                {
                    "type": MessageType.DM_READ.value,
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "up_to_message_id": up_to_message_id
                },
                exclude_user=user_id
            )

        return marked_count

    def get_unread_count(self, conversation_id: str, user_id: str) -> int:
        """Get number of unread messages for a user."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return 0

        return sum(
            1 for msg in conversation.messages
            if msg.sender_id != user_id and user_id not in msg.read_by
        )

    def get_total_unread_count(self, user_id: str) -> int:
        """Get total unread messages across all conversations."""
        conversation_ids = self._user_conversations.get(user_id, set())
        return sum(
            self.get_unread_count(cid, user_id)
            for cid in conversation_ids
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MESSAGE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def _handle_send_message(self, connection, message: Dict) -> None:
        """Handle incoming message from WebSocket."""
        conversation_id = message.get("conversation_id")
        content = message.get("content", "")
        reply_to = message.get("reply_to_id")

        if content:
            await self.send_message(
                conversation_id,
                connection.user_id,
                content,
                reply_to_id=reply_to
            )

    async def _handle_typing(self, connection, message: Dict) -> None:
        """Handle typing indicator from WebSocket."""
        conversation_id = message.get("conversation_id")
        is_typing = message.get("is_typing", True)

        await self.set_typing(conversation_id, connection.user_id, is_typing)

    async def _handle_read_receipt(self, connection, message: Dict) -> None:
        """Handle read receipt from WebSocket."""
        conversation_id = message.get("conversation_id")
        up_to_message_id = message.get("up_to_message_id")

        await self.mark_as_read(
            conversation_id,
            connection.user_id,
            up_to_message_id
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def _broadcast_message(self, conversation: Conversation, message: Message) -> None:
        """Broadcast a new message to conversation participants."""
        message_data = {
            "type": MessageType.DM_SEND.value,
            "conversation_id": conversation.id,
            "message": {
                "id": message.id,
                "sender_id": message.sender_id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "reply_to_id": message.reply_to_id,
                "attachments": message.attachments
            }
        }

        await self._broadcast_to_conversation(
            conversation,
            message_data,
            exclude_user=message.sender_id
        )

    async def _broadcast_to_conversation(
        self,
        conversation: Conversation,
        message: Dict,
        exclude_user: str = None
    ) -> None:
        """Broadcast message to all participants in a conversation."""
        message["conversation_id"] = conversation.id

        for user_id in conversation.participants:
            if user_id != exclude_user:
                # Skip if muted (except for actual messages)
                if user_id in conversation.muted_by and message.get("type") != MessageType.DM_SEND.value:
                    continue

                await self._ws_manager.send_to_user(user_id, message)

    async def _send_system_message(self, conversation_id: str, content: str) -> None:
        """Send a system message to a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return

        message = Message(
            id=f"sys_{uuid.uuid4().hex[:8]}",
            conversation_id=conversation_id,
            sender_id="system",
            content=content
        )

        conversation.messages.append(message)

        await self._broadcast_to_conversation(
            conversation,
            {
                "type": MessageType.DM_SEND.value,
                "message": {
                    "id": message.id,
                    "sender_id": "system",
                    "content": content,
                    "is_system": True,
                    "created_at": message.created_at.isoformat()
                }
            }
        )

    async def mute_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Mute notifications for a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation or user_id not in conversation.participants:
            return False

        conversation.muted_by.add(user_id)
        return True

    async def unmute_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Unmute notifications for a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False

        conversation.muted_by.discard(user_id)
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            **self._stats,
            "active_conversations": len(self._conversations)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_service: Optional[DirectMessagingService] = None


def get_messaging_service() -> DirectMessagingService:
    """Get or create the global messaging service instance."""
    global _service
    if _service is None:
        _service = DirectMessagingService()
    return _service
