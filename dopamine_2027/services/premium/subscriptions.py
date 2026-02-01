"""
Subscription Management
Premium tiers and subscription status.
"""

from typing import Dict, Optional
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class SubscriptionTier(Enum):
    """Available subscription tiers."""
    FREE = "free"
    PLUS = "plus"
    PRO = "pro"


@dataclass
class TierLimits:
    """Limits for a subscription tier."""
    mrdp_chats_daily: int
    recommendations_daily: int
    quick_hits_daily: int
    watch_parties: bool
    analytics_access: bool
    ad_free: bool
    priority_support: bool
    points_multiplier: float
    badge: Optional[str]


# Tier configurations
TIER_CONFIGS: Dict[SubscriptionTier, TierLimits] = {
    SubscriptionTier.FREE: TierLimits(
        mrdp_chats_daily=5,
        recommendations_daily=10,
        quick_hits_daily=3,
        watch_parties=True,
        analytics_access=False,
        ad_free=False,
        priority_support=False,
        points_multiplier=1.0,
        badge=None
    ),
    SubscriptionTier.PLUS: TierLimits(
        mrdp_chats_daily=999,  # Unlimited
        recommendations_daily=999,
        quick_hits_daily=999,
        watch_parties=True,
        analytics_access=True,
        ad_free=True,
        priority_support=False,
        points_multiplier=2.0,
        badge="👑"
    ),
    SubscriptionTier.PRO: TierLimits(
        mrdp_chats_daily=999,
        recommendations_daily=999,
        quick_hits_daily=999,
        watch_parties=True,
        analytics_access=True,
        ad_free=True,
        priority_support=True,
        points_multiplier=3.0,
        badge="💎"
    ),
}

# Pricing
TIER_PRICING = {
    SubscriptionTier.FREE: {"monthly": 0, "yearly": 0},
    SubscriptionTier.PLUS: {"monthly": 4.99, "yearly": 49.99},
    SubscriptionTier.PRO: {"monthly": 9.99, "yearly": 99.99},
}


@dataclass
class UserSubscription:
    """User's subscription data."""
    user_id: str
    tier: SubscriptionTier = SubscriptionTier.FREE
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    billing_cycle: str = "monthly"  # monthly, yearly
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    canceled: bool = False
    cancel_at_period_end: bool = False


# In-memory storage
_user_subscriptions: Dict[str, UserSubscription] = {}


def get_user_subscription(user_id: str) -> UserSubscription:
    """Get user's subscription."""
    if user_id not in _user_subscriptions:
        _user_subscriptions[user_id] = UserSubscription(user_id=user_id)
    return _user_subscriptions[user_id]


def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    """Get limits for a tier."""
    return TIER_CONFIGS[tier]


def is_premium(user_id: str) -> bool:
    """Check if user has any premium tier."""
    sub = get_user_subscription(user_id)
    return sub.tier != SubscriptionTier.FREE


def get_user_tier(user_id: str) -> SubscriptionTier:
    """Get user's subscription tier."""
    sub = get_user_subscription(user_id)
    return sub.tier


def get_subscription_info(user_id: str) -> Dict:
    """Get full subscription information for user."""
    sub = get_user_subscription(user_id)
    limits = get_tier_limits(sub.tier)

    return {
        "user_id": user_id,
        "tier": sub.tier.value,
        "is_premium": sub.tier != SubscriptionTier.FREE,
        "started_at": sub.started_at.isoformat() if sub.started_at else None,
        "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
        "billing_cycle": sub.billing_cycle,
        "canceled": sub.canceled,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "limits": {
            "mrdp_chats_daily": limits.mrdp_chats_daily,
            "recommendations_daily": limits.recommendations_daily,
            "quick_hits_daily": limits.quick_hits_daily,
            "watch_parties": limits.watch_parties,
            "analytics_access": limits.analytics_access,
            "ad_free": limits.ad_free,
            "points_multiplier": limits.points_multiplier
        },
        "badge": limits.badge
    }


