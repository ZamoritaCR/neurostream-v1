# gamification_enhanced.py
# --------------------------------------------------
# DOPAMINE.WATCH - ENHANCED GAMIFICATION SYSTEM
# --------------------------------------------------
# Features:
# 1. Points System with Leaderboards
# 2. Streak Tracking with Milestones
# 3. 30 Achievements System
# 4. Streamlit UI Components
# --------------------------------------------------

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math

# --------------------------------------------------
# 1. POINTS SYSTEM
# --------------------------------------------------

class PointAction(Enum):
    """Actions that earn dopamine points."""
    # Content interactions
    CONTENT_VIEW = 5
    CONTENT_COMPLETE = 15
    CONTENT_RATE = 10
    CONTENT_SAVE = 5
    CONTENT_SHARE = 20

    # Mr.DP interactions
    MRDP_CHAT = 10
    MRDP_SUGGESTION_ACCEPT = 15
    QUICK_DOPE_HIT = 5

    # Mood tracking
    MOOD_LOG = 5
    MOOD_STREAK_BONUS = 25

    # Social
    FRIEND_ADD = 20
    WATCH_PARTY_HOST = 30
    WATCH_PARTY_JOIN = 15

    # Engagement
    DAILY_LOGIN = 10
    STREAK_7_DAYS = 100
    STREAK_30_DAYS = 500
    STREAK_100_DAYS = 2000

    # Achievements
    ACHIEVEMENT_UNLOCK = 50
    LEVEL_UP = 100

    # Feedback
    FEEDBACK_SUBMIT = 100
    REFERRAL_SUCCESS = 200


@dataclass
class UserPoints:
    """User's dopamine points data."""
    user_id: str
    total_points: int = 0
    level: int = 1
    points_today: int = 0
    last_activity_date: Optional[date] = None
    point_history: list = field(default_factory=list)

    def calculate_level(self) -> int:
        """Calculate level from points (sqrt formula)."""
        return int(math.sqrt(self.total_points / 100)) + 1

    def points_to_next_level(self) -> int:
        """Calculate points needed for next level."""
        next_level = self.level + 1
        required = ((next_level - 1) ** 2) * 100
        return max(0, required - self.total_points)


# In-memory storage (falls back to session state in Streamlit)
def _get_points_storage() -> Dict[str, UserPoints]:
    """Get points storage from session state."""
    if 'gamification_points' not in st.session_state:
        st.session_state.gamification_points = {}
    return st.session_state.gamification_points


def get_user_points(user_id: str) -> UserPoints:
    """Get user's points data."""
    storage = _get_points_storage()
    if user_id not in storage:
        storage[user_id] = UserPoints(user_id=user_id)
    return storage[user_id]


def add_points(
    user_id: str,
    action: PointAction,
    multiplier: float = 1.0,
    bonus: int = 0
) -> Dict:
    """
    Add dopamine points to user.

    Args:
        user_id: User identifier
        action: The action that earned points
        multiplier: Point multiplier (e.g., 2x for premium)
        bonus: Additional bonus points

    Returns:
        Dictionary with points info and level up status
    """
    user = get_user_points(user_id)

    # Calculate points
    base_points = action.value
    earned = int(base_points * multiplier) + bonus

    # Track daily points
    today = date.today()
    if user.last_activity_date != today:
        user.points_today = 0
        user.last_activity_date = today

    # Add points
    old_level = user.level
    user.total_points += earned
    user.points_today += earned

    # Recalculate level
    user.level = user.calculate_level()
    level_up = user.level > old_level

    # Add to history
    user.point_history.append({
        "action": action.name,
        "points": earned,
        "timestamp": datetime.now().isoformat(),
        "total_after": user.total_points
    })

    # Keep only last 100 entries
    if len(user.point_history) > 100:
        user.point_history = user.point_history[-100:]

    return {
        "earned": earned,
        "total": user.total_points,
        "level": user.level,
        "level_up": level_up,
        "points_today": user.points_today,
        "to_next_level": user.points_to_next_level()
    }


def get_points_summary(user_id: str) -> Dict:
    """Get user's points summary."""
    user = get_user_points(user_id)
    return {
        "user_id": user_id,
        "total_points": user.total_points,
        "level": user.level,
        "points_today": user.points_today,
        "to_next_level": user.points_to_next_level(),
        "recent_activity": user.point_history[-10:] if user.point_history else []
    }


