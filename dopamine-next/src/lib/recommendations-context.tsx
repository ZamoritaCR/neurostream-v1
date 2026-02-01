'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface MovieCard {
  id: string
  type: 'movie' | 'tv'
  title: string
  posterPath?: string
  rating?: number
  releaseDate?: string
  overview?: string
}

interface RecommendationsContextType {
  mrDpPicks: MovieCard[]
  setMrDpPicks: (picks: MovieCard[]) => void
  selectedMovie: MovieCard | null
  setSelectedMovie: (movie: MovieCard | null) => void
  showMovieModal: boolean
  setShowMovieModal: (show: boolean) => void
}

const RecommendationsContext = createContext<RecommendationsContextType | undefined>(undefined)

export function RecommendationsProvider({ children }: { children: ReactNode }) {
  const [mrDpPicks, setMrDpPicks] = useState<MovieCard[]>([])
  const [selectedMovie, setSelectedMovie] = useState<MovieCard | null>(null)
  const [showMovieModal, setShowMovieModal] = useState(false)

  return (
    <RecommendationsContext.Provider
      value={{
        mrDpPicks,
        setMrDpPicks,
        selectedMovie,
        setSelectedMovie,
        showMovieModal,
        setShowMovieModal,
      }}
    >
      {children}
    </RecommendationsContext.Provider>
  )
}

export function useRecommendations() {
  const context = useContext(RecommendationsContext)
  if (context === undefined) {
    throw new Error('useRecommendations must be used within a RecommendationsProvider')
  }
  return context
}
