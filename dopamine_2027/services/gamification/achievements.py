"""
Achievements System
Unlock achievements for various milestones and actions.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AchievementCategory(Enum):
    """Achievement categories."""
    GETTING_STARTED = "getting_started"
    CONTENT = "content"
    SOCIAL = "social"
    STREAKS = "streaks"
    MR_DP = "mr_dp"
    MOOD = "mood"
    SPECIAL = "special"


@dataclass
class Achievement:
    """Achievement definition."""
    id: str
    name: str
    description: str
    icon: str
    category: AchievementCategory
    points: int = 50
    secret: bool = False  # Hidden until unlocked
    requirement: Optional[str] = None  # Human-readable requirement


# All available achievements
ACHIEVEMENTS: Dict[str, Achievement] = {
    # Getting Started
    "first_mood": Achievement(
        id="first_mood",
        name="Mood Tracker",
        description="Logged your first mood",
        icon="🎭",
        category=AchievementCategory.GETTING_STARTED,
        points=25,
        requirement="Log your first mood"
    ),
    "first_recommendation": Achievement(
        id="first_recommendation",
        name="Content Explorer",
        description="Got your first recommendation",
        icon="🎬",
        category=AchievementCategory.GETTING_STARTED,
        points=25,
        requirement="Get a content recommendation"
    ),
    "first_chat": Achievement(
        id="first_chat",
        name="Mr.DP's Friend",
        description="Had your first chat with Mr.DP",
        icon="💬",
        category=AchievementCategory.GETTING_STARTED,
        points=25,
        requirement="Chat with Mr.DP"
    ),
    "profile_complete": Achievement(
        id="profile_complete",
        name="Identity Unlocked",
        description="Completed your profile",
        icon="👤",
        category=AchievementCategory.GETTING_STARTED,
        points=50,
        requirement="Complete your profile"
    ),

    # Content Achievements
    "watched_10": Achievement(
        id="watched_10",
        name="Casual Viewer",
        description="Watched 10 pieces of content",
        icon="📺",
        category=AchievementCategory.CONTENT,
        points=50,
        requirement="Watch 10 items"
    ),
    "watched_50": Achievement(
        id="watched_50",
        name="Content Consumer",
        description="Watched 50 pieces of content",
        icon="🎥",
        category=AchievementCategory.CONTENT,
        points=100,
        requirement="Watch 50 items"
    ),
    "watched_100": Achievement(
        id="watched_100",
        name="Binge Master",
        description="Watched 100 pieces of content",
        icon="🏆",
        category=AchievementCategory.CONTENT,
        points=200,
        requirement="Watch 100 items"
    ),
    "genre_explorer": Achievement(
        id="genre_explorer",
        name="Genre Explorer",
        description="Explored 5 different genres",
        icon="🗺️",
        category=AchievementCategory.CONTENT,
        points=75,
        requirement="Watch content from 5 different genres"
    ),
    "quick_picker": Achievement(
        id="quick_picker",
        name="Quick Picker",
        description="Used Quick Dope Hit 10 times",
        icon="⚡",
        category=AchievementCategory.CONTENT,
        points=50,
        requirement="Use Quick Dope Hit 10 times"
    ),

    # Social Achievements
    "first_friend": Achievement(
        id="first_friend",
        name="Social Butterfly",
        description="Added your first friend",
        icon="🦋",
        category=AchievementCategory.SOCIAL,
        points=50,
        requirement="Add a friend"
    ),
    "party_host": Achievement(
        id="party_host",
        name="Party Host",
        description="Hosted your first watch party",
        icon="🎉",
        category=AchievementCategory.SOCIAL,
        points=75,
        requirement="Host a watch party"
    ),
    "party_regular": Achievement(
        id="party_regular",
        name="Party Regular",
        description="Joined 10 watch parties",
        icon="🥳",
        category=AchievementCategory.SOCIAL,
        points=100,
        requirement="Join 10 watch parties"
    ),
    "referral_champion": Achievement(
        id="referral_champion",
        name="Referral Champion",
        description="Referred 5 friends",
        icon="📢",
        category=AchievementCategory.SOCIAL,
        points=200,
        requirement="Refer 5 friends"
    ),

    # Streak Achievements
    "streak_7": Achievement(
        id="streak_7",
        name="Week Warrior",
        description="7 day streak",
        icon="🔥",
        category=AchievementCategory.STREAKS,
        points=100,
        requirement="Maintain a 7-day streak"
    ),
    "streak_30": Achievement(
        id="streak_30",
        name="Monthly Master",
        description="30 day streak",
        icon="🌟",
        category=AchievementCategory.STREAKS,
        points=300,
        requirement="Maintain a 30-day streak"
    ),
    "streak_100": Achievement(
        id="streak_100",
        name="Century Legend",
        description="100 day streak",
        icon="💎",
        category=AchievementCategory.STREAKS,
        points=1000,
        requirement="Maintain a 100-day streak"
    ),

    # Mr.DP Achievements
    "mrdp_chat_10": Achievement(
        id="mrdp_chat_10",
        name="Chatty",
        description="Had 10 conversations with Mr.DP",
        icon="🗣️",
        category=AchievementCategory.MR_DP,
        points=50,
        requirement="Chat with Mr.DP 10 times"
    ),
    "mrdp_chat_50": Achievement(
        id="mrdp_chat_50",
        name="Best Friends",
        description="Had 50 conversations with Mr.DP",
        icon="💜",
        category=AchievementCategory.MR_DP,
        points=150,
        requirement="Chat with Mr.DP 50 times"
    ),
    "mrdp_accepted_all": Achievement(
        id="mrdp_accepted_all",
        name="Trust Fall",
        description="Accepted 10 Mr.DP suggestions in a row",
        icon="🤝",
        category=AchievementCategory.MR_DP,
        points=100,
        requirement="Accept 10 consecutive Mr.DP suggestions"
    ),

    # Mood Achievements
    "mood_tracker_7": Achievement(
        id="mood_tracker_7",
        name="Mood Aware",
        description="Tracked mood for 7 days",
        icon="📊",
        category=AchievementCategory.MOOD,
        points=75,
        requirement="Log mood for 7 days"
    ),
    "mood_variety": Achievement(
        id="mood_variety",
        name="Emotional Range",
        description="Experienced 8 different moods",
        icon="🌈",
        category=AchievementCategory.MOOD,
        points=100,
        requirement="Log 8 different moods"
    ),
    "mood_improved": Achievement(
        id="mood_improved",
        name="Mood Lifter",
        description="Improved mood 5 times after content",
        icon="📈",
        category=AchievementCategory.MOOD,
        points=100,
        requirement="Improve mood 5 times after watching content"
    ),

    # Special/Secret Achievements
    "night_owl": Achievement(
        id="night_owl",
        name="Night Owl",
        description="Used the app after midnight 10 times",
        icon="🦉",
        category=AchievementCategory.SPECIAL,
        points=50,
        secret=True,
        requirement="Use app after midnight 10 times"
    ),
    "early_bird": Achievement(
        id="early_bird",
        name="Early Bird",
        description="Used the app before 6am 5 times",
        icon="🐦",
        category=AchievementCategory.SPECIAL,
        points=50,
        secret=True,
        requirement="Use app before 6am 5 times"
    ),
    "marathon_watcher": Achievement(
        id="marathon_watcher",
        name="Marathon Watcher",
        description="Watched content for 4+ hours in one session",
        icon="🏃",
        category=AchievementCategory.SPECIAL,
        points=100,
        secret=True,
        requirement="Watch for 4+ hours in one session"
    ),
}


@dataclass
class UserAchievements:
    """User's achievement data."""
    user_id: str
    unlocked: Set[str] = field(default_factory=set)
    unlock_dates: Dict[str, str] = field(default_factory=dict)
    progress: Dict[str, int] = field(default_factory=dict)  # For progressive achievements


