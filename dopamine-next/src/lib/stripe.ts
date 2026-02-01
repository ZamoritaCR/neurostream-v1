// Stripe configuration for dopamine.watch Premium
// $4.99/month for unlimited Mr.DP chats

const PAYMENT_LINK = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK || ''
const CUSTOMER_PORTAL = process.env.NEXT_PUBLIC_STRIPE_CUSTOMER_PORTAL || ''

/**
 * Get Stripe checkout URL with user ID for tracking
 */
export function getCheckoutUrl(userId: string): string {
  if (!PAYMENT_LINK) {
    console.warn('Stripe payment link not configured')
    return '#'
  }

  const url = new URL(PAYMENT_LINK)
  url.searchParams.set('client_reference_id', userId)

  // Add success URL to redirect back to app
  if (typeof window !== 'undefined') {
    url.searchParams.set('success_url', `${window.location.origin}?upgraded=true`)
    url.searchParams.set('cancel_url', window.location.origin)
  }

  return url.toString()
}

/**
 * Get Stripe customer portal URL for subscription management
 */
export function getCustomerPortalUrl(customerId?: string): string {
  if (!CUSTOMER_PORTAL) {
    console.warn('Stripe customer portal not configured')
    return '#'
  }

  if (customerId) {
    return `${CUSTOMER_PORTAL}?prefilled_email=${customerId}`
  }

  return CUSTOMER_PORTAL
}

/**
 * Check if Stripe is configured
 */
export function isStripeConfigured(): boolean {
  return Boolean(PAYMENT_LINK && CUSTOMER_PORTAL)
}

/**
 * Premium pricing details
 */
export const PREMIUM_PRICING = {
  monthly: {
    price: 4.99,
    currency: 'USD',
    interval: 'month',
    features: [
      'Unlimited Mr.DP chats',
      'Priority recommendations',
      'Ad-free experience',
      'Early access to new features',
    ],
  },
} as const
