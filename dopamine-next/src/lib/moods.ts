import type { Mood, MoodId } from '@/types'

// Mood definitions with professional icons (Phosphor icon names)
export const moods: Mood[] = [
  {
    id: 'stressed',
    label: 'Stressed',
    description: 'Mind racing, need to unwind',
    icon: 'Lightning',
    gradient: 'from-red-500 to-orange-400',
    color: '#EF4444',
  },
  {
    id: 'anxious',
    label: 'Anxious',
    description: 'Feeling on edge, need calm',
    icon: 'Waves',
    gradient: 'from-amber-500 to-yellow-400',
    color: '#F59E0B',
  },
  {
    id: 'bored',
    label: 'Bored',
    description: 'Need stimulation and excitement',
    icon: 'Sparkle',
    gradient: 'from-violet-500 to-purple-400',
    color: '#8B5CF6',
  },
  {
    id: 'sad',
    label: 'Sad',
    description: 'Looking for comfort or uplift',
    icon: 'Sun',
    gradient: 'from-blue-500 to-cyan-400',
    color: '#3B82F6',
  },
  {
    id: 'happy',
    label: 'Happy',
    description: 'Feeling good, want to maintain it',
    icon: 'Star',
    gradient: 'from-emerald-500 to-teal-400',
    color: '#10B981',
  },
  {
    id: 'lonely',
    label: 'Lonely',
    description: 'Craving connection and warmth',
    icon: 'Users',
    gradient: 'from-pink-500 to-rose-400',
    color: '#EC4899',
  },
  {
    id: 'angry',
    label: 'Angry',
    description: 'Need to vent or find peace',
    icon: 'Fire',
    gradient: 'from-red-600 to-red-400',
    color: '#DC2626',
  },
  {
    id: 'tired',
    label: 'Tired',
    description: 'Low energy, need gentle content',
    icon: 'Moon',
    gradient: 'from-indigo-500 to-blue-400',
    color: '#6366F1',
  },
  {
    id: 'overwhelmed',
    label: 'Overwhelmed',
    description: 'Too much going on, need simplicity',
    icon: 'Feather',
    gradient: 'from-slate-500 to-gray-400',
    color: '#64748B',
  },
  {
    id: 'restless',
    label: 'Restless',
    description: 'Can\'t sit still, need movement',
    icon: 'ArrowsClockwise',
    gradient: 'from-orange-500 to-amber-400',
    color: '#F97316',
  },
  {
    id: 'focused',
    label: 'Focused',
    description: 'In the zone, want background content',
    icon: 'Target',
    gradient: 'from-cyan-500 to-blue-400',
    color: '#06B6D4',
  },
  {
    id: 'melancholic',
    label: 'Melancholic',
    description: 'Bittersweet mood, reflective',
    icon: 'CloudRain',
    gradient: 'from-purple-500 to-indigo-400',
    color: '#A855F7',
  },
]

// Get mood by ID
export function getMoodById(id: MoodId): Mood | undefined {
  return moods.find((mood) => mood.id === id)
}

// Get gradient style for mood
export function getMoodGradient(id: MoodId): string {
  const mood = getMoodById(id)
  return mood?.gradient || 'from-primary-500 to-secondary-400'
}

// Target moods - what state do you want to achieve
export const targetMoods = [
  { id: 'relaxed', label: 'Relaxed', icon: 'Couch', color: '#3EAFA1' },
  { id: 'energized', label: 'Energized', icon: 'Lightning', color: '#F4B942' },
  { id: 'entertained', label: 'Entertained', icon: 'Television', color: '#6B5CD8' },
  { id: 'inspired', label: 'Inspired', icon: 'Lightbulb', color: '#F97316' },
  { id: 'comforted', label: 'Comforted', icon: 'Heart', color: '#EC4899' },
  { id: 'distracted', label: 'Distracted', icon: 'Brain', color: '#8B5CF6' },
]
