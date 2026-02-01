"""
═══════════════════════════════════════════════════════════════════════════════
USER API ROUTES
User profile, preferences, and learning data.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from services.mr_dp.learning import get_learning_service, EventType

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class TrackEventRequest(BaseModel):
    user_id: str
    event_type: str
    data: Optional[dict] = None


class MoodLogRequest(BaseModel):
    user_id: str
    mood: str
    context: Optional[str] = None  # before_content, after_content, general


class ContentInteractionRequest(BaseModel):
    user_id: str
    content_id: str
    content_type: str
    title: str
    genres: Optional[List[str]] = None
    duration_minutes: Optional[float] = None
    mood: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# LEARNING & TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/track/event")
async def track_event(request: TrackEventRequest):
    """
    Track a user event for learning.

    Event types:
    - content_view, content_complete, content_skip, content_save, content_rate
    - search_query, search_click
    - mood_select, mood_transition
    - session_start, session_end
    """
    learning = get_learning_service()

    try:
        event_type = EventType(request.event_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid event type: {request.event_type}")

    await learning.track_event(
        user_id=request.user_id,
        event_type=event_type,
        data=request.data or {}
    )

    return {"status": "tracked", "event_type": request.event_type}


@router.post("/track/content-view")
async def track_content_view(request: ContentInteractionRequest):
    """Track when user views/starts content."""
    learning = get_learning_service()

    await learning.track_event(
        request.user_id,
        EventType.CONTENT_VIEW,
        {
            "content_id": request.content_id,
            "content_type": request.content_type,
            "title": request.title,
            "genres": request.genres or [],
            "mood": request.mood
        }
    )

    return {"status": "tracked", "action": "content_view"}


@router.post("/track/content-complete")
async def track_content_complete(
    user_id: str,
    content_id: str,
    watch_time_minutes: float,
    duration_minutes: float
):
    """Track when user completes content."""
    learning = get_learning_service()

    await learning.track_event(
        user_id,
        EventType.CONTENT_COMPLETE,
        {
            "content_id": content_id,
            "watch_time_minutes": watch_time_minutes,
            "duration_minutes": duration_minutes
        }
    )

    return {"status": "tracked", "action": "content_complete"}


@router.post("/track/content-skip")
async def track_content_skip(
    user_id: str,
    content_id: str,
    skip_at_minutes: float,
    duration_minutes: float,
    genres: Optional[List[str]] = None
):
    """Track when user skips/abandons content."""
    learning = get_learning_service()

    await learning.track_event(
        user_id,
        EventType.CONTENT_SKIP,
        {
            "content_id": content_id,
            "skip_at_minutes": skip_at_minutes,
            "duration_minutes": duration_minutes,
            "genres": genres or []
        }
    )

    return {"status": "tracked", "action": "content_skip"}


@router.post("/track/mood")
async def track_mood(request: MoodLogRequest):
    """Log user's current mood."""
    learning = get_learning_service()

    await learning.track_event(
        request.user_id,
        EventType.MOOD_SELECT,
        {
            "mood": request.mood,
            "context": request.context
        }
    )

    return {"status": "tracked", "mood": request.mood}


