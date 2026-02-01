"""
Streak Tracking System
Track consecutive day usage for engagement.
"""

from typing import Dict, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass


# Streak milestone rewards
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


def get_streak_milestone_reward(streak_days: int) -> Optional[Dict]:
    """Get milestone reward if streak days matches a milestone."""
    return STREAK_MILESTONES.get(streak_days)


@dataclass
class UserStreak:
    """User's streak data."""
    user_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    streak_started: Optional[date] = None
    total_active_days: int = 0

    def is_streak_active(self) -> bool:
        """Check if streak is still active (activity today or yesterday)."""
        if not self.last_activity_date:
            return False
        today = date.today()
        return (today - self.last_activity_date).days <= 1


# In-memory storage
_user_streaks: Dict[str, UserStreak] = {}


def get_user_streak(user_id: str) -> UserStreak:
    """Get user's streak data."""
    if user_id not in _user_streaks:
        _user_streaks[user_id] = UserStreak(user_id=user_id)
    return _user_streaks[user_id]


def update_streak(user_id: str) -> Dict:
    """
    Update user's streak on activity.

    Returns:
        Dictionary with streak info and milestone status
    """
    streak = get_user_streak(user_id)
    today = date.today()

    milestone = None
    streak_broken = False
    new_streak = False

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

    # Consecutive day - extend streak
    elif streak.last_activity_date == today - timedelta(days=1):
        streak.current_streak += 1
        streak.total_active_days += 1
        streak.last_activity_date = today

        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        # Check milestones
        if streak.current_streak == 7:
            milestone = "7_day_streak"
        elif streak.current_streak == 30:
            milestone = "30_day_streak"
        elif streak.current_streak == 100:
            milestone = "100_day_streak"
        elif streak.current_streak == 365:
            milestone = "365_day_streak"

    # Streak broken - reset
    else:
        streak_broken = streak.current_streak > 0
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
        "streak_broken": streak_broken,
        "new_streak": new_streak,
        "is_active": streak.is_streak_active()
    }


def get_streak_summary(user_id: str) -> Dict:
    """Get user's streak summary."""
    streak = get_user_streak(user_id)

    # Calculate days until streak breaks
    days_remaining = None
    if streak.last_activity_date:
        today = date.today()
        if streak.last_activity_date == today:
            days_remaining = 1  # Must log tomorrow
        elif streak.last_activity_date == today - timedelta(days=1):
            days_remaining = 0  # Must log today!

    return {
        "user_id": user_id,
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "total_active_days": streak.total_active_days,
        "streak_started": streak.streak_started.isoformat() if streak.streak_started else None,
        "last_activity": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
        "is_active": streak.is_streak_active(),
        "days_until_break": days_remaining,
        "next_milestone": _get_next_milestone(streak.current_streak)
    }


def _get_next_milestone(current: int) -> Dict:
    """Get the next streak milestone."""
    milestones = [
        (7, "Week Warrior", "7 days of consistent dopamine!"),
        (30, "Monthly Master", "30 days - you're unstoppable!"),
        (100, "Century Champion", "100 days - legendary status!"),
        (365, "Year of Dopamine", "365 days - ultimate dedication!")
    ]

    for days, name, description in milestones:
        if current < days:
            return {
                "days_needed": days,
                "days_remaining": days - current,
                "name": name,
                "description": description
            }

    return {
        "days_needed": None,
        "name": "Streak Legend",
        "description": "You've achieved all milestones!"
    }


def check_streak_at_risk(user_id: str) -> bool:
    """Check if user's streak is at risk of breaking."""
    streak = get_user_streak(user_id)

    if not streak.last_activity_date or streak.current_streak == 0:
        return False

    today = date.today()
    # Streak is at risk if last activity was yesterday and not today
    return streak.last_activity_date == today - timedelta(days=1)


def get_streak_leaderboard(limit: int = 10) -> list:
    """Get top users by current streak."""
    sorted_users = sorted(
        _user_streaks.values(),
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


# Service class
class StreakService:
    """Streak service for dependency injection."""

    def get(self, user_id: str) -> UserStreak:
        return get_user_streak(user_id)

    def update(self, user_id: str) -> Dict:
        return update_streak(user_id)

    def summary(self, user_id: str) -> Dict:
        return get_streak_summary(user_id)

    def at_risk(self, user_id: str) -> bool:
        return check_streak_at_risk(user_id)

    def leaderboard(self, limit: int = 10) -> list:
        return get_streak_leaderboard(limit)


_streak_service: Optional[StreakService] = None


def get_streak_service() -> StreakService:
    """Get singleton streak service."""
    global _streak_service
    if _streak_service is None:
        _streak_service = StreakService()
    return _streak_service
