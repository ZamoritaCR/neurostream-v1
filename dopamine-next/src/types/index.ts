// ============================================
// MOOD TYPES
// ============================================
export type MoodId =
  | 'stressed'
  | 'anxious'
  | 'bored'
  | 'sad'
  | 'happy'
  | 'lonely'
  | 'angry'
  | 'tired'
  | 'overwhelmed'
  | 'restless'
  | 'focused'
  | 'melancholic'

export interface Mood {
  id: MoodId
  label: string
  description: string
  icon: string // Phosphor icon name
  gradient: string // Tailwind gradient classes
  color: string // Primary color for the mood
}

// ============================================
// CONTENT TYPES
// ============================================
export type ContentType = 'movie' | 'tv' | 'music' | 'podcast' | 'audiobook' | 'short'

export interface Content {
  id: string
  type: ContentType
  title: string
  description?: string
  posterPath?: string
  backdropPath?: string
  releaseDate?: string
  rating?: number
  runtime?: number
  genres?: string[]
  platforms?: Platform[]
  trailerUrl?: string
}

export interface Platform {
  id: string
  name: string
  logo: string
  url?: string
}

export interface Movie extends Content {
  type: 'movie'
  director?: string
  cast?: string[]
}

export interface TVShow extends Content {
  type: 'tv'
  seasons?: number
  episodeRuntime?: number
}

export interface Music extends Content {
  type: 'music'
  artist?: string
  album?: string
  spotifyUrl?: string
  appleUrl?: string
}

// ============================================
// USER TYPES
// ============================================
export interface User {
  id: string
  email: string
  name?: string
  avatarUrl?: string
  isPremium: boolean
  premiumSince?: string
  createdAt: string
  preferences?: UserPreferences
}

export interface UserPreferences {
  preferredPlatforms?: string[]
  preferredGenres?: string[]
  contentRatings?: string[]
  language?: string
}

// ============================================
// CHAT TYPES
// ============================================
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  metadata?: {
    mood?: MoodId
    recommendations?: Content[]
  }
}

export interface ChatSession {
  id: string
  userId: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

// ============================================
// UI TYPES
// ============================================
export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface Toast {
  id: string
  type: ToastType
  title: string
  description?: string
  duration?: number
}

export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
}

// ============================================
// API TYPES
// ============================================
export interface APIResponse<T> {
  data?: T
  error?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  page: number
  totalPages: number
  totalItems: number
}

// ============================================
// ANALYTICS TYPES
// ============================================
export interface AnalyticsEvent {
  name: string
  properties?: Record<string, string | number | boolean>
}

// ============================================
// GAMIFICATION TYPES
// ============================================
export interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  unlockedAt?: Date
  progress?: number
  maxProgress?: number
}

export interface UserStats {
  totalPoints: number
  level: number
  streakDays: number
  achievementsUnlocked: number
  contentWatched: number
}
