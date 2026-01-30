"""
Dopamine.watch Time-Aware Micro-Picks
Feature: Content Recommendations Based on Available Time (Phase 2)

"I have 15 minutes" -> Get content that fits that time slot
"""
import streamlit as st
from datetime import datetime


# Time brackets for content filtering
TIME_BRACKETS = {
    "5_min": {"label": "5 min", "emoji": "⚡", "max_minutes": 5, "description": "Quick dopamine hit"},
    "15_min": {"label": "15 min", "emoji": "☕", "max_minutes": 15, "description": "Coffee break"},
    "30_min": {"label": "30 min", "emoji": "🍿", "max_minutes": 30, "description": "Short break"},
    "60_min": {"label": "1 hour", "emoji": "🎬", "max_minutes": 60, "description": "Movie time"},
    "90_min": {"label": "90+ min", "emoji": "🛋️", "max_minutes": 999, "description": "Full experience"},
}

# Content type typical durations (in minutes)
CONTENT_DURATIONS = {
    "movie": {"short": (60, 90), "medium": (90, 120), "long": (120, 180)},
    "tv_episode": {"short": (20, 30), "medium": (40, 50), "long": (55, 70)},
    "podcast_episode": {"short": (15, 30), "medium": (30, 60), "long": (60, 120)},
    "music_album": {"short": (20, 35), "medium": (35, 50), "long": (50, 80)},
    "audiobook_chapter": {"short": (15, 30), "medium": (30, 45), "long": (45, 90)},
    "youtube_video": {"short": (5, 15), "medium": (15, 30), "long": (30, 60)},
}

# Quick content suggestions by time bracket
QUICK_PICKS = {
    "5_min": [
        {"type": "youtube", "title": "ADHD Quick Tips", "duration": "3-5 min", "category": "educational"},
        {"type": "music", "title": "Pump-up Song", "duration": "3-4 min", "category": "energy"},
        {"type": "breathing", "title": "Quick Breathing Exercise", "duration": "2-3 min", "category": "calm"},
        {"type": "tiktok", "title": "Curated TikTok Scroll", "duration": "5 min", "category": "fun"},
    ],
    "15_min": [
        {"type": "tv", "title": "Animated Short", "duration": "10-15 min", "category": "entertainment"},
        {"type": "podcast", "title": "Daily News Brief", "duration": "10-15 min", "category": "informative"},
        {"type": "youtube", "title": "TED-Ed Video", "duration": "10-12 min", "category": "educational"},
        {"type": "meditation", "title": "Guided Meditation", "duration": "10-15 min", "category": "calm"},
    ],
    "30_min": [
        {"type": "tv", "title": "Sitcom Episode", "duration": "22-25 min", "category": "comedy"},
        {"type": "podcast", "title": "Podcast Episode", "duration": "25-35 min", "category": "various"},
        {"type": "documentary", "title": "Short Doc", "duration": "25-30 min", "category": "educational"},
        {"type": "youtube", "title": "Video Essay", "duration": "20-30 min", "category": "deep dive"},
    ],
    "60_min": [
        {"type": "tv", "title": "Drama Episode", "duration": "45-60 min", "category": "drama"},
        {"type": "movie", "title": "Short Film Collection", "duration": "50-60 min", "category": "various"},
        {"type": "podcast", "title": "Long-form Podcast", "duration": "45-60 min", "category": "deep dive"},
        {"type": "audiobook", "title": "Audiobook Chapter", "duration": "45-60 min", "category": "reading"},
    ],
    "90_min": [
        {"type": "movie", "title": "Feature Film", "duration": "90-120 min", "category": "cinema"},
        {"type": "documentary", "title": "Full Documentary", "duration": "90-120 min", "category": "educational"},
        {"type": "audiobook", "title": "Multiple Chapters", "duration": "90+ min", "category": "reading"},
        {"type": "series", "title": "2-3 Episode Binge", "duration": "90-120 min", "category": "binge"},
    ],
}


def get_time_bracket(minutes: int) -> str:
    """Get the appropriate time bracket for given minutes."""
    if minutes <= 5:
        return "5_min"
    elif minutes <= 15:
        return "15_min"
    elif minutes <= 30:
        return "30_min"
    elif minutes <= 60:
        return "60_min"
    else:
        return "90_min"


def filter_movies_by_runtime(movies: list, max_minutes: int) -> list:
    """
    Filter movie list to only include those under max_minutes runtime.

    Args:
        movies: List of movie dicts with 'runtime' field (in minutes)
        max_minutes: Maximum runtime to include
    """
    if max_minutes >= 999:
        return movies  # No filter for "unlimited" time

    return [m for m in movies if m.get('runtime', 0) and m.get('runtime', 0) <= max_minutes]


def filter_tv_by_episode_length(shows: list, max_minutes: int) -> list:
    """
    Filter TV shows by typical episode length.
    Shows with shorter episodes are prioritized for shorter time slots.
    """
    short_ep_genres = [10765, 16, 35, 10767]  # Animation, Comedy, Talk shows

    if max_minutes <= 30:
        return [s for s in shows if any(g in s.get('genre_ids', []) for g in short_ep_genres)]
    return shows


