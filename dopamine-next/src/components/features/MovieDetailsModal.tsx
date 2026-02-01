'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { motion } from 'framer-motion'
import {
  X,
  Star,
  Clock,
  Calendar,
  Play,
  Heart,
  Plus,
  ArrowSquareOut,
  Television,
  VideoCamera,
} from '@phosphor-icons/react'
import { cn, haptic } from '@/lib/utils'
import { Button } from '@/components/ui'

interface StreamingProvider {
  provider_id: number
  provider_name: string
  logo_path: string
}

interface MovieDetails {
  id: string
  type: 'movie' | 'tv'
  title: string
  posterPath?: string
  backdropPath?: string
  rating?: number
  releaseDate?: string
  overview?: string
  runtime?: number
  genres?: string[]
}

interface MovieDetailsModalProps {
  movie: MovieDetails | null
  isOpen: boolean
  onClose: () => void
}

export function MovieDetailsModal({ movie, isOpen, onClose }: MovieDetailsModalProps) {
  const [streamingProviders, setStreamingProviders] = useState<StreamingProvider[]>([])
  const [isLoadingProviders, setIsLoadingProviders] = useState(false)

  useEffect(() => {
    if (movie && isOpen) {
      fetchStreamingProviders()
    }
  }, [movie, isOpen])

  const fetchStreamingProviders = async () => {
    if (!movie) return

    setIsLoadingProviders(true)
    try {
      const endpoint = movie.type === 'tv' ? `/tv/${movie.id}/watch/providers` : `/movie/${movie.id}/watch/providers`
      const response = await fetch(`/api/tmdb?endpoint=${endpoint}`)
      if (response.ok) {
        const data = await response.json()
        // Get US providers, or fallback to first available region
        const region = data.results?.US || Object.values(data.results || {})[0] as any
        const providers = region?.flatrate || region?.rent || region?.buy || []
        setStreamingProviders(providers.slice(0, 6))
      }
    } catch (error) {
      console.error('Failed to fetch streaming providers:', error)
    } finally {
      setIsLoadingProviders(false)
    }
  }

  const openTMDB = () => {
    if (!movie) return
    const url = movie.type === 'tv'
      ? `https://www.themoviedb.org/tv/${movie.id}`
      : `https://www.themoviedb.org/movie/${movie.id}`
    window.open(url, '_blank')
  }

  const openJustWatch = () => {
    if (!movie) return
    const searchQuery = encodeURIComponent(movie.title)
    window.open(`https://www.justwatch.com/us/search?q=${searchQuery}`, '_blank')
  }

  if (!isOpen || !movie) return null

  const TypeIcon = movie.type === 'tv' ? Television : VideoCamera

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
        className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 50, scale: 0.95 }}
        className="fixed inset-x-4 top-[10%] md:inset-x-auto md:left-1/2 md:-translate-x-1/2 md:w-full md:max-w-2xl z-50 max-h-[80vh] overflow-hidden rounded-2xl bg-white dark:bg-dark-card shadow-2xl"
      >
        {/* Header with backdrop */}
        <div className="relative h-48 md:h-64">
          {movie.backdropPath || movie.posterPath ? (
            <Image
              src={`https://image.tmdb.org/t/p/w780${movie.backdropPath || movie.posterPath}`}
              alt={movie.title}
              fill
              className="object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-primary-500 to-secondary-400" />
          )}

          {/* Gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors"
          >
            <X size={20} weight="bold" />
          </button>

          {/* Title overlay */}
          <div className="absolute bottom-4 left-4 right-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2 py-1 rounded-lg text-xs font-medium bg-primary-500 text-white flex items-center gap-1">
                <TypeIcon size={12} weight="fill" />
                {movie.type === 'tv' ? 'TV Show' : 'Movie'}
              </span>
              {movie.rating && (
                <span className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-black/50 text-white">
                  <Star size={12} weight="fill" className="text-amber-400" />
                  {movie.rating.toFixed(1)}
                </span>
              )}
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-white">
              {movie.title}
            </h2>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 md:p-6 overflow-y-auto max-h-[calc(80vh-12rem)]">
          {/* Meta info */}
          <div className="flex flex-wrap gap-4 mb-4 text-sm text-surface-500 dark:text-surface-400">
            {movie.releaseDate && (
              <span className="flex items-center gap-1">
                <Calendar size={16} />
                {new Date(movie.releaseDate).getFullYear()}
              </span>
            )}
            {movie.runtime && (
              <span className="flex items-center gap-1">
                <Clock size={16} />
                {movie.runtime} min
              </span>
            )}
          </div>

          {/* Overview */}
          {movie.overview && (
            <p className="text-surface-700 dark:text-surface-300 mb-6 leading-relaxed">
              {movie.overview}
            </p>
          )}

          {/* Streaming providers */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white mb-3">
              Where to Watch
            </h3>
            {isLoadingProviders ? (
              <div className="flex gap-2">
                {[1, 2, 3].map(i => (
                  <div key={i} className="w-12 h-12 rounded-xl bg-surface-100 dark:bg-dark-hover animate-pulse" />
                ))}
              </div>
            ) : streamingProviders.length > 0 ? (
              <div className="flex flex-wrap gap-3">
                {streamingProviders.map(provider => (
                  <div
                    key={provider.provider_id}
                    className="flex flex-col items-center gap-1"
                    title={provider.provider_name}
                  >
                    <div className="w-12 h-12 rounded-xl overflow-hidden bg-surface-100 dark:bg-dark-hover">
                      <Image
                        src={`https://image.tmdb.org/t/p/w92${provider.logo_path}`}
                        alt={provider.provider_name}
                        width={48}
                        height={48}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <span className="text-[10px] text-surface-500 text-center max-w-[60px] truncate">
                      {provider.provider_name}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-surface-500">
                Streaming info not available. Check JustWatch for availability.
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <Button
              onClick={openJustWatch}
              icon={<Play size={18} weight="fill" />}
            >
              Find Where to Watch
            </Button>
            <Button
              variant="secondary"
              onClick={openTMDB}
              icon={<ArrowSquareOut size={18} />}
            >
              More Info
            </Button>
            <Button
              variant="ghost"
              onClick={() => haptic('light')}
              icon={<Heart size={18} />}
            >
              Save
            </Button>
          </div>
        </div>
      </motion.div>
    </>
  )
}

export default MovieDetailsModal
