"""
Stripe utilities for Dopamine.watch
NEW FILE - doesn't replace anything
"""
import os


def get_stripe():
    """Get configured Stripe client"""
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    return stripe


def create_checkout_url(user_id: str, user_email: str) -> str:
    """Create Stripe checkout session and return URL"""
    stripe = get_stripe()

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': os.getenv('STRIPE_PRICE_ID'),  # Your $4.99/mo price
            'quantity': 1,
        }],
        mode='subscription',
        success_url=os.getenv('APP_URL', 'https://app.dopamine.watch') + '?upgraded=true',
        cancel_url=os.getenv('APP_URL', 'https://app.dopamine.watch') + '?canceled=true',
        customer_email=user_email,
        metadata={'user_id': user_id}
    )

    return session.url


def handle_successful_upgrade(supabase_client, user_id: str, stripe_customer_id: str = None):
    """Update subscription status after successful payment"""
    from datetime import datetime, timedelta

    supabase_client.table('subscriptions').upsert({
        'user_id': user_id,
        'stripe_customer_id': stripe_customer_id,
        'plan_type': 'premium',
        'status': 'active',
        'current_period_end': (datetime.now() + timedelta(days=30)).isoformat(),
        'updated_at': datetime.now().isoformat()
    }, on_conflict='user_id').execute()
