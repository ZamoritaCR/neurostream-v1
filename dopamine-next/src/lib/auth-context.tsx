'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import type { User as SupabaseUser, Session } from '@supabase/supabase-js'
import { supabase, getProfile, checkPremiumStatus, updateStreak, getMrDpUsage } from './supabase'
import type { User, UserStats } from '@/types'

interface AuthContextType {
  user: User | null
  supabaseUser: SupabaseUser | null
  session: Session | null
  isLoading: boolean
  isPremium: boolean
  mrDpUsesRemaining: number
  signInWithGoogle: () => Promise<void>
  signInWithEmail: (email: string, password: string) => Promise<{ error: Error | null }>
  signUpWithEmail: (email: string, password: string) => Promise<{ error: Error | null }>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
  decrementMrDpUses: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [supabaseUser, setSupabaseUser] = useState<SupabaseUser | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isPremium, setIsPremium] = useState(false)
  const [mrDpUsesRemaining, setMrDpUsesRemaining] = useState(5)

  // Fetch user profile and premium status
  const fetchUserData = useCallback(async (supabaseUser: SupabaseUser) => {
    try {
      // Get profile
      const { data: profile } = await getProfile(supabaseUser.id)

      // Check premium status
      const { isPremium: premium } = await checkPremiumStatus(supabaseUser.id)

      // Update streak
      await updateStreak(supabaseUser.id)

      // Get Mr.DP usage
      const { usesRemaining } = await getMrDpUsage(supabaseUser.id)

      setUser({
        id: supabaseUser.id,
        email: supabaseUser.email || '',
        name: profile?.name || supabaseUser.user_metadata?.full_name,
        avatarUrl: profile?.avatar_url || supabaseUser.user_metadata?.avatar_url,
        isPremium: premium,
        premiumSince: profile?.premium_since,
        createdAt: supabaseUser.created_at,
      })
      setIsPremium(premium)
      setMrDpUsesRemaining(premium ? Infinity : usesRemaining)
    } catch (error) {
      console.error('Error fetching user data:', error)
    }
  }, [])

  // Initialize auth state
  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setSupabaseUser(session?.user || null)

      if (session?.user) {
        fetchUserData(session.user)
      }
      setIsLoading(false)
    })

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setSession(session)
        setSupabaseUser(session?.user || null)

        if (session?.user) {
          await fetchUserData(session.user)
        } else {
          setUser(null)
          setIsPremium(false)
          setMrDpUsesRemaining(5)
        }
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [fetchUserData])

  const signInWithGoogle = async () => {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    })
    if (error) throw error
  }

  const signInWithEmail = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { error: error ? new Error(error.message) : null }
  }

  const signUpWithEmail = async (email: string, password: string) => {
    const { error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { error: error ? new Error(error.message) : null }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
    setIsPremium(false)
    setMrDpUsesRemaining(5)
  }

  const refreshUser = async () => {
    if (supabaseUser) {
      await fetchUserData(supabaseUser)
    }
  }

  const decrementMrDpUses = () => {
    if (!isPremium && mrDpUsesRemaining > 0) {
      setMrDpUsesRemaining(prev => prev - 1)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        supabaseUser,
        session,
        isLoading,
        isPremium,
        mrDpUsesRemaining,
        signInWithGoogle,
        signInWithEmail,
        signUpWithEmail,
        signOut,
        refreshUser,
        decrementMrDpUses,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