def get_suggestions_for_time(minutes: int, current_feeling: str = None, desired_feeling: str = None) -> dict:
    """
    Get content suggestions based on available time.

    Returns dict with:
        - bracket: Time bracket info
        - suggestions: List of quick picks
        - tips: Helpful tips for this time slot
    """
    bracket_key = get_time_bracket(minutes)
    bracket = TIME_BRACKETS[bracket_key]
    suggestions = QUICK_PICKS.get(bracket_key, [])

    # Tips based on time available
    tips = {
        "5_min": "Perfect for a quick reset! Don't overthink it.",
        "15_min": "Great for a coffee break. One focused piece of content.",
        "30_min": "Sweet spot for a full episode or deep dive video.",
        "60_min": "Time for something substantial. Enjoy without rushing!",
        "90_min": "Full immersion time. You've got space to really sink in.",
    }

    return {
        "bracket": bracket,
        "bracket_key": bracket_key,
        "suggestions": suggestions,
        "tip": tips.get(bracket_key, ""),
        "minutes_available": minutes
    }


def render_time_picker():
    """
    Render the time picker UI component.

    Returns selected minutes, or None if not selected.
    """
    st.markdown("### ⏰ How Much Time Do You Have?")
    st.caption("We'll find content that fits your schedule")

    # Quick select buttons
    cols = st.columns(5)
    selected = None

    for i, (key, bracket) in enumerate(TIME_BRACKETS.items()):
        with cols[i]:
            if st.button(
                f"{bracket['emoji']}\n{bracket['label']}",
                key=f"time_{key}",
                use_container_width=True
            ):
                selected = bracket['max_minutes']
                st.session_state.time_available = selected

    # Or custom input
    st.markdown("---")
    custom = st.number_input(
        "Or enter exact minutes:",
        min_value=1,
        max_value=300,
        value=st.session_state.get('time_available', 30),
        step=5,
        key="custom_time"
    )

    if custom:
        st.session_state.time_available = custom

    return st.session_state.get('time_available')


def render_time_based_recommendations(st_instance, time_minutes: int,
                                       current_feeling: str = None,
                                       desired_feeling: str = None):
    """
    Render recommendations based on available time.
    """
    suggestions = get_suggestions_for_time(time_minutes, current_feeling, desired_feeling)
    bracket = suggestions['bracket']

    st_instance.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(6, 182, 212, 0.15));
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid rgba(139, 92, 246, 0.2);
    ">
        <div style="font-size: 2rem; margin-bottom: 10px;">
            {bracket['emoji']} {time_minutes} minutes
        </div>
        <div style="color: #94a3b8; font-size: 1rem;">
            {bracket['description']} • {suggestions['tip']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st_instance.markdown("#### Perfect for this time slot:")

    cols = st_instance.columns(2)
    for i, suggestion in enumerate(suggestions['suggestions']):
        with cols[i % 2]:
            st_instance.markdown(f"""
            <div style="
                background: rgba(30, 30, 40, 0.6);
                border-radius: 12px;
                padding: 16px;
                margin: 8px 0;
                border: 1px solid rgba(139, 92, 246, 0.2);
            ">
                <div style="font-weight: bold; color: #e2e8f0;">
                    {suggestion['title']}
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem;">
                    {suggestion['type'].upper()} • {suggestion['duration']}
                </div>
            </div>
            """, unsafe_allow_html=True)


def get_time_of_day_suggestions() -> dict:
    """
    Get suggestions based on current time of day.
    ADHD-aware: different energy levels at different times.
    """
    hour = datetime.now().hour

    if 5 <= hour < 9:
        return {
            "period": "Early Morning",
            "emoji": "🌅",
            "energy": "low-medium",
            "suggestion": "Light content to ease into the day. Coffee + short podcast?",
            "recommended_types": ["podcast", "music", "light_comedy"]
        }
    elif 9 <= hour < 12:
        return {
            "period": "Morning",
            "emoji": "☀️",
            "energy": "high",
            "suggestion": "Peak focus time! Educational content or engaging docs.",
            "recommended_types": ["documentary", "educational", "ted_talk"]
        }
    elif 12 <= hour < 14:
        return {
            "period": "Lunch",
            "emoji": "🍽️",
            "energy": "medium",
            "suggestion": "Perfect for a sitcom episode or fun podcast.",
            "recommended_types": ["comedy", "podcast", "light_content"]
        }
    elif 14 <= hour < 17:
        return {
            "period": "Afternoon",
            "emoji": "⏰",
            "energy": "medium-low",
            "suggestion": "Afternoon slump? Upbeat music or something stimulating.",
            "recommended_types": ["music", "action", "thriller"]
        }
    elif 17 <= hour < 20:
        return {
            "period": "Evening",
            "emoji": "🌆",
            "energy": "medium",
            "suggestion": "Wind-down time. Movies or engaging series.",
            "recommended_types": ["movie", "drama", "series"]
        }
    elif 20 <= hour < 23:
        return {
            "period": "Night",
            "emoji": "🌙",
            "energy": "low",
            "suggestion": "Cozy content time. Nothing too stimulating if sleep is soon!",
            "recommended_types": ["comfort_show", "audiobook", "calm_content"]
        }
    else:
        return {
            "period": "Late Night",
            "emoji": "🦉",
            "energy": "variable",
            "suggestion": "Night owl mode! Whatever captures your attention.",
            "recommended_types": ["any", "rabbit_hole", "deep_content"]
        }
