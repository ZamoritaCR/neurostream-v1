'use client'

import { motion } from 'framer-motion'
import {
  Crown,
  Check,
  Sparkle,
  X,
  Lightning,
  ChatCircle,
  Star,
  RocketLaunch,
} from '@phosphor-icons/react'
import { Button, Modal } from '@/components/ui'
import { useAuth } from '@/lib/auth-context'
import { getCheckoutUrl, isStripeConfigured, PREMIUM_PRICING } from '@/lib/stripe'
import { cn } from '@/lib/utils'

interface PricingModalProps {
  isOpen: boolean
  onClose: () => void
}

export function PricingModal({ isOpen, onClose }: PricingModalProps) {
  const { user } = useAuth()

  const handleUpgrade = () => {
    if (!user) {
      // Redirect to login if not authenticated
      window.location.href = '/login?redirect=premium'
      return
    }

    const checkoutUrl = getCheckoutUrl(user.id)
    if (checkoutUrl !== '#') {
      window.open(checkoutUrl, '_blank')
    } else {
      alert('Payment system is being configured. Please try again later.')
    }
    onClose()
  }

  const features = PREMIUM_PRICING.monthly.features

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="p-6 max-w-md mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg"
          >
            <Crown size={32} weight="fill" className="text-white" />
          </motion.div>
          <h2 className="text-2xl font-bold text-surface-900 dark:text-white mb-2">
            Upgrade to Premium
          </h2>
          <p className="text-surface-500 dark:text-surface-400">
            Unlock unlimited dopamine with Mr.DP
          </p>
        </div>

        {/* Pricing */}
        <div className="bg-gradient-to-br from-primary-500/5 to-secondary-400/5 rounded-2xl p-6 mb-6 border border-primary-200 dark:border-primary-500/20">
          <div className="flex items-baseline justify-center gap-1 mb-4">
            <span className="text-4xl font-bold text-surface-900 dark:text-white">
              ${PREMIUM_PRICING.monthly.price}
            </span>
            <span className="text-surface-500">/month</span>
          </div>

          {/* Features */}
          <ul className="space-y-3">
            {features.map((feature, index) => (
              <motion.li
                key={feature}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-3"
              >
                <div className="w-5 h-5 rounded-full bg-green-100 dark:bg-green-500/20 flex items-center justify-center flex-shrink-0">
                  <Check size={12} weight="bold" className="text-green-600 dark:text-green-400" />
                </div>
                <span className="text-surface-700 dark:text-surface-200">
                  {feature}
                </span>
              </motion.li>
            ))}
          </ul>
        </div>

        {/* CTA */}
        <Button
          onClick={handleUpgrade}
          className="w-full bg-gradient-to-r from-amber-500 to-orange-500 border-none text-white font-semibold"
          size="lg"
          icon={<RocketLaunch size={20} weight="fill" />}
        >
          Start Premium
        </Button>

        {/* Note */}
        <p className="text-center text-xs text-surface-400 mt-4">
          Cancel anytime. No commitments.
        </p>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-surface-100 dark:hover:bg-dark-hover transition-colors"
        >
          <X size={20} className="text-surface-500" />
        </button>
      </div>
    </Modal>
  )
}

// Compact Premium Banner for inline use
export function PremiumBanner({ onUpgrade }: { onUpgrade: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'p-4 rounded-2xl',
        'bg-gradient-to-r from-amber-500/10 to-orange-500/10',
        'border border-amber-200 dark:border-amber-500/20'
      )}
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center flex-shrink-0">
          <Crown size={20} weight="fill" className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-surface-900 dark:text-white text-sm">
            Go Premium
          </h4>
          <p className="text-xs text-surface-500">
            Unlimited Mr.DP chats for $4.99/mo
          </p>
        </div>
        <Button
          size="sm"
          onClick={onUpgrade}
          className="bg-gradient-to-r from-amber-500 to-orange-500 border-none"
        >
          Upgrade
        </Button>
      </div>
    </motion.div>
  )
}

export default PricingModal
