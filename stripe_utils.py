# stripe_utils.py
# --------------------------------------------------
# DOPAMINE.WATCH - STRIPE PAYMENT INTEGRATION
# --------------------------------------------------

import os
import streamlit as st
from datetime import datetime, timedelta

# Initialize Stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    stripe = None

# Stripe API Keys (from secrets or environment)
def get_stripe_keys():
    """Get Stripe API keys from secrets or environment variables"""
    secret_key = st.secrets.get("stripe", {}).get("secret_key", "") or os.environ.get("STRIPE_SECRET_KEY", "")
    publishable_key = st.secrets.get("stripe", {}).get("publishable_key", "") or os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
    webhook_secret = st.secrets.get("stripe", {}).get("webhook_secret", "") or os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    return {
        "secret_key": secret_key,
        "publishable_key": publishable_key,
        "webhook_secret": webhook_secret
    }

# Initialize Stripe with secret key
def init_stripe():
    """Initialize Stripe with API key"""
    if not STRIPE_AVAILABLE:
        return False

    keys = get_stripe_keys()
    if keys["secret_key"]:
        stripe.api_key = keys["secret_key"]
        return True
    return False

def get_stripe():
    """Get configured Stripe client (legacy support)"""
    init_stripe()
    return stripe

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "name_es": "Gratis",
        "price": 0,
        "price_id": None,
        "features": [
            "Mood-based discovery",
            "Quick Dope Hit",
            "All content types",
            "5 Mr.DP chats/day",
            "Community features"
        ],
        "features_es": [
            "Descubrimiento por estado de animo",
            "Dosis Rapida",
            "Todos los tipos de contenido",
            "5 chats de Mr.DP/dia",
            "Funciones de comunidad"
        ],
        "mr_dp_limit": 5,
        "recommendations_limit": 10,
        "quick_hits_limit": 3
    },
    "plus": {
        "name": "Plus",
        "name_es": "Plus",
        "price": 4.99,
        "price_id": os.environ.get("STRIPE_PLUS_PRICE_ID", "price_plus_monthly"),
        "features": [
            "Everything in Free",
            "Unlimited Mr.DP chats",
            "No ads ever",
            "2x Dopamine Points",
            "Mood analytics & insights",
            "Priority support"
        ],
        "features_es": [
            "Todo lo de Gratis",
            "Chats ilimitados con Mr.DP",
            "Sin anuncios",
            "2x Puntos de Dopamina",
            "Analisis de animo e insights",
            "Soporte prioritario"
        ],
        "mr_dp_limit": -1,  # Unlimited
        "recommendations_limit": -1,
        "quick_hits_limit": -1
    },
}

def create_checkout_url(user_id: str, user_email: str, plan: str = "plus") -> str:
    """Create Stripe checkout session and return URL"""
    if not STRIPE_AVAILABLE or not init_stripe():
        return None

    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["plus"])
    price_id = plan_info.get("price_id") or os.getenv("STRIPE_PRICE_ID")

    if not price_id:
        return None

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=os.getenv("APP_URL", "https://app.dopamine.watch") + "?upgraded=true",
            cancel_url=os.getenv("APP_URL", "https://app.dopamine.watch") + "?canceled=true",
            customer_email=user_email,
            metadata={"user_id": user_id, "plan": plan}
        )
        return session.url
    except Exception as e:
        print(f"Stripe checkout error: {e}")
        return None

def create_checkout_session(user_id: str, user_email: str, plan: str, success_url: str, cancel_url: str) -> dict:
    """Create a Stripe checkout session for subscription"""
    if not STRIPE_AVAILABLE or not init_stripe():
        return {"success": False, "error": "Stripe not configured"}

    plan_info = SUBSCRIPTION_PLANS.get(plan)
    if not plan_info or plan == "free":
        return {"success": False, "error": "Invalid plan"}

    try:
        # Create or retrieve customer
        customers = stripe.Customer.list(email=user_email, limit=1)
        if customers.data:
            customer = customers.data[0]
        else:
            customer = stripe.Customer.create(
                email=user_email,
                metadata={"user_id": user_id}
            )

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=["card"],
            line_items=[{
                "price": plan_info["price_id"],
                "quantity": 1
            }],
            mode="subscription",
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={
                "user_id": user_id,
                "plan": plan
            }
        )

        return {
            "success": True,
            "session_id": session.id,
            "checkout_url": session.url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_billing_portal_session(customer_id: str, return_url: str) -> dict:
    """Create a Stripe billing portal session for subscription management"""
    if not STRIPE_AVAILABLE or not init_stripe():
        return {"success": False, "error": "Stripe not configured"}

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url
        )
        return {
            "success": True,
            "portal_url": session.url
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_subscription_status(customer_id: str) -> dict:
    """Get subscription status for a customer"""
    if not STRIPE_AVAILABLE or not init_stripe():
        return {"active": False, "plan": "free"}

    try:
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1
        )

        if subscriptions.data:
            sub = subscriptions.data[0]
            # Determine plan from price ID
            price_id = sub["items"]["data"][0]["price"]["id"]
            plan = "free"
            for plan_key, plan_info in SUBSCRIPTION_PLANS.items():
                if plan_info.get("price_id") == price_id:
                    plan = plan_key
                    break

            return {
                "active": True,
                "plan": plan,
                "subscription_id": sub.id,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end
            }

        return {"active": False, "plan": "free"}
    except Exception as e:
        return {"active": False, "plan": "free", "error": str(e)}

