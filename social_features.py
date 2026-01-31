# social_features.py
# --------------------------------------------------
# DOPAMINE.WATCH - SOCIAL FEATURES
# --------------------------------------------------
# Features:
# 1. Watch Parties (synchronized viewing)
# 2. Direct Messaging
# 3. Friend System
# 4. Share & Referral
# 5. Social Feed
# --------------------------------------------------

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random
import string
import hashlib

# --------------------------------------------------
# 1. WATCH PARTIES
# --------------------------------------------------

@dataclass
class WatchParty:
    """Watch party session."""
    party_id: str
    host_id: str
    host_name: str
    content_id: str
    content_title: str
    content_type: str
    content_image: Optional[str] = None
    state: str = "lobby"  # lobby, playing, paused, ended
    current_position: float = 0  # seconds
    members: List[Dict] = field(default_factory=list)
    chat_messages: List[Dict] = field(default_factory=list)
    invite_code: str = ""
    is_private: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None


def _get_parties_storage() -> Dict[str, WatchParty]:
    """Get watch parties storage."""
    if 'watch_parties' not in st.session_state:
        st.session_state.watch_parties = {}
    return st.session_state.watch_parties


def _generate_invite_code() -> str:
    """Generate a unique invite code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_watch_party(
    host_id: str,
    host_name: str,
    content_id: str,
    content_title: str,
    content_type: str = "movie",
    content_image: Optional[str] = None,
    is_private: bool = True
) -> Dict:
    """Create a new watch party."""
    storage = _get_parties_storage()

    party_id = hashlib.md5(f"{host_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    invite_code = _generate_invite_code()

    party = WatchParty(
        party_id=party_id,
        host_id=host_id,
        host_name=host_name,
        content_id=content_id,
        content_title=content_title,
        content_type=content_type,
        content_image=content_image,
        invite_code=invite_code,
        is_private=is_private,
        members=[{"user_id": host_id, "name": host_name, "is_host": True, "joined_at": datetime.now().isoformat()}]
    )

    storage[party_id] = party

    return {
        "party_id": party_id,
        "invite_code": invite_code,
        "invite_link": f"https://dopamine.watch/party/{invite_code}",
        "content_title": content_title
    }


def join_watch_party(
    party_id: str = None,
    invite_code: str = None,
    user_id: str = None,
    user_name: str = "Guest"
) -> Optional[Dict]:
    """Join a watch party."""
    storage = _get_parties_storage()

    # Find party by ID or invite code
    party = None
    if party_id and party_id in storage:
        party = storage[party_id]
    elif invite_code:
        for p in storage.values():
            if p.invite_code == invite_code:
                party = p
                break

    if not party:
        return None

    # Check if already a member
    for member in party.members:
        if member["user_id"] == user_id:
            return {"party_id": party.party_id, "status": "already_member"}

    # Add member
    party.members.append({
        "user_id": user_id,
        "name": user_name,
        "is_host": False,
        "joined_at": datetime.now().isoformat()
    })

    # Add system message
    party.chat_messages.append({
        "type": "system",
        "content": f"{user_name} joined the party!",
        "timestamp": datetime.now().isoformat()
    })

    return {
        "party_id": party.party_id,
        "content_title": party.content_title,
        "host_name": party.host_name,
        "member_count": len(party.members)
    }


def leave_watch_party(party_id: str, user_id: str) -> bool:
    """Leave a watch party."""
    storage = _get_parties_storage()

    if party_id not in storage:
        return False

    party = storage[party_id]

    # Find and remove member
    for i, member in enumerate(party.members):
        if member["user_id"] == user_id:
            name = member["name"]
            party.members.pop(i)
            party.chat_messages.append({
                "type": "system",
                "content": f"{name} left the party",
                "timestamp": datetime.now().isoformat()
            })
            break

    # If host left, end party or transfer host
    if user_id == party.host_id:
        if party.members:
            party.members[0]["is_host"] = True
            party.host_id = party.members[0]["user_id"]
            party.host_name = party.members[0]["name"]
        else:
            party.state = "ended"

    return True


def send_party_message(party_id: str, user_id: str, user_name: str, content: str) -> Optional[Dict]:
    """Send a chat message in watch party."""
    storage = _get_parties_storage()

    if party_id not in storage:
        return None

    party = storage[party_id]

    message = {
        "type": "chat",
        "user_id": user_id,
        "user_name": user_name,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }

    party.chat_messages.append(message)

    # Keep only last 100 messages
    if len(party.chat_messages) > 100:
        party.chat_messages = party.chat_messages[-100:]

    return message


def send_party_reaction(party_id: str, user_id: str, user_name: str, emoji: str) -> Optional[Dict]:
    """Send a reaction in watch party."""
    storage = _get_parties_storage()

    if party_id not in storage:
        return None

    party = storage[party_id]

    reaction = {
        "type": "reaction",
        "user_id": user_id,
        "user_name": user_name,
        "emoji": emoji,
        "timestamp": datetime.now().isoformat()
    }

    party.chat_messages.append(reaction)
    return reaction


def get_party_state(party_id: str) -> Optional[Dict]:
    """Get current party state."""
    storage = _get_parties_storage()

    if party_id not in storage:
        return None

    party = storage[party_id]

    return {
        "party_id": party.party_id,
        "host_name": party.host_name,
        "content_title": party.content_title,
        "content_image": party.content_image,
        "state": party.state,
        "current_position": party.current_position,
        "members": party.members,
        "member_count": len(party.members),
        "chat_messages": party.chat_messages[-20:],  # Last 20 messages
        "invite_code": party.invite_code
    }


def get_public_parties() -> List[Dict]:
    """Get list of public watch parties."""
    storage = _get_parties_storage()

    public = []
    for party in storage.values():
        if not party.is_private and party.state != "ended":
            public.append({
                "party_id": party.party_id,
                "host_name": party.host_name,
                "content_title": party.content_title,
                "content_image": party.content_image,
                "member_count": len(party.members),
                "state": party.state
            })

    return public


# --------------------------------------------------
# 2. DIRECT MESSAGING
# --------------------------------------------------

@dataclass
class Conversation:
    """Direct message conversation."""
    conversation_id: str
    participants: List[str]  # user_ids
    participant_names: Dict[str, str]  # user_id -> name
    messages: List[Dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


def _get_conversations_storage() -> Dict[str, Conversation]:
    """Get conversations storage."""
    if 'dm_conversations' not in st.session_state:
        st.session_state.dm_conversations = {}
    return st.session_state.dm_conversations


def get_or_create_conversation(user1_id: str, user1_name: str, user2_id: str, user2_name: str) -> Dict:
    """Get or create a conversation between two users."""
    storage = _get_conversations_storage()

    # Check if conversation exists
    for conv in storage.values():
        if set(conv.participants) == {user1_id, user2_id}:
            return {"conversation_id": conv.conversation_id, "existing": True}

    # Create new conversation
    conv_id = hashlib.md5(f"{user1_id}{user2_id}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

    conversation = Conversation(
        conversation_id=conv_id,
        participants=[user1_id, user2_id],
        participant_names={user1_id: user1_name, user2_id: user2_name}
    )

    storage[conv_id] = conversation

    return {"conversation_id": conv_id, "existing": False}


def send_direct_message(conversation_id: str, sender_id: str, sender_name: str, content: str) -> Optional[Dict]:
    """Send a direct message."""
    storage = _get_conversations_storage()

    if conversation_id not in storage:
        return None

    conv = storage[conversation_id]

    message = {
        "message_id": hashlib.md5(f"{sender_id}{datetime.now().isoformat()}".encode()).hexdigest()[:8],
        "sender_id": sender_id,
        "sender_name": sender_name,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }

    conv.messages.append(message)
    conv.updated_at = datetime.now()

    return message


def get_conversation_messages(conversation_id: str, limit: int = 50) -> List[Dict]:
    """Get messages from a conversation."""
    storage = _get_conversations_storage()

    if conversation_id not in storage:
        return []

    return storage[conversation_id].messages[-limit:]


def get_user_conversations(user_id: str) -> List[Dict]:
    """Get all conversations for a user."""
    storage = _get_conversations_storage()

    conversations = []
    for conv in storage.values():
        if user_id in conv.participants:
            other_id = [p for p in conv.participants if p != user_id][0]
            other_name = conv.participant_names.get(other_id, "Unknown")

            last_message = conv.messages[-1] if conv.messages else None
            unread = sum(1 for m in conv.messages if not m.get("read") and m.get("sender_id") != user_id)

            conversations.append({
                "conversation_id": conv.conversation_id,
                "other_user_id": other_id,
                "other_user_name": other_name,
                "last_message": last_message,
                "unread_count": unread,
                "updated_at": conv.updated_at.isoformat()
            })

    # Sort by updated_at
    conversations.sort(key=lambda x: x["updated_at"], reverse=True)

    return conversations


def mark_messages_read(conversation_id: str, user_id: str) -> int:
    """Mark all messages as read for a user."""
    storage = _get_conversations_storage()

    if conversation_id not in storage:
        return 0

    conv = storage[conversation_id]
    count = 0

    for message in conv.messages:
        if message.get("sender_id") != user_id and not message.get("read"):
            message["read"] = True
            count += 1

    return count


# --------------------------------------------------
# 3. FRIEND SYSTEM
# --------------------------------------------------

def _get_friends_storage() -> Dict[str, List[str]]:
    """Get friends storage."""
    if 'user_friends' not in st.session_state:
        st.session_state.user_friends = {}
    return st.session_state.user_friends


def add_friend(user_id: str, friend_id: str) -> bool:
    """Add a friend connection."""
    storage = _get_friends_storage()

    if user_id not in storage:
        storage[user_id] = []
    if friend_id not in storage:
        storage[friend_id] = []

    if friend_id not in storage[user_id]:
        storage[user_id].append(friend_id)
    if user_id not in storage[friend_id]:
        storage[friend_id].append(user_id)

    return True


def remove_friend(user_id: str, friend_id: str) -> bool:
    """Remove a friend connection."""
    storage = _get_friends_storage()

    if user_id in storage and friend_id in storage[user_id]:
        storage[user_id].remove(friend_id)
    if friend_id in storage and user_id in storage[friend_id]:
        storage[friend_id].remove(user_id)

    return True


def get_friends(user_id: str) -> List[str]:
    """Get user's friends."""
    storage = _get_friends_storage()
    return storage.get(user_id, [])


