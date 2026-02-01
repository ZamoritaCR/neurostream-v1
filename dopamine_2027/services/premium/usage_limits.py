"""
Usage Limits System
Track and enforce daily usage limits based on subscription tier.
"""

from typing import Dict, Optional
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum

from .subscriptions import (
    get_user_subscription,
    get_tier_limits,
    SubscriptionTier
)


class UsageType(Enum):
    """Types of usage that can be limited."""
    MRDP_CHAT = "mrdp_chat"
    RECOMMENDATION = "recommendation"
    QUICK_HIT = "quick_hit"


@dataclass
class DailyUsage:
    """User's daily usage data."""
    user_id: str
    date: date = field(default_factory=date.today)
    mrdp_chats: int = 0
    recommendations: int = 0
    quick_hits: int = 0


# Usage limits by tier (for easy reference)
USAGE_LIMITS: Dict[UsageType, Dict[str, int]] = {
    UsageType.MRDP_CHAT: {"free": 5, "plus": 999, "pro": 999},
    UsageType.RECOMMENDATION: {"free": 10, "plus": 999, "pro": 999},
    UsageType.QUICK_HIT: {"free": 3, "plus": 999, "pro": 999}
}


# In-memory storage
_daily_usage: Dict[str, DailyUsage] = {}


def _get_usage_key(user_id: str) -> str:
    """Get storage key for user's daily usage."""
    return f"{user_id}_{date.today().isoformat()}"


def get_daily_usage(user_id: str) -> DailyUsage:
    """Get user's daily usage, creating if needed."""
    key = _get_usage_key(user_id)

    if key not in _daily_usage:
        _daily_usage[key] = DailyUsage(user_id=user_id)

    usage = _daily_usage[key]

    # Reset if new day
    if usage.date != date.today():
        usage = DailyUsage(user_id=user_id)
        _daily_usage[key] = usage

    return usage


def increment_usage(user_id: str, usage_type: UsageType) -> Dict:
    """
    Increment usage counter and check limit.

    Returns:
        Dictionary with success status and remaining usage
    """
    usage = get_daily_usage(user_id)
    sub = get_user_subscription(user_id)
    limits = get_tier_limits(sub.tier)

    # Get current count and limit
    if usage_type == UsageType.MRDP_CHAT:
        current = usage.mrdp_chats
        limit = limits.mrdp_chats_daily
        usage.mrdp_chats += 1
    elif usage_type == UsageType.RECOMMENDATION:
        current = usage.recommendations
        limit = limits.recommendations_daily
        usage.recommendations += 1
    elif usage_type == UsageType.QUICK_HIT:
        current = usage.quick_hits
        limit = limits.quick_hits_daily
        usage.quick_hits += 1
    else:
        return {"success": False, "error": "Invalid usage type"}

    remaining = max(0, limit - current - 1)

    return {
        "success": True,
        "usage_type": usage_type.value,
        "used": current + 1,
        "limit": limit,
        "remaining": remaining,
        "at_limit": remaining == 0
    }


def check_can_use(user_id: str, usage_type: UsageType) -> Dict:
    """
    Check if user can perform action (without incrementing).

    Returns:
        Dictionary with allowed status and usage info
    """
    usage = get_daily_usage(user_id)
    sub = get_user_subscription(user_id)
    limits = get_tier_limits(sub.tier)

    # Get current count and limit
    if usage_type == UsageType.MRDP_CHAT:
        current = usage.mrdp_chats
        limit = limits.mrdp_chats_daily
    elif usage_type == UsageType.RECOMMENDATION:
        current = usage.recommendations
        limit = limits.recommendations_daily
    elif usage_type == UsageType.QUICK_HIT:
        current = usage.quick_hits
        limit = limits.quick_hits_daily
    else:
        return {"allowed": False, "error": "Invalid usage type"}

    allowed = current < limit
    remaining = max(0, limit - current)

    return {
        "allowed": allowed,
        "usage_type": usage_type.value,
        "used": current,
        "limit": limit,
        "remaining": remaining,
        "tier": sub.tier.value,
        "upgrade_message": None if allowed else _get_upgrade_message(usage_type)
    }


