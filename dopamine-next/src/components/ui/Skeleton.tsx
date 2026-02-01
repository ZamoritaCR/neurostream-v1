'use client'

import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded'
  width?: string | number
  height?: string | number
  animation?: 'pulse' | 'shimmer' | 'none'
}

export function Skeleton({
  className,
  variant = 'rectangular',
  width,
  height,
  animation = 'shimmer',
}: SkeletonProps) {
  const variants = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-none',
    rounded: 'rounded-xl',
  }

  const animations = {
    pulse: 'animate-pulse',
    shimmer: 'skeleton-shimmer',
    none: '',
  }

  return (
    <div
      className={cn(
        'bg-surface-200 dark:bg-dark-border',
        variants[variant],
        animations[animation],
        className
      )}
      style={{
        width: width,
        height: height,
      }}
    />
  )
}

// Preset skeleton components
export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={cn('space-y-2', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          variant="text"
          className={cn(
            'h-4',
            i === lines - 1 && 'w-3/4' // Last line is shorter
          )}
        />
      ))}
    </div>
  )
}

export function SkeletonAvatar({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  }

  return <Skeleton variant="circular" className={sizes[size]} />
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('space-y-3', className)}>
      <Skeleton variant="rounded" className="w-full aspect-[2/3]" />
      <Skeleton variant="text" className="h-5 w-3/4" />
      <Skeleton variant="text" className="h-4 w-1/2" />
    </div>
  )
}

export function SkeletonContentCard({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'bg-white dark:bg-dark-card rounded-2xl overflow-hidden',
        'border border-surface-100 dark:border-dark-border',
        className
      )}
    >
      <Skeleton variant="rectangular" className="w-full aspect-[2/3]" />
      <div className="p-4 space-y-3">
        <Skeleton variant="text" className="h-5 w-3/4" />
        <Skeleton variant="text" className="h-4 w-1/2" />
        <div className="flex gap-2">
          <Skeleton variant="rounded" className="h-6 w-16" />
          <Skeleton variant="rounded" className="h-6 w-16" />
        </div>
      </div>
    </div>
  )
}

export function SkeletonMoodCard({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'rounded-3xl p-6 flex flex-col items-center justify-center gap-4',
        'bg-surface-100 dark:bg-dark-border',
        className
      )}
      style={{ minHeight: 160 }}
    >
      <Skeleton variant="circular" className="w-12 h-12" />
      <Skeleton variant="text" className="h-5 w-20" />
      <Skeleton variant="text" className="h-4 w-32" />
    </div>
  )
}

export function SkeletonChatBubble({ isUser = false }: { isUser?: boolean }) {
  return (
    <div
      className={cn(
        'flex',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'max-w-[80%] px-4 py-3 rounded-2xl space-y-2',
          isUser
            ? 'bg-primary-500/20 rounded-br-md'
            : 'bg-surface-100 dark:bg-dark-border rounded-bl-md'
        )}
      >
        <Skeleton variant="text" className="h-4 w-40" />
        <Skeleton variant="text" className="h-4 w-24" />
      </div>
    </div>
  )
}
