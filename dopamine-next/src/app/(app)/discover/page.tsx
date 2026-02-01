'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { MoodSelector } from '@/components/features/MoodSelector'
import { SkeletonContentCard } from '@/components/ui'
import type { MoodId } from '@/types'

export default function DiscoverPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleMoodComplete = (currentMood: MoodId, targetMood: string) => {
    setIsLoading(true)
    // Navigate to recommendations with mood parameters
    router.push(`/recommendations?from=${currentMood}&to=${targetMood}`)
  }

  return (
    <div className="min-h-screen">
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center min-h-[80vh] px-4"
          >
            <div className="w-16 h-16 mb-6 rounded-2xl bg-gradient-to-br from-primary-500 to-secondary-400 animate-pulse" />
            <h2 className="text-xl font-semibold text-surface-900 dark:text-white mb-2">
              Finding your perfect content...
            </h2>
            <p className="text-surface-500 dark:text-surface-400 mb-8">
              Our AI is curating recommendations just for you
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-w-2xl">
              {Array.from({ length: 6 }).map((_, i) => (
                <SkeletonContentCard key={i} />
              ))}
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="selector"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <MoodSelector onComplete={handleMoodComplete} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
