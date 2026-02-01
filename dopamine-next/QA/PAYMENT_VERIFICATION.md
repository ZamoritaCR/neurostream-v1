# Payment Integration Verification - dopamine.watch

**Date:** January 31, 2026
**Status:** NOT IMPLEMENTED

---

## Executive Summary

The Next.js rebuild does **not** currently have Stripe payment integration. The original Streamlit app has a working Stripe implementation that needs to be ported.

---

## Current State

### What Exists

1. **Premium CTAs in UI**
   - Home page: None
   - Profile page: "Go Premium" button (line 119-126)
   - Chat page: "Upgrade" button in header
   - MrDpFloating: "Upgrade" link in usage indicator

2. **Premium State Tracking**
   - `useAuth()` hook provides `isPremium` boolean
   - `mrDpUsesRemaining` tracks free tier usage
   - Profile type includes `isPremium`, `premiumSince`

3. **Supabase Functions**
   ```typescript
   // src/lib/supabase.ts
   checkPremiumStatus(userId) // Returns isPremium, premiumSince
   getMrDpUsage(userId)       // Returns usesRemaining
   ```

### What's Missing

1. **Environment Variables**
   - `STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_SECRET_KEY`
   - `STRIPE_PAYMENT_LINK_MONTHLY`
   - `STRIPE_CUSTOMER_PORTAL`
   - `STRIPE_WEBHOOK_SECRET`

2. **Stripe Integration Files**
   - No `src/lib/stripe.ts` utility
   - No checkout flow
   - No webhook handler

3. **API Routes**
   - No `/api/stripe/checkout` route
   - No `/api/stripe/webhook` route
   - No `/api/stripe/portal` route

4. **UI Components**
   - No pricing modal
   - No subscription management
   - No payment success/failure pages

---

## Original Streamlit Implementation

The existing Streamlit app has these Stripe components:

### From `stripe_utils.py`
```python
def get_pricing_page(user_id: str) -> str:
    """Generate Stripe payment link with user ID"""
    return f"{STRIPE_PAYMENT_LINK}?client_reference_id={user_id}"

def get_customer_portal(customer_id: str) -> str:
    """Generate Stripe customer portal link"""
    return f"{STRIPE_CUSTOMER_PORTAL}/sessions/portal?customer={customer_id}"
```

### From Supabase Edge Function
```typescript
// supabase/functions/stripe-webhook/index.ts
// Handles:
// - checkout.session.completed
// - customer.subscription.updated
// - customer.subscription.deleted
```

---

## Required Implementation

### 1. Environment Variables

Add to `.env.local`:
```env
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PAYMENT_LINK_MONTHLY=https://buy.stripe.com/xxx
STRIPE_CUSTOMER_PORTAL=https://billing.stripe.com/xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### 2. Stripe Utility (`src/lib/stripe.ts`)

```typescript
export function getCheckoutUrl(userId: string): string {
  const baseUrl = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK
  return `${baseUrl}?client_reference_id=${userId}&success_url=${window.location.origin}?upgraded=true`
}

export function getCustomerPortalUrl(customerId: string): string {
  return `${process.env.NEXT_PUBLIC_STRIPE_CUSTOMER_PORTAL}?customer=${customerId}`
}
```

### 3. API Routes

#### `/app/api/stripe/webhook/route.ts`
```typescript
import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'
import { createClient } from '@supabase/supabase-js'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(request: NextRequest) {
  const body = await request.text()
  const sig = request.headers.get('stripe-signature')!

  const event = stripe.webhooks.constructEvent(
    body,
    sig,
    process.env.STRIPE_WEBHOOK_SECRET!
  )

  switch (event.type) {
    case 'checkout.session.completed':
      // Set user as premium
      break
    case 'customer.subscription.updated':
      // Update subscription status
      break
    case 'customer.subscription.deleted':
      // Remove premium status
      break
  }

  return NextResponse.json({ received: true })
}
```

### 4. Pricing Modal Component

```typescript
// src/components/features/PricingModal.tsx
export function PricingModal({ isOpen, onClose }) {
  const { user } = useAuth()

  const handleUpgrade = () => {
    const checkoutUrl = getCheckoutUrl(user.id)
    window.open(checkoutUrl, '_blank')
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <h2>Upgrade to Premium</h2>
      <p>$4.99/month - Unlimited Mr.DP chats</p>
      <Button onClick={handleUpgrade}>Subscribe Now</Button>
    </Modal>
  )
}
```

### 5. Connect Premium CTAs

Update all "Go Premium" / "Upgrade" buttons to open checkout:

```typescript
// Example in profile/page.tsx
const [showPricing, setShowPricing] = useState(false)

<Button onClick={() => setShowPricing(true)}>
  Go Premium
</Button>

<PricingModal
  isOpen={showPricing}
  onClose={() => setShowPricing(false)}
/>
```

---

## Testing Checklist

Before launch, verify:

- [ ] Stripe publishable key is set
- [ ] Stripe secret key is set
- [ ] Webhook secret is configured
- [ ] Test checkout flow with test card (4242 4242 4242 4242)
- [ ] Verify webhook receives events
- [ ] Confirm `is_premium` updates in Supabase
- [ ] Test subscription cancellation
- [ ] Test customer portal access
- [ ] Verify Mr.DP unlimited usage for premium users

---

## Security Considerations

1. **Never expose secret key client-side**
   - Use `STRIPE_SECRET_KEY` (no NEXT_PUBLIC_ prefix)
   - Only access in API routes

2. **Validate webhook signatures**
   - Always verify `stripe-signature` header
   - Reject requests without valid signature

3. **Secure user ID passing**
   - Use `client_reference_id` in Stripe checkout
   - Verify user exists before updating premium status

---

## Pricing Structure

| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 5 Mr.DP chats/day |
| Premium | $4.99/mo | Unlimited chats, priority support |

---

## Status: Action Required

This needs to be implemented before the Next.js version can replace the Streamlit app in production.

**Priority:** Critical
**Estimated Effort:** 2-4 hours
**Dependencies:** Stripe account access, webhook endpoint deployed