def get_friends_count(user_id: str) -> int:
    """Get number of friends."""
    return len(get_friends(user_id))


# --------------------------------------------------
# 4. SHARE & REFERRAL
# --------------------------------------------------

def _get_referrals_storage() -> Dict[str, Dict]:
    """Get referrals storage."""
    if 'user_referrals' not in st.session_state:
        st.session_state.user_referrals = {}
    return st.session_state.user_referrals


def generate_referral_code(user_id: str) -> str:
    """Generate a unique referral code for user."""
    storage = _get_referrals_storage()

    if user_id not in storage:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        storage[user_id] = {
            "code": code,
            "referrals": [],
            "created_at": datetime.now().isoformat()
        }

    return storage[user_id]["code"]


def apply_referral_code(new_user_id: str, referral_code: str) -> Optional[Dict]:
    """Apply a referral code for a new user."""
    storage = _get_referrals_storage()

    # Find referrer
    referrer_id = None
    for uid, data in storage.items():
        if data["code"] == referral_code:
            referrer_id = uid
            break

    if not referrer_id:
        return None

    # Record referral
    storage[referrer_id]["referrals"].append({
        "user_id": new_user_id,
        "timestamp": datetime.now().isoformat()
    })

    return {
        "referrer_id": referrer_id,
        "bonus_points": 200  # Both get 200 DP
    }


