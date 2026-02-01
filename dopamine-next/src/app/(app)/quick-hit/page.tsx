'use client'

import { useState } from 'react'
import Image from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Lightning,
  ArrowsClockwise,
  Play,
  Heart,
  Plus,
  Star,
  Clock,
  Sparkle,
  Television,
  VideoCamera,
  Warning,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button, Card } from '@/components/ui'
import { getQuickHitRecommendation } from '@/lib/tmdb'
import type { Content } from '@/types'

export default function QuickHitPage() {
  const [currentContent, setCurrentContent] = useState<Content | null>(null)
  const [isRevealing, setIsRevealing] = useState(false)
  const [hasGenerated, setHasGenerated] = useState(false)
  const [isFavorite, setIsFavorite] = useState(false)
  const [isInQueue, setIsInQueue] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateQuickHit = async () => {
    haptic('heavy')
    setIsRevealing(true)
    setHasGenerated(true)
    setIsFavorite(false)
    setIsInQueue(false)
    setError(null)

    try {
      // Call real TMDB API
      const content = await getQuickHitRecommendation()
      setCurrentContent(content)
      haptic('heavy')
    } catch (err) {
      console.error('Failed to get recommendation:', err)
      setError('Failed to fetch recommendation. Please try again.')
    } finally {
      setIsRevealing(false)
    }
  }

  const toggleFavorite = () => {
    haptic('light')
    setIsFavorite(!isFavorite)
  }

  const toggleQueue = () => {
    haptic('light')
    setIsInQueue(!isInQueue)
  }

  const TypeIcon = currentContent?.type === 'tv' ? Television : VideoCamera

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <div className="text-center pt-8 pb-6 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary-500/10 to-secondary-400/10 text-primary-600 dark:text-primary-400 mb-4"
        >
          <Lightning size={18} weight="fill" />
          <span className="font-medium">Quick Dope Hit</span>
        </motion.div>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-3xl md:text-4xl font-bold text-surface-900 dark:text-white mb-3"
        >
          Can't decide?
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-surface-500 dark:text-surface-400 max-w-md mx-auto"
        >
          Let our AI pick the perfect thing for you right now. One tap. Zero scrolling.
        </motion.p>
      </div>

      {/* Main content area */}
      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <AnimatePresence mode="wait">
          {!hasGenerated ? (
            // Initial state - big button
            <motion.div
              key="initial"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="text-center"
            >
              <motion.button
                onClick={generateQuickHit}
                className={cn(
                  'relative w-48 h-48 md:w-64 md:h-64 rounded-full',
                  'bg-gradient-to-br from-primary-500 via-secondary-400 to-accent-400',
                  'shadow-glow hover:shadow-glow-lg',
                  'transition-all duration-300',
                  'flex items-center justify-center'
                )}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {/* Pulsing ring */}
                <motion.div
                  className="absolute inset-0 rounded-full bg-gradient-to-br from-primary-500 to-secondary-400"
                  animate={{
                    scale: [1, 1.1, 1],
                    opacity: [0.5, 0, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />

                <div className="relative flex flex-col items-center gap-2">
                  <Lightning size={64} weight="fill" className="text-white" />
                  <span className="text-white text-xl font-bold">Hit Me</span>
                </div>
              </motion.button>

              <p className="mt-6 text-sm text-surface-400">
                Tap the button to get your instant recommendation
              </p>
            </motion.div>
          ) : isRevealing ? (
            // Loading state
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center"
            >
              <div className="relative w-48 h-48 md:w-64 md:h-64 mx-auto">
                {/* Spinning gradient ring */}
                <motion.div
                  className="absolute inset-0 rounded-full"
                  style={{
                    background: 'conic-gradient(from 0deg, #6B5CD8, #3EAFA1, #F4B942, #6B5CD8)',
                  }}
                  animate={{ rotate: 360 }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: 'linear',
                  }}
                />
                <div className="absolute inset-2 rounded-full bg-white dark:bg-dark-bg flex items-center justify-center">
                  <motion.div
                    animate={{
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  >
                    <Sparkle size={48} weight="fill" className="text-primary-500" />
                  </motion.div>
                </div>
              </div>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="mt-6 text-surface-600 dark:text-surface-300 font-medium"
              >
                Finding your dopamine hit...
              </motion.p>
            </motion.div>
          ) : error ? (
            // Error state
            <motion.div
              key="error"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="text-center px-4"
            >
              <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-500/10 flex items-center justify-center">
                <Warning size={40} className="text-red-500" />
              </div>
              <h3 className="text-xl font-semibold text-surface-900 dark:text-white mb-2">
                Oops! Something went wrong
              </h3>
              <p className="text-surface-500 dark:text-surface-400 mb-6">
                {error}
              </p>
              <Button onClick={generateQuickHit}>
                Try Again
              </Button>
            </motion.div>
          ) : currentContent ? (
            // Result state
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              className="w-full max-w-lg"
            >
              <Card className="overflow-hidden p-0">
                {/* Backdrop image */}
                <div className="relative h-48 md:h-64">
                  {currentContent.backdropPath ? (
                    <Image
                      src={`https://image.tmdb.org/t/p/w780${currentContent.backdropPath}`}
                      alt=""
                      fill
                      className="object-cover"
                      sizes="(max-width: 768px) 100vw, 512px"
                      priority
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary-500 to-secondary-400" />
                  )}

                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

                  {/* Play button */}
                  <motion.button
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
                    className={cn(
                      'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
                      'w-16 h-16 rounded-full',
                      'bg-white/20 backdrop-blur-md',
                      'flex items-center justify-center',
                      'hover:bg-white/30 transition-colors'
                    )}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Play size={32} weight="fill" className="text-white ml-1" />
                  </motion.button>

                  {/* Type badge */}
                  <div className="absolute top-4 left-4">
                    <span className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-black/50 backdrop-blur-sm text-white text-sm font-medium">
                      <TypeIcon size={16} weight="fill" />
                      {currentContent.type === 'tv' ? 'TV Show' : 'Movie'}
                    </span>
                  </div>

                  {/* Rating */}
                  {currentContent.rating && (
                    <div className="absolute top-4 right-4">
                      <span className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-black/50 backdrop-blur-sm text-white text-sm font-medium">
                        <Star size={16} weight="fill" className="text-amber-400" />
                        {currentContent.rating.toFixed(1)}
                      </span>
                    </div>
                  )}

                  {/* Title overlay */}
                  <div className="absolute bottom-4 left-4 right-4">
                    <h2 className="text-2xl md:text-3xl font-bold text-white mb-1">
                      {currentContent.title}
                    </h2>
                    {currentContent.genres && (
                      <p className="text-white/70 text-sm">
                        {currentContent.genres.slice(0, 3).join(' • ')}
                      </p>
                    )}
                  </div>
                </div>

                {/* Content details */}
                <div className="p-6">
                  <p className="text-surface-600 dark:text-surface-300 mb-4 line-clamp-3">
                    {currentContent.description}
                  </p>

                  {/* Meta info */}
                  <div className="flex items-center gap-4 mb-6 text-sm text-surface-500">
                    {currentContent.runtime && (
                      <div className="flex items-center gap-1">
                        <Clock size={16} />
                        <span>{currentContent.runtime} min</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3">
                    <Button
                      className="flex-1"
                      icon={<Play size={20} weight="fill" />}
                    >
                      Watch Now
                    </Button>
                    <motion.button
                      whileTap={{ scale: 0.9 }}
                      onClick={toggleFavorite}
                      className={cn(
                        'w-12 h-12 rounded-xl flex items-center justify-center',
                        'border-2 transition-all duration-200',
                        isFavorite
                          ? 'border-red-500 bg-red-50 dark:bg-red-500/10 text-red-500'
                          : 'border-surface-200 dark:border-dark-border text-surface-500 hover:border-red-500 hover:text-red-500'
                      )}
                    >
                      <Heart size={22} weight={isFavorite ? 'fill' : 'regular'} />
                    </motion.button>
                    <motion.button
                      whileTap={{ scale: 0.9 }}
                      onClick={toggleQueue}
                      className={cn(
                        'w-12 h-12 rounded-xl flex items-center justify-center',
                        'border-2 transition-all duration-200',
                        isInQueue
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10 text-primary-500'
                          : 'border-surface-200 dark:border-dark-border text-surface-500 hover:border-primary-500 hover:text-primary-500'
                      )}
                    >
                      <Plus size={22} weight={isInQueue ? 'bold' : 'regular'} />
                    </motion.button>
                  </div>
                </div>
              </Card>

              {/* Try again */}
              <div className="mt-6 text-center">
                <Button
                  variant="ghost"
                  icon={<ArrowsClockwise size={18} />}
                  onClick={generateQuickHit}
                >
                  Not feeling it? Try again
                </Button>
              </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </div>
    </div>
  )
}
