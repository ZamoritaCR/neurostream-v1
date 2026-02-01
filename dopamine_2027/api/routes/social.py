"""
═══════════════════════════════════════════════════════════════════════════════
SOCIAL API ROUTES
Watch parties, messaging, and social features.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from services.realtime.watch_party import get_watch_party_service, PartyState
from services.social.messaging import get_messaging_service

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class CreatePartyRequest(BaseModel):
    host_id: str
    host_name: str
    content_id: str
    content_type: str
    content_title: str
    content_duration: int  # seconds
    is_private: bool = True
    anyone_can_control: bool = False


class JoinPartyRequest(BaseModel):
    user_id: str
    user_name: str
    party_id: Optional[str] = None
    invite_code: Optional[str] = None
    avatar_url: Optional[str] = None


class SendMessageRequest(BaseModel):
    conversation_id: str
    sender_id: str
    content: str
    reply_to_id: Optional[str] = None


class CreateGroupRequest(BaseModel):
    creator_id: str
    participant_ids: List[str]
    name: Optional[str] = None
    avatar_url: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# WATCH PARTY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/party/create")
async def create_watch_party(request: CreatePartyRequest):
    """
    Create a new watch party.

    Returns party details including invite code for private parties.
    """
    service = get_watch_party_service()

    party = await service.create_party(
        host_id=request.host_id,
        host_name=request.host_name,
        content_id=request.content_id,
        content_type=request.content_type,
        content_title=request.content_title,
        content_duration=request.content_duration,
        is_private=request.is_private,
        anyone_can_control=request.anyone_can_control
    )

    return {
        "party_id": party.party_id,
        "invite_code": party.invite_code,
        "content_title": party.content_title,
        "state": party.state.value,
        "max_members": party.max_members
    }


@router.post("/party/join")
async def join_watch_party(request: JoinPartyRequest):
    """
    Join an existing watch party.

    Can join by party_id (public) or invite_code (private).
    """
    service = get_watch_party_service()

    party = await service.join_party(
        party_id=request.party_id,
        invite_code=request.invite_code,
        user_id=request.user_id,
        user_name=request.user_name,
        avatar_url=request.avatar_url
    )

    if not party:
        raise HTTPException(status_code=404, detail="Party not found or cannot be joined")

    return {
        "party_id": party.party_id,
        "content_title": party.content_title,
        "state": party.state.value,
        "member_count": len(party.members),
        "host_id": party.host_id
    }


@router.post("/party/{party_id}/leave")
async def leave_watch_party(party_id: str, user_id: str):
    """Leave a watch party."""
    service = get_watch_party_service()

    success = await service.leave_party(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Could not leave party")

    return {"status": "left", "party_id": party_id}


@router.get("/party/{party_id}")
async def get_party_info(party_id: str):
    """Get watch party information."""
    service = get_watch_party_service()

    party = service.get_party(party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")

    return {
        "party_id": party.party_id,
        "content_id": party.content_id,
        "content_title": party.content_title,
        "content_type": party.content_type,
        "state": party.state.value,
        "current_position": party.current_position,
        "member_count": len(party.members),
        "host_id": party.host_id,
        "anyone_can_control": party.anyone_can_control,
        "members": [
            {
                "user_id": m.user_id,
                "display_name": m.display_name,
                "is_host": m.is_host,
                "is_ready": m.is_ready
            }
            for m in party.members.values()
        ]
    }


@router.post("/party/{party_id}/control")
async def party_control(
    party_id: str,
    user_id: str,
    action: str = Query(..., description="play, pause, seek"),
    position: Optional[float] = Query(None, description="Seek position in seconds")
):
    """
    Control watch party playback.

    Actions: play, pause, seek
    """
    service = get_watch_party_service()

    if action == "play":
        success = await service.play(user_id)
    elif action == "pause":
        success = await service.pause(user_id)
    elif action == "seek" and position is not None:
        success = await service.seek(user_id, position)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    if not success:
        raise HTTPException(status_code=403, detail="Cannot control playback")

    return {"status": "ok", "action": action}


@router.post("/party/{party_id}/chat")
async def party_chat(party_id: str, user_id: str, content: str):
    """Send a chat message in watch party."""
    service = get_watch_party_service()

    message = await service.send_chat(user_id, content)
    if not message:
        raise HTTPException(status_code=400, detail="Could not send message")

    return {
        "message_id": message.id,
        "content": message.content,
        "timestamp": message.timestamp.isoformat()
    }


@router.post("/party/{party_id}/reaction")
async def party_reaction(party_id: str, user_id: str, emoji: str):
    """Send a reaction in watch party."""
    service = get_watch_party_service()

    reaction = await service.send_reaction(user_id, emoji)
    if not reaction:
        raise HTTPException(status_code=400, detail="Could not send reaction")

    return {"status": "sent", "emoji": emoji}


# ═══════════════════════════════════════════════════════════════════════════════
# DIRECT MESSAGING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/dm/start")
async def start_dm(user1_id: str, user2_id: str):
    """Start or get existing DM conversation."""
    service = get_messaging_service()

    conversation = await service.get_or_create_dm(user1_id, user2_id)

    return {
        "conversation_id": conversation.id,
        "type": conversation.type.value,
        "participants": list(conversation.participants)
    }


@router.post("/group/create")
async def create_group(request: CreateGroupRequest):
    """Create a group conversation."""
    service = get_messaging_service()

    conversation = await service.create_group(
        creator_id=request.creator_id,
        participant_ids=request.participant_ids,
        name=request.name,
        avatar_url=request.avatar_url
    )

    return {
        "conversation_id": conversation.id,
        "name": conversation.name,
        "type": conversation.type.value,
        "participants": list(conversation.participants)
    }


@router.post("/message/send")
async def send_message(request: SendMessageRequest):
    """Send a direct message."""
    service = get_messaging_service()

    message = await service.send_message(
        conversation_id=request.conversation_id,
        sender_id=request.sender_id,
        content=request.content,
        reply_to_id=request.reply_to_id
    )

    if not message:
        raise HTTPException(status_code=400, detail="Could not send message")

    return {
        "message_id": message.id,
        "content": message.content,
        "created_at": message.created_at.isoformat()
    }


@router.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get all conversations for a user."""
    service = get_messaging_service()

    conversations = service.get_user_conversations(user_id)

    return {
        "conversations": [
            {
                "id": c.id,
                "type": c.type.value,
                "name": c.name,
                "participants": list(c.participants),
                "last_message": {
                    "content": c.last_message.content[:50] if c.last_message else None,
                    "timestamp": c.last_message.created_at.isoformat() if c.last_message else None
                },
                "unread_count": service.get_unread_count(c.id, user_id)
            }
            for c in conversations
        ],
        "total_unread": service.get_total_unread_count(user_id)
    }


