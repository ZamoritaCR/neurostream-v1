"""
Dopamine.watch 2027 - Configuration Settings
All constants, API keys, and app configuration.
"""

import os
import streamlit as st
from typing import Optional

# ═══════════════════════════════════════════════════════════════════════════════
# APP CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "dopamine.watch"
APP_VERSION = "2.0.0"
APP_TAGLINE = "Your AI-Powered Dopamine Curator"
APP_URL = "https://dopamine.watch"

# Feature flags
FEATURES = {
    "mr_dp_v2": True,           # Enhanced Mr.DP with memory
    "social_features": True,     # Friends, DMs, watch parties
    "watch_parties": True,       # Synchronized viewing
    "community_boards": False,   # Coming soon
    "premium_features": True,    # Stripe integration
    "dark_mode": True,           # Theme toggle
    "voice_input": False,        # Voice to text (future)
}

# ═══════════════════════════════════════════════════════════════════════════════
# API KEYS & SECRETS
# ═══════════════════════════════════════════════════════════════════════════════

def get_secret(section: str, key: str, env_var: Optional[str] = None) -> Optional[str]:
    """
    Get secret from Streamlit secrets or environment variables.
    Priority: st.secrets > env vars > None
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and section in st.secrets:
            return st.secrets[section].get(key)
    except Exception:
        pass

    # Try environment variable
    if env_var:
        return os.environ.get(env_var)

    # Try auto-generated env var name
    auto_env = f"{section.upper()}_{key.upper()}"
    return os.environ.get(auto_env)


# Supabase
SUPABASE_URL = get_secret("supabase", "url", "SUPABASE_URL")
SUPABASE_ANON_KEY = get_secret("supabase", "anon_key", "SUPABASE_ANON_KEY")
SUPABASE_ENABLED = bool(SUPABASE_URL and SUPABASE_ANON_KEY)

# OpenAI (for Mr.DP)
OPENAI_API_KEY = get_secret("openai", "api_key", "OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"  # or gpt-4-turbo
OPENAI_ENABLED = bool(OPENAI_API_KEY)

# TMDB (Movies & TV)
TMDB_API_KEY = get_secret("tmdb", "api_key", "TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
TMDB_ENABLED = bool(TMDB_API_KEY)

# Spotify (Music & Podcasts)
SPOTIFY_CLIENT_ID = get_secret("spotify", "client_id", "SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = get_secret("spotify", "client_secret", "SPOTIFY_CLIENT_SECRET")
SPOTIFY_ENABLED = bool(SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)

# YouTube
YOUTUBE_API_KEY = get_secret("youtube", "api_key", "YOUTUBE_API_KEY")
YOUTUBE_ENABLED = bool(YOUTUBE_API_KEY)

# Stripe (Premium)
STRIPE_PUBLISHABLE_KEY = get_secret("stripe", "publishable_key", "STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = get_secret("stripe", "secret_key", "STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = get_secret("stripe", "webhook_secret", "STRIPE_WEBHOOK_SECRET")
STRIPE_ENABLED = bool(STRIPE_PUBLISHABLE_KEY and STRIPE_SECRET_KEY)

# ═══════════════════════════════════════════════════════════════════════════════
# ADHD OPTIMIZATION SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

ADHD_CONFIG = {
    # Maximum choices to show (reduce decision paralysis)
    "max_choices": 3,
    "max_results_per_page": 12,

    # Time estimates (help with time blindness)
    "show_time_estimates": True,
    "quick_content_max_minutes": 30,

    # Progress tracking
    "show_streaks": True,
    "show_achievements": True,
    "celebration_animations": True,

    # Cognitive load
    "progressive_disclosure": True,
    "hide_secondary_actions": True,

    # Focus support
    "focus_mode_available": True,
    "break_reminders": True,
    "hyperfocus_alerts_minutes": 120,

    # Sensory
    "respect_reduced_motion": True,
    "default_animation_speed": "normal",  # slow, normal, fast

    # Typography
    "min_font_size_px": 16,
    "max_line_width_ch": 65,
    "line_height": 1.6,
}

# ═══════════════════════════════════════════════════════════════════════════════
# MR.DP CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

MR_DP_CONFIG = {
    "name": "Mr.DP",
    "full_name": "Mr. Dopamine",
    "tagline": "Your Dopamine Curator",

    # Personality
    "personality_traits": [
        "warm", "understanding", "casual", "helpful",
        "excited_but_not_too_much", "adhd_aware"
    ],

    # Response limits
    "max_response_sentences": 3,
    "max_suggestions": 3,
    "prefer_yes_no_questions": True,

    # Expressions
    "expressions": ["happy", "thinking", "excited", "concerned", "celebrating",
                   "sleeping", "listening", "sad", "love", "surprised",
                   "wink", "confused", "cool", "focused"],

    # Memory
    "remember_preferences": True,
    "remember_conversations": True,
    "context_window_messages": 20,

    # Safety
    "content_filter": True,
    "crisis_detection": True,
    "adult_content_block": True,
}

# ═══════════════════════════════════════════════════════════════════════════════
# PREMIUM / SUBSCRIPTION
# ═══════════════════════════════════════════════════════════════════════════════

PREMIUM_CONFIG = {
    "free_mr_dp_chats_per_day": 5,
    "premium_mr_dp_unlimited": True,

    "prices": {
        "monthly": {
            "amount": 4.99,
            "currency": "USD",
            "stripe_price_id": "price_monthly",  # Replace with actual
        },
        "yearly": {
            "amount": 39.99,
            "currency": "USD",
            "stripe_price_id": "price_yearly",  # Replace with actual
            "savings_percent": 33,
        }
    },

    "features": {
        "free": [
            "Basic mood-based recommendations",
            "5 Mr.DP chats per day",
            "Save content to queue",
        ],
        "premium": [
            "Unlimited Mr.DP conversations",
            "Priority AI responses",
            "Advanced content research",
            "Watch parties",
            "No ads",
            "Early access to new features",
        ]
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# MOOD & EMOTION MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

MOODS = {
    "stressed": {
        "emoji": "😰",
        "color": "#EF4444",
        "genres": ["documentary", "nature", "meditation"],
        "energy": "low",
        "mr_dp_tone": "calm and supportive"
    },
    "bored": {
        "emoji": "😐",
        "color": "#6B7280",
        "genres": ["comedy", "action", "thriller"],
        "energy": "high",
        "mr_dp_tone": "enthusiastic and engaging"
    },
    "sad": {
        "emoji": "😢",
        "color": "#3B82F6",
        "genres": ["comedy", "feel-good", "animation"],
        "energy": "comfort",
        "mr_dp_tone": "gentle and understanding"
    },
    "anxious": {
        "emoji": "😟",
        "color": "#F59E0B",
        "genres": ["nature", "cooking", "crafts"],
        "energy": "low",
        "mr_dp_tone": "reassuring and calm"
    },
    "happy": {
        "emoji": "😊",
        "color": "#10B981",
        "genres": ["adventure", "comedy", "music"],
        "energy": "match",
        "mr_dp_tone": "cheerful and fun"
    },
    "tired": {
        "emoji": "😴",
        "color": "#8B5CF6",
        "genres": ["nature", "documentary", "ambient"],
        "energy": "low",
        "mr_dp_tone": "soothing and brief"
    },
    "energetic": {
        "emoji": "⚡",
        "color": "#F97316",
        "genres": ["action", "sports", "dance"],
        "energy": "high",
        "mr_dp_tone": "high-energy and quick"
    },
    "focused": {
        "emoji": "🎯",
        "color": "#06B6D4",
        "genres": ["documentary", "educational", "ambient"],
        "energy": "medium",
        "mr_dp_tone": "direct and helpful"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT TYPES
# ═══════════════════════════════════════════════════════════════════════════════

CONTENT_TYPES = {
    "movies": {
        "emoji": "🎬",
        "label": "Movies",
        "api": "tmdb",
        "enabled": True,
    },
    "tv": {
        "emoji": "📺",
        "label": "TV Shows",
        "api": "tmdb",
        "enabled": True,
    },
    "music": {
        "emoji": "🎵",
        "label": "Music",
        "api": "spotify",
        "enabled": True,
    },
    "podcasts": {
        "emoji": "🎙️",
        "label": "Podcasts",
        "api": "spotify",
        "enabled": True,
    },
    "audiobooks": {
        "emoji": "📚",
        "label": "Audiobooks",
        "api": "audible",
        "enabled": False,  # Coming soon
    },
    "shorts": {
        "emoji": "⚡",
        "label": "Shorts",
        "api": "youtube",
        "enabled": True,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SOCIAL FEATURES CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

SOCIAL_CONFIG = {
    "max_friends": 500,
    "max_dm_length": 2000,
    "max_watch_party_size": 10,
    "watch_party_sync_interval_ms": 1000,

    "privacy_defaults": {
        "profile_visibility": "private",  # public, friends, private
        "show_activity": False,
        "show_watch_history": False,
    },

    "notifications": {
        "friend_requests": True,
        "messages": True,
        "watch_party_invites": True,
        "friend_activity": False,
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

PAGES = {
    "home": {"icon": "🏠", "label": "Home", "auth_required": True},
    "discover": {"icon": "🔍", "label": "Discover", "auth_required": True},
    "chat": {"icon": "💬", "label": "Mr.DP", "auth_required": True},
    "queue": {"icon": "📋", "label": "My Queue", "auth_required": True},
    "friends": {"icon": "👥", "label": "Friends", "auth_required": True},
    "profile": {"icon": "👤", "label": "Profile", "auth_required": True},
    "settings": {"icon": "⚙️", "label": "Settings", "auth_required": True},
    "premium": {"icon": "⭐", "label": "Premium", "auth_required": False},
}

# ═══════════════════════════════════════════════════════════════════════════════
# STREAMLIT PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

def get_page_config():
    """Return Streamlit page configuration."""
    return {
        "page_title": f"{APP_NAME} | {APP_TAGLINE}",
        "page_icon": "🧠",
        "layout": "wide",
        "initial_sidebar_state": "collapsed",
        "menu_items": {
            "Get Help": f"{APP_URL}/help",
            "Report a bug": "https://github.com/ZamoritaCR/neurostream-v1/issues",
            "About": f"# {APP_NAME}\n{APP_TAGLINE}\n\nBuilt for ADHD brains.",
        }
    }
