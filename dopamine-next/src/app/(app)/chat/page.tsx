'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  PaperPlaneTilt,
  Crown,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button } from '@/components/ui'
import { MrDpCharacter, type MrDpExpression } from '@/components/features/MrDpCharacter'
import type { ChatMessage } from '@/types'

type AnimationState = 'idle' | 'thinking' | 'speaking' | 'listening' | 'excited'

// Quick suggestions
const quickSuggestions = [
  "I'm bored, what should I watch?",
  "Something to help me relax",
  "I need a good laugh",
  "Recommend something for date night",
  "What's trending right now?",
]

// Initial messages from Mr.DP
const initialMessages: ChatMessage[] = [
  {
    id: '1',
    role: 'assistant',
    content: "Hey there! I'm Mr.DP, your personal dopamine curator. 🧠✨",
    timestamp: new Date(Date.now() - 60000),
  },
  {
    id: '2',
    role: 'assistant',
    content: "Tell me how you're feeling or what kind of vibe you're after, and I'll find the perfect content to match your mood!",
    timestamp: new Date(Date.now() - 30000),
  },
]

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [expression, setExpression] = useState<MrDpExpression>('happy')
  const [animState, setAnimState] = useState<AnimationState>('idle')
  const [isPremium, setIsPremium] = useState(false)
  const [chatCount, setChatCount] = useState(3)
  const maxFreeChats = 5

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim()
    if (!messageText) return

    // Check usage limit
    if (!isPremium && chatCount >= maxFreeChats) {
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

    // Call OpenAI API
    setIsTyping(true)
    setExpression('thinking')
    setAnimState('thinking')

    try {
      // Build messages for API (without timestamp)
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
      }

      setMessages(prev => [...prev, assistantMessage])
      setExpression('excited')
      setAnimState('speaking')
      setChatCount(prev => prev + 1)
    } catch (error) {
      console.error('Chat error:', error)
      // Show error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Hmm, I'm having a moment. Could you try that again?",
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

  const handleQuickSuggestion = (suggestion: string) => {
    haptic('medium')
    handleSendMessage(suggestion)
  }

  const remainingChats = maxFreeChats - chatCount
  const showUpgradePrompt = !isPremium && remainingChats <= 2

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] md:h-[calc(100vh-6rem)]">
      {/* Chat header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-surface-100 dark:border-dark-border bg-white/80 dark:bg-dark-bg/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <MrDpCharacter expression={expression} size="md" animated animationState={animState} />
          <div>
            <h1 className="font-semibold text-surface-900 dark:text-white">Mr.DP</h1>
            <p className="text-xs text-surface-500">Your dopamine curator</p>
          </div>
        </div>

        {/* Usage indicator */}
        {!isPremium && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-surface-500">
              {remainingChats} / {maxFreeChats} chats left
            </span>
            <button
              onClick={() => setIsPremium(true)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-medium"
            >
              <Crown size={14} weight="fill" />
              Upgrade
            </button>
          </div>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin">
        {messages.map((message, index) => (
          <ChatBubble
            key={message.id}
            message={message}
            isLatest={index === messages.length - 1}
            expression={expression}
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
                      animate={{
                        y: [0, -6, 0],
                      }}
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

      {/* Quick suggestions */}
      {messages.length <= 3 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-surface-500 mb-2">Quick suggestions:</p>
          <div className="flex flex-wrap gap-2">
            {quickSuggestions.slice(0, 3).map((suggestion, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => handleQuickSuggestion(suggestion)}
                className="px-3 py-1.5 rounded-full bg-surface-100 dark:bg-dark-card text-sm text-surface-600 dark:text-surface-300 hover:bg-primary-50 dark:hover:bg-primary-500/10 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                {suggestion}
              </motion.button>
            ))}
          </div>
        </div>
      )}

      {/* Upgrade prompt */}
      <AnimatePresence>
        {showUpgradePrompt && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="px-4 pb-2"
          >
            <div className="p-3 rounded-xl bg-gradient-to-r from-primary-500/10 to-secondary-400/10 border border-primary-200 dark:border-primary-500/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Crown size={20} weight="fill" className="text-amber-500" />
                  <span className="text-sm font-medium text-surface-900 dark:text-white">
                    {remainingChats === 0 ? 'Out of free chats!' : `Only ${remainingChats} chat${remainingChats === 1 ? '' : 's'} left`}
                  </span>
                </div>
                <Button size="sm" onClick={() => setIsPremium(true)}>
                  Go Premium
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area */}
      <div className="px-4 pb-4 pt-2 border-t border-surface-100 dark:border-dark-border bg-white dark:bg-dark-bg">
        <div className="flex items-end gap-2">
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
                !isPremium && chatCount >= maxFreeChats
                  ? 'Upgrade to continue chatting...'
                  : "What's on your mind?"
              }
              disabled={!isPremium && chatCount >= maxFreeChats}
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

            {/* Send button */}
            <motion.button
              whileTap={{ scale: 0.9 }}
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || (!isPremium && chatCount >= maxFreeChats)}
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
    </div>
  )
}

// Chat Bubble Component
interface ChatBubbleProps {
  message: ChatMessage
  isLatest: boolean
  expression: MrDpExpression
}

function ChatBubble({ message, isLatest, expression }: ChatBubbleProps) {
  const isUser = message.role === 'user'

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

      <div
        className={cn(
          'max-w-[80%] px-4 py-3 rounded-2xl',
          isUser
            ? 'bg-primary-500 text-white rounded-br-md'
            : 'bg-surface-100 dark:bg-dark-card text-surface-900 dark:text-white rounded-bl-md'
        )}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>
      </div>
    </motion.div>
  )
}
