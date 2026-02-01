'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

// ============================================
// TYPES
// ============================================
export type MrDpExpression =
  | 'happy'
  | 'thinking'
  | 'excited'
  | 'listening'
  | 'sleeping'
  | 'sad'
  | 'love'
  | 'surprised'
  | 'wink'
  | 'confused'
  | 'cool'
  | 'focused'

interface ExpressionConfig {
  leftEye: string
  rightEye: string
  mouth: 'smile' | 'sleeping' | 'hmm' | 'big_smile' | 'open' | 'sad' | 'wow' | 'determined'
  blush: boolean
  glowColor: string
}

interface MrDpCharacterProps {
  expression?: MrDpExpression
  size?: 'sm' | 'md' | 'lg' | 'xl'
  animated?: boolean
  animationState?: 'idle' | 'thinking' | 'speaking' | 'listening' | 'excited'
  className?: string
}

// ============================================
// EXPRESSION CONFIGURATIONS
// ============================================
const expressions: Record<MrDpExpression, ExpressionConfig> = {
  happy: { leftEye: '◠', rightEye: '◠', mouth: 'smile', blush: true, glowColor: '#8b5cf6' },
  sleeping: { leftEye: '−', rightEye: '−', mouth: 'sleeping', blush: false, glowColor: '#6366f1' },
  thinking: { leftEye: '•', rightEye: '◐', mouth: 'hmm', blush: false, glowColor: '#8b5cf6' },
  excited: { leftEye: '★', rightEye: '★', mouth: 'big_smile', blush: true, glowColor: '#a855f7' },
  listening: { leftEye: '◉', rightEye: '◉', mouth: 'open', blush: false, glowColor: '#06b6d4' },
  sad: { leftEye: '◡', rightEye: '◡', mouth: 'sad', blush: false, glowColor: '#6366f1' },
  love: { leftEye: '♥', rightEye: '♥', mouth: 'smile', blush: true, glowColor: '#ec4899' },
  surprised: { leftEye: '◯', rightEye: '◯', mouth: 'wow', blush: false, glowColor: '#f59e0b' },
  wink: { leftEye: '◠', rightEye: '−', mouth: 'smile', blush: true, glowColor: '#8b5cf6' },
  confused: { leftEye: '◔', rightEye: '◕', mouth: 'hmm', blush: false, glowColor: '#8b5cf6' },
  cool: { leftEye: '▬', rightEye: '▬', mouth: 'smile', blush: false, glowColor: '#10b981' },
  focused: { leftEye: '●', rightEye: '●', mouth: 'determined', blush: false, glowColor: '#06b6d4' },
}

// ============================================
// MOUTH PATHS
// ============================================
const mouthPaths: Record<string, React.ReactNode> = {
  smile: <path d="M24 38 Q32 46 40 38" stroke="#ff6b9d" strokeWidth="3" fill="none" strokeLinecap="round" />,
  sleeping: <path d="M26 40 L38 40" stroke="#ff6b9d" strokeWidth="2" fill="none" strokeLinecap="round" />,
  hmm: <path d="M26 40 L38 38" stroke="#ff6b9d" strokeWidth="2.5" fill="none" strokeLinecap="round" />,
  big_smile: <path d="M22 36 Q32 48 42 36" stroke="#ff6b9d" strokeWidth="3" fill="none" strokeLinecap="round" />,
  open: <ellipse cx="32" cy="40" rx="6" ry="4" fill="#ff6b9d" />,
  sad: <path d="M24 42 Q32 36 40 42" stroke="#ff6b9d" strokeWidth="3" fill="none" strokeLinecap="round" />,
  wow: <ellipse cx="32" cy="40" rx="5" ry="6" fill="#ff6b9d" />,
  determined: <path d="M26 40 L38 40" stroke="#ff6b9d" strokeWidth="3" fill="none" strokeLinecap="round" />,
}

