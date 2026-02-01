"""
Dopamine.watch 2027 - Session State Management
Centralized session state initialization and management.
ADHD-optimized: Save state automatically, never lose progress.
"""

import streamlit as st
from typing import Any, Optional, Dict, List
from datetime import datetime

from config.settings import ADHD_CONFIG, MR_DP_CONFIG


def init_session_state():
    """
    Initialize all session state variables.
    Call this at the start of the app.
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION STATE
    # ═══════════════════════════════════════════════════════════════════════════

    defaults = {
        # User
        "user": None,
        "is_authenticated": False,
        "auth_token": None,

        # ═══════════════════════════════════════════════════════════════════════
        # NAVIGATION STATE
        # ═══════════════════════════════════════════════════════════════════════

        "current_page": "home",
        "previous_page": None,
        "sidebar_expanded": False,
        "show_command_palette": False,

        # ═══════════════════════════════════════════════════════════════════════
        # MR.DP STATE
        # ═══════════════════════════════════════════════════════════════════════

        "mr_dp_chat_history": [],
        "mr_dp_conversation_id": None,
        "mr_dp_open": False,
        "mr_dp_thinking": False,
        "mr_dp_just_responded": False,
        "mr_dp_expression": "happy",
        "mr_dp_animation_state": "idle",
        "mr_dp_v2_response": None,
        "mr_dp_context": {},  # User preferences, mood history, etc.
        "mr_dp_uses_today": 0,

        # ═══════════════════════════════════════════════════════════════════════
        # MOOD STATE
        # ═══════════════════════════════════════════════════════════════════════

        "current_mood": None,
        "desired_mood": None,
        "mood_history": [],
        "mood_streak": 0,

        # ═══════════════════════════════════════════════════════════════════════
        # CONTENT STATE
        # ═══════════════════════════════════════════════════════════════════════

        "active_content_type": "movies",
        "search_query": "",
        "search_results": [],
        "recommendations": [],
        "selected_content": None,
        "content_preview_open": False,

        # Queue
        "user_queue": [],
        "queue_loading": False,

        # Continue watching
        "continue_watching": [],

        # ═══════════════════════════════════════════════════════════════════════
        # SOCIAL STATE
        # ═══════════════════════════════════════════════════════════════════════

        "friends_list": [],
        "friend_requests": [],
        "unread_messages": 0,
        "active_conversation": None,
        "dm_messages": [],

        # Watch parties
        "active_watch_party": None,
        "watch_party_messages": [],
        "watch_party_participants": [],

        # ═══════════════════════════════════════════════════════════════════════
        # UI STATE
        # ═══════════════════════════════════════════════════════════════════════

        "theme": "light",
        "show_modal": None,  # "premium", "login", "settings", etc.
        "toast_queue": [],
        "loading_states": {},
        "animations_enabled": True,

        # ADHD-specific
        "focus_mode": False,
        "reduced_motion": False,
        "show_time_estimates": ADHD_CONFIG["show_time_estimates"],

        # ═══════════════════════════════════════════════════════════════════════
        # GAMIFICATION STATE
        # ═══════════════════════════════════════════════════════════════════════

        "dopamine_points": 0,
        "level": 1,
        "achievements": [],
        "recent_achievement": None,
        "show_celebration": False,

        # ═══════════════════════════════════════════════════════════════════════
        # FEEDBACK STATE
        # ═══════════════════════════════════════════════════════════════════════

        "show_feedback_modal": False,
        "feedback_step": 0,
        "feedback_answers": {},
    }

    # Initialize each key if not already set
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_state(key: str, default: Any = None) -> Any:
    """Get a session state value with optional default."""
    return st.session_state.get(key, default)


def set_state(key: str, value: Any) -> None:
    """Set a session state value."""
    st.session_state[key] = value


def update_state(updates: Dict[str, Any]) -> None:
    """Update multiple session state values at once."""
    for key, value in updates.items():
        st.session_state[key] = value


def clear_state(*keys: str) -> None:
    """Clear specific session state keys (reset to None)."""
    for key in keys:
        if key in st.session_state:
            st.session_state[key] = None


def reset_state() -> None:
    """Reset all session state (used on logout)."""
    # Keep theme preference
    theme = st.session_state.get("theme", "light")

    # Clear all keys
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Reinitialize
    init_session_state()

    # Restore theme
    st.session_state.theme = theme


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIFIC STATE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def set_user(user: Dict[str, Any]) -> None:
    """Set the authenticated user."""
    st.session_state.user = user
    st.session_state.is_authenticated = bool(user)


def get_user() -> Optional[Dict[str, Any]]:
    """Get the current user."""
    return st.session_state.get("user")


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("is_authenticated", False)


def is_premium() -> bool:
    """Check if user has premium subscription."""
    user = get_user()
    return user.get("is_premium", False) if user else False


def navigate_to(page: str) -> None:
    """Navigate to a different page."""
    st.session_state.previous_page = st.session_state.current_page
    st.session_state.current_page = page


def go_back() -> None:
    """Go back to previous page."""
    if st.session_state.previous_page:
        st.session_state.current_page = st.session_state.previous_page
        st.session_state.previous_page = None


# ═══════════════════════════════════════════════════════════════════════════════
# MR.DP STATE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def add_mr_dp_message(role: str, content: str) -> None:
    """Add a message to Mr.DP chat history."""
    st.session_state.mr_dp_chat_history.append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Keep only last N messages for context
    max_messages = MR_DP_CONFIG.get("context_window_messages", 20)
    if len(st.session_state.mr_dp_chat_history) > max_messages:
        st.session_state.mr_dp_chat_history = st.session_state.mr_dp_chat_history[-max_messages:]


def set_mr_dp_expression(expression: str) -> None:
    """Set Mr.DP's facial expression."""
    if expression in MR_DP_CONFIG["expressions"]:
        st.session_state.mr_dp_expression = expression


