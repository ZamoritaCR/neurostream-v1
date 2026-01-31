// Stripe Webhook Handler for dopamine.watch
// Handles checkout.session.completed and subscription cancellation events

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import Stripe from 'https://esm.sh/stripe@11.1.0?target=deno'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') || '', {
  apiVersion: '2023-10-16',
})

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey)

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, stripe-signature',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const signature = req.headers.get('stripe-signature')
  const body = await req.text()
  const webhookSecret = Deno.env.get('STRIPE_WEBHOOK_SECRET')

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature!,
      webhookSecret!
    )
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message)
    return new Response(
      JSON.stringify({ error: `Webhook Error: ${err.message}` }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  console.log(`Received event: ${event.type}`)

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        const userId = session.client_reference_id
        const customerEmail = session.customer_email || session.customer_details?.email

        console.log(`Checkout completed for user: ${userId}, email: ${customerEmail}`)

        if (userId) {
          // Update user to premium by ID
          const { error } = await supabaseAdmin
            .from('profiles')
            .update({
              is_premium: true,
              stripe_customer_id: session.customer as string,
              subscription_id: session.subscription as string,
              premium_since: new Date().toISOString()
            })
            .eq('id', userId)

          if (error) {
            console.error('Error updating user by ID:', error)
          } else {
            console.log(`User ${userId} upgraded to premium`)
          }
        } else if (customerEmail) {
          // Fallback: Update by email
          const { error } = await supabaseAdmin
            .from('profiles')
            .update({
              is_premium: true,
              stripe_customer_id: session.customer as string,
              subscription_id: session.subscription as string,
              premium_since: new Date().toISOString()
            })
            .eq('email', customerEmail)

          if (error) {
            console.error('Error updating user by email:', error)
          } else {
            console.log(`User ${customerEmail} upgraded to premium`)
          }
        }
        break
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription
        const status = subscription.status

        console.log(`Subscription updated: ${subscription.id}, status: ${status}`)

        // Handle subscription status changes
        if (status === 'active' || status === 'trialing') {
          await supabaseAdmin
            .from('profiles')
            .update({ is_premium: true })
            .eq('subscription_id', subscription.id)
        } else if (status === 'canceled' || status === 'unpaid' || status === 'past_due') {
          await supabaseAdmin
            .from('profiles')
            .update({ is_premium: false })
            .eq('subscription_id', subscription.id)
        }
        break
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription

        console.log(`Subscription deleted: ${subscription.id}`)

        // Remove premium status
        const { error } = await supabaseAdmin
          .from('profiles')
          .update({
            is_premium: false,
            subscription_id: null
          })
          .eq('subscription_id', subscription.id)

        if (error) {
          console.error('Error removing premium status:', error)
        } else {
          console.log(`Premium status removed for subscription ${subscription.id}`)
        }
        break
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice
        const customerId = invoice.customer as string

        console.log(`Payment failed for customer: ${customerId}`)

        // Optionally notify user or mark account as past due
        // For now, we'll let subscription.updated handle the status change
        break
      }

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return new Response(
      JSON.stringify({ received: true }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (err) {
    console.error('Error processing webhook:', err)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
