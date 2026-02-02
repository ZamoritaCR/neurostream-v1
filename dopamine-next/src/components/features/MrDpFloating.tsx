'use client'

import { useState, useRef, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X,
  Minus,
  ArrowsOutSimple,
  PaperPlaneTilt,
  Sparkle,
  Lightning,
  Heart,
  Moon,
  Sun,
  Fire,
  Crown,
  CaretDown,
  Brain,
  Star,
  Play,
  Headphones,
  Microphone,
  MusicNotes,
  VideoCamera,
  Television,
} from '@phosphor-icons/react'
import Image from 'next/image'
import { cn, haptic } from '@/lib/utils'
import { useAuth } from '@/lib/auth-context'
import { useRecommendations } from '@/lib/recommendations-context'
import { MrDpCharacter, type MrDpExpression } from './MrDpCharacter'
import type { ChatMessage } from '@/types'

// ============================================
// TYPES
// ============================================
type MrDpState = 'minimized' | 'expanded' | 'full'
type AnimationState = 'idle' | 'thinking' | 'speaking' | 'listening' | 'excited'

interface ContextualSuggestion {
  text: string
  icon: React.ReactNode
  action?: () => void
}

// ============================================
// CONTEXTUAL SUGGESTIONS BY PAGE
// ============================================
const getPageSuggestions = (pathname: string): ContextualSuggestion[] => {
  if (pathname === '/home' || pathname === '/') {
    return [
      { text: "What's good tonight?", icon: <Moon size={16} weight="fill" /> },
      { text: 'I need a quick dopamine hit', icon: <Lightning size={16} weight="fill" /> },
      { text: 'Surprise me!', icon: <Sparkle size={16} weight="fill" /> },
    ]
  }
  if (pathname === '/discover') {
    return [
      { text: "Can't decide my mood", icon: <Heart size={16} weight="fill" /> },
      { text: 'Something comforting', icon: <Sun size={16} weight="fill" /> },
      { text: 'I want to feel pumped', icon: <Fire size={16} weight="fill" /> },
    ]
  }
  if (pathname === '/recommendations') {
    return [
      { text: 'Tell me more about this', icon: <Sparkle size={16} weight="fill" /> },
      { text: 'Something similar but different', icon: <Lightning size={16} weight="fill" /> },
      { text: 'Why this for my mood?', icon: <Heart size={16} weight="fill" /> },
    ]
  }
  if (pathname === '/profile') {
    return [
      { text: 'How do I unlock achievements?', icon: <Crown size={16} weight="fill" /> },
      { text: "What's my watching pattern?", icon: <Brain size={16} weight="fill" /> },
      { text: 'Recommend based on history', icon: <Sparkle size={16} weight="fill" /> },
    ]
  }
  return [
    { text: 'What should I watch?', icon: <Sparkle size={16} weight="fill" /> },
    { text: "I'm feeling adventurous", icon: <Lightning size={16} weight="fill" /> },
    { text: 'Help me decide', icon: <Heart size={16} weight="fill" /> },
  ]
}

// ============================================
// GREETING MESSAGES
// ============================================
const getGreeting = (): string => {
  const hour = new Date().getHours()
  if (hour < 6) return "Late night vibes? I've got perfect picks for you"
  if (hour < 12) return "Good morning! Ready for some dopamine?"
  if (hour < 17) return "Afternoon pick-me-up? I'm on it!"
  if (hour < 21) return "Evening entertainment awaits!"
  return "Night owl mode activated!"
}