# In-memory storage
_user_achievements: Dict[str, UserAchievements] = {}


def get_user_achievements(user_id: str) -> UserAchievements:
    """Get user's achievements data."""
    if user_id not in _user_achievements:
        _user_achievements[user_id] = UserAchievements(user_id=user_id)
    return _user_achievements[user_id]


def unlock_achievement(user_id: str, achievement_id: str) -> Optional[Dict]:
    """
    Unlock an achievement for user.

    Returns:
        Achievement details if newly unlocked, None if already unlocked or invalid
    """
    if achievement_id not in ACHIEVEMENTS:
        return None

    user = get_user_achievements(user_id)

    if achievement_id in user.unlocked:
        return None  # Already unlocked

    # Unlock it
    achievement = ACHIEVEMENTS[achievement_id]
    user.unlocked.add(achievement_id)
    user.unlock_dates[achievement_id] = datetime.now().isoformat()

    return {
        "achievement": {
            "id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "category": achievement.category.value,
            "points": achievement.points
        },
        "unlocked_at": user.unlock_dates[achievement_id],
        "total_unlocked": len(user.unlocked),
        "total_available": len(ACHIEVEMENTS)
    }


def check_and_unlock(user_id: str, achievement_id: str, condition: bool) -> Optional[Dict]:
    """Check condition and unlock achievement if met."""
    if condition:
        return unlock_achievement(user_id, achievement_id)
    return None


