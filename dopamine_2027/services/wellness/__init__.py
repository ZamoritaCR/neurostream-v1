"""
Wellness Services
SOS calm mode, focus timer, and mental health support.
"""

from .sos_mode import (
    CalmingTechnique,
    BreathingExercise,
    BREATHING_EXERCISES,
    GROUNDING_54321,
    CALMING_VIDEOS,
    AFFIRMATIONS,
    SOSUsage,
    log_sos_usage,
    get_breathing_exercise,
    get_all_breathing_exercises,
    get_grounding_exercise,
    get_calming_videos,
    get_affirmation,
    get_affirmations,
    get_sos_content,
    get_user_sos_stats,
    get_sos_service,
    SOSModeService
)

from .focus_timer import (
    SessionType,
    FocusSession,
    SESSION_PRESETS,
    BREAK_ACTIVITIES,
    start_session,
    end_session,
    get_session_status,
    take_break,
    get_break_activities,
    get_session_presets,
    get_user_session_stats,
    should_remind_break,
    get_focus_service,
    FocusTimerService
)

__all__ = [
    # SOS Mode
    "CalmingTechnique",
    "BreathingExercise",
    "BREATHING_EXERCISES",
    "GROUNDING_54321",
    "CALMING_VIDEOS",
    "AFFIRMATIONS",
    "SOSUsage",
    "log_sos_usage",
    "get_breathing_exercise",
    "get_all_breathing_exercises",
    "get_grounding_exercise",
    "get_calming_videos",
    "get_affirmation",
    "get_affirmations",
    "get_sos_content",
    "get_user_sos_stats",
    "get_sos_service",
    "SOSModeService",

    # Focus Timer
    "SessionType",
    "FocusSession",
    "SESSION_PRESETS",
    "BREAK_ACTIVITIES",
    "start_session",
    "end_session",
    "get_session_status",
    "take_break",
    "get_break_activities",
    "get_session_presets",
    "get_user_session_stats",
    "should_remind_break",
    "get_focus_service",
    "FocusTimerService",
]