def get_leaderboard(limit: int = 10) -> List[Dict]:
    """Get top users by points."""
    storage = _get_points_storage()
    sorted_users = sorted(
        storage.values(),
        key=lambda u: u.total_points,
        reverse=True
    )
    return [
        {
            "rank": i + 1,
            "user_id": u.user_id,
            "points": u.total_points,
            "level": u.level
        }
        for i, u in enumerate(sorted_users[:limit])
    ]


def get_user_rank(user_id: str) -> int:
    """Get user's rank in leaderboard."""
    storage = _get_points_storage()
    if user_id not in storage:
        return 0

    user_points = storage[user_id].total_points
    rank = 1
    for u in storage.values():
        if u.total_points > user_points:
            rank += 1
    return rank


def calculate_level(total_points: int) -> Dict:
    """Calculate level from points (standalone function)."""
    level = int(math.sqrt(total_points / 100)) + 1
    current_level_points = ((level - 1) ** 2) * 100
    next_level_points = (level ** 2) * 100
    progress = total_points - current_level_points
    needed = next_level_points - current_level_points

    return {
        "level": level,
        "total_points": total_points,
        "progress": progress,
        "needed_for_next": needed - progress,
        "percentage": round((progress / needed) * 100, 1) if needed > 0 else 100
    }


# --------------------------------------------------
# 2. STREAK SYSTEM
# --------------------------------------------------

# Grace period for streaks (Brain 5, Section 4 - prevents shame spirals)
# Research: ADHD executive dysfunction means missing a day is not a moral failure
STREAK_GRACE_PERIOD_DAYS = 3

STREAK_MILESTONES: Dict[int, Dict] = {
    7: {
        "title": "Week Warrior",
        "emoji": "🔥",
        "description": "7 days of consistent dopamine!",
        "bonus_points": 100
    },
    30: {
        "title": "Monthly Master",
        "emoji": "🌟",
        "description": "30 days - you're unstoppable!",
        "bonus_points": 500
    },
    100: {
        "title": "Century Champion",
        "emoji": "💎",
        "description": "100 days - legendary status!",
        "bonus_points": 2000
    },
    365: {
        "title": "Year of Dopamine",
        "emoji": "👑",
        "description": "365 days - ultimate dedication!",
        "bonus_points": 10000
    }
}


@dataclass
class UserStreak:
    """User's streak data."""
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    streak_started: Optional[date] = None
    total_active_days: int = 0

    def is_streak_active(self, grace_period: int = None) -> bool:
        """Check if streak is still active (within grace period).

        Research: Brain 5, Section 4 - Grace periods prevent shame spirals
        ADHD users need flexibility; missing one day shouldn't break progress.
        """
        if not self.last_activity_date:
            return False
        if grace_period is None:
            grace_period = STREAK_GRACE_PERIOD_DAYS
        today = date.today()
        return (today - self.last_activity_date).days <= grace_period


def _get_streak_storage() -> Dict[str, UserStreak]:
    """Get streak storage from session state."""
    if 'gamification_streaks' not in st.session_state:
        st.session_state.gamification_streaks = {}
    return st.session_state.gamification_streaks


def get_user_streak(user_id: str) -> UserStreak:
    """Get user's streak data."""
    storage = _get_streak_storage()
    if user_id not in storage:
        storage[user_id] = UserStreak(user_id=user_id)
    return storage[user_id]