def get_referral_stats(user_id: str) -> Dict:
    """Get user's referral statistics."""
    storage = _get_referrals_storage()

    if user_id not in storage:
        return {"code": generate_referral_code(user_id), "count": 0, "referrals": []}

    data = storage[user_id]
    return {
        "code": data["code"],
        "count": len(data["referrals"]),
        "referrals": data["referrals"],
        "link": f"https://dopamine.watch/?ref={data['code']}"
    }


def generate_share_link(content_id: str, content_title: str, user_id: str = None) -> Dict:
    """Generate shareable links for content."""
    base_url = "https://dopamine.watch"

    # Add referral code if user is logged in
    ref_param = ""
    if user_id:
        ref_code = generate_referral_code(user_id)
        ref_param = f"&ref={ref_code}"

    share_url = f"{base_url}/watch/{content_id}?utm_source=share{ref_param}"

    # Generate social share links
    encoded_title = content_title.replace(" ", "%20")

    return {
        "url": share_url,
        "twitter": f"https://twitter.com/intent/tweet?text=Check%20out%20{encoded_title}%20on%20dopamine.watch!&url={share_url}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={share_url}",
        "whatsapp": f"https://wa.me/?text=Check%20out%20{encoded_title}%20on%20dopamine.watch!%20{share_url}",
        "copy_text": f"Check out {content_title} on dopamine.watch! {share_url}"
    }


