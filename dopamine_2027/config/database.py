"""
Dopamine.watch 2027 - Database Configuration
Supabase client, auth functions, and database utilities.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

from .settings import SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_ENABLED

# Initialize Supabase client
supabase = None

if SUPABASE_ENABLED:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        print(f"Failed to initialize Supabase: {e}")
        supabase = None


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

def sign_up(email: str, password: str) -> Dict[str, Any]:
    """Sign up a new user with email and password."""
    if not supabase:
        return {"error": "Database not available"}

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if response.user:
            # Create profile
            create_user_profile(response.user.id, email)
            return {"user": response.user, "session": response.session}
        return {"error": "Sign up failed"}
    except Exception as e:
        return {"error": str(e)}


def sign_in(email: str, password: str) -> Dict[str, Any]:
    """Sign in with email and password."""
    if not supabase:
        return {"error": "Database not available"}

    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return {"user": response.user, "session": response.session}
        return {"error": "Sign in failed"}
    except Exception as e:
        return {"error": str(e)}


def sign_in_with_google() -> str:
    """Get Google OAuth URL for sign in."""
    if not supabase:
        return ""

    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": st.secrets.get("app", {}).get("url", "http://localhost:8501")
            }
        })
        return response.url if response else ""
    except Exception:
        return ""


def sign_out() -> bool:
    """Sign out the current user."""
    if not supabase:
        return False

    try:
        supabase.auth.sign_out()
        return True
    except Exception:
        return False


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the currently authenticated user."""
    if not supabase:
        return None

    try:
        response = supabase.auth.get_user()
        if response and response.user:
            # Get full profile
            profile = get_user_profile(response.user.id)
            return {
                "id": response.user.id,
                "email": response.user.email,
                **profile
            }
        return None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# USER PROFILES
# ═══════════════════════════════════════════════════════════════════════════════

