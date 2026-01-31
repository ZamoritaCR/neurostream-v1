# user_learning.py
# --------------------------------------------------
# DOPAMINE.WATCH - USER LEARNING SYSTEM
# --------------------------------------------------
# Features:
# 1. Event Tracking (17 event types)
# 2. Pattern Detection (binge, mood, attention)
# 3. Genre & Content Preferences
# 4. ADHD-Optimized Personalization
# 5. Mr.DP Context Generation
# --------------------------------------------------

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import math

# --------------------------------------------------
# 1. EVENT TYPES
# --------------------------------------------------

class EventType(Enum):
    """Types of user events to track."""
    # Content interactions
    CONTENT_VIEW = "content_view"
    CONTENT_COMPLETE = "content_complete"
    CONTENT_SKIP = "content_skip"
    CONTENT_SAVE = "content_save"
    CONTENT_SHARE = "content_share"
    CONTENT_RATE = "content_rate"

    # Search behavior
    SEARCH_QUERY = "search_query"
    SEARCH_CLICK = "search_click"

    # Mood tracking
    MOOD_SELECT = "mood_select"
    MOOD_TRANSITION = "mood_transition"

    # Session behavior
    SESSION_START = "session_start"
    SESSION_END = "session_end"

    # Mr.DP interactions
    MRDP_CHAT = "mrdp_chat"
    MRDP_SUGGESTION_ACCEPT = "mrdp_suggestion_accept"
    MRDP_SUGGESTION_REJECT = "mrdp_suggestion_reject"

    # Wellness
    SOS_MODE_USED = "sos_mode_used"
    FOCUS_SESSION = "focus_session"


# --------------------------------------------------
# 2. DATA CLASSES
# --------------------------------------------------

@dataclass
class UserEvent:
    """A tracked user event."""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPattern:
    """Detected patterns in user behavior."""
    pattern_type: str
    confidence: float  # 0-1
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserProfile:
    """Learned user profile and preferences."""
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Content preferences
    favorite_genres: Dict[str, float] = field(default_factory=dict)
    favorite_content_types: Dict[str, float] = field(default_factory=dict)
    preferred_duration: Tuple[int, int] = (30, 120)  # min, max minutes

    # Mood patterns
    common_moods: Dict[str, float] = field(default_factory=dict)
    mood_to_content: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Time patterns
    active_hours: Dict[int, float] = field(default_factory=dict)
    active_days: Dict[int, float] = field(default_factory=dict)
    avg_session_duration: float = 30

    # ADHD-specific patterns
    attention_span_estimate: float = 45  # minutes
    preferred_content_length: str = "medium"
    needs_variety: bool = True

    # Detected patterns
    patterns: List[UserPattern] = field(default_factory=list)

    # Event history
    events: List[UserEvent] = field(default_factory=list)


# --------------------------------------------------
# 3. STORAGE
# --------------------------------------------------

def _get_learning_storage() -> Dict[str, UserProfile]:
    """Get learning storage from session state."""
    if 'user_learning_profiles' not in st.session_state:
        st.session_state.user_learning_profiles = {}
    return st.session_state.user_learning_profiles


def _get_or_create_profile(user_id: str) -> UserProfile:
    """Get or create user profile."""
    storage = _get_learning_storage()
    if user_id not in storage:
        storage[user_id] = UserProfile(user_id=user_id)
    return storage[user_id]


# --------------------------------------------------
# 4. EVENT TRACKING
# --------------------------------------------------

def track_learning_event(
    user_id: str,
    event_type: EventType,
    data: Dict[str, Any] = None
) -> None:
    """
    Track a user event for learning.

    Args:
        user_id: User's ID
        event_type: Type of event
        data: Event-specific data
    """
    profile = _get_or_create_profile(user_id)

    event = UserEvent(
        event_type=event_type,
        timestamp=datetime.utcnow(),
        data=data or {}
    )

    profile.events.append(event)

    # Keep only last 1000 events
    if len(profile.events) > 1000:
        profile.events = profile.events[-1000:]

    # Process event
    _process_event(profile, event)
    profile.updated_at = datetime.utcnow()


def _process_event(profile: UserProfile, event: UserEvent) -> None:
    """Process an event and update learned data."""
    if event.event_type == EventType.CONTENT_VIEW:
        _process_content_view(profile, event)
    elif event.event_type == EventType.CONTENT_COMPLETE:
        _process_content_complete(profile, event)
    elif event.event_type == EventType.CONTENT_SKIP:
        _process_content_skip(profile, event)
    elif event.event_type == EventType.MOOD_SELECT:
        _process_mood_select(profile, event)
    elif event.event_type == EventType.SESSION_START:
        _process_session_start(profile, event)
    elif event.event_type == EventType.SESSION_END:
        _process_session_end(profile, event)
    elif event.event_type == EventType.MRDP_SUGGESTION_ACCEPT:
        _process_suggestion_response(profile, event, accepted=True)
    elif event.event_type == EventType.MRDP_SUGGESTION_REJECT:
        _process_suggestion_response(profile, event, accepted=False)


