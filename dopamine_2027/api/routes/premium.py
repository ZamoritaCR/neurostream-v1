"""
Premium API Routes
Subscription management and usage limits.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from services.premium import (
    get_subscription_service,
    get_usage_service,
    SubscriptionTier,
    UsageType
)

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class UpgradeRequest(BaseModel):
    user_id: str
    tier: str
    billing_cycle: str = "monthly"
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None


class CancelRequest(BaseModel):
    user_id: str
    at_period_end: bool = True


class UsageRequest(BaseModel):
    user_id: str
    usage_type: str


# ═══════════════════════════════════════════════════════════════════════════════
# SUBSCRIPTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/subscription/{user_id}")
async def get_subscription(user_id: str):
    """Get user's subscription information."""
    service = get_subscription_service()
    return service.info(user_id)


@router.get("/subscription/{user_id}/is-premium")
async def check_premium(user_id: str):
    """Check if user has premium subscription."""
    service = get_subscription_service()
    return {
        "user_id": user_id,
        "is_premium": service.is_premium(user_id)
    }


@router.post("/subscription/upgrade")
async def upgrade_subscription(request: UpgradeRequest):
    """Upgrade user's subscription."""
    try:
        tier = SubscriptionTier(request.tier.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier: {request.tier}. Valid tiers: free, plus, pro"
        )

    service = get_subscription_service()
    return service.upgrade(
        request.user_id,
        tier,
        billing_cycle=request.billing_cycle,
        stripe_customer_id=request.stripe_customer_id,
        stripe_subscription_id=request.stripe_subscription_id
    )


@router.post("/subscription/cancel")
async def cancel_subscription(request: CancelRequest):
    """Cancel user's subscription."""
    service = get_subscription_service()
    return service.cancel(request.user_id, request.at_period_end)


@router.get("/pricing")
async def get_pricing():
    """Get pricing information for all tiers."""
    service = get_subscription_service()
    return service.pricing()


# ═══════════════════════════════════════════════════════════════════════════════
# USAGE LIMITS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/usage/{user_id}")
async def get_usage(user_id: str):
    """Get user's daily usage summary."""
    service = get_usage_service()
    return service.summary(user_id)


@router.post("/usage/check")
async def check_usage(request: UsageRequest):
    """Check if user can perform an action."""
    try:
        usage_type = UsageType(request.usage_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid usage type: {request.usage_type}. Valid types: mrdp_chat, recommendation, quick_hit"
        )

    service = get_usage_service()
    return service.can_use(request.user_id, usage_type)


@router.post("/usage/increment")
async def increment_usage(request: UsageRequest):
    """Increment usage counter for an action."""
    try:
        usage_type = UsageType(request.usage_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid usage type: {request.usage_type}"
        )

    service = get_usage_service()
    return service.increment(request.user_id, usage_type)


@router.get("/usage/{user_id}/should-upgrade")
async def should_show_upgrade(user_id: str):
    """Check if upgrade prompt should be shown."""
    service = get_usage_service()
    return service.should_upgrade(user_id)


# ═══════════════════════════════════════════════════════════════════════════════
# COMBINED INFO
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/status/{user_id}")
async def get_premium_status(user_id: str):
    """Get combined premium status and usage for user."""
    sub_service = get_subscription_service()
    usage_service = get_usage_service()

    subscription = sub_service.info(user_id)
    usage = usage_service.summary(user_id)
    upgrade_prompt = usage_service.should_upgrade(user_id)

    return {
        "user_id": user_id,
        "subscription": {
            "tier": subscription["tier"],
            "is_premium": subscription["is_premium"],
            "badge": subscription.get("badge"),
            "expires_at": subscription.get("expires_at")
        },
        "usage": usage["usage"],
        "show_upgrade_prompt": upgrade_prompt.get("show", False),
        "upgrade_triggers": upgrade_prompt.get("triggers", [])
    }
