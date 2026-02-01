'use client'

import { useState, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform, PanInfo } from 'framer-motion'
import {
  Lightning,
  Waves,
  Sparkle,
  Sun,
  Star,
  Users,
  Fire,
  Moon,
  Feather,
  ArrowsClockwise,
  Target,
  CloudRain,
  ArrowRight,
  Check,
} from '@phosphor-icons/react'
import { cn, haptic, isMobile } from '@/lib/utils'
import { moods, targetMoods } from '@/lib/moods'
import type { MoodId } from '@/types'
import { Button } from '@/components/ui'

// Icon map for dynamic rendering
const iconMap: Record<string, typeof Lightning> = {
  Lightning,
  Waves,
  Sparkle,
  Sun,
  Star,
  Users,
  Fire,
  Moon,
  Feather,
  ArrowsClockwise,
  Target,
  CloudRain,
}

interface MoodSelectorProps {
  onComplete: (currentMood: MoodId, targetMood: string) => void
}

export function MoodSelector({ onComplete }: MoodSelectorProps) {
  const [step, setStep] = useState<'current' | 'target'>('current')
  const [selectedMood, setSelectedMood] = useState<MoodId | null>(null)
  const [selectedTarget, setSelectedTarget] = useState<string | null>(null)

  const handleMoodSelect = (moodId: MoodId) => {
    haptic('medium')
    setSelectedMood(moodId)
    // Small delay before transitioning
    setTimeout(() => setStep('target'), 300)
  }

  const handleTargetSelect = (targetId: string) => {
    haptic('medium')
    setSelectedTarget(targetId)
  }

  const handleContinue = () => {
    if (selectedMood && selectedTarget) {
      onComplete(selectedMood, selectedTarget)
    }
  }

  return (
    <div className="min-h-screen-safe flex flex-col">
      {/* Header */}
      <div className="text-center pt-8 pb-6 px-4">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <h1 className="text-2xl md:text-3xl font-bold text-surface-900 dark:text-white mb-2">
              {step === 'current' ? "How are you feeling?" : "How do you want to feel?"}
            </h1>
            <p className="text-surface-500 dark:text-surface-400">
              {step === 'current'
                ? "Select your current emotional state"
                : "Choose your destination mood"}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Step indicator */}
      <div className="flex justify-center gap-2 mb-6">
        <div
          className={cn(
            'w-2 h-2 rounded-full transition-colors',
            step === 'current' ? 'bg-primary-500' : 'bg-surface-300'
          )}
        />
        <div
          className={cn(
            'w-2 h-2 rounded-full transition-colors',
            step === 'target' ? 'bg-primary-500' : 'bg-surface-300'
          )}
        />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <AnimatePresence mode="wait">
          {step === 'current' ? (
            <motion.div
              key="current"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="h-full"
            >
              {isMobile() ? (
                <MoodCarousel
                  moods={moods}
                  selectedMood={selectedMood}
                  onSelect={handleMoodSelect}
                />
              ) : (
                <MoodGrid
                  moods={moods}
                  selectedMood={selectedMood}
                  onSelect={handleMoodSelect}
                />
              )}
            </motion.div>
          ) : (
            <motion.div
              key="target"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              className="px-4 md:px-8"
            >
              <TargetMoodGrid
                targets={targetMoods}
                selectedTarget={selectedTarget}
                onSelect={handleTargetSelect}
              />

              {/* Continue button */}
              <div className="mt-8 flex justify-center">
                <Button
                  size="lg"
                  disabled={!selectedTarget}
                  onClick={handleContinue}
                  icon={<ArrowRight size={20} weight="bold" />}
                  iconPosition="right"
                  className="px-12"
                >
                  Find My Content
                </Button>
              </div>

              {/* Back button */}
              <button
                onClick={() => setStep('current')}
                className="mt-4 mx-auto block text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 transition-colors"
              >
                ← Go back
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Mobile: Swipeable Carousel
interface MoodCarouselProps {
  moods: typeof import('@/lib/moods').moods
  selectedMood: MoodId | null
  onSelect: (id: MoodId) => void
}

function MoodCarousel({ moods, selectedMood, onSelect }: MoodCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleDragEnd = (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const threshold = 50
    if (info.offset.x > threshold && currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
      haptic('light')
    } else if (info.offset.x < -threshold && currentIndex < moods.length - 1) {
      setCurrentIndex(currentIndex + 1)
      haptic('light')
    }
  }

  return (
    <div className="relative h-full flex flex-col items-center justify-center">
      {/* Carousel */}
      <div
        ref={containerRef}
        className="relative w-full overflow-hidden"
        style={{ height: 320 }}
      >
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0.1}
          onDragEnd={handleDragEnd}
        >
          {moods.map((mood, index) => {
            const Icon = iconMap[mood.icon] || Sparkle
            const isActive = index === currentIndex
            const offset = index - currentIndex

            return (
              <motion.div
                key={mood.id}
                className="absolute"
                animate={{
                  x: offset * 280,
                  scale: isActive ? 1 : 0.85,
                  opacity: Math.abs(offset) > 1 ? 0 : isActive ? 1 : 0.5,
                  rotateY: offset * -15,
                }}
                transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                style={{ transformStyle: 'preserve-3d' }}
              >
                <motion.button
                  className={cn(
                    'w-64 h-72 rounded-3xl p-6',
                    'flex flex-col items-center justify-center gap-4',
                    'bg-gradient-to-br',
                    mood.gradient,
                    'shadow-xl',
                    'transition-shadow duration-300',
                    isActive && 'shadow-2xl',
                    selectedMood === mood.id && 'ring-4 ring-white ring-offset-4'
                  )}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => isActive && onSelect(mood.id)}
                >
                  <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center">
                    <Icon size={40} weight="fill" className="text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-white">{mood.label}</h3>
                  <p className="text-white/80 text-center text-sm">{mood.description}</p>
                </motion.button>
              </motion.div>
            )
          })}
        </motion.div>
      </div>

      {/* Dots indicator */}
      <div className="flex gap-2 mt-6">
        {moods.map((mood, index) => (
          <button
            key={mood.id}
            className={cn(
              'w-2 h-2 rounded-full transition-all duration-200',
              index === currentIndex
                ? 'w-6 bg-primary-500'
                : 'bg-surface-300 dark:bg-surface-600'
            )}
            onClick={() => {
              setCurrentIndex(index)
              haptic('light')
            }}
          />
        ))}
      </div>

      {/* Tap to select hint */}
      <p className="mt-4 text-sm text-surface-500">Swipe to browse • Tap to select</p>
    </div>
  )
}

// Desktop: Grid Layout
interface MoodGridProps {
  moods: typeof import('@/lib/moods').moods
  selectedMood: MoodId | null
  onSelect: (id: MoodId) => void
}

function MoodGrid({ moods, selectedMood, onSelect }: MoodGridProps) {
  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {moods.map((mood, index) => {
          const Icon = iconMap[mood.icon] || Sparkle
          const isSelected = selectedMood === mood.id

          return (
            <motion.button
              key={mood.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={cn(
                'relative p-6 rounded-2xl',
                'flex flex-col items-center justify-center gap-3',
                'bg-gradient-to-br',
                mood.gradient,
                'shadow-lg hover:shadow-xl',
                'transition-all duration-300',
                isSelected && 'ring-4 ring-white ring-offset-4 scale-105'
              )}
              style={{ minHeight: 160 }}
              whileHover={{ scale: 1.02, y: -4 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onSelect(mood.id)}
            >
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-3 right-3 w-6 h-6 bg-white rounded-full flex items-center justify-center"
                >
                  <Check size={14} weight="bold" className="text-primary-500" />
                </motion.div>
              )}
              <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
                <Icon size={28} weight="fill" className="text-white" />
              </div>
              <h3 className="text-lg font-bold text-white">{mood.label}</h3>
              <p className="text-white/70 text-center text-xs">{mood.description}</p>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}

// Target Mood Grid
interface TargetMoodGridProps {
  targets: typeof targetMoods
  selectedTarget: string | null
  onSelect: (id: string) => void
}

function TargetMoodGrid({ targets, selectedTarget, onSelect }: TargetMoodGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-w-2xl mx-auto">
      {targets.map((target, index) => {
        const isSelected = selectedTarget === target.id

        return (
          <motion.button
            key={target.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={cn(
              'relative p-6 rounded-2xl',
              'flex flex-col items-center justify-center gap-3',
              'border-2 transition-all duration-200',
              isSelected
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10'
                : 'border-surface-200 dark:border-dark-border bg-white dark:bg-dark-card hover:border-primary-300'
            )}
            style={{ minHeight: 120 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSelect(target.id)}
          >
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: `${target.color}20` }}
            >
              <span className="text-2xl" style={{ color: target.color }}>
                {/* Icon placeholder - we'd use Phosphor icons here */}
                ●
              </span>
            </div>
            <h3 className="font-semibold text-surface-900 dark:text-white">
              {target.label}
            </h3>
            {isSelected && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute top-2 right-2 w-5 h-5 bg-primary-500 rounded-full flex items-center justify-center"
              >
                <Check size={12} weight="bold" className="text-white" />
              </motion.div>
            )}
          </motion.button>
        )
      })}
    </div>
  )
}