def _process_content_view(profile: UserProfile, event: UserEvent) -> None:
    """Process content view event."""
    genres = event.data.get("genres", [])
    content_type = event.data.get("content_type", "movie")

    # Update genre preferences
    for genre in genres:
        profile.favorite_genres[genre] = profile.favorite_genres.get(genre, 0) + 1

    # Update content type preferences
    profile.favorite_content_types[content_type] = (
        profile.favorite_content_types.get(content_type, 0) + 1
    )


def _process_content_complete(profile: UserProfile, event: UserEvent) -> None:
    """Process content completion."""
    genres = event.data.get("genres", [])
    duration = event.data.get("duration_minutes", 0)
    mood = event.data.get("mood")

    # Boost genres for completed content
    for genre in genres:
        profile.favorite_genres[genre] = profile.favorite_genres.get(genre, 0) + 2

    # Update mood→content mapping
    if mood and genres:
        if mood not in profile.mood_to_content:
            profile.mood_to_content[mood] = {}
        for genre in genres:
            profile.mood_to_content[mood][genre] = (
                profile.mood_to_content[mood].get(genre, 0) + 1
            )

    # Update duration preference
    if duration > 0:
        min_pref, max_pref = profile.preferred_duration
        if duration > max_pref:
            max_pref = int(duration * 1.1)
        profile.preferred_duration = (min_pref, max_pref)

        # Update attention span estimate
        if duration > profile.attention_span_estimate:
            profile.attention_span_estimate = (
                profile.attention_span_estimate * 0.9 + duration * 0.1
            )


def _process_content_skip(profile: UserProfile, event: UserEvent) -> None:
    """Process content skip."""
    skip_time = event.data.get("watch_time_minutes", 0)
    genres = event.data.get("genres", [])

    # Slightly decrease genre preference
    for genre in genres:
        profile.favorite_genres[genre] = max(
            0, profile.favorite_genres.get(genre, 0) - 0.5
        )

    # Update attention estimate
    if skip_time > 0 and skip_time < profile.attention_span_estimate:
        profile.attention_span_estimate = (
            profile.attention_span_estimate * 0.95 + skip_time * 0.05
        )


def _process_mood_select(profile: UserProfile, event: UserEvent) -> None:
    """Process mood selection."""
    mood = event.data.get("mood")
    if mood:
        profile.common_moods[mood] = profile.common_moods.get(mood, 0) + 1


def _process_session_start(profile: UserProfile, event: UserEvent) -> None:
    """Process session start."""
    hour = datetime.utcnow().hour
    day = datetime.utcnow().weekday()
    profile.active_hours[hour] = profile.active_hours.get(hour, 0) + 1
    profile.active_days[day] = profile.active_days.get(day, 0) + 1


def _process_session_end(profile: UserProfile, event: UserEvent) -> None:
    """Process session end."""
    duration = event.data.get("duration_minutes", 0)
    if duration > 0:
        profile.avg_session_duration = (
            profile.avg_session_duration * 0.9 + duration * 0.1
        )


def _process_suggestion_response(
    profile: UserProfile,
    event: UserEvent,
    accepted: bool
) -> None:
    """Process Mr.DP suggestion response."""
    genres = event.data.get("genres", [])

    if accepted:
        for genre in genres:
            profile.favorite_genres[genre] = (
                profile.favorite_genres.get(genre, 0) + 1.5
            )
    else:
        for genre in genres:
            profile.favorite_genres[genre] = max(
                0, profile.favorite_genres.get(genre, 0) - 0.5
            )


def init_learning_session(user_id: str) -> None:
    """Initialize a new learning session."""
    track_learning_event(user_id, EventType.SESSION_START, {
        "timestamp": datetime.utcnow().isoformat()
    })


# --------------------------------------------------
# 5. PATTERN DETECTION
# --------------------------------------------------

