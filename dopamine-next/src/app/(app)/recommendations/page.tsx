'use client'

import { useState, useEffect, Suspense, useCallback } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Play,
  Heart,
  Plus,
  ArrowsClockwise,
  Star,
  Clock,
  Television,
  MusicNote,
  Microphone,
  Book,
  VideoCamera,
  Lightning,
  Sparkle,
  Warning,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button, Card, SkeletonContentCard } from '@/components/ui'
import { getMoodById, getMoodGradient, targetMoods } from '@/lib/moods'
import { getMoodBasedRecommendations, getTrending } from '@/lib/tmdb'
import type { Content, ContentType, MoodId } from '@/types'

// Content type tabs (only show movie/tv for now since TMDB doesn't have music/podcasts)
const contentTabs: { id: ContentType | 'all'; label: string; icon: typeof Television }[] = [
  { id: 'all', label: 'All', icon: Sparkle },
  { id: 'movie', label: 'Movies', icon: VideoCamera },
  { id: 'tv', label: 'TV Shows', icon: Television },
]

function RecommendationsContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const fromMood = searchParams.get('from') as MoodId | null
  const toMood = searchParams.get('to')

  const [activeTab, setActiveTab] = useState<ContentType | 'all'>('all')
  const [content, setContent] = useState<Content[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [favorites, setFavorites] = useState<Set<string>>(new Set())
  const [queue, setQueue] = useState<Set<string>>(new Set())

  const currentMoodData = fromMood ? getMoodById(fromMood) : null
  const targetMoodData = targetMoods.find(t => t.id === toMood)

  const fetchContent = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      let results: Content[]

      if (fromMood && toMood) {
        // Get mood-based recommendations
        const contentType = activeTab === 'all' ? 'all' : activeTab as 'movie' | 'tv'
        results = await getMoodBasedRecommendations(fromMood, toMood, contentType)
      } else {
        // Fallback to trending if no mood selected
        results = await getTrending(activeTab === 'all' ? 'all' : activeTab as 'movie' | 'tv')
      }

      setContent(results)
    } catch (err) {
      console.error('Failed to fetch recommendations:', err)
      setError('Failed to load recommendations. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [fromMood, toMood, activeTab])

  useEffect(() => {
    fetchContent()
  }, [fetchContent])

  // Content is already filtered by the API based on activeTab
  const filteredContent = content

  const toggleFavorite = (id: string) => {
    haptic('light')
    setFavorites(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const toggleQueue = (id: string) => {
    haptic('light')
    setQueue(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const handleRefresh = () => {
    haptic('medium')
    fetchContent()
  }

  return (
    <div className="min-h-screen pb-8">
      {/* Header with mood context */}
      <div className="px-4 md:px-8 py-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
        >
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-surface-900 dark:text-white mb-2">
              Your Recommendations
            </h1>
            {currentMoodData && targetMoodData && (
              <div className="flex items-center gap-2 text-sm text-surface-600 dark:text-surface-400">
                <span
                  className="px-3 py-1 rounded-full text-white font-medium"
                  style={{ backgroundColor: currentMoodData.color }}
                >
                  {currentMoodData.label}
                </span>
                <span>→</span>
                <span
                  className="px-3 py-1 rounded-full text-white font-medium"
                  style={{ backgroundColor: targetMoodData.color }}
                >
                  {targetMoodData.label}
                </span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              icon={<ArrowsClockwise size={18} />}
              onClick={handleRefresh}
            >
              Refresh
            </Button>
            <Button
              size="sm"
              icon={<Lightning size={18} weight="fill" />}
              onClick={() => router.push('/quick-hit')}
            >
              Quick Hit
            </Button>
          </div>
        </motion.div>
      </div>

      {/* Content type tabs */}
      <div className="px-4 md:px-8 mb-6">
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {contentTabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => {
                  haptic('light')
                  setActiveTab(tab.id)
                }}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-full whitespace-nowrap',
                  'font-medium text-sm transition-all duration-200',
                  isActive
                    ? 'bg-primary-500 text-white shadow-glow-sm'
                    : 'bg-surface-100 dark:bg-dark-card text-surface-600 dark:text-surface-300 hover:bg-surface-200 dark:hover:bg-dark-hover'
                )}
              >
                <Icon size={18} weight={isActive ? 'fill' : 'regular'} />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content grid */}
      <div className="px-4 md:px-8">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
            >
              {Array.from({ length: 10 }).map((_, i) => (
                <SkeletonContentCard key={i} />
              ))}
            </motion.div>
          ) : error ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-16"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center">
                <Warning size={32} className="text-red-500" />
              </div>
              <h3 className="text-lg font-semibold text-surface-900 dark:text-white mb-2">
                Something went wrong
              </h3>
              <p className="text-surface-500 dark:text-surface-400 mb-4">
                {error}
              </p>
              <Button onClick={handleRefresh}>Try Again</Button>
            </motion.div>
          ) : filteredContent.length > 0 ? (
            <motion.div
              key="content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
            >
              {filteredContent.map((item, index) => (
                <ContentCard
                  key={item.id}
                  content={item}
                  index={index}
                  isFavorite={favorites.has(item.id)}
                  isInQueue={queue.has(item.id)}
                  onToggleFavorite={() => toggleFavorite(item.id)}
                  onToggleQueue={() => toggleQueue(item.id)}
                />
              ))}
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-16"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-surface-100 dark:bg-dark-card flex items-center justify-center">
                <Sparkle size={32} className="text-surface-400" />
              </div>
              <h3 className="text-lg font-semibold text-surface-900 dark:text-white mb-2">
                No content found
              </h3>
              <p className="text-surface-500 dark:text-surface-400 mb-4">
                Try adjusting your filters or refreshing
              </p>
              <Button onClick={handleRefresh}>Refresh Results</Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Content Card Component
interface ContentCardProps {
  content: Content
  index: number
  isFavorite: boolean
  isInQueue: boolean
  onToggleFavorite: () => void
  onToggleQueue: () => void
}

function ContentCard({
  content,
  index,
  isFavorite,
  isInQueue,
  onToggleFavorite,
  onToggleQueue,
}: ContentCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  // Get content type icon
  const TypeIcon = {
    movie: VideoCamera,
    tv: Television,
    music: MusicNote,
    podcast: Microphone,
    audiobook: Book,
    short: Play,
  }[content.type]

  // Placeholder image based on content type
  const placeholderGradient = {
    movie: 'from-violet-500 to-purple-600',
    tv: 'from-blue-500 to-cyan-500',
    music: 'from-green-500 to-emerald-500',
    podcast: 'from-orange-500 to-red-500',
    audiobook: 'from-amber-500 to-yellow-500',
    short: 'from-pink-500 to-rose-500',
  }[content.type]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative"
    >
      <Card
        interactive
        className="overflow-hidden p-0"
      >
        {/* Poster / Thumbnail */}
        <div className="relative aspect-[2/3]">
          {content.posterPath ? (
            <Image
              src={`https://image.tmdb.org/t/p/w500${content.posterPath}`}
              alt={content.title}
              fill
              className="object-cover"
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
            />
          ) : (
            <div className={cn(
              'w-full h-full flex items-center justify-center',
              'bg-gradient-to-br',
              placeholderGradient
            )}>
              <TypeIcon size={48} weight="fill" className="text-white/50" />
            </div>
          )}

          {/* Hover overlay */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/60 flex items-center justify-center"
              >
                <Button
                  size="lg"
                  icon={<Play size={24} weight="fill" />}
                  className="rounded-full w-14 h-14 p-0"
                >
                  <span className="sr-only">Play</span>
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Type badge */}
          <div className="absolute top-2 left-2">
            <span className={cn(
              'px-2 py-1 rounded-lg text-xs font-medium',
              'bg-black/50 text-white backdrop-blur-sm'
            )}>
              {content.type === 'tv' ? 'TV' : content.type.charAt(0).toUpperCase() + content.type.slice(1)}
            </span>
          </div>

          {/* Rating badge */}
          {content.rating && (
            <div className="absolute top-2 right-2">
              <span className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-black/50 text-white backdrop-blur-sm">
                <Star size={12} weight="fill" className="text-amber-400" />
                {content.rating.toFixed(1)}
              </span>
            </div>
          )}

          {/* Action buttons */}
          <div className="absolute bottom-2 right-2 flex gap-1">
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation()
                onToggleFavorite()
              }}
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center',
                'backdrop-blur-sm transition-colors',
                isFavorite
                  ? 'bg-red-500 text-white'
                  : 'bg-black/50 text-white hover:bg-red-500'
              )}
            >
              <Heart size={16} weight={isFavorite ? 'fill' : 'regular'} />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation()
                onToggleQueue()
              }}
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center',
                'backdrop-blur-sm transition-colors',
                isInQueue
                  ? 'bg-primary-500 text-white'
                  : 'bg-black/50 text-white hover:bg-primary-500'
              )}
            >
              <Plus size={16} weight={isInQueue ? 'bold' : 'regular'} />
            </motion.button>
          </div>
        </div>

        {/* Info */}
        <div className="p-3">
          <h3 className="font-semibold text-surface-900 dark:text-white line-clamp-1 mb-1">
            {content.title}
          </h3>
          {content.genres && content.genres.length > 0 && (
            <p className="text-xs text-surface-500 dark:text-surface-400 line-clamp-1">
              {content.genres.slice(0, 2).join(' / ')}
            </p>
          )}
          {content.runtime && (
            <div className="flex items-center gap-1 mt-2 text-xs text-surface-400">
              <Clock size={12} />
              <span>{content.runtime} min</span>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  )
}

// Main page component with Suspense
export default function RecommendationsPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-400 animate-pulse" />
      </div>
    }>
      <RecommendationsContent />
    </Suspense>
  )
}