# Alias for convenience
check_achievement = check_and_unlock


def update_progress(user_id: str, achievement_id: str, increment: int = 1) -> Optional[Dict]:
    """
    Update progress towards a progressive achievement.

    Returns:
        Achievement if unlocked, progress info otherwise
    """
    user = get_user_achievements(user_id)

    # Already unlocked
    if achievement_id in user.unlocked:
        return None

    # Update progress
    current = user.progress.get(achievement_id, 0) + increment
    user.progress[achievement_id] = current

    # Check thresholds
    thresholds = {
        "watched_10": 10,
        "watched_50": 50,
        "watched_100": 100,
        "mrdp_chat_10": 10,
        "mrdp_chat_50": 50,
        "quick_picker": 10,
        "party_regular": 10,
        "referral_champion": 5,
        "mood_tracker_7": 7,
        "night_owl": 10,
        "early_bird": 5,
        "mrdp_accepted_all": 10,
        "mood_improved": 5,
    }

    threshold = thresholds.get(achievement_id)
    if threshold and current >= threshold:
        return unlock_achievement(user_id, achievement_id)

    return {
        "achievement_id": achievement_id,
        "progress": current,
        "threshold": threshold,
        "percentage": (current / threshold * 100) if threshold else 0
    }


def get_achievements_summary(user_id: str) -> Dict:
    """Get user's achievements summary."""
    user = get_user_achievements(user_id)

    # Get unlocked achievements
    unlocked_list = []
    for aid in user.unlocked:
        if aid in ACHIEVEMENTS:
            a = ACHIEVEMENTS[aid]
            unlocked_list.append({
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "category": a.category.value,
                "points": a.points,
                "unlocked_at": user.unlock_dates.get(aid)
            })

    # Get locked achievements (non-secret only)
    locked_list = []
    for aid, a in ACHIEVEMENTS.items():
        if aid not in user.unlocked and not a.secret:
            progress = user.progress.get(aid, 0)
            locked_list.append({
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "category": a.category.value,
                "points": a.points,
                "requirement": a.requirement,
                "progress": progress
            })

    # Calculate total points from achievements
    total_points = sum(
        ACHIEVEMENTS[aid].points for aid in user.unlocked if aid in ACHIEVEMENTS
    )

    return {
        "user_id": user_id,
        "total_unlocked": len(user.unlocked),
        "total_available": len(ACHIEVEMENTS),
        "total_points": total_points,
        "unlocked": unlocked_list,
        "locked": locked_list,
        "completion_percentage": round(len(user.unlocked) / len(ACHIEVEMENTS) * 100, 1)
    }


def get_recent_achievements(user_id: str, limit: int = 5) -> List[Dict]:
    """Get user's most recently unlocked achievements."""
    user = get_user_achievements(user_id)

    # Sort by unlock date
    sorted_achievements = sorted(
        user.unlock_dates.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    result = []
    for aid, unlock_date in sorted_achievements:
        if aid in ACHIEVEMENTS:
            a = ACHIEVEMENTS[aid]
            result.append({
                "id": a.id,
                "name": a.name,
                "icon": a.icon,
                "points": a.points,
                "unlocked_at": unlock_date
            })

    return result


# Service class
class AchievementService:
    """Achievement service for dependency injection."""

    def get(self, user_id: str) -> UserAchievements:
        return get_user_achievements(user_id)

    def unlock(self, user_id: str, achievement_id: str) -> Optional[Dict]:
        return unlock_achievement(user_id, achievement_id)

    def check(self, user_id: str, achievement_id: str, condition: bool) -> Optional[Dict]:
        return check_and_unlock(user_id, achievement_id, condition)

    def progress(self, user_id: str, achievement_id: str, increment: int = 1) -> Optional[Dict]:
        return update_progress(user_id, achievement_id, increment)

    def summary(self, user_id: str) -> Dict:
        return get_achievements_summary(user_id)

    def recent(self, user_id: str, limit: int = 5) -> List[Dict]:
        return get_recent_achievements(user_id, limit)

    @property
    def all_achievements(self) -> Dict[str, Achievement]:
        return ACHIEVEMENTS


_achievement_service: Optional[AchievementService] = None


def get_achievement_service() -> AchievementService:
    """Get singleton achievement service."""
    global _achievement_service
    if _achievement_service is None:
        _achievement_service = AchievementService()
    return _achievement_service