def update_streak(user_id: str, grace_period: int = None) -> Dict:
    """
    Update user's streak on activity with grace period support.

    Research: Brain 5, Section 4 - Grace periods prevent shame spirals
    ADHD executive dysfunction means missing days is not a moral failure.
    Users can return within the grace period without losing their streak.

    Args:
        user_id: User identifier
        grace_period: Days of grace before streak resets (default: STREAK_GRACE_PERIOD_DAYS)

    Returns:
        Dictionary with streak info and milestone status
    """
    if grace_period is None:
        grace_period = STREAK_GRACE_PERIOD_DAYS

    streak = get_user_streak(user_id)
    today = date.today()

    milestone = None
    returning_after_break = False  # Renamed from streak_broken - more positive framing
    new_streak = False
    days_since_activity = None

    # First activity ever
    if streak.last_activity_date is None:
        streak.current_streak = 1
        streak.longest_streak = 1
        streak.streak_started = today
        streak.total_active_days = 1
        streak.last_activity_date = today
        new_streak = True

    # Same day - no change
    elif streak.last_activity_date == today:
        pass

    else:
        days_since_activity = (today - streak.last_activity_date).days

        # Within grace period - continue streak! (Research: Brain 5, Section 4)
        if days_since_activity <= grace_period:
            streak.current_streak += 1
            streak.total_active_days += 1
            streak.last_activity_date = today

            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak

            # Check milestones
            if streak.current_streak in STREAK_MILESTONES:
                milestone = STREAK_MILESTONES[streak.current_streak]

        # Beyond grace period - reset (but celebrate the return!)
        else:
            returning_after_break = streak.current_streak > 0
            streak.current_streak = 1
            streak.streak_started = today
            streak.total_active_days += 1
            streak.last_activity_date = today
            new_streak = True

    return {
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "streak_started": streak.streak_started.isoformat() if streak.streak_started else None,
        "total_active_days": streak.total_active_days,
        "milestone": milestone,
        "streak_broken": returning_after_break,  # Keep key for backwards compat
        "returning_user": returning_after_break,  # New positive key
        "new_streak": new_streak,
        "is_active": streak.is_streak_active(grace_period),
        "grace_period_days": grace_period
    }


def get_streak_summary(user_id: str, grace_period: int = None) -> Dict:
    """Get user's streak summary with grace period info.

    Research: Brain 5, Section 4 - Users should see how much grace time remains
    This creates awareness without shame or pressure.
    """
    if grace_period is None:
        grace_period = STREAK_GRACE_PERIOD_DAYS

    streak = get_user_streak(user_id)

    grace_days_remaining = None
    if streak.last_activity_date:
        today = date.today()
        days_since = (today - streak.last_activity_date).days
        if days_since <= grace_period:
            grace_days_remaining = grace_period - days_since

    return {
        "user_id": user_id,
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_active_days": streak.total_active_days,
        "is_active": streak.is_streak_active(grace_period),
        "grace_days_remaining": grace_days_remaining,
        "grace_period_days": grace_period
    }


def check_streak_at_risk(user_id: str, grace_period: int = None) -> bool:
    """Check if user's streak is approaching end of grace period.

    Research: Brain 5, Section 4 - Gentle reminder, not guilt-inducing alert
    Returns True when on the last day of grace period (time to come back!)
    """
    if grace_period is None:
        grace_period = STREAK_GRACE_PERIOD_DAYS

    streak = get_user_streak(user_id)
    if not streak.last_activity_date or streak.current_streak == 0:
        return False
    today = date.today()
    days_since = (today - streak.last_activity_date).days
    # At risk = on the last day of grace period
    return days_since == grace_period


def get_streak_leaderboard(limit: int = 10) -> List[Dict]:
    """Get top users by current streak."""
    storage = _get_streak_storage()
    sorted_users = sorted(
        storage.values(),
        key=lambda s: s.current_streak,
        reverse=True
    )
    return [
        {
            "rank": i + 1,
            "user_id": s.user_id,
            "current_streak": s.current_streak,
            "longest_streak": s.longest_streak
        }
        for i, s in enumerate(sorted_users[:limit])
    ]


# --------------------------------------------------
# 3. ACHIEVEMENTS SYSTEM (30 Achievements)
# --------------------------------------------------

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
    secret: bool = False
    requirement: Optional[str] = None


