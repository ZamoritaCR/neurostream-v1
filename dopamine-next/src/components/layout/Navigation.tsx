'use client'

import { useState } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  House,
  Compass,
  Sparkle,
  ChatCircle,
  User,
  MagnifyingGlass,
  Bell,
  Crown,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { PricingModal } from '@/components/features'
import { useAuth } from '@/lib/auth-context'

// Navigation items - these are relative to the (app) route group
const navItems = [
  { href: '/home', label: 'Home', icon: House },
  { href: '/discover', label: 'Discover', icon: Compass },
  { href: '/quick-hit', label: 'Quick Hit', icon: Sparkle, isSpecial: true },
  { href: '/chat', label: 'Mr.DP', icon: ChatCircle },
  { href: '/profile', label: 'Profile', icon: User },
]

// Mobile Bottom Navigation
export function MobileNavigation() {
  const pathname = usePathname()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 md:hidden">
      {/* Blur backdrop */}
      <div className="absolute inset-0 bg-white/80 dark:bg-dark-bg/80 backdrop-blur-xl border-t border-surface-100 dark:border-dark-border" />

      {/* Nav content */}
      <div className="relative flex items-center justify-around px-2 pb-safe pt-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon

          if (item.isSpecial) {
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => haptic('medium')}
                className="relative -mt-6"
              >
                <motion.div
                  className={cn(
                    'w-14 h-14 rounded-full flex items-center justify-center',
                    'bg-gradient-to-r from-primary-500 to-secondary-400',
                    'shadow-glow'
                  )}
                  whileTap={{ scale: 0.95 }}
                >
                  <Icon size={28} weight="fill" className="text-white" />
                </motion.div>
              </Link>
            )
          }

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => haptic('light')}
              className={cn(
                'flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-xl',
                'transition-colors duration-200',
                'min-w-[64px] min-h-[44px]',
                isActive
                  ? 'text-primary-500 dark:text-primary-400'
                  : 'text-surface-500 dark:text-surface-400'
              )}
            >
              <motion.div
                animate={isActive ? { scale: 1.1 } : { scale: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 17 }}
              >
                <Icon size={24} weight={isActive ? 'fill' : 'regular'} />
              </motion.div>
              <span className="text-xs font-medium">{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="nav-indicator"
                  className="absolute -bottom-1 w-1 h-1 rounded-full bg-primary-500"
                />
              )}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}

// Desktop Header Navigation
export function DesktopNavigation() {
  const pathname = usePathname()
  const { isPremium } = useAuth()
  const [showPricing, setShowPricing] = useState(false)

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-40 hidden md:block">
        {/* Blur backdrop */}
        <div className="absolute inset-0 bg-white/80 dark:bg-dark-bg/80 backdrop-blur-xl border-b border-surface-100 dark:border-dark-border" />

        {/* Nav content */}
        <div className="relative max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-400 flex items-center justify-center">
              <Sparkle size={24} weight="fill" className="text-white" />
            </div>
            <span className="text-xl font-bold">
              dopamine<span className="gradient-text">.watch</span>
            </span>
          </Link>

          {/* Center nav */}
          <nav className="flex items-center gap-1">
            {navItems.slice(0, 4).map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex items-center gap-2 px-4 py-2 rounded-full',
                    'transition-all duration-200',
                    'font-medium',
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-400'
                      : 'text-surface-600 dark:text-surface-300 hover:bg-surface-100 dark:hover:bg-dark-hover'
                  )}
                >
                  <Icon size={20} weight={isActive ? 'fill' : 'regular'} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* Right section */}
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-full hover:bg-surface-100 dark:hover:bg-dark-hover transition-colors">
              <MagnifyingGlass size={20} className="text-surface-600 dark:text-surface-300" />
            </button>
            <button className="p-2 rounded-full hover:bg-surface-100 dark:hover:bg-dark-hover transition-colors relative">
              <Bell size={20} className="text-surface-600 dark:text-surface-300" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            {isPremium ? (
              <div className="ml-2 flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-amber-400 to-orange-500 text-white font-semibold">
                <Crown size={18} weight="fill" />
                <span>Premium</span>
              </div>
            ) : (
              <button
                onClick={() => {
                  haptic('medium')
                  setShowPricing(true)
                }}
                className="ml-2 flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary-500 to-secondary-400 text-white font-semibold shadow-glow-sm hover:shadow-glow transition-shadow"
              >
                <Crown size={18} weight="fill" />
                <span>Go Pro</span>
              </button>
            )}
            <Link
              href="/profile"
              className="ml-2 w-10 h-10 rounded-full bg-surface-200 dark:bg-dark-border flex items-center justify-center"
            >
              <User size={20} className="text-surface-600 dark:text-surface-300" />
            </Link>
          </div>
        </div>
      </header>

      {/* Pricing Modal */}
      <PricingModal isOpen={showPricing} onClose={() => setShowPricing(false)} />
    </>
  )
}

// Combined Navigation component
export function Navigation() {
  return (
    <>
      <DesktopNavigation />
      <MobileNavigation />
    </>
  )
}

// Page wrapper that adds proper spacing for nav
export function PageWrapper({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <main
      className={cn(
        // Desktop: top padding for header
        'md:pt-20',
        // Mobile: bottom padding for nav
        'pb-24 md:pb-8',
        // Safe areas
        'pt-safe px-safe',
        className
      )}
    >
      {children}
    </main>
  )
}
