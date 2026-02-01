"""
Focus Timer / Pomodoro System
ADHD-friendly focus sessions with break reminders.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class SessionType(Enum):
    """Types of focus sessions."""
    QUICK = "quick"         # 25 min (Pomodoro)
    STANDARD = "standard"   # 45 min
    MOVIE = "movie"         # 90 min
    BINGE = "binge"         # 120 min
    CUSTOM = "custom"


@dataclass
class FocusSession:
    """A focus/watch session."""
    id: str
    user_id: str
    session_type: SessionType
    duration_minutes: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    content_id: Optional[str] = None
    content_title: Optional[str] = None
    breaks_taken: int = 0
    paused_duration_seconds: int = 0
    completed: bool = False


# Session presets
SESSION_PRESETS = {
    SessionType.QUICK: {
        "name": "Quick Session",
        "duration_minutes": 25,
        "break_minutes": 5,
        "description": "Perfect for a short watch or podcast episode",
        "icon": "⚡"
    },
    SessionType.STANDARD: {
        "name": "Standard Session",
        "duration_minutes": 45,
        "break_minutes": 10,
        "description": "Great for a TV episode or documentary",
        "icon": "📺"
    },
    SessionType.MOVIE: {
        "name": "Movie Time",
        "duration_minutes": 90,
        "break_minutes": 15,
        "description": "Settle in for a full movie",
        "icon": "🎬"
    },
    SessionType.BINGE: {
        "name": "Binge Mode",
        "duration_minutes": 120,
        "break_minutes": 20,
        "description": "Multiple episodes with strategic breaks",
        "icon": "🍿"
    }
}


# Break activities
BREAK_ACTIVITIES = [
    {
        "id": "stretch",
        "name": "Quick Stretch",
        "description": "Stand up and stretch your arms above your head",
        "icon": "🤸",
        "duration_seconds": 30
    },
    {
        "id": "water",
        "name": "Hydration Break",
        "description": "Get a glass of water",
        "icon": "💧",
        "duration_seconds": 60
    },
    {
        "id": "eyes",
        "name": "20-20-20 Rule",
        "description": "Look at something 20 feet away for 20 seconds",
        "icon": "👀",
        "duration_seconds": 20
    },
    {
        "id": "walk",
        "name": "Quick Walk",
        "description": "Walk around for a minute",
        "icon": "🚶",
        "duration_seconds": 60
    },
    {
        "id": "breathe",
        "name": "Deep Breaths",
        "description": "Take 5 deep breaths",
        "icon": "🌬️",
        "duration_seconds": 30
    },
    {
        "id": "snack",
        "name": "Healthy Snack",
        "description": "Grab a healthy snack",
        "icon": "🍎",
        "duration_seconds": 120
    }
]


# In-memory storage
_active_sessions: Dict[str, FocusSession] = {}  # user_id -> session
_session_history: List[FocusSession] = []
_session_counter = 0


def _generate_session_id() -> str:
    """Generate unique session ID."""
    global _session_counter
    _session_counter += 1
    return f"session_{_session_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def start_session(
    user_id: str,
    session_type: SessionType = SessionType.STANDARD,
    custom_duration: Optional[int] = None,
    content_id: Optional[str] = None,
    content_title: Optional[str] = None
) -> Dict:
    """Start a new focus session."""
    # End any existing session
    if user_id in _active_sessions:
        end_session(user_id)

    # Get duration
    if session_type == SessionType.CUSTOM and custom_duration:
        duration = custom_duration
    else:
        duration = SESSION_PRESETS[session_type]["duration_minutes"]

    # Create session
    session = FocusSession(
        id=_generate_session_id(),
        user_id=user_id,
        session_type=session_type,
        duration_minutes=duration,
        started_at=datetime.now(),
        content_id=content_id,
        content_title=content_title
    )

    _active_sessions[user_id] = session

    preset = SESSION_PRESETS.get(session_type, SESSION_PRESETS[SessionType.STANDARD])

    return {
        "session_id": session.id,
        "started": True,
        "session_type": session_type.value,
        "duration_minutes": duration,
        "break_minutes": preset["break_minutes"],
        "started_at": session.started_at.isoformat(),
        "ends_at": (session.started_at + timedelta(minutes=duration)).isoformat(),
        "content_id": content_id,
        "content_title": content_title
    }


def end_session(user_id: str, completed: bool = False) -> Dict:
    """End the current session."""
    if user_id not in _active_sessions:
        return {"ended": False, "error": "No active session"}

    session = _active_sessions[user_id]
    session.ended_at = datetime.now()
    session.completed = completed

    # Calculate actual duration
    actual_minutes = (session.ended_at - session.started_at).total_seconds() / 60
    actual_minutes -= session.paused_duration_seconds / 60

    # Move to history
    _session_history.append(session)
    del _active_sessions[user_id]

    return {
        "ended": True,
        "session_id": session.id,
        "planned_minutes": session.duration_minutes,
        "actual_minutes": round(actual_minutes, 1),
        "completed": completed,
        "breaks_taken": session.breaks_taken,
        "started_at": session.started_at.isoformat(),
        "ended_at": session.ended_at.isoformat()
    }


def get_session_status(user_id: str) -> Dict:
    """Get current session status."""
    if user_id not in _active_sessions:
        return {
            "active": False,
            "message": "No active session"
        }

    session = _active_sessions[user_id]
    elapsed = datetime.now() - session.started_at
    elapsed_minutes = elapsed.total_seconds() / 60
    remaining_minutes = max(0, session.duration_minutes - elapsed_minutes)

    # Check if break is due (every 25 minutes)
    break_due = elapsed_minutes > 0 and int(elapsed_minutes) % 25 == 0 and session.breaks_taken < int(elapsed_minutes / 25)

    return {
        "active": True,
        "session_id": session.id,
        "session_type": session.session_type.value,
        "duration_minutes": session.duration_minutes,
        "elapsed_minutes": round(elapsed_minutes, 1),
        "remaining_minutes": round(remaining_minutes, 1),
        "progress_percentage": min(100, round((elapsed_minutes / session.duration_minutes) * 100, 1)),
        "breaks_taken": session.breaks_taken,
        "break_due": break_due,
        "content_title": session.content_title,
        "started_at": session.started_at.isoformat()
    }


def take_break(user_id: str) -> Dict:
    """Record that user took a break."""
    if user_id not in _active_sessions:
        return {"success": False, "error": "No active session"}

    session = _active_sessions[user_id]
    session.breaks_taken += 1

    # Get random break activity suggestion
    import random
    activity = random.choice(BREAK_ACTIVITIES)

    preset = SESSION_PRESETS.get(session.session_type, SESSION_PRESETS[SessionType.STANDARD])

    return {
        "success": True,
        "breaks_taken": session.breaks_taken,
        "suggested_activity": activity,
        "break_duration_minutes": preset["break_minutes"],
        "message": f"Break #{session.breaks_taken} - {activity['name']}"
    }


def get_break_activities() -> List[Dict]:
    """Get all available break activities."""
    return BREAK_ACTIVITIES


def get_session_presets() -> Dict:
    """Get all session presets."""
    return {
        session_type.value: {
            **preset,
            "type": session_type.value
        }
        for session_type, preset in SESSION_PRESETS.items()
    }


def get_user_session_stats(user_id: str) -> Dict:
    """Get user's focus session statistics."""
    user_sessions = [s for s in _session_history if s.user_id == user_id]

    if not user_sessions:
        return {
            "total_sessions": 0,
            "total_minutes": 0,
            "completed_sessions": 0,
            "total_breaks": 0
        }

    total_minutes = sum(
        (s.ended_at - s.started_at).total_seconds() / 60
        for s in user_sessions
        if s.ended_at
    )

    completed = sum(1 for s in user_sessions if s.completed)
    total_breaks = sum(s.breaks_taken for s in user_sessions)

    return {
        "total_sessions": len(user_sessions),
        "total_minutes": round(total_minutes, 1),
        "total_hours": round(total_minutes / 60, 1),
        "completed_sessions": completed,
        "completion_rate": round((completed / len(user_sessions)) * 100, 1) if user_sessions else 0,
        "total_breaks": total_breaks,
        "avg_session_minutes": round(total_minutes / len(user_sessions), 1) if user_sessions else 0
    }