def upgrade_subscription(
    user_id: str,
    tier: SubscriptionTier,
    billing_cycle: str = "monthly",
    stripe_customer_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None
) -> Dict:
    """Upgrade user's subscription."""
    from datetime import timedelta

    sub = get_user_subscription(user_id)

    # Set new tier
    old_tier = sub.tier
    sub.tier = tier
    sub.started_at = datetime.now()
    sub.billing_cycle = billing_cycle
    sub.canceled = False
    sub.cancel_at_period_end = False

    # Set expiration
    if billing_cycle == "yearly":
        sub.expires_at = datetime.now() + timedelta(days=365)
    else:
        sub.expires_at = datetime.now() + timedelta(days=30)

    # Store Stripe IDs if provided
    if stripe_customer_id:
        sub.stripe_customer_id = stripe_customer_id
    if stripe_subscription_id:
        sub.stripe_subscription_id = stripe_subscription_id

    return {
        "success": True,
        "user_id": user_id,
        "old_tier": old_tier.value,
        "new_tier": tier.value,
        "expires_at": sub.expires_at.isoformat(),
        "message": f"Welcome to {tier.value.title()}!"
    }


def cancel_subscription(user_id: str, at_period_end: bool = True) -> Dict:
    """Cancel user's subscription."""
    sub = get_user_subscription(user_id)

    if sub.tier == SubscriptionTier.FREE:
        return {
            "success": False,
            "message": "No active subscription to cancel"
        }

    if at_period_end:
        sub.cancel_at_period_end = True
        return {
            "success": True,
            "message": f"Subscription will cancel at end of period ({sub.expires_at.strftime('%Y-%m-%d') if sub.expires_at else 'unknown'})",
            "effective_date": sub.expires_at.isoformat() if sub.expires_at else None
        }
    else:
        sub.tier = SubscriptionTier.FREE
        sub.canceled = True
        return {
            "success": True,
            "message": "Subscription canceled immediately",
            "effective_date": datetime.now().isoformat()
        }


def check_subscription_expired(user_id: str) -> bool:
    """Check if subscription has expired."""
    sub = get_user_subscription(user_id)

    if sub.tier == SubscriptionTier.FREE:
        return False

    if sub.expires_at and datetime.now() > sub.expires_at:
        # Downgrade to free
        sub.tier = SubscriptionTier.FREE
        sub.canceled = True
        return True

    return False


def get_pricing_info() -> Dict:
    """Get pricing information for all tiers."""
    return {
        "tiers": [
            {
                "id": tier.value,
                "name": tier.value.title(),
                "monthly_price": TIER_PRICING[tier]["monthly"],
                "yearly_price": TIER_PRICING[tier]["yearly"],
                "yearly_savings": (TIER_PRICING[tier]["monthly"] * 12) - TIER_PRICING[tier]["yearly"],
                "limits": {
                    "mrdp_chats": TIER_CONFIGS[tier].mrdp_chats_daily,
                    "recommendations": TIER_CONFIGS[tier].recommendations_daily,
                    "quick_hits": TIER_CONFIGS[tier].quick_hits_daily,
                    "analytics": TIER_CONFIGS[tier].analytics_access,
                    "ad_free": TIER_CONFIGS[tier].ad_free,
                    "points_multiplier": TIER_CONFIGS[tier].points_multiplier
                },
                "badge": TIER_CONFIGS[tier].badge
            }
            for tier in SubscriptionTier
        ]
    }


# Service class
class SubscriptionService:
    """Subscription service for dependency injection."""

    def get(self, user_id: str) -> UserSubscription:
        return get_user_subscription(user_id)

    def info(self, user_id: str) -> Dict:
        return get_subscription_info(user_id)

    def is_premium(self, user_id: str) -> bool:
        return is_premium(user_id)

    def upgrade(self, user_id: str, tier: SubscriptionTier, **kwargs) -> Dict:
        return upgrade_subscription(user_id, tier, **kwargs)

    def cancel(self, user_id: str, at_period_end: bool = True) -> Dict:
        return cancel_subscription(user_id, at_period_end)

    def check_expired(self, user_id: str) -> bool:
        return check_subscription_expired(user_id)

    def pricing(self) -> Dict:
        return get_pricing_info()

    def limits(self, tier: SubscriptionTier) -> TierLimits:
        return get_tier_limits(tier)


_subscription_service: Optional[SubscriptionService] = None


def get_subscription_service() -> SubscriptionService:
    """Get singleton subscription service."""
    global _subscription_service
    if _subscription_service is None:
        _subscription_service = SubscriptionService()
    return _subscription_service