# All 30 achievements
ACHIEVEMENTS_ENHANCED: Dict[str, Achievement] = {
    # Getting Started (4)
    "first_mood": Achievement(
        id="first_mood", name="Mood Tracker",
        description="Logged your first mood", icon="🎭",
        category=AchievementCategory.GETTING_STARTED, points=25,
        requirement="Log your first mood"
    ),
    "first_recommendation": Achievement(
        id="first_recommendation", name="Content Explorer",
        description="Got your first recommendation", icon="🎬",
        category=AchievementCategory.GETTING_STARTED, points=25,
        requirement="Get a content recommendation"
    ),
    "first_chat": Achievement(
        id="first_chat", name="Mr.DP's Friend",
        description="Had your first chat with Mr.DP", icon="💬",
        category=AchievementCategory.GETTING_STARTED, points=25,
        requirement="Chat with Mr.DP"
    ),
    "profile_complete": Achievement(
        id="profile_complete", name="Identity Unlocked",
        description="Completed your profile", icon="👤",
        category=AchievementCategory.GETTING_STARTED, points=50,
        requirement="Complete your profile"
    ),

    # Content (5)
    "watched_10": Achievement(
        id="watched_10", name="Casual Viewer",
        description="Watched 10 pieces of content", icon="📺",
        category=AchievementCategory.CONTENT, points=50,
        requirement="Watch 10 items"
    ),
    "watched_50": Achievement(
        id="watched_50", name="Content Consumer",
        description="Watched 50 pieces of content", icon="🎥",
        category=AchievementCategory.CONTENT, points=100,
        requirement="Watch 50 items"
    ),
    "watched_100": Achievement(
        id="watched_100", name="Binge Master",
        description="Watched 100 pieces of content", icon="🏆",
        category=AchievementCategory.CONTENT, points=200,
        requirement="Watch 100 items"
    ),
    "genre_explorer": Achievement(
        id="genre_explorer", name="Genre Explorer",
        description="Explored 5 different genres", icon="🗺️",
        category=AchievementCategory.CONTENT, points=75,
        requirement="Watch content from 5 different genres"
    ),
    "quick_picker": Achievement(
        id="quick_picker", name="Quick Picker",
        description="Used Quick Dope Hit 10 times", icon="⚡",
        category=AchievementCategory.CONTENT, points=50,
        requirement="Use Quick Dope Hit 10 times"
    ),

    # Social (4)
    "first_friend": Achievement(
        id="first_friend", name="Social Butterfly",
        description="Added your first friend", icon="🦋",
        category=AchievementCategory.SOCIAL, points=50,
        requirement="Add a friend"
    ),
    "party_host": Achievement(
        id="party_host", name="Party Host",
        description="Hosted your first watch party", icon="🎉",
        category=AchievementCategory.SOCIAL, points=75,
        requirement="Host a watch party"
    ),
    "party_regular": Achievement(
        id="party_regular", name="Party Regular",
        description="Joined 10 watch parties", icon="🥳",
        category=AchievementCategory.SOCIAL, points=100,
        requirement="Join 10 watch parties"
    ),
    "referral_champion": Achievement(
        id="referral_champion", name="Referral Champion",
        description="Referred 5 friends", icon="📢",
        category=AchievementCategory.SOCIAL, points=200,
        requirement="Refer 5 friends"
    ),

    # Streaks (4)
    "streak_3": Achievement(
        id="streak_3", name="Getting Started",
        description="3 day streak", icon="✨",
        category=AchievementCategory.STREAKS, points=25,
        requirement="Maintain a 3-day streak"
    ),
    "streak_7": Achievement(
        id="streak_7", name="Week Warrior",
        description="7 day streak", icon="🔥",
        category=AchievementCategory.STREAKS, points=100,
        requirement="Maintain a 7-day streak"
    ),
    "streak_30": Achievement(
        id="streak_30", name="Monthly Master",
        description="30 day streak", icon="🌟",
        category=AchievementCategory.STREAKS, points=300,
        requirement="Maintain a 30-day streak"
    ),
    "streak_100": Achievement(
        id="streak_100", name="Century Legend",
        description="100 day streak", icon="💎",
        category=AchievementCategory.STREAKS, points=1000,
        requirement="Maintain a 100-day streak"
    ),

    # Mr.DP (4)
    "mrdp_chat_10": Achievement(
        id="mrdp_chat_10", name="Chatty",
        description="Had 10 conversations with Mr.DP", icon="🗣️",
        category=AchievementCategory.MR_DP, points=50,
        requirement="Chat with Mr.DP 10 times"
    ),
    "mrdp_chat_50": Achievement(
        id="mrdp_chat_50", name="Best Friends",
        description="Had 50 conversations with Mr.DP", icon="💜",
        category=AchievementCategory.MR_DP, points=150,
        requirement="Chat with Mr.DP 50 times"
    ),
    "mrdp_accepted_all": Achievement(
        id="mrdp_accepted_all", name="Trust Fall",
        description="Accepted 10 Mr.DP suggestions in a row", icon="🤝",
        category=AchievementCategory.MR_DP, points=100,
        requirement="Accept 10 consecutive Mr.DP suggestions"
    ),
    "mrdp_marathon": Achievement(
        id="mrdp_marathon", name="Marathon Planner",
        description="Used marathon mode 5 times", icon="🏃",
        category=AchievementCategory.MR_DP, points=75,
        requirement="Use marathon mode 5 times"
    ),

    # Mood (4)
    "mood_tracker_7": Achievement(
        id="mood_tracker_7", name="Mood Aware",
        description="Tracked mood for 7 days", icon="📊",
        category=AchievementCategory.MOOD, points=75,
        requirement="Log mood for 7 days"
    ),
    "mood_variety": Achievement(
        id="mood_variety", name="Emotional Range",
        description="Experienced 8 different moods", icon="🌈",
        category=AchievementCategory.MOOD, points=100,
        requirement="Log 8 different moods"
    ),
    "mood_improved": Achievement(
        id="mood_improved", name="Mood Lifter",
        description="Improved mood 5 times after content", icon="📈",
        category=AchievementCategory.MOOD, points=100,
        requirement="Improve mood 5 times after watching content"
    ),
    "calm_seeker": Achievement(
        id="calm_seeker", name="Calm Seeker",
        description="Used SOS calm mode 5 times", icon="🧘",
        category=AchievementCategory.MOOD, points=50,
        requirement="Use SOS calm mode 5 times"
    ),

    # Special/Secret (5)
    "night_owl": Achievement(
        id="night_owl", name="Night Owl",
        description="Used the app after midnight 10 times", icon="🦉",
        category=AchievementCategory.SPECIAL, points=50, secret=True,
        requirement="Use app after midnight 10 times"
    ),
    "early_bird": Achievement(
        id="early_bird", name="Early Bird",
        description="Used the app before 6am 5 times", icon="🐦",
        category=AchievementCategory.SPECIAL, points=50, secret=True,
        requirement="Use app before 6am 5 times"
    ),
    "marathon_watcher": Achievement(
        id="marathon_watcher", name="Marathon Watcher",
        description="Watched content for 4+ hours in one session", icon="🎬",
        category=AchievementCategory.SPECIAL, points=100, secret=True,
        requirement="Watch for 4+ hours in one session"
    ),
    "weekend_warrior": Achievement(
        id="weekend_warrior", name="Weekend Warrior",
        description="Used the app every weekend for a month", icon="📅",
        category=AchievementCategory.SPECIAL, points=75, secret=True,
        requirement="Use app every weekend for a month"
    ),
    "completionist": Achievement(
        id="completionist", name="Completionist",
        description="Unlocked all non-secret achievements", icon="🏅",
        category=AchievementCategory.SPECIAL, points=500, secret=True,
        requirement="Unlock all non-secret achievements"
    ),
}


