'use client'

import { Fragment, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from '@phosphor-icons/react'
import { cn } from '@/lib/utils'
import { IconButton } from './Button'

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  description?: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
  closeOnOverlayClick?: boolean
  className?: string
}

const sizes = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-[95vw] md:max-w-4xl',
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  className,
}: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <Fragment>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeOnOverlayClick ? onClose : undefined}
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              className={cn(
                'relative w-full pointer-events-auto',
                'bg-white dark:bg-dark-card',
                'rounded-2xl shadow-2xl',
                'overflow-hidden',
                sizes[size],
                className
              )}
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ type: 'spring', duration: 0.3, bounce: 0.25 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              {(title || showCloseButton) && (
                <div className="flex items-start justify-between p-4 md:p-6 border-b border-surface-100 dark:border-dark-border">
                  <div className="flex-1 pr-4">
                    {title && (
                      <h2 className="text-xl font-semibold text-surface-900 dark:text-white">
                        {title}
                      </h2>
                    )}
                    {description && (
                      <p className="mt-1 text-sm text-surface-500 dark:text-surface-400">
                        {description}
                      </p>
                    )}
                  </div>
                  {showCloseButton && (
                    <IconButton
                      icon={<X size={20} weight="bold" />}
                      label="Close"
                      size="sm"
                      onClick={onClose}
                      className="flex-shrink-0"
                    />
                  )}
                </div>
              )}

              {/* Content */}
              <div className="p-4 md:p-6 max-h-[70vh] overflow-y-auto scrollbar-thin">
                {children}
              </div>
            </motion.div>
          </div>
        </Fragment>
      )}
    </AnimatePresence>
  )
}

// Bottom Sheet variant for mobile
export interface BottomSheetProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  className?: string
}

export function BottomSheet({
  isOpen,
  onClose,
  title,
  children,
  className,
}: BottomSheetProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <Fragment>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Sheet */}
          <motion.div
            className={cn(
              'fixed inset-x-0 bottom-0 z-50',
              'bg-white dark:bg-dark-card',
              'rounded-t-3xl shadow-2xl',
              'pb-safe',
              'max-h-[90vh]',
              className
            )}
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            drag="y"
            dragConstraints={{ top: 0 }}
            dragElastic={{ top: 0, bottom: 0.5 }}
            onDragEnd={(_, info) => {
              if (info.offset.y > 100 || info.velocity.y > 500) {
                onClose()
              }
            }}
          >
            {/* Handle */}
            <div className="flex justify-center pt-3 pb-2">
              <div className="w-10 h-1.5 bg-surface-300 dark:bg-surface-600 rounded-full" />
            </div>

            {/* Header */}
            {title && (
              <div className="px-4 pb-4 border-b border-surface-100 dark:border-dark-border">
                <h2 className="text-lg font-semibold text-center text-surface-900 dark:text-white">
                  {title}
                </h2>
              </div>
            )}

            {/* Content */}
            <div className="p-4 overflow-y-auto max-h-[calc(90vh-100px)] scrollbar-thin">
              {children}
            </div>
          </motion.div>
        </Fragment>
      )}
    </AnimatePresence>
  )
}