def cancel_subscription(subscription_id: str) -> dict:
    """Cancel a subscription at period end"""
    if not STRIPE_AVAILABLE or not init_stripe():
        return {"success": False, "error": "Stripe not configured"}

    try:
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        return {
            "success": True,
            "cancel_at": subscription.cancel_at
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def handle_successful_upgrade(supabase_client, user_id: str, stripe_customer_id: str = None, plan: str = "plus"):
    """Update subscription status after successful payment"""
    try:
        supabase_client.table("subscriptions").upsert({
            "user_id": user_id,
            "stripe_customer_id": stripe_customer_id,
            "plan_type": plan,
            "status": "active",
            "current_period_end": (datetime.now() + timedelta(days=30)).isoformat(),
            "updated_at": datetime.now().isoformat()
        }, on_conflict="user_id").execute()

        # Update profile
        supabase_client.table("profiles").update({
            "is_premium": True
        }).eq("id", user_id).execute()

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def handle_webhook_event(payload: bytes, sig_header: str) -> dict:
    """Handle incoming Stripe webhook events"""
    if not STRIPE_AVAILABLE or not init_stripe():
        return {"success": False, "error": "Stripe not configured"}

    keys = get_stripe_keys()
    webhook_secret = keys["webhook_secret"]

    if not webhook_secret:
        return {"success": False, "error": "Webhook secret not configured"}

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return {"success": False, "error": "Invalid payload"}
    except stripe.error.SignatureVerificationError:
        return {"success": False, "error": "Invalid signature"}

    # Handle specific events
    event_type = event["type"]
    data = event["data"]["object"]

    result = {"success": True, "event_type": event_type}

    if event_type == "checkout.session.completed":
        result["action"] = "subscription_created"
        result["user_id"] = data.get("metadata", {}).get("user_id")
        result["plan"] = data.get("metadata", {}).get("plan")
        result["customer_id"] = data.get("customer")

    elif event_type == "customer.subscription.updated":
        result["action"] = "subscription_updated"
        result["subscription_id"] = data.get("id")
        result["status"] = data.get("status")

    elif event_type == "customer.subscription.deleted":
        result["action"] = "subscription_cancelled"
        result["subscription_id"] = data.get("id")

    elif event_type == "invoice.payment_failed":
        result["action"] = "payment_failed"
        result["customer_id"] = data.get("customer")

    return result

def render_pricing_page():
    """Render a full pricing page with feature comparison"""

    st.markdown("""
    <style>
    .pricing-hero {
        text-align: center;
        padding: 40px 20px;
    }
    .pricing-hero h1 {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #8A56E2, #00C9A7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
    }
    .pricing-hero p {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1.1rem;
    }
    .pricing-grid-full {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 24px;
        margin: 32px 0;
    }
    .price-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 32px;
        transition: all 0.3s ease;
        position: relative;
    }
    .price-card:hover {
        transform: translateY(-8px);
        border-color: #8A56E2;
    }
    .price-card.popular {
        border-color: #8A56E2;
        background: linear-gradient(180deg, rgba(138, 86, 226, 0.15) 0%, rgba(0, 201, 167, 0.05) 100%);
    }
    .price-card.popular::before {
        content: "MOST POPULAR";
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #8A56E2, #00C9A7);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 6px 20px;
        border-radius: 20px;
        letter-spacing: 1px;
    }
    .price-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 8px;
    }
    .price-amount {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #8A56E2, #00C9A7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .price-period {
        color: rgba(255, 255, 255, 0.5);
        font-size: 1rem;
        margin-bottom: 24px;
    }
    .price-features {
        margin: 24px 0;
    }
    .price-feature {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.95rem;
    }
    .price-feature .check {
        color: #00C9A7;
        font-weight: bold;
    }
    .faq-section {
        margin-top: 60px;
        padding: 40px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 24px;
    }
    .faq-item {
        padding: 20px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .faq-question {
        font-weight: 600;
        color: white;
        margin-bottom: 8px;
    }
    .faq-answer {
        color: rgba(255, 255, 255, 0.6);
        line-height: 1.6;
    }
    </style>

    <div class="pricing-hero">
        <h1>Simple, Transparent Pricing</h1>
        <p>Choose the plan that works best for your brain. Cancel anytime.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature comparison data
    lang = st.session_state.get("lang", "en")

    st.markdown('<div class="pricing-grid-full">', unsafe_allow_html=True)

    for plan_key, plan in SUBSCRIPTION_PLANS.items():
        popular_class = "popular" if plan_key == "plus" else ""
        features = plan.get(f"features_{lang}", plan["features"])
        name = plan.get(f"name_{lang}", plan["name"])

        price_display = f"${plan['price']}" if plan["price"] > 0 else "$0"
        period = "/month" if plan["price"] > 0 else "forever"

        features_html = "".join([
            f'<div class="price-feature"><span class="check">✓</span> {f}</div>'
            for f in features
        ])

        st.markdown(f"""
        <div class="price-card {popular_class}">
            <div class="price-name">{name}</div>
            <div class="price-amount">{price_display}</div>
            <div class="price-period">{period}</div>
            <div class="price-features">
                {features_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # CTA Buttons - Only Free and Plus ($4.99)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Stay Free", use_container_width=True, key="plan_free"):
            st.toast("You're on the Free plan!")

    with col2:
        if st.button("Get Plus - $4.99/mo", use_container_width=True, key="plan_plus", type="primary"):
            user_id = st.session_state.get("db_user_id")
            user_email = st.session_state.get("user", {}).get("email", "")
            if user_id and user_email:
                checkout_url = create_checkout_url(user_id, user_email, "plus")
                if checkout_url:
                    st.markdown(f'<meta http-equiv="refresh" content="0;url={checkout_url}">', unsafe_allow_html=True)
                else:
                    st.error("Payment system not configured. Please contact support.")
            else:
                st.warning("Please log in to upgrade.")

    # FAQ Section - Using native Streamlit expanders
    st.markdown("---")
    st.markdown("### Frequently Asked Questions")

    with st.expander("Can I cancel anytime?"):
        st.write("Yes! You can cancel your subscription at any time. You'll continue to have access until the end of your billing period.")

    with st.expander("What payment methods do you accept?"):
        st.write("We accept all major credit cards (Visa, Mastercard, American Express) through our secure payment processor, Stripe.")

    with st.expander("Is there a free trial?"):
        st.write("Our Free plan lets you try all the core features! When you're ready for unlimited access, upgrade to Plus for just $4.99/month.")

    with st.expander("What happens to my data if I downgrade?"):
        st.write("Your data is always safe. If you downgrade, you keep all your history and preferences. You'll just have daily limits on certain features.")

def check_subscription_limits(user_id: str, action: str, supabase_client) -> dict:
    """Check if user has reached their subscription limits"""
    # Get user's current plan
    try:
        profile = supabase_client.table("profiles").select("*").eq("id", user_id).single().execute()
        if profile.data:
            is_premium = profile.data.get("is_premium", False)
            plan = "plus" if is_premium else "free"
        else:
            plan = "free"
    except:
        plan = "free"

    plan_limits = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["free"])

    # Get today's usage
    try:
        from datetime import date
        today = date.today().isoformat()
        usage = supabase_client.table("daily_usage").select("*").eq("user_id", user_id).eq("date", today).single().execute()

        if usage.data:
            current_usage = usage.data
        else:
            current_usage = {
                "recommendations_count": 0,
                "mr_dp_chats_count": 0,
                "quick_dope_hits_count": 0
            }
    except:
        current_usage = {
            "recommendations_count": 0,
            "mr_dp_chats_count": 0,
            "quick_dope_hits_count": 0
        }

    # Check limits based on action
    if action == "mr_dp_chat":
        limit = plan_limits.get("mr_dp_limit", 5)
        current = current_usage.get("mr_dp_chats_count", 0)
        if limit == -1:  # Unlimited
            return {"allowed": True, "remaining": -1}
        return {
            "allowed": current < limit,
            "remaining": max(0, limit - current),
            "limit": limit,
            "current": current
        }

    elif action == "quick_hit":
        limit = plan_limits.get("quick_hits_limit", 3)
        current = current_usage.get("quick_dope_hits_count", 0)
        if limit == -1:
            return {"allowed": True, "remaining": -1}
        return {
            "allowed": current < limit,
            "remaining": max(0, limit - current),
            "limit": limit,
            "current": current
        }

    elif action == "recommendation":
        limit = plan_limits.get("recommendations_limit", 10)
        current = current_usage.get("recommendations_count", 0)
        if limit == -1:
            return {"allowed": True, "remaining": -1}
        return {
            "allowed": current < limit,
            "remaining": max(0, limit - current),
            "limit": limit,
            "current": current
        }

    return {"allowed": True}
