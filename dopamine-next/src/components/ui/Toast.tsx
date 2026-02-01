'use client'

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, XCircle, Info, Warning } from '@phosphor-icons/react'
import { cn, generateId } from '@/lib/utils'
import type { Toast as ToastType, ToastType as ToastVariant } from '@/types'

// Toast Context
interface ToastContextType {
  toasts: ToastType[]
  addToast: (toast: Omit<ToastType, 'id'>) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | null>(null)

// Hook to use toast
export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }

  const toast = useCallback(
    (props: Omit<ToastType, 'id'>) => {
      context.addToast(props)
    },
    [context]
  )

  return {
    toast,
    success: (title: string, description?: string) =>
      toast({ type: 'success', title, description }),
    error: (title: string, description?: string) =>
      toast({ type: 'error', title, description }),
    info: (title: string, description?: string) =>
      toast({ type: 'info', title, description }),
    warning: (title: string, description?: string) =>
      toast({ type: 'warning', title, description }),
  }
}

// Toast Provider
interface ToastProviderProps {
  children: ReactNode
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<ToastType[]>([])

  const addToast = useCallback((toast: Omit<ToastType, 'id'>) => {
    const id = generateId()
    setToasts((prev) => [...prev, { ...toast, id }])

    // Auto remove after duration
    const duration = toast.duration ?? 5000
    if (duration > 0) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
      }, duration)
    }
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

// Toast Container
interface ToastContainerProps {
  toasts: ToastType[]
  onRemove: (id: string) => void
}

function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 right-4 left-4 md:left-auto md:w-96 z-[100] flex flex-col gap-3 pointer-events-none">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={() => onRemove(toast.id)} />
        ))}
      </AnimatePresence>
    </div>
  )
}

// Single Toast Item
interface ToastItemProps {
  toast: ToastType
  onClose: () => void
}

const icons: Record<ToastVariant, typeof CheckCircle> = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
  warning: Warning,
}

const styles: Record<ToastVariant, string> = {
  success: 'bg-emerald-500 text-white',
  error: 'bg-red-500 text-white',
  info: 'bg-primary-500 text-white',
  warning: 'bg-amber-500 text-white',
}

function ToastItem({ toast, onClose }: ToastItemProps) {
  const Icon = icons[toast.type]

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.9 }}
      className={cn(
        'flex items-start gap-3 px-4 py-3 rounded-xl shadow-xl pointer-events-auto',
        styles[toast.type]
      )}
    >
      <Icon size={24} weight="fill" className="flex-shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        <p className="font-semibold">{toast.title}</p>
        {toast.description && (
          <p className="text-sm opacity-90 mt-0.5">{toast.description}</p>
        )}
      </div>
      <button
        onClick={onClose}
        className="flex-shrink-0 p-1 rounded-full hover:bg-white/20 transition-colors"
      >
        <X size={16} weight="bold" />
      </button>
    </motion.div>
  )
}