// ============================================
// MAIN COMPONENT
// ============================================
export function MrDpFloating() {
  const pathname = usePathname()
  const { user, isPremium, mrDpUsesRemaining, decrementMrDpUses } = useAuth()
  const { setMrDpPicks, setSelectedMovie, setShowMovieModal } = useRecommendations()

  const [state, setState] = useState<MrDpState>('minimized')
  const [expression, setExpression] = useState<MrDpExpression>('happy')
  const [animState, setAnimState] = useState<AnimationState>('idle')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [hasUnread, setHasUnread] = useState(false)
  const [showProactiveBubble, setShowProactiveBubble] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const maxFreeChats = 5
  const suggestions = getPageSuggestions(pathname)

  // Update expression based on state
  useEffect(() => {
    if (state === 'minimized') {
      setExpression('sleeping')
      setAnimState('idle')
    } else {
      setExpression('happy')
      setAnimState('idle')
    }
  }, [state])

  // Show proactive bubble after delay on page change
  useEffect(() => {
    setShowProactiveBubble(false)
    const timer = setTimeout(() => {
      if (state === 'minimized') {
        setShowProactiveBubble(true)
      }
    }, 5000)
    return () => clearTimeout(timer)
  }, [pathname, state])

  // Scroll to bottom when messages change
  useEffect(() => {
    if (state === 'full') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, state])

  // Focus input when opening full chat
  useEffect(() => {
    if (state === 'full') {
      setTimeout(() => inputRef.current?.focus(), 300)
    }
  }, [state])

  // Hide chat page nav item when Mr.DP is active
  const isOnChatPage = pathname === '/chat'

  const handleMinimize = () => {
    haptic('light')
    setState('minimized')
    setShowProactiveBubble(false)
    setExpression('sleeping')
    setAnimState('idle')
  }

  const handleExpand = () => {
    haptic('medium')
    setState('expanded')
    setShowProactiveBubble(false)
    setHasUnread(false)
    setExpression('happy')
    setAnimState('excited')
    setTimeout(() => setAnimState('idle'), 1500)
  }

  const handleOpenFull = () => {
    haptic('heavy')
    setState('full')
    setShowProactiveBubble(false)
    setHasUnread(false)
    setExpression('excited')
    setAnimState('excited')
    setTimeout(() => {
      setExpression('happy')
      setAnimState('idle')
    }, 1500)

    // Add greeting if no messages
    if (messages.length === 0) {
      setMessages([
        {
          id: '1',
          role: 'assistant',
          content: `Hey there! ${getGreeting()} What are you in the mood for?`,
          timestamp: new Date(),
        },
      ])
    }
  }

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim()
    if (!messageText) return

    // Check usage limit
    if (!isPremium && mrDpUsesRemaining <= 0) {
      return
    }

    haptic('light')
    setInputValue('')
    setExpression('listening')
    setAnimState('listening')

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])

    // Decrement usage
    decrementMrDpUses()

    // Call OpenAI API
    setIsTyping(true)
    setExpression('thinking')
    setAnimState('thinking')

    try {
      // Build messages for API (without timestamp for API call)
      const apiMessages = [...messages, userMessage].map(m => ({
        role: m.role,
        content: m.content,
      }))

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: apiMessages }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
        metadata: data.movies?.length > 0 ? { recommendations: data.movies } : undefined,
      }

      setMessages(prev => [...prev, assistantMessage])

      // Update Mr.DP picks for main screen display
      if (data.movies?.length > 0) {
        setMrDpPicks(data.movies)
      }

      setExpression('excited')
      setAnimState('speaking')
    } catch (error) {
      console.error('Chat error:', error)
      // Fallback to a helpful error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Oops! I'm having trouble connecting right now. Try again in a moment?",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
      setExpression('sad')
    } finally {
      setIsTyping(false)
      setTimeout(() => {
        setExpression('happy')
        setAnimState('idle')
      }, 2000)
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    if (state === 'expanded') {
      handleOpenFull()
      setTimeout(() => handleSendMessage(suggestion), 500)
    } else {
      handleSendMessage(suggestion)
    }
  }

  // Don't show on chat page (it has its own full implementation)
  if (isOnChatPage) return null

  return (
    <>
      {/* Backdrop for full state */}
      <AnimatePresence>
        {state === 'full' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleMinimize}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:bg-transparent md:backdrop-blur-none"
          />
        )}
      </AnimatePresence>

      {/* Main floating container */}
      <div className="fixed bottom-20 right-4 md:bottom-6 md:right-6 z-50">
        <AnimatePresence mode="wait">
          {/* ============================================ */}
          {/* MINIMIZED STATE - Just the FAB */}
          {/* ============================================ */}
          {state === 'minimized' && (
            <motion.div
              key="minimized"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              className="relative"
            >
              {/* Proactive suggestion bubble */}
              <AnimatePresence>
                {showProactiveBubble && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.9 }}
                    className="absolute bottom-full right-0 mb-3 w-64"
                  >
                    <div className="bg-white dark:bg-dark-card rounded-2xl rounded-br-md shadow-xl p-3 border border-surface-100 dark:border-dark-border">
                      <p className="text-sm text-surface-700 dark:text-surface-200 mb-2">
                        {suggestions[0].text}
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSuggestionClick(suggestions[0].text)}
                          className="flex-1 text-xs font-medium text-primary-500 hover:text-primary-600 py-1"
                        >
                          Yes, help me!
                        </button>
                        <button
                          onClick={() => setShowProactiveBubble(false)}
                          className="text-xs text-surface-400 hover:text-surface-600 py-1"
                        >
                          Maybe later
                        </button>
                      </div>
                    </div>
                    {/* Arrow pointer */}
                    <div className="absolute -bottom-2 right-6 w-4 h-4 bg-white dark:bg-dark-card border-r border-b border-surface-100 dark:border-dark-border transform rotate-45" />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* FAB Button - Mr.DP Character */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleExpand}
                className="relative"
              >
                <MrDpCharacter
                  expression={expression}
                  size="lg"
                  animated={true}
                  animationState={animState}
                />

                {/* Unread indicator */}
                {hasUnread && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center z-20">
                    <span className="text-[10px] text-white font-bold">1</span>
                  </span>
                )}
              </motion.button>
            </motion.div>
          )}

          {/* ============================================ */}
          {/* EXPANDED STATE - Bubble with suggestions */}
          {/* ============================================ */}
          {state === 'expanded' && (
            <motion.div
              key="expanded"
              initial={{ scale: 0.8, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0, y: 20 }}
              className="w-80 bg-white dark:bg-dark-card rounded-3xl shadow-2xl overflow-hidden border border-surface-100 dark:border-dark-border"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-surface-100 dark:border-dark-border">
                <div className="flex items-center gap-3">
                  <MrDpCharacter expression={expression} size="sm" animated animationState={animState} />
                  <div>
                    <h3 className="font-semibold text-surface-900 dark:text-white text-sm">
                      Mr.DP
                    </h3>
                    <p className="text-xs text-surface-500">Your dopamine curator</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={handleOpenFull}
                    className="p-2 hover:bg-surface-100 dark:hover:bg-dark-hover rounded-full transition-colors"
                    title="Open full chat"
                  >
                    <ArrowsOutSimple size={18} className="text-surface-500" />
                  </button>
                  <button
                    onClick={handleMinimize}
                    className="p-2 hover:bg-surface-100 dark:hover:bg-dark-hover rounded-full transition-colors"
                    title="Minimize"
                  >
                    <Minus size={18} className="text-surface-500" />
                  </button>
                </div>
              </div>

              {/* Greeting */}
              <div className="p-4">
                <p className="text-sm text-surface-700 dark:text-surface-200 mb-4">
                  {getGreeting()} What can I help you find?
                </p>

                {/* Quick suggestions */}
                <div className="space-y-2">
                  {suggestions.map((suggestion, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => handleSuggestionClick(suggestion.text)}
                      className={cn(
                        'w-full flex items-center gap-3 p-3 rounded-xl',
                        'bg-surface-50 dark:bg-dark-hover',
                        'hover:bg-primary-50 dark:hover:bg-primary-500/10',
                        'text-left transition-colors',
                        'group'
                      )}
                    >
                      <span className="text-surface-400 group-hover:text-primary-500 transition-colors">
                        {suggestion.icon}
                      </span>
                      <span className="text-sm text-surface-700 dark:text-surface-200 group-hover:text-primary-600 dark:group-hover:text-primary-400">
                        {suggestion.text}
                      </span>
                    </motion.button>
                  ))}
                </div>

                {/* Open full chat CTA */}
                <button
                  onClick={handleOpenFull}
                  className="w-full mt-4 py-2 text-sm text-primary-500 hover:text-primary-600 font-medium"
                >
                  Open full chat
                </button>
              </div>

              {/* Usage indicator (free users) */}
              {!isPremium && (
                <div className="px-4 pb-4">
                  <div className="flex items-center justify-between text-xs text-surface-500">
                    <span>{mrDpUsesRemaining} / {maxFreeChats} chats left today</span>
                    <button className="flex items-center gap-1 text-amber-500 hover:text-amber-600 font-medium">
                      <Crown size={12} weight="fill" />
                      Upgrade
                    </button>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* ============================================ */}
          {/* FULL STATE - Complete chat interface */}
          {/* ============================================ */}
          {state === 'full' && (
            <motion.div
              key="full"
              initial={{ y: '100%', opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: '100%', opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className={cn(
                'fixed inset-x-0 bottom-0 md:relative md:inset-auto',
                'md:w-96',
                'bg-white dark:bg-dark-bg md:rounded-3xl shadow-2xl overflow-hidden',
                'md:border md:border-surface-100 md:dark:border-dark-border',
                'flex flex-col',
                'h-[85vh] md:h-[600px]'
              )}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-surface-100 dark:border-dark-border bg-white dark:bg-dark-bg">
                <div className="flex items-center gap-3">
                  <MrDpCharacter expression={expression} size="md" animated animationState={animState} />
                  <div>
                    <h3 className="font-semibold text-surface-900 dark:text-white">
                      Mr.DP
                    </h3>
                    <p className="text-xs text-surface-500">Your dopamine curator</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setState('expanded')}
                    className="p-2 hover:bg-surface-100 dark:hover:bg-dark-hover rounded-full transition-colors"
                    title="Collapse"
                  >
                    <CaretDown size={20} className="text-surface-500" />
                  </button>
                  <button
                    onClick={handleMinimize}
                    className="p-2 hover:bg-surface-100 dark:hover:bg-dark-hover rounded-full transition-colors"
                    title="Close"
                  >
                    <X size={20} className="text-surface-500" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                  <ChatBubble
                    key={message.id}
                    message={message}
                    isLatest={index === messages.length - 1}
                    expression={expression}
                    animState={animState}
                    onMovieClick={(movie) => {
                      setSelectedMovie(movie)
                      setShowMovieModal(true)
                    }}
                  />
                ))}

                {/* Typing indicator */}
                <AnimatePresence>
                  {isTyping && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="flex items-end gap-2"
                    >
                      <MrDpCharacter expression={expression} size="sm" animated animationState={animState} />
                      <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-surface-100 dark:bg-dark-card">
                        <div className="flex gap-1">
                          {[0, 1, 2].map((i) => (
                            <motion.div
                              key={i}
                              className="w-2 h-2 rounded-full bg-primary-500"
                              animate={{ y: [0, -6, 0] }}
                              transition={{
                                duration: 0.6,
                                repeat: Infinity,
                                delay: i * 0.15,
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <div ref={messagesEndRef} />
              </div>

              {/* Quick suggestions (only when few messages) */}
              {messages.length <= 2 && (
                <div className="px-4 pb-2">
                  <div className="flex flex-wrap gap-2">
                    {suggestions.slice(0, 2).map((suggestion, index) => (
                      <motion.button
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        onClick={() => handleSendMessage(suggestion.text)}
                        className="px-3 py-1.5 rounded-full bg-surface-100 dark:bg-dark-card text-sm text-surface-600 dark:text-surface-300 hover:bg-primary-50 dark:hover:bg-primary-500/10 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                      >
                        {suggestion.text}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}

              {/* Usage warning */}
              {!isPremium && mrDpUsesRemaining <= 2 && mrDpUsesRemaining > 0 && (
                <div className="px-4 pb-2">
                  <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-500/10 text-center">
                    <span className="text-xs text-amber-600 dark:text-amber-400">
                      {mrDpUsesRemaining} chat{mrDpUsesRemaining === 1 ? '' : 's'} left today
                    </span>
                  </div>
                </div>
              )}

              {/* Input */}
              <div className="p-4 border-t border-surface-100 dark:border-dark-border bg-white dark:bg-dark-bg pb-safe">
                <div className="flex items-center gap-2">
                  <div className="flex-1 relative">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          handleSendMessage()
                        }
                      }}
                      placeholder={
                        !isPremium && mrDpUsesRemaining <= 0
                          ? 'Upgrade for unlimited chats...'
                          : "What's on your mind?"
                      }
                      disabled={!isPremium && mrDpUsesRemaining <= 0}
                      className={cn(
                        'w-full px-4 py-3 pr-12 rounded-2xl',
                        'bg-surface-100 dark:bg-dark-card',
                        'border border-transparent focus:border-primary-500',
                        'text-surface-900 dark:text-white',
                        'placeholder:text-surface-400',
                        'transition-all duration-200',
                        'focus:outline-none focus:ring-2 focus:ring-primary-500/20',
                        'disabled:opacity-50 disabled:cursor-not-allowed'
                      )}
                    />
                    <motion.button
                      whileTap={{ scale: 0.9 }}
                      onClick={() => handleSendMessage()}
                      disabled={!inputValue.trim() || (!isPremium && mrDpUsesRemaining <= 0)}
                      className={cn(
                        'absolute right-2 top-1/2 -translate-y-1/2',
                        'w-8 h-8 rounded-full',
                        'flex items-center justify-center',
                        'transition-all duration-200',
                        inputValue.trim()
                          ? 'bg-primary-500 text-white'
                          : 'bg-surface-200 dark:bg-dark-hover text-surface-400',
                        'disabled:opacity-50 disabled:cursor-not-allowed'
                      )}
                    >
                      <PaperPlaneTilt size={18} weight="fill" />
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  )
}

// ============================================
// CHAT BUBBLE COMPONENT
// ============================================
interface ChatBubbleProps {
  message: ChatMessage
  isLatest: boolean
  expression: MrDpExpression
  animState: AnimationState
  onMovieClick?: (movie: any) => void
}

// Get content type icon and label
function getContentTypeInfo(type: string): { icon: React.ReactNode; label: string; color: string } {
  switch (type) {
    case 'tv':
      return { icon: <Television size={8} weight="fill" />, label: 'TV', color: 'bg-blue-500' }
    case 'podcast':
      return { icon: <Microphone size={8} weight="fill" />, label: 'Podcast', color: 'bg-purple-500' }
    case 'audiobook':
      return { icon: <Headphones size={8} weight="fill" />, label: 'Audiobook', color: 'bg-orange-500' }
    case 'music':
      return { icon: <MusicNotes size={8} weight="fill" />, label: 'Music', color: 'bg-green-500' }
    default:
      return { icon: <VideoCamera size={8} weight="fill" />, label: 'Movie', color: 'bg-primary-500' }
  }
}

// Get poster URL based on content type
function getPosterUrl(item: any): string | null {
  // iTunes/Apple content returns full URLs
  if (item.type === 'podcast' || item.type === 'audiobook' || item.type === 'music') {
    return item.posterPath || null
  }
  // TMDB content returns relative paths
  if (item.posterPath) {
    return `https://image.tmdb.org/t/p/w200${item.posterPath}`
  }
  return null
}

// Handle content click based on type - opens streaming service
function handleContentClick(item: any, onMovieClick?: (movie: any) => void) {
  haptic('light')

  // For movies and TV, open the modal (which shows streaming providers)
  if (item.type === 'movie' || item.type === 'tv') {
    if (onMovieClick) {
      onMovieClick(item)
    }
    return
  }

  // Use platform links from API if available, otherwise fallback to search URLs
  const searchQuery = encodeURIComponent(item.title + (item.artist ? ' ' + item.artist : ''))

  // For podcasts - prefer Spotify, fallback to Apple Podcasts
  if (item.type === 'podcast') {
    const url = item.platforms?.spotify ||
                item.platforms?.applePodcasts ||
                `https://open.spotify.com/search/${searchQuery}/shows`
    window.open(url, '_blank')
    return
  }

  // For audiobooks - prefer Audible (most popular), fallback to Apple Books
  if (item.type === 'audiobook') {
    const url = item.platforms?.audible ||
                item.platforms?.appleBooks ||
                `https://www.audible.com/search?keywords=${searchQuery}`
    window.open(url, '_blank')
    return
  }

  // For music - prefer Spotify (most popular), fallback to Apple Music
  if (item.type === 'music') {
    const url = item.platforms?.spotify ||
                item.platforms?.appleMusic ||
                `https://open.spotify.com/search/${searchQuery}`
    window.open(url, '_blank')
    return
  }
}

function ChatBubble({ message, isLatest, expression, animState, onMovieClick }: ChatBubbleProps) {
  const isUser = message.role === 'user'
  const recommendations = message.metadata?.recommendations

  return (
    <motion.div
      initial={isLatest ? { opacity: 0, y: 10 } : false}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'flex items-end gap-2',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {!isUser && <MrDpCharacter expression={expression} size="sm" animated={false} />}

      <div className="max-w-[85%] space-y-2">
        <div
          className={cn(
            'px-4 py-3 rounded-2xl',
            isUser
              ? 'bg-primary-500 text-white rounded-br-md'
              : 'bg-surface-100 dark:bg-dark-card text-surface-900 dark:text-white rounded-bl-md'
          )}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* Content recommendations cards (movies, TV, podcasts, audiobooks, music) */}
        {recommendations && recommendations.length > 0 && (
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {recommendations.map((item: any) => {
              const typeInfo = getContentTypeInfo(item.type)
              const posterUrl = getPosterUrl(item)
              const isAudioContent = ['podcast', 'audiobook', 'music'].includes(item.type)

              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex-shrink-0 w-28 rounded-xl overflow-hidden bg-surface-100 dark:bg-dark-card border border-surface-200 dark:border-dark-border hover:border-primary-500 transition-colors cursor-pointer group"
                  onClick={() => handleContentClick(item, onMovieClick)}
                >
                  <div className={cn("relative", isAudioContent ? "aspect-square" : "aspect-[2/3]")}>
                    {posterUrl ? (
                      <Image
                        src={posterUrl}
                        alt={item.title}
                        fill
                        className="object-cover"
                        sizes="112px"
                        unoptimized={isAudioContent} // iTunes URLs don't work with Next.js image optimization
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-primary-500 to-secondary-400 flex items-center justify-center">
                        {isAudioContent ? (
                          <Headphones size={24} weight="fill" className="text-white/50" />
                        ) : (
                          <Play size={24} weight="fill" className="text-white/50" />
                        )}
                      </div>
                    )}
                    {/* Hover overlay */}
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      {isAudioContent ? (
                        <Headphones size={24} weight="fill" className="text-white" />
                      ) : (
                        <Play size={24} weight="fill" className="text-white" />
                      )}
                    </div>
                    {/* Rating badge (for movies/TV) */}
                    {item.rating && !isAudioContent && (
                      <div className="absolute top-1 right-1">
                        <span className="flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-black/60 text-white">
                          <Star size={8} weight="fill" className="text-amber-400" />
                          {item.rating.toFixed(1)}
                        </span>
                      </div>
                    )}
                    {/* Type badge */}
                    <div className="absolute top-1 left-1">
                      <span className={cn(
                        "flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium text-white",
                        typeInfo.color
                      )}>
                        {typeInfo.icon}
                        {typeInfo.label}
                      </span>
                    </div>
                  </div>
                  <div className="p-2">
                    <h4 className="text-xs font-medium text-surface-900 dark:text-white line-clamp-2 leading-tight">
                      {item.title}
                    </h4>
                    {/* Show artist for audio content */}
                    {item.artist && (
                      <p className="text-[10px] text-surface-500 dark:text-surface-400 line-clamp-1 mt-0.5">
                        {item.artist}
                      </p>
                    )}
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}
      </div>
    </motion.div>
  )
}

export default MrDpFloating
