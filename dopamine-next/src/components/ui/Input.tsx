'use client'

import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
  fullWidth?: boolean
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      label,
      error,
      hint,
      icon,
      iconPosition = 'left',
      fullWidth = true,
      disabled,
      ...props
    },
    ref
  ) => {
    const hasError = !!error

    return (
      <div className={cn('flex flex-col gap-1.5', fullWidth && 'w-full')}>
        {label && (
          <label className="text-sm font-medium text-surface-700 dark:text-surface-300">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400">
              {icon}
            </div>
          )}
          <input
            type={type}
            ref={ref}
            disabled={disabled}
            className={cn(
              // Base
              'w-full px-4 py-3',
              'bg-surface-50 dark:bg-dark-card',
              'border rounded-xl',
              'text-surface-900 dark:text-white',
              'placeholder:text-surface-400',
              // Transitions
              'transition-all duration-200',
              // Focus
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              // States
              hasError
                ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500'
                : 'border-surface-200 dark:border-dark-border focus:ring-primary-500/20 focus:border-primary-500',
              // Disabled
              disabled && 'opacity-50 cursor-not-allowed bg-surface-100 dark:bg-dark-border',
              // Icon padding
              icon && iconPosition === 'left' && 'pl-11',
              icon && iconPosition === 'right' && 'pr-11',
              // Font size 16px to prevent iOS zoom
              'text-base',
              className
            )}
            {...props}
          />
          {icon && iconPosition === 'right' && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400">
              {icon}
            </div>
          )}
        </div>
        {(error || hint) && (
          <p
            className={cn(
              'text-sm',
              hasError ? 'text-red-500' : 'text-surface-500 dark:text-surface-400'
            )}
          >
            {error || hint}
          </p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

// Textarea variant
export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  hint?: string
  fullWidth?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    { className, label, error, hint, fullWidth = true, disabled, ...props },
    ref
  ) => {
    const hasError = !!error

    return (
      <div className={cn('flex flex-col gap-1.5', fullWidth && 'w-full')}>
        {label && (
          <label className="text-sm font-medium text-surface-700 dark:text-surface-300">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          disabled={disabled}
          className={cn(
            // Base
            'w-full px-4 py-3 min-h-[120px]',
            'bg-surface-50 dark:bg-dark-card',
            'border rounded-xl',
            'text-surface-900 dark:text-white',
            'placeholder:text-surface-400',
            'resize-none',
            // Transitions
            'transition-all duration-200',
            // Focus
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            // States
            hasError
              ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500'
              : 'border-surface-200 dark:border-dark-border focus:ring-primary-500/20 focus:border-primary-500',
            // Disabled
            disabled && 'opacity-50 cursor-not-allowed',
            // Font size 16px to prevent iOS zoom
            'text-base',
            className
          )}
          {...props}
        />
        {(error || hint) && (
          <p
            className={cn(
              'text-sm',
              hasError ? 'text-red-500' : 'text-surface-500 dark:text-surface-400'
            )}
          >
            {error || hint}
          </p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
