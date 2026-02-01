import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Create Supabase admin client lazily to avoid build-time errors
function getSupabaseAdmin() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  if (!url || !key) {
    throw new Error('Supabase credentials not configured')
  }

  return createClient(url, key)
}

interface StripeEvent {
  id: string
  type: string
  data: {
    object: {
      id: string
      client_reference_id?: string
      customer?: string
      subscription?: string
      status?: string
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.text()
    const signature = request.headers.get('stripe-signature')

    // In production, verify the webhook signature
    // For now, we'll parse the event directly
    // TODO: Add proper Stripe signature verification when deploying
    let event: StripeEvent

    try {
      event = JSON.parse(body)
    } catch {
      return NextResponse.json({ error: 'Invalid payload' }, { status: 400 })
    }

    // Log the event for debugging
    console.log('Stripe webhook event:', event.type)

    switch (event.type) {
      case 'checkout.session.completed': {
        // User completed checkout
        const session = event.data.object
        const userId = session.client_reference_id

        if (userId) {
          // Update user to premium
          const { error } = await getSupabaseAdmin()
            .from('profiles')
            .update({
              is_premium: true,
              premium_since: new Date().toISOString(),
              stripe_customer_id: session.customer,
              subscription_id: session.subscription,
            })
            .eq('id', userId)

          if (error) {
            console.error('Failed to update premium status:', error)
          } else {
            console.log(`User ${userId} upgraded to premium`)
          }
        }
        break
      }

      case 'customer.subscription.updated': {
        // Subscription status changed
        const subscription = event.data.object
        const status = subscription.status

        // Find user by subscription ID
        const { data: profile } = await getSupabaseAdmin()
          .from('profiles')
          .select('id')
          .eq('subscription_id', subscription.id)
          .single()

        if (profile) {
          const isPremium = status === 'active' || status === 'trialing'

          await getSupabaseAdmin()
            .from('profiles')
            .update({ is_premium: isPremium })
            .eq('id', profile.id)

          console.log(`User ${profile.id} subscription status: ${status}`)
        }
        break
      }

      case 'customer.subscription.deleted': {
        // Subscription cancelled
        const subscription = event.data.object

        // Find and update user
        const { data: profile } = await getSupabaseAdmin()
          .from('profiles')
          .select('id')
          .eq('subscription_id', subscription.id)
          .single()

        if (profile) {
          await getSupabaseAdmin()
            .from('profiles')
            .update({
              is_premium: false,
              subscription_id: null,
            })
            .eq('id', profile.id)

          console.log(`User ${profile.id} subscription cancelled`)
        }
        break
      }

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return NextResponse.json({ received: true })
  } catch (error) {
    console.error('Webhook error:', error)
    return NextResponse.json(
      { error: 'Webhook handler failed' },
      { status: 500 }
    )
  }
}
