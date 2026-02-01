import { createClient, SupabaseClient } from '@supabase/supabase-js'
import type { User, UserStats, Content, ChatMessage } from '@/types'

// Initialize Supabase client - lazy initialization to support SSG
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

let supabaseInstance: SupabaseClient | null = null

function getSupabase(): SupabaseClient {
  if (!supabaseInstance) {
    if (!supabaseUrl || !supabaseAnonKey) {
      throw new Error('Supabase URL and anon key are required')
    }
    supabaseInstance = createClient(supabaseUrl, supabaseAnonKey)
  }
  return supabaseInstance
}

// Export a proxy that lazily initializes the client
export const supabase = new Proxy({} as SupabaseClient, {
  get(_, prop) {
    // During SSG, return stub functions that return null
    if (typeof window === 'undefined' && (!supabaseUrl || !supabaseAnonKey)) {
      return () => Promise.resolve({ data: null, error: null })
    }
    const client = getSupabase()
    const value = (client as any)[prop]
    if (typeof value === 'function') {
      return value.bind(client)
    }
    return value
  }
})

// ============================================
// AUTH FUNCTIONS
// ============================================

export async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`,
    },
  })
  return { data, error }
}

export async function signInWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  return { data, error }
}

export async function signUpWithEmail(email: string, password: string) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  })
  return { data, error }
}

export async function signOut() {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export async function getCurrentUser() {
  const { data: { user }, error } = await supabase.auth.getUser()
  return { user, error }
}

export async function getSession() {
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}

// ============================================
// PROFILE FUNCTIONS
// ============================================

export async function getProfile(userId: string) {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single()
  return { data, error }
}

export async function updateProfile(userId: string, updates: Partial<User>) {
  const { data, error } = await supabase
    .from('profiles')
    .update(updates)
    .eq('id', userId)
    .select()
    .single()
  return { data, error }
}

export async function getUserStats(userId: string): Promise<{ data: UserStats | null; error: Error | null }> {
  const { data, error } = await supabase
    .from('user_points')
    .select('total_points, level, streak_days')
    .eq('user_id', userId)
    .single()

  if (error) {
    return { data: null, error: new Error(error.message) }
  }

  // Get achievements count
  const { count: achievementsCount } = await supabase
    .from('user_achievements')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId)

  // Get watched content count
  const { count: watchedCount } = await supabase
    .from('watch_history')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId)

  return {
    data: {
      totalPoints: data?.total_points || 0,
      level: data?.level || 1,
      streakDays: data?.streak_days || 0,
      achievementsUnlocked: achievementsCount || 0,
      contentWatched: watchedCount || 0,
    },
    error: null,
  }
}

// ============================================
// MOOD FUNCTIONS
// ============================================

export async function logMood(userId: string, currentMood: string, targetMood: string) {
  const { data, error } = await supabase
    .from('mood_logs')
    .insert({
      user_id: userId,
      current_mood: currentMood,
      target_mood: targetMood,
    })
    .select()
    .single()
  return { data, error }
}

export async function getMoodHistory(userId: string, limit = 10) {
  const { data, error } = await supabase
    .from('mood_logs')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(limit)
  return { data, error }
}

// ============================================
// WATCH QUEUE FUNCTIONS
// ============================================

export async function addToWatchQueue(userId: string, content: Content) {
  const { data, error } = await supabase
    .from('watch_queue')
    .insert({
      user_id: userId,
      content_id: content.id,
      content_type: content.type,
      title: content.title,
      poster_path: content.posterPath,
    })
    .select()
    .single()
  return { data, error }
}

export async function removeFromWatchQueue(userId: string, contentId: string) {
  const { error } = await supabase
    .from('watch_queue')
    .delete()
    .eq('user_id', userId)
    .eq('content_id', contentId)
  return { error }
}

export async function getWatchQueue(userId: string) {
  const { data, error } = await supabase
    .from('watch_queue')
    .select('*')
    .eq('user_id', userId)
    .order('added_at', { ascending: false })
  return { data, error }
}

// ============================================
// FAVORITES FUNCTIONS
// ============================================

export async function addToFavorites(userId: string, content: Content) {
  const { data, error } = await supabase
    .from('favorites')
    .insert({
      user_id: userId,
      content_id: content.id,
      content_type: content.type,
      title: content.title,
      poster_path: content.posterPath,
    })
    .select()
    .single()
  return { data, error }
}

export async function removeFromFavorites(userId: string, contentId: string) {
  const { error } = await supabase
    .from('favorites')
    .delete()
    .eq('user_id', userId)
    .eq('content_id', contentId)
  return { error }
}

export async function getFavorites(userId: string) {
  const { data, error } = await supabase
    .from('favorites')
    .select('*')
    .eq('user_id', userId)
    .order('added_at', { ascending: false })
  return { data, error }
}

// ============================================
// CHAT FUNCTIONS
// ============================================

export async function saveChatMessage(userId: string, message: Omit<ChatMessage, 'id'>) {
  const { data, error } = await supabase
    .from('chat_messages')
    .insert({
      user_id: userId,
      role: message.role,
      content: message.content,
    })
    .select()
    .single()
  return { data, error }
}

export async function getChatHistory(userId: string, limit = 50) {
  const { data, error } = await supabase
    .from('chat_messages')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: true })
    .limit(limit)
  return { data, error }
}

// ============================================
// GAMIFICATION FUNCTIONS
// ============================================

export async function addPoints(userId: string, points: number, reason: string) {
  // First get current points
  const { data: currentData } = await supabase
    .from('user_points')
    .select('total_points, level')
    .eq('user_id', userId)
    .single()

  const currentPoints = currentData?.total_points || 0
  const newTotalPoints = currentPoints + points

  // Calculate new level (every 500 points = 1 level)
  const newLevel = Math.floor(newTotalPoints / 500) + 1

  const { data, error } = await supabase
    .from('user_points')
    .upsert({
      user_id: userId,
      total_points: newTotalPoints,
      level: newLevel,
      last_active: new Date().toISOString(),
    })
    .select()
    .single()

  // Log the points transaction
  if (!error) {
    await supabase.from('points_log').insert({
      user_id: userId,
      points,
      reason,
    })
  }

  return { data, error, leveledUp: newLevel > (currentData?.level || 1) }
}

export async function updateStreak(userId: string) {
  const { data: currentData } = await supabase
    .from('user_points')
    .select('streak_days, last_active')
    .eq('user_id', userId)
    .single()

  const today = new Date().toDateString()
  const lastActive = currentData?.last_active
    ? new Date(currentData.last_active).toDateString()
    : null

  let newStreakDays = 1

  if (lastActive) {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)

    if (lastActive === today) {
      // Already logged in today, keep current streak
      newStreakDays = currentData?.streak_days || 1
    } else if (lastActive === yesterday.toDateString()) {
      // Logged in yesterday, increment streak
      newStreakDays = (currentData?.streak_days || 0) + 1
    }
    // Otherwise, streak resets to 1
  }

  const { data, error } = await supabase
    .from('user_points')
    .upsert({
      user_id: userId,
      streak_days: newStreakDays,
      last_active: new Date().toISOString(),
    })
    .select()
    .single()

  return { data, error, streakDays: newStreakDays }
}

export async function getAchievements(userId: string) {
  const { data, error } = await supabase
    .from('user_achievements')
    .select('*')
    .eq('user_id', userId)
    .order('unlocked_at', { ascending: false })
  return { data, error }
}

export async function unlockAchievement(userId: string, achievementId: string) {
  // Check if already unlocked
  const { data: existing } = await supabase
    .from('user_achievements')
    .select('id')
    .eq('user_id', userId)
    .eq('achievement_id', achievementId)
    .single()

  if (existing) {
    return { data: existing, error: null, isNew: false }
  }

  const { data, error } = await supabase
    .from('user_achievements')
    .insert({
      user_id: userId,
      achievement_id: achievementId,
    })
    .select()
    .single()

  return { data, error, isNew: true }
}

// ============================================
// PREMIUM / SUBSCRIPTION
// ============================================

export async function checkPremiumStatus(userId: string) {
  const { data, error } = await supabase
    .from('profiles')
    .select('is_premium, premium_since, subscription_id')
    .eq('id', userId)
    .single()

  return {
    isPremium: data?.is_premium || false,
    premiumSince: data?.premium_since,
    subscriptionId: data?.subscription_id,
    error,
  }
}

export async function getMrDpUsage(userId: string) {
  const today = new Date().toISOString().split('T')[0]

  const { data, error } = await supabase
    .from('profiles')
    .select('mr_dp_uses, last_mr_dp_reset')
    .eq('id', userId)
    .single()

  // Reset count if it's a new day
  if (data?.last_mr_dp_reset !== today) {
    await supabase
      .from('profiles')
      .update({
        mr_dp_uses: 0,
        last_mr_dp_reset: today,
      })
      .eq('id', userId)

    return { usesRemaining: 5, error: null }
  }

  return {
    usesRemaining: Math.max(0, 5 - (data?.mr_dp_uses || 0)),
    error,
  }
}

export async function incrementMrDpUsage(userId: string) {
  const { data, error } = await supabase.rpc('increment_mr_dp_uses', {
    user_id_param: userId,
  })
  return { data, error }
}
