'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Sparkle,
  GoogleLogo,
  EnvelopeSimple,
  Lock,
  Eye,
  EyeSlash,
  ArrowLeft,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button, Input, Card } from '@/components/ui'
import { useAuth } from '@/lib/auth-context'

export default function LoginPage() {
  const router = useRouter()
  const { signInWithGoogle, signInWithEmail, signUpWithEmail } = useAuth()

  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGoogleSignIn = async () => {
    haptic('medium')
    setIsLoading(true)
    setError(null)
    try {
      await signInWithGoogle()
    } catch (err) {
      setError('Failed to sign in with Google')
    } finally {
      setIsLoading(false)
    }
  }

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    haptic('light')
    setIsLoading(true)
    setError(null)

    try {
      if (mode === 'login') {
        const { error } = await signInWithEmail(email, password)
        if (error) throw error
        router.push('/home')
      } else {
        const { error } = await signUpWithEmail(email, password)
        if (error) throw error
        // Show success message or redirect
        setError('Check your email to confirm your account!')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-to-br from-surface-50 to-surface-100 dark:from-dark-bg dark:to-dark-card">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-primary-500/10 blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-secondary-400/10 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Back link */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 mb-8"
        >
          <ArrowLeft size={20} />
          <span>Back to home</span>
        </Link>

        <Card className="p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-2 mb-8">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-400 flex items-center justify-center shadow-glow-sm">
              <Sparkle size={28} weight="fill" className="text-white" />
            </div>
            <span className="text-2xl font-bold text-surface-900 dark:text-white">
              dopamine<span className="gradient-text">.watch</span>
            </span>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold text-center text-surface-900 dark:text-white mb-2">
            {mode === 'login' ? 'Welcome back!' : 'Create account'}
          </h1>
          <p className="text-center text-surface-500 dark:text-surface-400 mb-8">
            {mode === 'login'
              ? 'Sign in to continue your journey'
              : 'Start your dopamine-optimized experience'}
          </p>

          {/* Google Sign In */}
          <Button
            variant="secondary"
            className="w-full mb-4"
            icon={<GoogleLogo size={20} weight="bold" />}
            onClick={handleGoogleSignIn}
            loading={isLoading}
          >
            Continue with Google
          </Button>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-surface-200 dark:bg-dark-border" />
            <span className="text-sm text-surface-400">or</span>
            <div className="flex-1 h-px bg-surface-200 dark:bg-dark-border" />
          </div>

          {/* Email form */}
          <form onSubmit={handleEmailSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1"
              >
                Email
              </label>
              <div className="relative">
                <EnvelopeSimple
                  size={20}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400"
                />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className={cn(
                    'w-full pl-10 pr-4 py-3 rounded-xl',
                    'bg-surface-50 dark:bg-dark-hover',
                    'border border-surface-200 dark:border-dark-border',
                    'text-surface-900 dark:text-white',
                    'placeholder:text-surface-400',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500',
                    'transition-all duration-200'
                  )}
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-1"
              >
                Password
              </label>
              <div className="relative">
                <Lock
                  size={20}
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400"
                />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={6}
                  className={cn(
                    'w-full pl-10 pr-12 py-3 rounded-xl',
                    'bg-surface-50 dark:bg-dark-hover',
                    'border border-surface-200 dark:border-dark-border',
                    'text-surface-900 dark:text-white',
                    'placeholder:text-surface-400',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500',
                    'transition-all duration-200'
                  )}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 dark:hover:text-surface-300"
                >
                  {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className={cn(
                  'text-sm text-center p-3 rounded-lg',
                  error.includes('Check your email')
                    ? 'bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400'
                    : 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400'
                )}
              >
                {error}
              </motion.p>
            )}

            <Button type="submit" className="w-full" loading={isLoading}>
              {mode === 'login' ? 'Sign In' : 'Create Account'}
            </Button>
          </form>

          {/* Toggle mode */}
          <p className="mt-6 text-center text-surface-500 dark:text-surface-400">
            {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
            <button
              onClick={() => {
                setMode(mode === 'login' ? 'signup' : 'login')
                setError(null)
              }}
              className="text-primary-500 hover:text-primary-600 font-medium"
            >
              {mode === 'login' ? 'Sign up' : 'Sign in'}
            </button>
          </p>
        </Card>

        {/* Terms */}
        <p className="mt-6 text-center text-xs text-surface-400">
          By continuing, you agree to our{' '}
          <Link href="/terms" className="underline hover:text-surface-600">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/privacy" className="underline hover:text-surface-600">
            Privacy Policy
          </Link>
        </p>
      </motion.div>
    </div>
  )
}
