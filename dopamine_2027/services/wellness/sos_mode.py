"""
SOS Calm Mode
Emergency wellness features for anxiety and overwhelm.
"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import random


class CalmingTechnique(Enum):
    """Available calming techniques."""
    BOX_BREATHING = "box_breathing"
    BREATHING_478 = "breathing_478"
    DEEP_BREATHING = "deep_breathing"
    GROUNDING_54321 = "grounding_54321"
    BODY_SCAN = "body_scan"
    PROGRESSIVE_RELAXATION = "progressive_relaxation"


@dataclass
class BreathingExercise:
    """Breathing exercise configuration."""
    id: str
    name: str
    description: str
    icon: str
    inhale_seconds: int
    hold_seconds: int
    exhale_seconds: int
    hold_after_exhale: int = 0
    cycles: int = 4
    instructions: List[str] = field(default_factory=list)


# Breathing exercise configurations
BREATHING_EXERCISES: Dict[str, BreathingExercise] = {
    "box_breathing": BreathingExercise(
        id="box_breathing",
        name="Box Breathing",
        description="Navy SEAL technique for instant calm",
        icon="📦",
        inhale_seconds=4,
        hold_seconds=4,
        exhale_seconds=4,
        hold_after_exhale=4,
        cycles=4,
        instructions=[
            "Sit comfortably with your back straight",
            "Breathe in slowly through your nose for 4 seconds",
            "Hold your breath for 4 seconds",
            "Exhale slowly through your mouth for 4 seconds",
            "Hold empty for 4 seconds",
            "Repeat 4 times"
        ]
    ),
    "breathing_478": BreathingExercise(
        id="breathing_478",
        name="4-7-8 Breathing",
        description="Dr. Weil's relaxing breath technique",
        icon="🌙",
        inhale_seconds=4,
        hold_seconds=7,
        exhale_seconds=8,
        cycles=4,
        instructions=[
            "Place the tip of your tongue behind your upper front teeth",
            "Exhale completely through your mouth, making a whoosh sound",
            "Close your mouth and inhale quietly through your nose for 4 seconds",
            "Hold your breath for 7 seconds",
            "Exhale completely through your mouth for 8 seconds",
            "Repeat 4 times"
        ]
    ),
    "deep_breathing": BreathingExercise(
        id="deep_breathing",
        name="Simple Deep Breathing",
        description="Easy and effective for beginners",
        icon="🌬️",
        inhale_seconds=4,
        hold_seconds=2,
        exhale_seconds=6,
        cycles=6,
        instructions=[
            "Find a comfortable position",
            "Place one hand on your chest, one on your belly",
            "Breathe in slowly through your nose for 4 seconds",
            "Feel your belly rise (not your chest)",
            "Hold briefly for 2 seconds",
            "Exhale slowly through your mouth for 6 seconds",
            "Repeat 6 times"
        ]
    )
}


# Grounding techniques
GROUNDING_54321 = {
    "name": "5-4-3-2-1 Grounding",
    "description": "Engage all your senses to ground yourself in the present moment",
    "icon": "🌍",
    "steps": [
        {
            "count": 5,
            "sense": "see",
            "prompt": "Name 5 things you can SEE",
            "examples": ["the color of the wall", "your hands", "a plant", "the ceiling", "your phone"]
        },
        {
            "count": 4,
            "sense": "touch",
            "prompt": "Name 4 things you can TOUCH",
            "examples": ["the texture of your clothes", "your chair", "the floor", "your hair"]
        },
        {
            "count": 3,
            "sense": "hear",
            "prompt": "Name 3 things you can HEAR",
            "examples": ["traffic outside", "your breathing", "a fan humming"]
        },
        {
            "count": 2,
            "sense": "smell",
            "prompt": "Name 2 things you can SMELL",
            "examples": ["coffee", "fresh air", "laundry detergent"]
        },
        {
            "count": 1,
            "sense": "taste",
            "prompt": "Name 1 thing you can TASTE",
            "examples": ["your morning coffee", "toothpaste", "lunch"]
        }
    ]
}


# Calming video suggestions
CALMING_VIDEOS = [
    {
        "id": "rain",
        "name": "Gentle Rain",
        "description": "Soft rain sounds for relaxation",
        "icon": "🌧️",
        "youtube_search": "relaxing rain sounds for sleep",
        "duration_minutes": 30
    },
    {
        "id": "ocean",
        "name": "Ocean Waves",
        "description": "Peaceful ocean wave sounds",
        "icon": "🌊",
        "youtube_search": "ocean waves sounds for relaxation",
        "duration_minutes": 30
    },
    {
        "id": "fireplace",
        "name": "Cozy Fireplace",
        "description": "Crackling fire for comfort",
        "icon": "🔥",
        "youtube_search": "cozy fireplace crackling sounds",
        "duration_minutes": 60
    },
    {
        "id": "forest",
        "name": "Forest Ambience",
        "description": "Peaceful forest sounds with birds",
        "icon": "🌲",
        "youtube_search": "forest nature sounds birds",
        "duration_minutes": 45
    },
    {
        "id": "thunderstorm",
        "name": "Distant Thunder",
        "description": "Gentle thunderstorm for relaxation",
        "icon": "⛈️",
        "youtube_search": "gentle thunderstorm sounds sleep",
        "duration_minutes": 60
    },
    {
        "id": "meditation",
        "name": "Guided Meditation",
        "description": "Calming guided meditation",
        "icon": "🧘",
        "youtube_search": "5 minute guided meditation anxiety",
        "duration_minutes": 5
    }
]


# Affirmations for different states
AFFIRMATIONS = {
    "anxious": [
        "This feeling is temporary. It will pass.",
        "I am safe in this moment.",
        "I can handle this, one breath at a time.",
        "My feelings are valid, but they don't define me.",
        "I've survived every hard moment before this one."
    ],
    "overwhelmed": [
        "I don't have to do everything right now.",
        "It's okay to take a break.",
        "One step at a time is enough.",
        "I give myself permission to rest.",
        "Not everything is urgent."
    ],
    "sad": [
        "It's okay to feel sad. This is part of being human.",
        "I am worthy of love and kindness.",
        "Tomorrow is a new day.",
        "I am doing the best I can.",
        "This sadness will lift."
    ],
    "stressed": [
        "I release what I cannot control.",
        "I am capable and resilient.",
        "Stress does not define my worth.",
        "I choose calm over chaos.",
        "I can only do what I can do."
    ],
    "general": [
        "You're doing better than you think.",
        "It's okay to not be okay.",
        "You matter.",
        "Take it one moment at a time.",
        "Be gentle with yourself."
    ]
}


@dataclass
class SOSUsage:
    """Track SOS mode usage for analytics."""
    user_id: str
    timestamp: datetime
    technique_used: Optional[str] = None
    duration_seconds: int = 0
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None


# In-memory storage for usage tracking
_sos_usage: List[SOSUsage] = []


def log_sos_usage(
    user_id: str,
    technique: Optional[str] = None,
    duration_seconds: int = 0,
    mood_before: Optional[str] = None,
    mood_after: Optional[str] = None
) -> Dict:
    """Log SOS mode usage."""
    usage = SOSUsage(
        user_id=user_id,
        timestamp=datetime.now(),
        technique_used=technique,
        duration_seconds=duration_seconds,
        mood_before=mood_before,
        mood_after=mood_after
    )
    _sos_usage.append(usage)

    return {
        "logged": True,
        "timestamp": usage.timestamp.isoformat()
    }


def get_breathing_exercise(exercise_id: str) -> Optional[Dict]:
    """Get a specific breathing exercise."""
    exercise = BREATHING_EXERCISES.get(exercise_id)
    if not exercise:
        return None

    return {
        "id": exercise.id,
        "name": exercise.name,
        "description": exercise.description,
        "icon": exercise.icon,
        "timing": {
            "inhale": exercise.inhale_seconds,
            "hold": exercise.hold_seconds,
            "exhale": exercise.exhale_seconds,
            "hold_after_exhale": exercise.hold_after_exhale,
            "cycles": exercise.cycles,
            "total_seconds": (
                exercise.inhale_seconds +
                exercise.hold_seconds +
                exercise.exhale_seconds +
                exercise.hold_after_exhale
            ) * exercise.cycles
        },
        "instructions": exercise.instructions
    }


def get_all_breathing_exercises() -> List[Dict]:
    """Get all available breathing exercises."""
    return [
        get_breathing_exercise(eid)
        for eid in BREATHING_EXERCISES.keys()
    ]


def get_grounding_exercise() -> Dict:
    """Get the 5-4-3-2-1 grounding exercise."""
    return GROUNDING_54321


def get_calming_videos() -> List[Dict]:
    """Get list of calming video suggestions."""
    return CALMING_VIDEOS


def get_affirmation(mood: Optional[str] = None) -> str:
    """Get a random affirmation for the given mood."""
    mood_key = mood.lower() if mood and mood.lower() in AFFIRMATIONS else "general"
    return random.choice(AFFIRMATIONS[mood_key])


def get_affirmations(mood: Optional[str] = None, count: int = 3) -> List[str]:
    """Get multiple affirmations for the given mood."""
    mood_key = mood.lower() if mood and mood.lower() in AFFIRMATIONS else "general"
    available = AFFIRMATIONS[mood_key]
    return random.sample(available, min(count, len(available)))


def get_sos_content(mood: Optional[str] = None) -> Dict:
    """Get complete SOS mode content package."""
    return {
        "breathing_exercises": get_all_breathing_exercises(),
        "grounding": get_grounding_exercise(),
        "calming_videos": get_calming_videos(),
        "affirmations": get_affirmations(mood, count=3),
        "quick_tips": [
            "Put one hand on your heart and one on your belly",
            "Splash cold water on your face",
            "Hold an ice cube in your hand",
            "Step outside for fresh air if possible",
            "Name 5 things around you that are blue"
        ],
        "crisis_resources": {
            "text": "If you're in crisis, you're not alone.",
            "hotline": "988",
            "hotline_name": "Suicide & Crisis Lifeline",
            "chat": "988lifeline.org/chat"
        }
    }


def get_user_sos_stats(user_id: str) -> Dict:
    """Get user's SOS usage statistics."""
    user_usage = [u for u in _sos_usage if u.user_id == user_id]

    if not user_usage:
        return {
            "total_uses": 0,
            "techniques_used": [],
            "avg_duration_seconds": 0
        }

    techniques = [u.technique_used for u in user_usage if u.technique_used]
    durations = [u.duration_seconds for u in user_usage if u.duration_seconds > 0]

    return {
        "total_uses": len(user_usage),
        "techniques_used": list(set(techniques)),
        "most_used_technique": max(set(techniques), key=techniques.count) if techniques else None,
        "avg_duration_seconds": sum(durations) / len(durations) if durations else 0,
        "last_used": user_usage[-1].timestamp.isoformat() if user_usage else None
    }


# Service class
class SOSModeService:
    """SOS Mode service for dependency injection."""

    def get_content(self, mood: Optional[str] = None) -> Dict:
        return get_sos_content(mood)

    def get_breathing(self, exercise_id: str) -> Optional[Dict]:
        return get_breathing_exercise(exercise_id)

    def all_breathing(self) -> List[Dict]:
        return get_all_breathing_exercises()

    def get_grounding(self) -> Dict:
        return get_grounding_exercise()

    def get_videos(self) -> List[Dict]:
        return get_calming_videos()

    def get_affirmation(self, mood: Optional[str] = None) -> str:
        return get_affirmation(mood)

    def log_usage(self, user_id: str, **kwargs) -> Dict:
        return log_sos_usage(user_id, **kwargs)

    def stats(self, user_id: str) -> Dict:
        return get_user_sos_stats(user_id)


_sos_service: Optional[SOSModeService] = None


def get_sos_service() -> SOSModeService:
    """Get singleton SOS mode service."""
    global _sos_service
    if _sos_service is None:
        _sos_service = SOSModeService()
    return _sos_service