def analyze_user_patterns(user_id: str) -> List[Dict]:
    """Analyze user behavior and detect patterns."""
    profile = _get_learning_storage().get(user_id)
    if not profile:
        return []

    patterns = []

    # Detect binge pattern
    binge = _detect_binge_pattern(profile)
    if binge:
        patterns.append(binge)

    # Detect mood pattern
    mood = _detect_mood_pattern(profile)
    if mood:
        patterns.append(mood)

    # Detect attention pattern
    attention = _detect_attention_pattern(profile)
    if attention:
        patterns.append(attention)

    # Detect time pattern
    time = _detect_time_pattern(profile)
    if time:
        patterns.append(time)

    # Store patterns
    profile.patterns = [
        UserPattern(
            pattern_type=p["type"],
            confidence=p["confidence"],
            description=p["description"],
            data=p.get("data", {})
        ) for p in patterns
    ]

    return patterns


def _detect_binge_pattern(profile: UserProfile) -> Optional[Dict]:
    """Detect binge-watching behavior."""
    recent_events = [
        e for e in profile.events
        if e.event_type == EventType.CONTENT_COMPLETE
        and (datetime.utcnow() - e.timestamp) < timedelta(days=7)
    ]

    if len(recent_events) < 5:
        return None

    type_counts = defaultdict(int)
    for event in recent_events:
        content_type = event.data.get("content_type", "unknown")
        type_counts[content_type] += 1

    for content_type, count in type_counts.items():
        if count >= 5:
            return {
                "type": "binge_watching",
                "confidence": min(1.0, count / 10),
                "description": f"You tend to binge {content_type} content",
                "data": {"content_type": content_type, "weekly_count": count}
            }

    return None


def _detect_mood_pattern(profile: UserProfile) -> Optional[Dict]:
    """Detect mood-based content selection pattern."""
    if not profile.mood_to_content:
        return None

    for mood, genres in profile.mood_to_content.items():
        if genres:
            top_genre = max(genres.items(), key=lambda x: x[1])
            if top_genre[1] >= 3:
                return {
                    "type": "mood_preference",
                    "confidence": min(1.0, top_genre[1] / 5),
                    "description": f"When {mood}, you prefer {top_genre[0]}",
                    "data": {"mood": mood, "genre": top_genre[0]}
                }

    return None


def _detect_attention_pattern(profile: UserProfile) -> Optional[Dict]:
    """Detect attention span pattern."""
    attention_span = profile.attention_span_estimate

    if attention_span < 30:
        return {
            "type": "short_attention_span",
            "confidence": 0.8,
            "description": "You prefer shorter content (under 30 min)",
            "data": {"estimated_span": attention_span, "recommendation": "short"}
        }
    elif attention_span > 90:
        return {
            "type": "long_attention_span",
            "confidence": 0.8,
            "description": "You can engage with longer content (90+ min)",
            "data": {"estimated_span": attention_span, "recommendation": "long"}
        }

    return None


def _detect_time_pattern(profile: UserProfile) -> Optional[Dict]:
    """Detect time-based viewing pattern."""
    if not profile.active_hours:
        return None

    peak_hour = max(profile.active_hours.items(), key=lambda x: x[1])
    total_activity = sum(profile.active_hours.values())

    if total_activity < 5:
        return None

    if peak_hour[1] / total_activity > 0.3:
        time_label = _hour_to_label(peak_hour[0])
        return {
            "type": "time_preference",
            "confidence": peak_hour[1] / total_activity,
            "description": f"You're most active in the {time_label}",
            "data": {"peak_hour": peak_hour[0], "time_label": time_label}
        }

    return None


def _hour_to_label(hour: int) -> str:
    """Convert hour to human-readable label."""
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "late night"


# --------------------------------------------------
# 6. PREFERENCE GETTERS
# --------------------------------------------------

def get_genre_preferences(user_id: str, top_n: int = 5) -> List[Tuple[str, float]]:
    """Get user's top genre preferences."""
    profile = _get_learning_storage().get(user_id)
    if not profile or not profile.favorite_genres:
        return []

    total = sum(profile.favorite_genres.values())
    if total == 0:
        return []

    normalized = {
        genre: score / total
        for genre, score in profile.favorite_genres.items()
    }

    return sorted(normalized.items(), key=lambda x: x[1], reverse=True)[:top_n]


