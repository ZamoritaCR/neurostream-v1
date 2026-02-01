"""
Gamification Services
Points, streaks, and achievements for user engagement.
"""

from .points import (
    PointAction,
    UserPoints,
    get_user_points,
    add_points,
    get_points_summary,
    get_leaderboard,
    get_user_rank,
    get_points_service,
    PointsService
)

from .streaks import (
    UserStreak,
    get_user_streak,
    update_streak,
    get_streak_summary,
    check_streak_at_risk,
    get_streak_leaderboard,
    get_streak_service,
    StreakService
)

from .achievements import (
    Achievement,
    AchievementCategory,
    ACHIEVEMENTS,
    UserAchievements,
    get_user_achievements,
    unlock_achievement,
    check_and_unlock,
    update_progress,
    get_achievements_summary,
    get_recent_achievements,
    get_achievement_service,
    AchievementService
)

__all__ = [
    # Points
    "PointAction",
    "UserPoints",
    "get_user_points",
    "add_points",
    "get_points_summary",
    "get_leaderboard",
    "get_user_rank",
    "get_points_service",
    "PointsService",

    # Streaks
    "UserStreak",
    "get_user_streak",
    "update_streak",
    "get_streak_summary",
    "check_streak_at_risk",
    "get_streak_leaderboard",
    "get_streak_service",
    "StreakService",

    # Achievements
    "Achievement",
    "AchievementCategory",
    "ACHIEVEMENTS",
    "UserAchievements",
    "get_user_achievements",
    "unlock_achievement",
    "check_and_unlock",
    "update_progress",
    "get_achievements_summary",
    "get_recent_achievements",
    "get_achievement_service",
    "AchievementService",
]