// ============================================
// ANIMATION VARIANTS
// ============================================
const containerVariants = {
  idle: {
    y: [0, -6, -3, -8, -4, -10, 0],
    rotate: [0, -2, 0, 2, 0, -1, 0],
    transition: { duration: 6, repeat: Infinity, ease: 'easeInOut' },
  },
  thinking: {
    rotate: [-8, 8, -8],
    y: [-5, -3, -5],
    transition: { duration: 1, repeat: Infinity, ease: 'easeInOut' },
  },
  speaking: {
    scale: [1, 1.08, 1],
    transition: { duration: 0.5, repeat: Infinity, ease: 'easeInOut' },
  },
  listening: {
    scale: [1, 1.05, 1],
    rotate: [-3, 3, -3],
    transition: { duration: 0.8, repeat: Infinity, ease: 'easeInOut' },
  },
  excited: {
    y: [0, -15, 0],
    scale: [1, 1.1, 1],
    transition: { duration: 0.4, repeat: Infinity, ease: 'easeInOut' },
  },
}

const glowVariants = {
  idle: {
    boxShadow: [
      '0 10px 40px rgba(139,92,246,0.7), 0 0 80px rgba(139,92,246,0.4)',
      '0 15px 60px rgba(139,92,246,0.9), 0 0 120px rgba(139,92,246,0.6)',
      '0 10px 40px rgba(139,92,246,0.7), 0 0 80px rgba(139,92,246,0.4)',
    ],
    transition: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
  },
  thinking: {
    boxShadow: [
      '0 10px 40px rgba(6,182,212,0.7), 0 0 80px rgba(6,182,212,0.4)',
      '0 15px 60px rgba(6,182,212,0.9), 0 0 120px rgba(6,182,212,0.6)',
      '0 10px 40px rgba(6,182,212,0.7), 0 0 80px rgba(6,182,212,0.4)',
    ],
    transition: { duration: 1.5, repeat: Infinity, ease: 'easeInOut' },
  },
  speaking: {
    boxShadow: [
      '0 10px 40px rgba(168,85,247,0.7), 0 0 80px rgba(168,85,247,0.4)',
      '0 15px 60px rgba(236,72,153,0.9), 0 0 120px rgba(236,72,153,0.6)',
      '0 10px 40px rgba(168,85,247,0.7), 0 0 80px rgba(168,85,247,0.4)',
    ],
    transition: { duration: 0.8, repeat: Infinity, ease: 'easeInOut' },
  },
  listening: {
    boxShadow: [
      '0 10px 40px rgba(6,182,212,0.7), 0 0 80px rgba(6,182,212,0.4)',
      '0 15px 60px rgba(6,182,212,0.9), 0 0 120px rgba(6,182,212,0.6)',
      '0 10px 40px rgba(6,182,212,0.7), 0 0 80px rgba(6,182,212,0.4)',
    ],
    transition: { duration: 1.2, repeat: Infinity, ease: 'easeInOut' },
  },
  excited: {
    boxShadow: [
      '0 10px 40px rgba(168,85,247,0.8), 0 0 100px rgba(168,85,247,0.5)',
      '0 20px 80px rgba(236,72,153,1), 0 0 150px rgba(236,72,153,0.7)',
      '0 10px 40px rgba(168,85,247,0.8), 0 0 100px rgba(168,85,247,0.5)',
    ],
    transition: { duration: 0.4, repeat: Infinity, ease: 'easeInOut' },
  },
}

