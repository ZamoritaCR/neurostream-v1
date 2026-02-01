"""
Wellness API Routes
SOS calm mode, focus timer, and mental health support.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from services.wellness import (
    get_sos_service,
    get_focus_service,
    SessionType
)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SOSLogRequest(BaseModel):
    user_id: str
    technique: Optional[str] = None
    duration_seconds: int = 0
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None


class FocusSessionRequest(BaseModel):
    user_id: str
    session_type: str = "standard"
    custom_duration: Optional[int] = None
    content_id: Optional[str] = None
    content_title: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# SOS CALM MODE ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/sos")
async def get_sos_content(mood: Optional[str] = None):
    """
    Get complete SOS calm mode content package.

    Includes breathing exercises, grounding techniques,
    calming videos, and affirmations.
    """
    service = get_sos_service()
    return service.get_content(mood)


@router.get("/sos/breathing")
async def get_all_breathing_exercises():
    """Get all available breathing exercises."""
    service = get_sos_service()
    return {
        "exercises": service.all_breathing()
    }


@router.get("/sos/breathing/{exercise_id}")
async def get_breathing_exercise(exercise_id: str):
    """Get a specific breathing exercise."""
    service = get_sos_service()
    exercise = service.get_breathing(exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=404,
            detail=f"Breathing exercise not found: {exercise_id}"
        )

    return exercise


@router.get("/sos/grounding")
async def get_grounding_exercise():
    """Get the 5-4-3-2-1 grounding exercise."""
    service = get_sos_service()
    return service.get_grounding()


@router.get("/sos/videos")
async def get_calming_videos():
    """Get list of calming video suggestions."""
    service = get_sos_service()
    return {
        "videos": service.get_videos()
    }


@router.get("/sos/affirmation")
async def get_affirmation(mood: Optional[str] = None):
    """Get a random affirmation for the given mood."""
    service = get_sos_service()
    return {
        "affirmation": service.get_affirmation(mood),
        "mood": mood
    }


@router.post("/sos/log")
async def log_sos_usage(request: SOSLogRequest):
    """Log SOS mode usage for analytics."""
    service = get_sos_service()
    return service.log_usage(
        request.user_id,
        technique=request.technique,
        duration_seconds=request.duration_seconds,
        mood_before=request.mood_before,
        mood_after=request.mood_after
    )


@router.get("/sos/stats/{user_id}")
async def get_sos_stats(user_id: str):
    """Get user's SOS mode usage statistics."""
    service = get_sos_service()
    return service.stats(user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# FOCUS TIMER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/focus/presets")
async def get_focus_presets():
    """Get available focus session presets."""
    service = get_focus_service()
    return {
        "presets": service.presets()
    }


@router.post("/focus/start")
async def start_focus_session(request: FocusSessionRequest):
    """Start a new focus session."""
    try:
        session_type = SessionType(request.session_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid session type: {request.session_type}. Valid types: quick, standard, movie, binge, custom"
        )

    service = get_focus_service()
    return service.start(
        request.user_id,
        session_type=session_type,
        custom_duration=request.custom_duration,
        content_id=request.content_id,
        content_title=request.content_title
    )


@router.post("/focus/{user_id}/end")
async def end_focus_session(user_id: str, completed: bool = False):
    """End the current focus session."""
    service = get_focus_service()
    return service.end(user_id, completed)


@router.get("/focus/{user_id}/status")
async def get_focus_status(user_id: str):
    """Get current focus session status."""
    service = get_focus_service()
    return service.status(user_id)


@router.post("/focus/{user_id}/break")
async def take_break(user_id: str):
    """Record that user took a break."""
    service = get_focus_service()
    return service.take_break(user_id)


@router.get("/focus/{user_id}/should-break")
async def should_take_break(user_id: str):
    """Check if user should take a break."""
    service = get_focus_service()
    return service.should_break(user_id)


@router.get("/focus/break-activities")
async def get_break_activities():
    """Get available break activities."""
    service = get_focus_service()
    return {
        "activities": service.break_activities()
    }


@router.get("/focus/stats/{user_id}")
async def get_focus_stats(user_id: str):
    """Get user's focus session statistics."""
    service = get_focus_service()
    return service.stats(user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED WELLNESS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/wellness/{user_id}")
async def get_wellness_summary(user_id: str):
    """Get combined wellness summary for user."""
    sos_service = get_sos_service()
    focus_service = get_focus_service()

    sos_stats = sos_service.stats(user_id)
    focus_stats = focus_service.stats(user_id)
    focus_status = focus_service.status(user_id)

    return {
        "user_id": user_id,
        "sos_mode": {
            "total_uses": sos_stats["total_uses"],
            "most_used_technique": sos_stats.get("most_used_technique"),
            "last_used": sos_stats.get("last_used")
        },
        "focus_sessions": {
            "total_sessions": focus_stats["total_sessions"],
            "total_hours": focus_stats["total_hours"],
            "completion_rate": focus_stats["completion_rate"],
            "active_session": focus_status.get("active", False)
        },
        "quick_help": {
            "breathing": "Try box breathing for instant calm",
            "grounding": "Use 5-4-3-2-1 grounding technique",
            "affirmation": sos_service.get_affirmation()
        }
    }
