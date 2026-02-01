"""
Gamification API Routes
Points, streaks, and achievements endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from services.gamification import (
    get_points_service,
    get_streak_service,
    get_achievement_service,
    PointAction
)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AddPointsRequest(BaseModel):
    user_id: str
    action: str
    multiplier: float = 1.0
    bonus: int = 0


class UnlockAchievementRequest(BaseModel):
    user_id: str
    achievement_id: str


class ProgressRequest(BaseModel):
    user_id: str
    achievement_id: str
    increment: int = 1


# ═══════════════════════════════════════════════════════════════════════════════
# POINTS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/points/{user_id}")
async def get_points(user_id: str):
    """Get user's dopamine points summary."""
    service = get_points_service()
    return service.summary(user_id)


@router.post("/points/add")
async def add_points(request: AddPointsRequest):
    """Add dopamine points for an action."""
    try:
        action = PointAction[request.action.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action: {request.action}. Valid actions: {[a.name for a in PointAction]}"
        )

    service = get_points_service()
    result = service.add(
        request.user_id,
        action,
        multiplier=request.multiplier,
        bonus=request.bonus
    )

    return result


@router.get("/leaderboard/points")
async def points_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """Get top users by dopamine points."""
    service = get_points_service()
    return {
        "leaderboard": service.leaderboard(limit),
        "type": "points"
    }


@router.get("/rank/{user_id}")
async def get_user_rank(user_id: str):
    """Get user's rank in the leaderboard."""
    service = get_points_service()
    return {
        "user_id": user_id,
        "rank": service.rank(user_id)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STREAK ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/streak/{user_id}")
async def get_streak(user_id: str):
    """Get user's streak information."""
    service = get_streak_service()
    return service.summary(user_id)


@router.post("/streak/{user_id}/update")
async def update_streak(user_id: str):
    """Update user's streak (call on daily activity)."""
    service = get_streak_service()
    return service.update(user_id)


@router.get("/streak/{user_id}/at-risk")
async def check_streak_risk(user_id: str):
    """Check if user's streak is at risk of breaking."""
    service = get_streak_service()
    return {
        "user_id": user_id,
        "at_risk": service.at_risk(user_id),
        "message": "Log in today to keep your streak!" if service.at_risk(user_id) else "Your streak is safe!"
    }


@router.get("/leaderboard/streaks")
async def streak_leaderboard(limit: int = Query(10, ge=1, le=100)):
    """Get top users by streak."""
    service = get_streak_service()
    return {
        "leaderboard": service.leaderboard(limit),
        "type": "streaks"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/achievements/{user_id}")
async def get_achievements(user_id: str):
    """Get user's achievements summary."""
    service = get_achievement_service()
    return service.summary(user_id)


@router.get("/achievements/{user_id}/recent")
async def get_recent_achievements(user_id: str, limit: int = Query(5, ge=1, le=20)):
    """Get user's recently unlocked achievements."""
    service = get_achievement_service()
    return {
        "user_id": user_id,
        "recent": service.recent(user_id, limit)
    }


@router.post("/achievements/unlock")
async def unlock_achievement(request: UnlockAchievementRequest):
    """Manually unlock an achievement."""
    service = get_achievement_service()

    if request.achievement_id not in service.all_achievements:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid achievement: {request.achievement_id}"
        )

    result = service.unlock(request.user_id, request.achievement_id)

    if result is None:
        return {
            "unlocked": False,
            "message": "Achievement already unlocked or invalid"
        }

    return {
        "unlocked": True,
        **result
    }


@router.post("/achievements/progress")
async def update_achievement_progress(request: ProgressRequest):
    """Update progress towards a progressive achievement."""
    service = get_achievement_service()
    result = service.progress(request.user_id, request.achievement_id, request.increment)

    if result is None:
        return {
            "updated": False,
            "message": "Achievement already unlocked or invalid"
        }

    return {
        "updated": True,
        **result
    }


@router.get("/achievements/all")
async def list_all_achievements():
    """List all available achievements."""
    service = get_achievement_service()
    achievements = service.all_achievements

    return {
        "total": len(achievements),
        "achievements": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "category": a.category.value,
                "points": a.points,
                "secret": a.secret,
                "requirement": a.requirement
            }
            for a in achievements.values()
            if not a.secret
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED STATS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/stats/{user_id}")
async def get_gamification_stats(user_id: str):
    """Get combined gamification stats for user."""
    points_service = get_points_service()
    streak_service = get_streak_service()
    achievement_service = get_achievement_service()

    points = points_service.summary(user_id)
    streak = streak_service.summary(user_id)
    achievements = achievement_service.summary(user_id)

    return {
        "user_id": user_id,
        "points": {
            "total": points["total_points"],
            "level": points["level"],
            "today": points["points_today"],
            "to_next_level": points["to_next_level"]
        },
        "streak": {
            "current": streak["current_streak"],
            "longest": streak["longest_streak"],
            "is_active": streak["is_active"],
            "at_risk": streak_service.at_risk(user_id)
        },
        "achievements": {
            "unlocked": achievements["total_unlocked"],
            "total": achievements["total_available"],
            "completion": achievements["completion_percentage"],
            "total_points": achievements["total_points"]
        }
    }