def set_mr_dp_animation(state: str) -> None:
    """Set Mr.DP's animation state."""
    valid_states = ["idle", "thinking", "speaking", "listening", "excited"]
    if state in valid_states:
        st.session_state.mr_dp_animation_state = state


def mr_dp_start_thinking() -> None:
    """Set Mr.DP to thinking state."""
    st.session_state.mr_dp_thinking = True
    set_mr_dp_expression("thinking")
    set_mr_dp_animation("thinking")


def mr_dp_done_thinking() -> None:
    """Reset Mr.DP from thinking state."""
    st.session_state.mr_dp_thinking = False
    st.session_state.mr_dp_just_responded = True
    set_mr_dp_expression("excited")
    set_mr_dp_animation("speaking")


def clear_mr_dp_chat() -> None:
    """Clear Mr.DP chat history."""
    st.session_state.mr_dp_chat_history = []
    st.session_state.mr_dp_conversation_id = None


# ═══════════════════════════════════════════════════════════════════════════════
# MOOD STATE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def set_mood(current: str, desired: str = None) -> None:
    """Set user's current and desired mood."""
    st.session_state.current_mood = current
    if desired:
        st.session_state.desired_mood = desired

    # Add to history
    st.session_state.mood_history.append({
        "current": current,
        "desired": desired,
        "timestamp": datetime.utcnow().isoformat()
    })


# ═══════════════════════════════════════════════════════════════════════════════
# UI STATE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def show_modal(modal_name: str) -> None:
    """Show a modal dialog."""
    st.session_state.show_modal = modal_name


def hide_modal() -> None:
    """Hide the current modal."""
    st.session_state.show_modal = None


def add_toast(message: str, type: str = "info", duration: int = 3000) -> None:
    """Add a toast notification."""
    st.session_state.toast_queue.append({
        "message": message,
        "type": type,  # success, error, warning, info
        "duration": duration,
        "timestamp": datetime.utcnow().isoformat()
    })


def toggle_theme() -> None:
    """Toggle between light and dark theme."""
    current = st.session_state.get("theme", "light")
    st.session_state.theme = "dark" if current == "light" else "light"


def toggle_focus_mode() -> None:
    """Toggle focus mode (hide distractions)."""
    st.session_state.focus_mode = not st.session_state.get("focus_mode", False)


def set_loading(key: str, is_loading: bool) -> None:
    """Set loading state for a specific operation."""
    if "loading_states" not in st.session_state:
        st.session_state.loading_states = {}
    st.session_state.loading_states[key] = is_loading


def is_loading(key: str) -> bool:
    """Check if a specific operation is loading."""
    return st.session_state.get("loading_states", {}).get(key, False)


# ═══════════════════════════════════════════════════════════════════════════════
# GAMIFICATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def add_points(points: int, reason: str = "") -> int:
    """Add dopamine points. Returns new total."""
    current = st.session_state.get("dopamine_points", 0)
    new_total = current + points
    st.session_state.dopamine_points = new_total

    # Check for level up
    check_level_up()

    # Show celebration for significant points
    if points >= 50:
        st.session_state.show_celebration = True

    return new_total


def check_level_up() -> bool:
    """Check if user leveled up. Returns True if leveled up."""
    points = st.session_state.get("dopamine_points", 0)
    current_level = st.session_state.get("level", 1)

    # Simple level calculation: level = sqrt(points / 100)
    import math
    new_level = max(1, int(math.sqrt(points / 100)) + 1)

    if new_level > current_level:
        st.session_state.level = new_level
        add_toast(f"Level Up! You're now level {new_level}!", "success")
        return True
    return False


def unlock_achievement(achievement_id: str, title: str) -> None:
    """Unlock an achievement locally."""
    if achievement_id not in [a["id"] for a in st.session_state.get("achievements", [])]:
        achievement = {
            "id": achievement_id,
            "title": title,
            "unlocked_at": datetime.utcnow().isoformat()
        }
        st.session_state.achievements.append(achievement)
        st.session_state.recent_achievement = achievement
        st.session_state.show_celebration = True