def create_user_profile(user_id: str, email: str) -> bool:
    """Create a new user profile."""
    if not supabase:
        return False

    try:
        # Generate username from email
        username = email.split("@")[0][:20]

        supabase.table("profiles").insert({
            "id": user_id,
            "username": username,
            "display_name": username,
            "created_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Failed to create profile: {e}")
        return False


def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get a user's profile by ID."""
    if not supabase:
        return {}

    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data if response.data else {}
    except Exception:
        return {}


def update_user_profile(user_id: str, updates: Dict[str, Any]) -> bool:
    """Update a user's profile."""
    if not supabase:
        return False

    try:
        updates["updated_at"] = datetime.utcnow().isoformat()
        supabase.table("profiles").update(updates).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Failed to update profile: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MR.DP USAGE TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

def get_mr_dp_usage(user_id: str) -> Dict[str, Any]:
    """Get Mr.DP usage stats for a user."""
    if not supabase:
        return {"uses_today": 0, "total_uses": 0}

    try:
        response = supabase.table("profiles").select(
            "mr_dp_uses, mr_dp_last_reset, is_premium"
        ).eq("id", user_id).single().execute()

        if not response.data:
            return {"uses_today": 0, "total_uses": 0, "is_premium": False}

        data = response.data
        last_reset = data.get("mr_dp_last_reset")

        # Check if we need to reset daily counter
        if last_reset:
            last_reset_date = datetime.fromisoformat(last_reset.replace("Z", "+00:00"))
            if last_reset_date.date() < datetime.utcnow().date():
                # Reset counter
                supabase.table("profiles").update({
                    "mr_dp_uses": 0,
                    "mr_dp_last_reset": datetime.utcnow().isoformat()
                }).eq("id", user_id).execute()
                return {"uses_today": 0, "is_premium": data.get("is_premium", False)}

        return {
            "uses_today": data.get("mr_dp_uses", 0),
            "is_premium": data.get("is_premium", False)
        }
    except Exception as e:
        print(f"Failed to get Mr.DP usage: {e}")
        return {"uses_today": 0, "is_premium": False}


def increment_mr_dp_usage(user_id: str) -> int:
    """Increment Mr.DP usage counter. Returns new count."""
    if not supabase:
        return 0

    try:
        # Get current usage
        current = get_mr_dp_usage(user_id)
        new_count = current.get("uses_today", 0) + 1

        supabase.table("profiles").update({
            "mr_dp_uses": new_count,
            "mr_dp_last_reset": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()

        return new_count
    except Exception as e:
        print(f"Failed to increment Mr.DP usage: {e}")
        return 0


# ═══════════════════════════════════════════════════════════════════════════════
# SAVED CONTENT / QUEUE
# ═══════════════════════════════════════════════════════════════════════════════

def save_to_queue(user_id: str, content: Dict[str, Any]) -> bool:
    """Save content to user's queue."""
    if not supabase:
        return False

    try:
        supabase.table("user_queue").insert({
            "user_id": user_id,
            "content_id": content.get("id"),
            "content_type": content.get("type", "movie"),
            "title": content.get("title"),
            "poster_url": content.get("poster_url"),
            "metadata": json.dumps(content),
            "added_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Failed to save to queue: {e}")
        return False


def get_user_queue(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get user's saved content queue."""
    if not supabase:
        return []

    try:
        response = supabase.table("user_queue").select("*").eq(
            "user_id", user_id
        ).order("added_at", desc=True).limit(limit).execute()

        items = []
        for item in response.data or []:
            metadata = json.loads(item.get("metadata", "{}"))
            items.append({
                "id": item["id"],
                "content_id": item["content_id"],
                "content_type": item["content_type"],
                "title": item["title"],
                "poster_url": item["poster_url"],
                "added_at": item["added_at"],
                **metadata
            })
        return items
    except Exception as e:
        print(f"Failed to get queue: {e}")
        return []


def remove_from_queue(user_id: str, item_id: str) -> bool:
    """Remove item from user's queue."""
    if not supabase:
        return False

    try:
        supabase.table("user_queue").delete().eq(
            "user_id", user_id
        ).eq("id", item_id).execute()
        return True
    except Exception as e:
        print(f"Failed to remove from queue: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MOOD LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

def log_mood(user_id: str, current_mood: str, desired_mood: str = None, source: str = "manual") -> bool:
    """Log a mood selection."""
    if not supabase:
        return False

    try:
        supabase.table("mood_logs").insert({
            "user_id": user_id,
            "current_mood": current_mood,
            "desired_mood": desired_mood,
            "source": source,
            "logged_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Failed to log mood: {e}")
        return False


def get_mood_history(user_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """Get user's mood history for analytics."""
    if not supabase:
        return []

    try:
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        response = supabase.table("mood_logs").select("*").eq(
            "user_id", user_id
        ).gte("logged_at", since).order("logged_at", desc=True).execute()

        return response.data or []
    except Exception as e:
        print(f"Failed to get mood history: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# MR.DP CONVERSATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def save_mr_dp_conversation(user_id: str, messages: List[Dict[str, Any]]) -> str:
    """Save a Mr.DP conversation. Returns conversation ID."""
    if not supabase:
        return ""

    try:
        response = supabase.table("mr_dp_conversations").insert({
            "user_id": user_id,
            "messages": json.dumps(messages),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()

        return response.data[0]["id"] if response.data else ""
    except Exception as e:
        print(f"Failed to save conversation: {e}")
        return ""


def get_mr_dp_conversations(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Get user's Mr.DP conversation history."""
    if not supabase:
        return []

    try:
        response = supabase.table("mr_dp_conversations").select("*").eq(
            "user_id", user_id
        ).order("updated_at", desc=True).limit(limit).execute()

        conversations = []
        for conv in response.data or []:
            messages = json.loads(conv.get("messages", "[]"))
            conversations.append({
                "id": conv["id"],
                "messages": messages,
                "created_at": conv["created_at"],
                "updated_at": conv["updated_at"],
                "preview": messages[0]["content"][:100] if messages else ""
            })
        return conversations
    except Exception as e:
        print(f"Failed to get conversations: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENTS / GAMIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def add_dopamine_points(user_id: str, points: int, reason: str = "") -> int:
    """Add dopamine points to user. Returns new total."""
    if not supabase:
        return 0

    try:
        # Get current points
        profile = get_user_profile(user_id)
        current = profile.get("dopamine_points", 0)
        new_total = current + points

        # Update points
        supabase.table("profiles").update({
            "dopamine_points": new_total
        }).eq("id", user_id).execute()

        # Log the points gain
        supabase.table("points_log").insert({
            "user_id": user_id,
            "points": points,
            "reason": reason,
            "earned_at": datetime.utcnow().isoformat(),
        }).execute()

        return new_total
    except Exception as e:
        print(f"Failed to add points: {e}")
        return 0


def get_user_achievements(user_id: str) -> List[Dict[str, Any]]:
    """Get user's unlocked achievements."""
    if not supabase:
        return []

    try:
        response = supabase.table("user_achievements").select(
            "*, achievements(*)"
        ).eq("user_id", user_id).execute()

        return response.data or []
    except Exception as e:
        print(f"Failed to get achievements: {e}")
        return []


def unlock_achievement(user_id: str, achievement_id: str) -> bool:
    """Unlock an achievement for a user."""
    if not supabase:
        return False

    try:
        # Check if already unlocked
        existing = supabase.table("user_achievements").select("id").eq(
            "user_id", user_id
        ).eq("achievement_id", achievement_id).execute()

        if existing.data:
            return False  # Already unlocked

        supabase.table("user_achievements").insert({
            "user_id": user_id,
            "achievement_id": achievement_id,
            "unlocked_at": datetime.utcnow().isoformat(),
        }).execute()
        return True
    except Exception as e:
        print(f"Failed to unlock achievement: {e}")
        return False
