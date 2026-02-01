'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { motion } from 'framer-motion'
import {
  User,
  Crown,
  SignOut,
  Heart,
  Trophy,
  Fire,
  Star,
  Moon,
  Bell,
  Shield,
  Question,
  ChatCircle,
  CaretRight,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button, Card } from '@/components/ui'
import { PricingModal } from '@/components/features'
import { useAuth } from '@/lib/auth-context'
import type { UserStats, Achievement } from '@/types'

// Default stats for users without data
const defaultStats: UserStats = {
  totalPoints: 0,
  level: 1,
  streakDays: 0,
  achievementsUnlocked: 0,
  contentWatched: 0,
}

// Sample achievements (will be fetched from Supabase in production)
const sampleAchievements: Achievement[] = [
  { id: '1', name: 'First Pick', description: 'Made your first recommendation', icon: '🎯', unlockedAt: new Date() },
  { id: '2', name: 'Streak Starter', description: '3 day streak', icon: '🔥', unlockedAt: new Date() },
  { id: '3', name: 'Mood Master', description: 'Tried all mood categories', icon: '🌈', unlockedAt: new Date() },
  { id: '4', name: 'Quick Draw', description: 'Used Quick Hit 5 times', icon: '⚡', unlockedAt: new Date() },
]

const settingsItems = [
  { id: 'notifications', label: 'Notifications', icon: Bell, value: 'On' },
  { id: 'theme', label: 'Dark Mode', icon: Moon, value: 'Auto' },
  { id: 'privacy', label: 'Privacy', icon: Shield },
  { id: 'help', label: 'Help & Support', icon: Question },
  { id: 'feedback', label: 'Send Feedback', icon: ChatCircle },
]