def _get_upgrade_message(usage_type: UsageType) -> str:
    """Get upgrade message for when limit is reached."""
    messages = {
        UsageType.MRDP_CHAT: "You've used all your Mr.DP chats today! Upgrade to Plus for unlimited chats.",
        UsageType.RECOMMENDATION: "You've reached your daily recommendation limit! Upgrade for unlimited recommendations.",
        UsageType.QUICK_HIT: "No more Quick Dope Hits today! Upgrade to Plus for unlimited instant picks."
    }
    return messages.get(usage_type, "Daily limit reached. Upgrade for unlimited access!")


def get_usage_summary(user_id: str) -> Dict:
    """Get complete usage summary for user."""
    usage = get_daily_usage(user_id)
    sub = get_user_subscription(user_id)
    limits = get_tier_limits(sub.tier)

    return {
        "user_id": user_id,
        "tier": sub.tier.value,
        "date": usage.date.isoformat(),
        "usage": {
            "mrdp_chats": {
                "used": usage.mrdp_chats,
                "limit": limits.mrdp_chats_daily,
                "remaining": max(0, limits.mrdp_chats_daily - usage.mrdp_chats),
                "percentage": min(100, (usage.mrdp_chats / limits.mrdp_chats_daily) * 100)
            },
            "recommendations": {
                "used": usage.recommendations,
                "limit": limits.recommendations_daily,
                "remaining": max(0, limits.recommendations_daily - usage.recommendations),
                "percentage": min(100, (usage.recommendations / limits.recommendations_daily) * 100)
            },
            "quick_hits": {
                "used": usage.quick_hits,
                "limit": limits.quick_hits_daily,
                "remaining": max(0, limits.quick_hits_daily - usage.quick_hits),
                "percentage": min(100, (usage.quick_hits / limits.quick_hits_daily) * 100)
            }
        },
        "is_premium": sub.tier != SubscriptionTier.FREE,
        "resets_at": "midnight local time"
    }


def should_show_upgrade_prompt(user_id: str) -> Dict:
    """Check if we should show an upgrade prompt."""
    usage = get_daily_usage(user_id)
    sub = get_user_subscription(user_id)

    if sub.tier != SubscriptionTier.FREE:
        return {"show": False}

    limits = get_tier_limits(sub.tier)

    # Check if any limit is at 80% or more
    triggers = []

    if usage.mrdp_chats >= limits.mrdp_chats_daily * 0.8:
        triggers.append({
            "type": "mrdp_chats",
            "message": f"You've used {usage.mrdp_chats} of {limits.mrdp_chats_daily} Mr.DP chats"
        })

    if usage.recommendations >= limits.recommendations_daily * 0.8:
        triggers.append({
            "type": "recommendations",
            "message": f"You've used {usage.recommendations} of {limits.recommendations_daily} recommendations"
        })

    if usage.quick_hits >= limits.quick_hits_daily * 0.8:
        triggers.append({
            "type": "quick_hits",
            "message": f"You've used {usage.quick_hits} of {limits.quick_hits_daily} Quick Dope Hits"
        })

    if triggers:
        return {
            "show": True,
            "triggers": triggers,
            "cta": "Upgrade to Plus for unlimited access!",
            "price": "$4.99/month"
        }

    return {"show": False}


# Service class
class UsageLimitService:
    """Usage limit service for dependency injection."""

    def get_usage(self, user_id: str) -> DailyUsage:
        return get_daily_usage(user_id)

    def increment(self, user_id: str, usage_type: UsageType) -> Dict:
        return increment_usage(user_id, usage_type)

    def can_use(self, user_id: str, usage_type: UsageType) -> Dict:
        return check_can_use(user_id, usage_type)

    def summary(self, user_id: str) -> Dict:
        return get_usage_summary(user_id)

    def should_upgrade(self, user_id: str) -> Dict:
        return should_show_upgrade_prompt(user_id)


_usage_service: Optional[UsageLimitService] = None


def get_usage_service() -> UsageLimitService:
    """Get singleton usage limit service."""
    global _usage_service
    if _usage_service is None:
        _usage_service = UsageLimitService()
    return _usage_service
