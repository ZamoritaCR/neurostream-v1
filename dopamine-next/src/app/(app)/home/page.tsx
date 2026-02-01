'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import Image from 'next/image'
import {
  Lightning,
  Compass,
  Brain,
  Fire,
  Clock,
  Heart,
  Play,
  Star,
  ArrowRight,
  Sparkle,
  Sun,
  Moon,
  CloudSun,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button, Card, SkeletonContentCard } from '@/components/ui'
import { getTrending } from '@/lib/tmdb'
import type { Content } from '@/types'

// Get time-based greeting
function getGreeting(): { text: string; icon: typeof Sun } {
  const hour = new Date().getHours()
  if (hour < 12) return { text: 'Good morning', icon: Sun }
  if (hour < 17) return { text: 'Good afternoon', icon: CloudSun }
  return { text: 'Good evening', icon: Moon }
}

// Continue watching placeholder - will be replaced with user data from Supabase
const continueWatchingPlaceholder: Content[] = []

export default function AppHomePage() {
  const greeting = getGreeting()
  const GreetingIcon = greeting.icon
  const [streakDays] = useState(7)
  const [forYou, setForYou] = useState<Content[]>([])
  const [continueWatching] = useState<Content[]>(continueWatchingPlaceholder)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchContent() {
      try {
        const trending = await getTrending('all', 'week')
        // Get first 6 items for the "For You" section
        setForYou(trending.slice(0, 6))
      } catch (err) {
        console.error('Failed to fetch trending content:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchContent()
  }, [])

  return (
    <div className="min-h-screen pb-8">
      {/* Header */}
      <div className="px-4 md:px-8 pt-4 pb-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between"
        >
          <div>
            <div className="flex items-center gap-2 text-surface-500 dark:text-surface-400 text-sm mb-1">
              <GreetingIcon size={18} weight="fill" className="text-amber-500" />
              <span>{greeting.text}</span>
            </div>
            <h1 className="text-2xl font-bold text-surface-900 dark:text-white">
              What's your vibe today?
            </h1>
          </div>

          {/* Streak badge */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.2 }}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-orange-50 dark:bg-orange-500/10"
          >
            <Fire size={20} weight="fill" className="text-orange-500" />
            <span className="font-bold text-orange-600 dark:text-orange-400">
              {streakDays} day streak!
            </span>
          </motion.div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div className="px-4 md:px-8 mb-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickAction
            href="/quick-hit"
            icon={<Lightning size={28} weight="fill" />}
            label="Quick Hit"
            description="Instant pick"
            gradient="from-primary-500 to-secondary-400"
            delay={0}
          />
          <QuickAction
            href="/discover"
            icon={<Compass size={28} weight="fill" />}
            label="Discover"
            description="By mood"
            gradient="from-violet-500 to-purple-500"
            delay={0.1}
          />
          <QuickAction
            href="/chat"
            icon={<Brain size={28} weight="fill" />}
            label="Ask Mr.DP"
            description="AI chat"
            gradient="from-pink-500 to-rose-500"
            delay={0.2}
          />
          <QuickAction
            href="/profile"
            icon={<Heart size={28} weight="fill" />}
            label="Saved"
            description="Your queue"
            gradient="from-red-500 to-orange-500"
            delay={0.3}
          />
        </div>
      </div>

      {/* Continue Watching */}
      {continueWatching.length > 0 && (
        <section className="mb-8">
          <div className="px-4 md:px-8 flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock size={20} className="text-surface-500" />
              <h2 className="text-lg font-semibold text-surface-900 dark:text-white">
                Continue Watching
              </h2>
            </div>
            <button className="text-primary-500 text-sm font-medium">
              See all
            </button>
          </div>

          <div className="px-4 md:px-8">
            <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 md:mx-0 md:px-0">
              {continueWatching.map((content, index) => (
                <ContinueWatchingCard key={content.id} content={content} index={index} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* For You */}
      <section className="mb-8">
        <div className="px-4 md:px-8 flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkle size={20} weight="fill" className="text-primary-500" />
            <h2 className="text-lg font-semibold text-surface-900 dark:text-white">
              For You
            </h2>
          </div>
          <Link href="/discover" className="text-primary-500 text-sm font-medium">
            See all
          </Link>
        </div>

        <div className="px-4 md:px-8">
          <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-6 gap-4">
            {isLoading ? (
              // Loading skeletons
              Array.from({ length: 6 }).map((_, i) => (
                <SkeletonContentCard key={i} />
              ))
            ) : (
              forYou.map((content, index) => (
                <ContentThumbnail key={content.id} content={content} index={index} />
              ))
            )}
          </div>
        </div>
      </section>

      {/* Mr.DP Prompt */}
      <section className="px-4 md:px-8 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="p-0 overflow-hidden">
            <div className="flex items-center gap-4 p-4 md:p-6 bg-gradient-to-r from-primary-500/5 to-secondary-400/5">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-400 flex items-center justify-center shadow-glow-sm flex-shrink-0">
                <Brain size={28} weight="fill" className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-surface-900 dark:text-white mb-1">
                  Need help deciding?
                </h3>
                <p className="text-sm text-surface-500 dark:text-surface-400">
                  Chat with Mr.DP for personalized recommendations
                </p>
              </div>
              <Link href="/chat">
                <Button
                  size="sm"
                  icon={<ArrowRight size={16} weight="bold" />}
                  iconPosition="right"
                >
                  Chat
                </Button>
              </Link>
            </div>
          </Card>
        </motion.div>
      </section>

      {/* Mood-based suggestions */}
      <section className="px-4 md:px-8">
        <h2 className="text-lg font-semibold text-surface-900 dark:text-white mb-4">
          Based on your mood
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MoodCategory
            label="Need to Relax"
            gradient="from-teal-400 to-cyan-500"
            count={12}
          />
          <MoodCategory
            label="Feel Good"
            gradient="from-amber-400 to-orange-500"
            count={18}
          />
          <MoodCategory
            label="Get Energized"
            gradient="from-violet-500 to-purple-600"
            count={15}
          />
          <MoodCategory
            label="Deep Focus"
            gradient="from-blue-500 to-indigo-600"
            count={9}
          />
        </div>
      </section>
    </div>
  )
}

// Quick Action Button
interface QuickActionProps {
  href: string
  icon: React.ReactNode
  label: string
  description: string
  gradient: string
  delay: number
}

function QuickAction({ href, icon, label, description, gradient, delay }: QuickActionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
    >
      <Link href={href}>
        <Card
          interactive
          className="p-4 h-full"
        >
          <div
            className={cn(
              'w-12 h-12 rounded-xl flex items-center justify-center mb-3',
              'bg-gradient-to-br',
              gradient,
              'text-white shadow-lg'
            )}
          >
            {icon}
          </div>
          <h3 className="font-semibold text-surface-900 dark:text-white">
            {label}
          </h3>
          <p className="text-xs text-surface-500">{description}</p>
        </Card>
      </Link>
    </motion.div>
  )
}

// Continue Watching Card
interface ContinueWatchingCardProps {
  content: Content
  index: number
}

function ContinueWatchingCard({ content, index }: ContinueWatchingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="flex-shrink-0 w-72 md:w-80"
    >
      <Card interactive className="p-0 overflow-hidden">
        <div className="relative aspect-video">
          {content.posterPath ? (
            <Image
              src={`https://image.tmdb.org/t/p/w500${content.posterPath}`}
              alt={content.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 288px, 320px"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary-500 to-secondary-400" />
          )}

          {/* Play button overlay */}
          <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 hover:opacity-100 transition-opacity">
            <motion.div
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="w-14 h-14 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center"
            >
              <Play size={28} weight="fill" className="text-white ml-1" />
            </motion.div>
          </div>

          {/* Progress bar */}
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
            <div className="h-full bg-primary-500 w-2/3" />
          </div>
        </div>

        <div className="p-3">
          <h3 className="font-semibold text-surface-900 dark:text-white line-clamp-1">
            {content.title}
          </h3>
          <p className="text-xs text-surface-500">{content.description}</p>
        </div>
      </Card>
    </motion.div>
  )
}

// Content Thumbnail
interface ContentThumbnailProps {
  content: Content
  index: number
}

function ContentThumbnail({ content, index }: ContentThumbnailProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group"
    >
      <Card interactive className="p-0 overflow-hidden">
        <div className="relative aspect-[2/3]">
          {content.posterPath ? (
            <Image
              src={`https://image.tmdb.org/t/p/w300${content.posterPath}`}
              alt={content.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 33vw, (max-width: 1024px) 20vw, 16vw"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary-500 to-secondary-400" />
          )}

          {/* Rating badge */}
          {content.rating && (
            <div className="absolute top-2 right-2">
              <span className="flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-medium bg-black/50 backdrop-blur-sm text-white">
                <Star size={10} weight="fill" className="text-amber-400" />
                {content.rating.toFixed(1)}
              </span>
            </div>
          )}

          {/* Hover overlay */}
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <Play size={24} weight="fill" className="text-white" />
          </div>
        </div>
      </Card>
      <h3 className="mt-2 text-sm font-medium text-surface-900 dark:text-white line-clamp-1">
        {content.title}
      </h3>
    </motion.div>
  )
}

// Mood Category Card
interface MoodCategoryProps {
  label: string
  gradient: string
  count: number
}

function MoodCategory({ label, gradient, count }: MoodCategoryProps) {
  return (
    <Link href="/discover">
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={cn(
          'relative p-4 rounded-2xl overflow-hidden',
          'bg-gradient-to-br',
          gradient,
          'cursor-pointer'
        )}
      >
        <div className="relative z-10">
          <h3 className="font-semibold text-white mb-1">{label}</h3>
          <p className="text-white/70 text-sm">{count} picks</p>
        </div>

        {/* Background pattern */}
        <div className="absolute inset-0 opacity-20">
          <div
            className="h-full w-full"
            style={{
              backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '16px 16px',
            }}
          />
        </div>
      </motion.div>
    </Link>
  )
}