@router.get("/conversation/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get messages from a conversation."""
    service = get_messaging_service()

    conversation = service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = conversation.messages[-(offset + limit):-offset if offset else None]

    return {
        "messages": [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
                "status": m.status.value,
                "reply_to_id": m.reply_to_id,
                "reactions": m.reactions
            }
            for m in messages
        ],
        "total": len(conversation.messages)
    }


@router.post("/conversation/{conversation_id}/read")
async def mark_as_read(conversation_id: str, user_id: str, up_to_message_id: Optional[str] = None):
    """Mark messages as read."""
    service = get_messaging_service()

    count = await service.mark_as_read(conversation_id, user_id, up_to_message_id)

    return {"marked_read": count}


@router.post("/conversation/{conversation_id}/typing")
async def set_typing(conversation_id: str, user_id: str, is_typing: bool = True):
    """Set typing indicator."""
    service = get_messaging_service()

    await service.set_typing(conversation_id, user_id, is_typing)

    return {"status": "ok"}


@router.post("/message/{message_id}/reaction")
async def add_message_reaction(message_id: str, user_id: str, emoji: str):
    """Add reaction to a message."""
    service = get_messaging_service()

    success = await service.add_reaction(message_id, user_id, emoji)
    if not success:
        raise HTTPException(status_code=400, detail="Could not add reaction")

    return {"status": "added", "emoji": emoji}
