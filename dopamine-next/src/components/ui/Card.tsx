'use client'

import { forwardRef, type HTMLAttributes, type ReactNode } from 'react'
import { motion, type MotionProps } from 'framer-motion'
import { cn } from '@/lib/utils'

type CardBaseProps = Omit<HTMLAttributes<HTMLDivElement>, 'onAnimationStart' | 'onDrag' | 'onDragEnd' | 'onDragStart'>

export interface CardProps extends CardBaseProps {
  variant?: 'default' | 'glass' | 'elevated' | 'outlined'
  interactive?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
  animate?: boolean
}

const variants = {
  default: 'bg-white dark:bg-dark-card border border-surface-100 dark:border-dark-border',
  glass: 'glass',
  elevated: 'bg-white dark:bg-dark-card shadow-lg',
  outlined: 'bg-transparent border-2 border-surface-200 dark:border-dark-border',
}

const paddings = {
  none: '',
  sm: 'p-3',
  md: 'p-4 md:p-6',
  lg: 'p-6 md:p-8',
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant = 'default',
      interactive = false,
      padding = 'md',
      animate = true,
      children,
      onClick,
      ...props
    },
    ref
  ) => {
    const Component = animate ? motion.div : 'div'
    const motionProps = animate
      ? {
          whileHover: interactive ? { y: -4, transition: { duration: 0.2 } } : {},
          whileTap: interactive ? { scale: 0.99 } : {},
        }
      : {}

    return (
      <Component
        ref={ref}
        className={cn(
          'rounded-2xl',
          'transition-shadow duration-300',
          variants[variant],
          paddings[padding],
          interactive && 'cursor-pointer hover:shadow-card-hover',
          className
        )}
        onClick={onClick}
        {...motionProps}
        {...props}
      >
        {children}
      </Component>
    )
  }
)

Card.displayName = 'Card'

// Card Header
export interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  title?: string
  subtitle?: string
  action?: ReactNode
}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, title, subtitle, action, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('flex items-start justify-between gap-4 mb-4', className)}
        {...props}
      >
        <div className="flex-1 min-w-0">
          {title && (
            <h3 className="text-lg font-semibold text-surface-900 dark:text-white truncate">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-surface-500 dark:text-surface-400 mt-1">
              {subtitle}
            </p>
          )}
          {children}
        </div>
        {action && <div className="flex-shrink-0">{action}</div>}
      </div>
    )
  }
)

CardHeader.displayName = 'CardHeader'

// Card Content
export const CardContent = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('', className)} {...props} />
))

CardContent.displayName = 'CardContent'

// Card Footer
export const CardFooter = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center gap-4 mt-4 pt-4 border-t border-surface-100 dark:border-dark-border', className)}
    {...props}
  />
))

CardFooter.displayName = 'CardFooter'