def should_remind_break(user_id: str) -> Dict:
    """Check if user should be reminded to take a break."""
    status = get_session_status(user_id)

    if not status.get("active"):
        return {"remind": False}

    elapsed = status.get("elapsed_minutes", 0)

    # Remind every 25 minutes if no break taken
    expected_breaks = int(elapsed / 25)
    actual_breaks = status.get("breaks_taken", 0)

    if expected_breaks > actual_breaks:
        return {
            "remind": True,
            "message": "Time for a quick break!",
            "elapsed_since_break": round(elapsed - (actual_breaks * 25), 1),
            "suggested_activity": BREAK_ACTIVITIES[actual_breaks % len(BREAK_ACTIVITIES)]
        }

    return {"remind": False}


# Service class
class FocusTimerService:
    """Focus timer service for dependency injection."""

    def start(self, user_id: str, **kwargs) -> Dict:
        return start_session(user_id, **kwargs)

    def end(self, user_id: str, completed: bool = False) -> Dict:
        return end_session(user_id, completed)

    def status(self, user_id: str) -> Dict:
        return get_session_status(user_id)

    def take_break(self, user_id: str) -> Dict:
        return take_break(user_id)

    def presets(self) -> Dict:
        return get_session_presets()

    def break_activities(self) -> List[Dict]:
        return get_break_activities()

    def stats(self, user_id: str) -> Dict:
        return get_user_session_stats(user_id)

    def should_break(self, user_id: str) -> Dict:
        return should_remind_break(user_id)


_focus_service: Optional[FocusTimerService] = None


def get_focus_service() -> FocusTimerService:
    """Get singleton focus timer service."""
    global _focus_service
    if _focus_service is None:
        _focus_service = FocusTimerService()
    return _focus_service