@router.post("/track/mood-transition")
async def track_mood_transition(
    user_id: str,
    from_mood: str,
    to_mood: str,
    content_id: Optional[str] = None
):
    """Track mood change after consuming content."""
    learning = get_learning_service()

    await learning.track_event(
        user_id,
        EventType.MOOD_TRANSITION,
        {
            "from_mood": from_mood,
            "to_mood": to_mood,
            "content_id": content_id
        }
    )

    return {
        "status": "tracked",
        "transition": f"{from_mood} -> {to_mood}"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PREFERENCES & PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """Get learned user preferences."""
    learning = get_learning_service()

    profile = learning.get_profile(user_id)
    if not profile:
        return {
            "user_id": user_id,
            "has_data": False,
            "message": "No learning data yet. Keep using dopamine.watch!"
        }

    return {
        "user_id": user_id,
        "has_data": True,
        "preferences": {
            "top_genres": learning.get_genre_preferences(user_id, top_n=5),
            "favorite_content_types": dict(list(profile.favorite_content_types.items())[:5]),
            "preferred_duration": {
                "min": profile.preferred_duration[0],
                "max": profile.preferred_duration[1]
            },
            "attention_span": profile.attention_span_estimate,
            "avg_session_duration": profile.avg_session_duration
        },
        "patterns": {
            "common_moods": dict(list(profile.common_moods.items())[:5]),
            "peak_hours": dict(sorted(profile.active_hours.items(), key=lambda x: -x[1])[:5]),
            "optimal_time": learning.get_optimal_time(user_id)
        }
    }


@router.get("/patterns/{user_id}")
async def get_user_patterns(user_id: str):
    """Analyze and return detected patterns."""
    learning = get_learning_service()

    patterns = await learning.analyze_patterns(user_id)

    return {
        "user_id": user_id,
        "patterns": [
            {
                "type": p.pattern_type,
                "description": p.description,
                "confidence": round(p.confidence, 2),
                "data": p.data
            }
            for p in patterns
        ],
        "insights": _generate_insights(patterns)
    }


def _generate_insights(patterns) -> List[str]:
    """Generate human-readable insights from patterns."""
    insights = []

    for pattern in patterns:
        if pattern.pattern_type == "binge_watching":
            insights.append(f"You've been enjoying {pattern.data.get('content_type', 'content')} lately!")
        elif pattern.pattern_type == "mood_genre_correlation":
            mood = pattern.data.get("mood", "")
            genre = pattern.data.get("genre", "")
            insights.append(f"When you're {mood}, you tend to enjoy {genre} content")
        elif pattern.pattern_type == "peak_usage_time":
            time = pattern.data.get("time_label", "")
            insights.append(f"You're most active in the {time}")
        elif pattern.pattern_type == "genre_fatigue":
            genre = pattern.data.get("genre", "")
            insights.append(f"You might want to take a break from {genre} content")
        elif pattern.pattern_type == "short_attention_span":
            insights.append("Shorter content works best for you - we'll prioritize quick watches!")
        elif pattern.pattern_type == "long_attention_span":
            insights.append("You can handle longer content - great for movie marathons!")

    return insights


@router.get("/recommendations/{user_id}")
async def get_personalized_recommendations(
    user_id: str,
    mood: Optional[str] = None,
    content_type: Optional[str] = None
):
    """Get personalized recommendation parameters."""
    learning = get_learning_service()

    # Get mood-specific genres
    if mood:
        genre_weights = learning.get_mood_recommendations(user_id, mood)
    else:
        genre_weights = dict(learning.get_genre_preferences(user_id, top_n=5))

    # Get duration recommendation
    duration = learning.get_duration_recommendation(user_id)

    # Check if variety needed
    needs_variety = learning.should_suggest_variety(user_id)

    return {
        "user_id": user_id,
        "mood": mood,
        "recommendation_params": {
            "preferred_genres": genre_weights,
            "duration": duration,
            "needs_variety": needs_variety,
            "content_type": content_type
        },
        "tips": [
            f"Ideal content length: {duration['ideal']} minutes",
            "Variety suggested!" if needs_variety else "Stick to your favorites!"
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/profile/{user_id}/export")
async def export_profile(user_id: str):
    """Export user's learning profile."""
    learning = get_learning_service()

    data = learning.export_profile(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="No profile data found")

    return {"profile": data}


@router.post("/profile/{user_id}/import")
async def import_profile(user_id: str, profile_data: dict):
    """Import user's learning profile."""
    learning = get_learning_service()

    profile = learning.import_profile(user_id, profile_data)

    return {
        "status": "imported",
        "user_id": user_id,
        "preferences_loaded": len(profile.favorite_genres) > 0
    }


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user's viewing statistics."""
    learning = get_learning_service()

    profile = learning.get_profile(user_id)
    if not profile:
        return {"user_id": user_id, "has_data": False}

    # Calculate stats
    total_interactions = len(profile.content_interactions)
    total_completions = sum(
        i.completion_count for i in profile.content_interactions.values()
    )
    total_watch_time = sum(
        i.total_watch_time for i in profile.content_interactions.values()
    )

    return {
        "user_id": user_id,
        "has_data": True,
        "stats": {
            "total_content_viewed": total_interactions,
            "total_completions": total_completions,
            "total_watch_time_hours": round(total_watch_time / 60, 1),
            "avg_session_minutes": round(profile.avg_session_duration, 1),
            "attention_span_minutes": round(profile.attention_span_estimate, 1),
            "hyperfocus_count": len(profile.hyperfocus_content),
            "events_tracked": len(profile.events)
        },
        "activity": {
            "most_active_hour": learning.get_optimal_time(user_id),
            "top_moods": list(profile.common_moods.keys())[:3]
        }
    }