def get_mood_recommendations(user_id: str, current_mood: str) -> Dict[str, float]:
    """Get genre recommendations based on current mood."""
    profile = _get_learning_storage().get(user_id)
    if not profile:
        return {}

    mood_genres = profile.mood_to_content.get(current_mood, {})
    if not mood_genres:
        # Fall back to general preferences
        return dict(get_genre_preferences(user_id, top_n=5))

    total = sum(mood_genres.values())
    if total == 0:
        return {}

    return {
        genre: score / total
        for genre, score in sorted(
            mood_genres.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
    }


def get_duration_recommendation(user_id: str) -> Dict[str, Any]:
    """Get content duration recommendation for user."""
    profile = _get_learning_storage().get(user_id)
    if not profile:
        return {"min": 30, "max": 120, "ideal": 60}

    min_dur, max_dur = profile.preferred_duration
    attention = profile.attention_span_estimate

    return {
        "min": min_dur,
        "max": max_dur,
        "ideal": int(attention),
        "attention_span": attention
    }


def get_optimal_viewing_time(user_id: str) -> Optional[int]:
    """Get user's optimal viewing time (hour of day)."""
    profile = _get_learning_storage().get(user_id)
    if not profile or not profile.active_hours:
        return None
    return max(profile.active_hours.items(), key=lambda x: x[1])[0]


def should_suggest_variety(user_id: str) -> bool:
    """Check if user needs content variety suggestion."""
    profile = _get_learning_storage().get(user_id)
    if not profile:
        return False

    # Check for repetitive viewing
    if profile.favorite_genres:
        top_genre_score = max(profile.favorite_genres.values())
        total_score = sum(profile.favorite_genres.values())
        if total_score > 0 and top_genre_score / total_score > 0.6:
            return True

    return False


# --------------------------------------------------
# 7. MR.DP CONTEXT
# --------------------------------------------------

def get_mrdp_personalization_context(user_id: str) -> Dict[str, Any]:
    """
    Get context for Mr.DP to personalize responses.

    Returns personality adjustments and user-specific info.
    """
    profile = _get_learning_storage().get(user_id)
    if not profile:
        return {}

    # Analyze patterns
    patterns = analyze_user_patterns(user_id)

    context = {
        "user_profile": {
            "top_genres": get_genre_preferences(user_id, top_n=3),
            "preferred_duration": profile.preferred_duration,
            "attention_span": profile.attention_span_estimate,
            "common_moods": list(profile.common_moods.keys())[:3] if profile.common_moods else [],
            "total_interactions": len(profile.events)
        },
        "patterns": patterns[:5],
        "suggestions": {
            "suggest_variety": should_suggest_variety(user_id),
            "optimal_duration": get_duration_recommendation(user_id),
            "peak_time": get_optimal_viewing_time(user_id)
        },
        "adhd_adjustments": {
            "keep_responses_short": profile.attention_span_estimate < 45,
            "limit_options": profile.attention_span_estimate < 45,
            "prefer_familiar": not profile.needs_variety,
            "content_length_preference": profile.preferred_content_length
        }
    }

    # Add time-based context
    hour = datetime.utcnow().hour
    context["time_context"] = {
        "hour": hour,
        "time_of_day": _hour_to_label(hour),
        "is_optimal_time": hour == get_optimal_viewing_time(user_id)
    }

    return context


# --------------------------------------------------
# 8. STREAMLIT UI COMPONENTS
# --------------------------------------------------

def render_insights_dashboard(user_id: str):
    """Render user insights dashboard."""
    profile = _get_learning_storage().get(user_id)

    if not profile or len(profile.events) < 5:
        st.info("Keep using the app to see your personalized insights!")
        return

    st.markdown("### 📊 Your Viewing Insights")

    # Top genres
    top_genres = get_genre_preferences(user_id, top_n=5)
    if top_genres:
        st.markdown("#### 🎬 Your Top Genres")
        for genre, score in top_genres:
            st.progress(min(1.0, score), text=f"{genre}: {score*100:.0f}%")

    # Patterns
    patterns = analyze_user_patterns(user_id)
    if patterns:
        st.markdown("#### 🔍 Detected Patterns")
        for pattern in patterns:
            confidence_emoji = "🟢" if pattern["confidence"] > 0.7 else "🟡" if pattern["confidence"] > 0.4 else "🔴"
            st.markdown(f"{confidence_emoji} **{pattern['type'].replace('_', ' ').title()}**: {pattern['description']}")

    # Duration recommendation
    duration = get_duration_recommendation(user_id)
    st.markdown("#### ⏱️ Your Attention Profile")
    st.markdown(f"""
    - **Ideal content length**: {duration['ideal']} minutes
    - **Attention span estimate**: {duration['attention_span']:.0f} minutes
    - **Preferred range**: {duration['min']}-{duration['max']} minutes
    """)

    # Activity patterns
    if profile.active_hours:
        st.markdown("#### 🕐 When You're Most Active")
        optimal = get_optimal_viewing_time(user_id)
        if optimal is not None:
            st.markdown(f"Peak activity: **{_hour_to_label(optimal)}** ({optimal}:00)")


def render_pattern_notification(pattern: Dict):
    """Render a pattern notification."""
    st.info(f"📊 **Insight**: {pattern.get('description', 'Pattern detected')}")