# --------------------------------------------------
# 5. STREAMLIT UI COMPONENTS
# --------------------------------------------------

def render_watch_party_card(party: Dict):
    """Render a watch party card."""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
                padding: 20px; border-radius: 16px; color: white; margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 1.2rem; font-weight: bold;">{party['content_title']}</div>
                <div style="opacity: 0.8;">Hosted by {party['host_name']}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.5rem;">{party['member_count']} 👥</div>
                <div style="opacity: 0.8;">{party['state'].title()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_create_party_modal(user_id: str, user_name: str):
    """Render create watch party modal."""
    st.markdown("### 🎉 Create Watch Party")

    content_title = st.text_input("What are you watching?", placeholder="Movie or show title")
    content_type = st.selectbox("Type", ["movie", "tv", "video"])
    is_private = st.checkbox("Private party (invite only)", value=True)

    if st.button("Create Party", type="primary"):
        if content_title:
            result = create_watch_party(
                host_id=user_id,
                host_name=user_name,
                content_id=hashlib.md5(content_title.encode()).hexdigest()[:8],
                content_title=content_title,
                content_type=content_type,
                is_private=is_private
            )
            st.success(f"Party created! Invite code: **{result['invite_code']}**")
            st.code(result['invite_link'])
            return result
    return None


def render_join_party_modal(user_id: str, user_name: str):
    """Render join watch party modal."""
    st.markdown("### 🎬 Join Watch Party")

    invite_code = st.text_input("Enter invite code", placeholder="ABC123")

    if st.button("Join Party", type="primary"):
        if invite_code:
            result = join_watch_party(
                invite_code=invite_code.upper(),
                user_id=user_id,
                user_name=user_name
            )
            if result:
                st.success(f"Joined {result.get('content_title', 'party')}!")
                return result
            else:
                st.error("Party not found. Check the invite code.")
    return None


def render_party_chat(party_id: str, user_id: str, user_name: str):
    """Render watch party chat."""
    state = get_party_state(party_id)
    if not state:
        st.error("Party not found")
        return

    st.markdown(f"### 💬 Party Chat - {state['content_title']}")
    st.markdown(f"**{state['member_count']}** people watching")

    # Chat messages
    chat_container = st.container()
    with chat_container:
        for msg in state['chat_messages']:
            if msg['type'] == 'system':
                st.markdown(f"<div style='text-align: center; color: #888; font-size: 0.8rem;'>{msg['content']}</div>", unsafe_allow_html=True)
            elif msg['type'] == 'reaction':
                st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{msg['emoji']}</div>", unsafe_allow_html=True)
            else:
                is_me = msg.get('user_id') == user_id
                align = "right" if is_me else "left"
                bg = "#7c3aed" if is_me else "#333"
                st.markdown(f"""
                <div style="text-align: {align}; margin: 8px 0;">
                    <span style="background: {bg}; padding: 8px 12px; border-radius: 12px; display: inline-block; max-width: 70%;">
                        <strong>{msg.get('user_name', 'User')}:</strong> {msg['content']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # Message input
    col1, col2 = st.columns([4, 1])
    with col1:
        message = st.text_input("Type a message...", key=f"party_msg_{party_id}")
    with col2:
        if st.button("Send", key=f"party_send_{party_id}"):
            if message:
                send_party_message(party_id, user_id, user_name, message)
                st.rerun()

    # Reactions
    st.markdown("Quick reactions:")
    reaction_cols = st.columns(6)
    reactions = ["😂", "🔥", "😱", "❤️", "👏", "🎉"]
    for i, emoji in enumerate(reactions):
        with reaction_cols[i]:
            if st.button(emoji, key=f"reaction_{party_id}_{emoji}"):
                send_party_reaction(party_id, user_id, user_name, emoji)
                st.rerun()


def render_messages_sidebar(user_id: str, user_name: str):
    """Render direct messages in sidebar."""
    conversations = get_user_conversations(user_id)

    st.markdown("### 💬 Messages")

    if not conversations:
        st.info("No messages yet. Start a conversation!")
        return

    for conv in conversations[:5]:
        unread_badge = f"🔴 {conv['unread_count']}" if conv['unread_count'] > 0 else ""
        last_msg = conv.get('last_message', {}).get('content', 'No messages')[:30]

        if st.button(f"**{conv['other_user_name']}** {unread_badge}\n{last_msg}...", key=f"conv_{conv['conversation_id']}"):
            st.session_state.active_conversation = conv['conversation_id']
            st.rerun()


def render_share_buttons(content_id: str, content_title: str, user_id: str = None):
    """Render share buttons for content."""
    links = generate_share_link(content_id, content_title, user_id)

    st.markdown("### 📤 Share")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"[🐦 Twitter]({links['twitter']})")
    with col2:
        st.markdown(f"[📘 Facebook]({links['facebook']})")
    with col3:
        st.markdown(f"[💬 WhatsApp]({links['whatsapp']})")
    with col4:
        if st.button("📋 Copy"):
            st.code(links['copy_text'])


def render_referral_section(user_id: str):
    """Render referral section."""
    stats = get_referral_stats(user_id)

    st.markdown("### 🎁 Invite Friends, Get Rewards!")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
                padding: 20px; border-radius: 16px; color: white; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 10px;">🎁</div>
        <div style="font-size: 1.2rem; font-weight: bold;">Your Referral Code</div>
        <div style="font-size: 2rem; font-family: monospace; margin: 10px 0;">{stats['code']}</div>
        <div style="opacity: 0.8;">You've referred {stats['count']} friends!</div>
    </div>
    """, unsafe_allow_html=True)

    st.code(stats['link'])

    st.markdown("**Rewards:**")
    st.markdown("- You get **200 DP** for each friend who joins")
    st.markdown("- Your friend gets **200 DP** bonus too!")

    # Milestones
    milestones = [
        (1, "🎯 First Friend", "100 bonus DP"),
        (5, "👥 Squad Builder", "500 bonus DP"),
        (10, "🌟 Networker", "1000 bonus DP"),
        (25, "🚀 Influencer", "2500 bonus DP"),
    ]

    st.markdown("**Milestones:**")
    for count, title, reward in milestones:
        achieved = "✅" if stats['count'] >= count else "🔒"
        st.markdown(f"{achieved} **{title}** ({count} referrals) - {reward}")