@dataclass
class UserAchievements:
    """User's achievement data."""
    user_id: str
    unlocked: Set[str] = field(default_factory=set)
    unlock_dates: Dict[str, str] = field(default_factory=dict)
    progress: Dict[str, int] = field(default_factory=dict)


def _get_achievements_storage() -> Dict[str, UserAchievements]:
    """Get achievements storage from session state."""
    if 'gamification_achievements' not in st.session_state:
        st.session_state.gamification_achievements = {}
    return st.session_state.gamification_achievements


def get_user_achievements(user_id: str) -> UserAchievements:
    """Get user's achievements data."""
    storage = _get_achievements_storage()
    if user_id not in storage:
        storage[user_id] = UserAchievements(user_id=user_id)
    return storage[user_id]


def unlock_achievement(user_id: str, achievement_id: str) -> Optional[Dict]:
    """Unlock an achievement for user."""
    if achievement_id not in ACHIEVEMENTS_ENHANCED:
        return None

    user = get_user_achievements(user_id)
    if achievement_id in user.unlocked:
        return None

    achievement = ACHIEVEMENTS_ENHANCED[achievement_id]
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
        "total_available": len(ACHIEVEMENTS_ENHANCED)
    }


def update_achievement_progress(user_id: str, achievement_id: str, increment: int = 1) -> Optional[Dict]:
    """Update progress towards a progressive achievement."""
    user = get_user_achievements(user_id)

    if achievement_id in user.unlocked:
        return None

    current = user.progress.get(achievement_id, 0) + increment
    user.progress[achievement_id] = current

    # Check thresholds
    thresholds = {
        "watched_10": 10, "watched_50": 50, "watched_100": 100,
        "mrdp_chat_10": 10, "mrdp_chat_50": 50,
        "quick_picker": 10, "party_regular": 10,
        "referral_champion": 5, "mood_tracker_7": 7,
        "night_owl": 10, "early_bird": 5,
        "mrdp_accepted_all": 10, "mood_improved": 5,
        "calm_seeker": 5, "mrdp_marathon": 5,
        "streak_3": 3, "streak_7": 7, "streak_30": 30, "streak_100": 100,
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

    unlocked_list = []
    for aid in user.unlocked:
        if aid in ACHIEVEMENTS_ENHANCED:
            a = ACHIEVEMENTS_ENHANCED[aid]
            unlocked_list.append({
                "id": a.id, "name": a.name, "description": a.description,
                "icon": a.icon, "category": a.category.value, "points": a.points,
                "unlocked_at": user.unlock_dates.get(aid)
            })

    locked_list = []
    for aid, a in ACHIEVEMENTS_ENHANCED.items():
        if aid not in user.unlocked and not a.secret:
            locked_list.append({
                "id": a.id, "name": a.name, "description": a.description,
                "icon": a.icon, "category": a.category.value, "points": a.points,
                "requirement": a.requirement,
                "progress": user.progress.get(aid, 0)
            })

    total_points = sum(
        ACHIEVEMENTS_ENHANCED[aid].points for aid in user.unlocked
        if aid in ACHIEVEMENTS_ENHANCED
    )

    return {
        "user_id": user_id,
        "total_unlocked": len(user.unlocked),
        "total_available": len(ACHIEVEMENTS_ENHANCED),
        "total_points": total_points,
        "unlocked": unlocked_list,
        "locked": locked_list,
        "completion_percentage": round(len(user.unlocked) / len(ACHIEVEMENTS_ENHANCED) * 100, 1)
    }


def get_recent_achievements(user_id: str, limit: int = 5) -> List[Dict]:
    """Get user's most recently unlocked achievements."""
    user = get_user_achievements(user_id)
    sorted_achievements = sorted(
        user.unlock_dates.items(),
        key=lambda x: x[1],
        reverse=True
    )[:limit]

    result = []
    for aid, unlock_date in sorted_achievements:
        if aid in ACHIEVEMENTS_ENHANCED:
            a = ACHIEVEMENTS_ENHANCED[aid]
            result.append({
                "id": a.id, "name": a.name, "icon": a.icon,
                "points": a.points, "unlocked_at": unlock_date
            })
    return result


# --------------------------------------------------
# 4. STREAMLIT UI COMPONENTS
# --------------------------------------------------

# Leaderboard Preference (Research: Brain 5, Section 7 - RSD triggers)
# Social comparison can trigger Rejection Sensitive Dysphoria in ADHD users
# Leaderboards are OPT-IN by default to protect emotional wellbeing

def get_leaderboard_preference(user_id: str) -> bool:
    """Check if user has opted into seeing leaderboards.

    Research: Brain 5, Section 7 - Social comparison is an RSD trigger
    Default is OFF to protect users from unwanted comparison stress.
    """
    if 'leaderboard_preferences' not in st.session_state:
        st.session_state.leaderboard_preferences = {}
    # Default to False (opt-in required)
    return st.session_state.leaderboard_preferences.get(user_id, False)


def set_leaderboard_preference(user_id: str, show_leaderboard: bool):
    """Set user's leaderboard visibility preference."""
    if 'leaderboard_preferences' not in st.session_state:
        st.session_state.leaderboard_preferences = {}
    st.session_state.leaderboard_preferences[user_id] = show_leaderboard


def render_leaderboard_widget(leaderboard_type: str = "points", user_id: str = None):
    """Render a leaderboard widget (opt-in only).

    Research: Brain 5, Section 7 - Social comparison triggers RSD
    Users must explicitly enable leaderboards to see them.
    """
    # Check if user has opted into leaderboards
    if user_id and not get_leaderboard_preference(user_id):
        st.markdown("""
        <div style="padding: 16px; background: rgba(168, 85, 247, 0.05); border-radius: 12px; text-align: center;">
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 12px;">
                Leaderboards are hidden by default to keep things chill.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Show Leaderboard", key=f"enable_lb_{leaderboard_type}"):
            set_leaderboard_preference(user_id, True)
            st.rerun()
        return

    st.markdown("### 🏆 Leaderboard")

    # Add option to hide
    if user_id:
        if st.button("Hide Leaderboard", key=f"hide_lb_{leaderboard_type}", help="Social comparison isn't for everyone - and that's okay!"):
            set_leaderboard_preference(user_id, False)
            st.rerun()

    if leaderboard_type == "points":
        data = get_leaderboard(10)
        if not data:
            st.info("No leaderboard data yet. Be the first!")
            return

        for entry in data:
            rank_emoji = "🥇" if entry["rank"] == 1 else "🥈" if entry["rank"] == 2 else "🥉" if entry["rank"] == 3 else f"#{entry['rank']}"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 8px; margin: 4px 0; background: rgba(168, 85, 247, 0.1); border-radius: 8px;">
                <span>{rank_emoji} {entry['user_id'][:20]}...</span>
                <span><strong>{entry['points']:,}</strong> DP (Lv.{entry['level']})</span>
            </div>
            """, unsafe_allow_html=True)

    elif leaderboard_type == "streaks":
        data = get_streak_leaderboard(10)
        if not data:
            st.info("No streak data yet. Start your streak!")
            return

        for entry in data:
            rank_emoji = "🥇" if entry["rank"] == 1 else "🥈" if entry["rank"] == 2 else "🥉" if entry["rank"] == 3 else f"#{entry['rank']}"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 8px; margin: 4px 0; background: rgba(168, 85, 247, 0.1); border-radius: 8px;">
                <span>{rank_emoji} {entry['user_id'][:20]}...</span>
                <span>🔥 <strong>{entry['current_streak']}</strong> days</span>
            </div>
            """, unsafe_allow_html=True)


def render_streak_card(user_id: str):
    """Render a streak card for the user."""
    summary = get_streak_summary(user_id)

    streak_emoji = "🔥" if summary["current_streak"] >= 7 else "✨" if summary["current_streak"] >= 3 else "💫"

    at_risk = check_streak_at_risk(user_id)
    risk_badge = "⚠️ Log today to keep your streak!" if at_risk else ""

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); padding: 20px; border-radius: 16px; color: white; text-align: center;">
        <div style="font-size: 3rem;">{streak_emoji}</div>
        <div style="font-size: 2.5rem; font-weight: bold;">{summary['current_streak']} Day Streak</div>
        <div style="opacity: 0.8;">Longest: {summary['longest_streak']} days | Total: {summary['total_active_days']} days</div>
        <div style="color: #fbbf24; margin-top: 8px;">{risk_badge}</div>
    </div>
    """, unsafe_allow_html=True)


