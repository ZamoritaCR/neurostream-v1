"""
Dopamine Points System
Reward system for user engagement and gamification.
"""

from typing import Dict, Optional
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum


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
        import math
        return int(math.sqrt(self.total_points / 100)) + 1

    def points_to_next_level(self) -> int:
        """Calculate points needed for next level."""
        next_level = self.level + 1
        required = ((next_level - 1) ** 2) * 100
        return max(0, required - self.total_points)


# In-memory storage (replace with database in production)
_user_points: Dict[str, UserPoints] = {}


def get_user_points(user_id: str) -> UserPoints:
    """Get user's points data."""
    if user_id not in _user_points:
        _user_points[user_id] = UserPoints(user_id=user_id)
    return _user_points[user_id]


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


def get_leaderboard(limit: int = 10) -> list:
    """Get top users by points."""
    sorted_users = sorted(
        _user_points.values(),
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
    if user_id not in _user_points:
        return 0

    user_points = _user_points[user_id].total_points
    rank = 1

    for u in _user_points.values():
        if u.total_points > user_points:
            rank += 1

    return rank


def calculate_level(total_points: int) -> Dict:
    """
    Calculate level from points (standalone function).

    Args:
        total_points: Total dopamine points

    Returns:
        Dictionary with level info
    """
    import math
    level = int(math.sqrt(total_points / 100)) + 1
    current_level_points = ((level - 1) ** 2) * 100
    next_level_points = (level ** 2) * 100
    progress = total_points - current_level_points
    needed = next_level_points - current_level_points

    return {
        "level": level,
        "total_points": total_points,
        "current_level_points": current_level_points,
        "next_level_points": next_level_points,
        "progress": progress,
        "needed_for_next": needed - progress,
        "percentage": round((progress / needed) * 100, 1) if needed > 0 else 100
    }


# Singleton service
class PointsService:
    """Service class for dependency injection."""

    def get_points(self, user_id: str) -> UserPoints:
        return get_user_points(user_id)

    def add(self, user_id: str, action: PointAction, **kwargs) -> Dict:
        return add_points(user_id, action, **kwargs)

    def summary(self, user_id: str) -> Dict:
        return get_points_summary(user_id)

    def leaderboard(self, limit: int = 10) -> list:
        return get_leaderboard(limit)

    def rank(self, user_id: str) -> int:
        return get_user_rank(user_id)


_points_service: Optional[PointsService] = None


def get_points_service() -> PointsService:
    """Get singleton points service."""
    global _points_service
    if _points_service is None:
        _points_service = PointsService()
    return _points_service