export default function ProfilePage() {
  const router = useRouter()
  const { user, isPremium, signOut, isLoading } = useAuth()
  const [stats] = useState(defaultStats)
  const [achievements] = useState(sampleAchievements)
  const [showPricingModal, setShowPricingModal] = useState(false)
  const [isSigningOut, setIsSigningOut] = useState(false)

  const levelProgress = (stats.totalPoints % 500) / 500 * 100

  const handleSignOut = async () => {
    setIsSigningOut(true)
    haptic('medium')
    try {
      await signOut()
      router.push('/')
    } catch (error) {
      console.error('Sign out error:', error)
    } finally {
      setIsSigningOut(false)
    }
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-400 animate-pulse" />
      </div>
    )
  }

  // If not logged in, show login prompt
  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-4">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-400 flex items-center justify-center mb-6">
          <User size={40} className="text-white" />
        </div>
        <h1 className="text-2xl font-bold text-surface-900 dark:text-white mb-2">
          Sign in to view your profile
        </h1>
        <p className="text-surface-500 dark:text-surface-400 mb-6 text-center">
          Track your progress, achievements, and customize your experience
        </p>
        <Button onClick={() => router.push('/login')}>
          Sign In
        </Button>
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-8">
      {/* Header with gradient background */}
      <div className="relative h-32 bg-gradient-to-r from-primary-500 via-secondary-400 to-accent-400">
        <div className="absolute inset-0 opacity-20">
          <div
            className="h-full w-full"
            style={{
              backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '24px 24px',
            }}
          />
        </div>
      </div>

      {/* Profile info */}
      <div className="px-4 md:px-8 -mt-16 relative z-10">
        <div className="flex flex-col md:flex-row md:items-end gap-4">
          {/* Avatar */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="relative"
          >
            <div className="w-24 h-24 md:w-32 md:h-32 rounded-2xl bg-white dark:bg-dark-card shadow-xl flex items-center justify-center border-4 border-white dark:border-dark-bg overflow-hidden">
              {user.avatarUrl ? (
                <Image
                  src={user.avatarUrl}
                  alt={user.name || 'User avatar'}
                  width={128}
                  height={128}
                  className="w-full h-full object-cover"
                />
              ) : (
                <User size={48} className="text-surface-400" />
              )}
            </div>
            {isPremium && (
              <div className="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-gradient-to-r from-amber-400 to-orange-500 flex items-center justify-center shadow-lg">
                <Crown size={16} weight="fill" className="text-white" />
              </div>
            )}
          </motion.div>

          {/* Name and email */}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
              {user.name || 'User'}
            </h1>
            <p className="text-surface-500 dark:text-surface-400">{user.email}</p>
          </div>

          {/* Premium CTA */}
          {!isPremium && (
            <Button
              icon={<Crown size={18} weight="fill" />}
              className="bg-gradient-to-r from-amber-500 to-orange-500 border-none"
              onClick={() => setShowPricingModal(true)}
            >
              Go Premium
            </Button>
          )}
        </div>
      </div>

      {/* Stats cards */}
      <div className="px-4 md:px-8 mt-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            icon={<Star size={24} weight="fill" className="text-amber-500" />}
            value={stats.totalPoints.toLocaleString()}
            label="Total Points"
          />
          <StatCard
            icon={<Fire size={24} weight="fill" className="text-orange-500" />}
            value={stats.streakDays}
            label="Day Streak"
          />
          <StatCard
            icon={<Trophy size={24} weight="fill" className="text-primary-500" />}
            value={stats.achievementsUnlocked}
            label="Achievements"
          />
          <StatCard
            icon={<Heart size={24} weight="fill" className="text-red-500" />}
            value={stats.contentWatched}
            label="Watched"
          />
        </div>
      </div>

      {/* Level progress */}
      <div className="px-4 md:px-8 mt-8">
        <Card className="p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-surface-900 dark:text-white">
                Level {stats.level}
              </span>
            </div>
            <span className="text-sm text-surface-500">
              {stats.totalPoints % 500} / 500 XP
            </span>
          </div>
          <div className="h-3 bg-surface-100 dark:bg-dark-hover rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${levelProgress}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-primary-500 to-secondary-400 rounded-full"
            />
          </div>
        </Card>
      </div>

      {/* Achievements */}
      <div className="px-4 md:px-8 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-surface-900 dark:text-white">
            Achievements
          </h2>
          <button className="text-primary-500 text-sm font-medium">
            View All
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {achievements.map((achievement, index) => (
            <motion.div
              key={achievement.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-4 text-center">
                <div className="text-3xl mb-2">{achievement.icon}</div>
                <h3 className="font-semibold text-surface-900 dark:text-white text-sm">
                  {achievement.name}
                </h3>
                <p className="text-xs text-surface-500 mt-1">
                  {achievement.description}
                </p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Settings */}
      <div className="px-4 md:px-8 mt-8">
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
          Settings
        </h2>

        <Card className="divide-y divide-surface-100 dark:divide-dark-border overflow-hidden p-0">
          {settingsItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                onClick={() => haptic('light')}
                className={cn(
                  'w-full flex items-center justify-between p-4',
                  'hover:bg-surface-50 dark:hover:bg-dark-hover',
                  'transition-colors'
                )}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-surface-100 dark:bg-dark-hover flex items-center justify-center">
                    <Icon size={20} className="text-surface-600 dark:text-surface-300" />
                  </div>
                  <span className="font-medium text-surface-900 dark:text-white">
                    {item.label}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-surface-400">
                  {item.value && <span className="text-sm">{item.value}</span>}
                  <CaretRight size={18} />
                </div>
              </button>
            )
          })}
        </Card>
      </div>

      {/* Sign out */}
      <div className="px-4 md:px-8 mt-8">
        <Button
          variant="ghost"
          className="w-full text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10"
          icon={<SignOut size={20} />}
          onClick={handleSignOut}
          loading={isSigningOut}
        >
          Sign Out
        </Button>
      </div>

      {/* Pricing Modal */}
      <PricingModal
        isOpen={showPricingModal}
        onClose={() => setShowPricingModal(false)}
      />
    </div>
  )
}

// Stat Card Component
interface StatCardProps {
  icon: React.ReactNode
  value: string | number
  label: string
}

function StatCard({ icon, value, label }: StatCardProps) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-surface-50 dark:bg-dark-hover flex items-center justify-center">
          {icon}
        </div>
        <div>
          <div className="text-xl font-bold text-surface-900 dark:text-white">
            {value}
          </div>
          <div className="text-xs text-surface-500">{label}</div>
        </div>
      </div>
    </Card>
  )
}