def render_achievement_toast(achievement_data: Dict):
    """Render an achievement unlock toast."""
    ach = achievement_data.get("achievement", {})
    st.balloons()
    st.success(f"""
    🎉 **Achievement Unlocked!**

    {ach.get('icon', '🏆')} **{ach.get('name', 'Achievement')}**

    {ach.get('description', '')}

    +{ach.get('points', 50)} Dopamine Points!
    """)


def render_achievements_grid(user_id: str):
    """Render achievements in a grid."""
    summary = get_achievements_summary(user_id)

    st.markdown(f"### 🏆 Achievements ({summary['total_unlocked']}/{summary['total_available']})")
    st.progress(summary['completion_percentage'] / 100)

    # Show unlocked
    if summary['unlocked']:
        st.markdown("#### ✅ Unlocked")
        cols = st.columns(4)
        for i, ach in enumerate(summary['unlocked']):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: rgba(34, 197, 94, 0.1); border-radius: 12px; margin: 4px;">
                    <div style="font-size: 2rem;">{ach['icon']}</div>
                    <div style="font-size: 0.8rem; font-weight: bold;">{ach['name']}</div>
                </div>
                """, unsafe_allow_html=True)

    # Show locked
    if summary['locked']:
        st.markdown("#### 🔒 Locked")
        cols = st.columns(4)
        for i, ach in enumerate(summary['locked'][:8]):  # Show first 8
            with cols[i % 4]:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: rgba(107, 114, 128, 0.1); border-radius: 12px; margin: 4px; opacity: 0.6;">
                    <div style="font-size: 2rem;">🔒</div>
                    <div style="font-size: 0.8rem;">{ach['name']}</div>
                </div>
                """, unsafe_allow_html=True)