// ============================================
// MAIN COMPONENT
// ============================================
export function MrDpCharacter({
  expression = 'happy',
  size = 'md',
  animated = true,
  animationState = 'idle',
  className,
}: MrDpCharacterProps) {
  const config = expressions[expression]
  const id = `mrdp-${Math.random().toString(36).substr(2, 9)}`

  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-14 h-14',
    lg: 'w-20 h-20',
    xl: 'w-28 h-28',
  }

  return (
    <motion.div
      className={cn(
        sizeClasses[size],
        'rounded-full relative',
        'bg-gradient-to-br from-[#1a1a2e] to-[#16213e]',
        'border-4 border-primary-500/60',
        'flex items-center justify-center p-2',
        className
      )}
      animate={animated ? containerVariants[animationState] : undefined}
      style={{
        boxShadow: '0 10px 40px rgba(139,92,246,0.7), 0 0 80px rgba(139,92,246,0.4)',
      }}
    >
      {/* Glow effect */}
      {animated && (
        <motion.div
          className="absolute inset-0 rounded-full"
          animate={glowVariants[animationState]}
        />
      )}

      {/* SVG Character */}
      <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" className="w-full h-full relative z-10">
        <defs>
          {/* Neuron body gradient */}
          <linearGradient id={`${id}-body`} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a78bfa" />
            <stop offset="50%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#7c3aed" />
          </linearGradient>
          {/* Axon gradient */}
          <linearGradient id={`${id}-axon`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>

        {/* Dendrites (top branches) */}
        <g>
          {/* Left dendrite */}
          <path
            d="M32 12 Q28 4 20 2"
            stroke={`url(#${id}-axon)`}
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="20" cy="2" r="3" fill="#06b6d4" />

          {/* Right dendrite */}
          <path
            d="M32 12 Q36 4 44 2"
            stroke={`url(#${id}-axon)`}
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="44" cy="2" r="3" fill="#06b6d4" />

          {/* Middle dendrite */}
          <path
            d="M32 12 Q32 6 32 0"
            stroke={`url(#${id}-axon)`}
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="32" cy="0" r="2.5" fill="#10b981" />

          {/* Left side dendrite */}
          <path
            d="M12 28 Q4 24 0 20"
            stroke={`url(#${id}-axon)`}
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="0" cy="20" r="2.5" fill="#f59e0b" />

          {/* Right side dendrite */}
          <path
            d="M52 28 Q60 24 64 20"
            stroke={`url(#${id}-axon)`}
            strokeWidth="2.5"
            fill="none"
            strokeLinecap="round"
          />
          <circle cx="64" cy="20" r="2.5" fill="#f59e0b" />
        </g>

        {/* Axon (bottom tail) */}
        <path
          d="M32 52 Q32 58 28 62"
          stroke={`url(#${id}-axon)`}
          strokeWidth="4"
          fill="none"
          strokeLinecap="round"
        />
        <circle cx="28" cy="62" r="3" fill="#10b981" />

        {/* Main neuron body */}
        <ellipse cx="32" cy="32" rx="22" ry="20" fill={`url(#${id}-body)`} />

        {/* Highlight shine */}
        <ellipse cx="26" cy="24" rx="8" ry="5" fill="white" opacity="0.3" />

        {/* Eyes */}
        <text
          x="22"
          y="32"
          fontSize="10"
          fill="white"
          textAnchor="middle"
          fontFamily="Arial, sans-serif"
        >
          {config.leftEye}
        </text>
        <text
          x="42"
          y="32"
          fontSize="10"
          fill="white"
          textAnchor="middle"
          fontFamily="Arial, sans-serif"
        >
          {config.rightEye}
        </text>

        {/* Eyebrows */}
        <path d="M18 24 Q22 22 26 24" stroke="white" strokeWidth="1.5" fill="none" opacity="0.8" />
        <path d="M38 24 Q42 22 46 24" stroke="white" strokeWidth="1.5" fill="none" opacity="0.8" />

        {/* Mouth */}
        {mouthPaths[config.mouth]}

        {/* Blush */}
        {config.blush && (
          <>
            <circle cx="18" cy="36" r="5" fill="#ff6b9d" opacity="0.3" />
            <circle cx="46" cy="36" r="5" fill="#ff6b9d" opacity="0.3" />
          </>
        )}

        {/* Sparkles */}
        <text x="54" y="14" fontSize="8" fill="#ffd700" opacity="0.8">
          ✦
        </text>
        <text x="8" y="18" fontSize="6" fill="#ffd700" opacity="0.6">
          ✦
        </text>
      </svg>

      {/* Online badge */}
      <motion.div
        className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-[#1a1a2e]"
        animate={{
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
    </motion.div>
  )
}

export default MrDpCharacter
