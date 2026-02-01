import type { Content, Movie, TVShow, ContentType } from '@/types'

// TMDB API configuration
const TMDB_API_KEY = process.env.NEXT_PUBLIC_TMDB_API_KEY || ''
const TMDB_BASE_URL = 'https://api.themoviedb.org/3'
const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p'

// Image size options
export const imageSizes = {
  poster: {
    small: '/w185',
    medium: '/w342',
    large: '/w500',
    original: '/original',
  },
  backdrop: {
    small: '/w300',
    medium: '/w780',
    large: '/w1280',
    original: '/original',
  },
  profile: {
    small: '/w45',
    medium: '/w185',
    large: '/h632',
    original: '/original',
  },
}

// Helper to construct image URLs
export function getImageUrl(
  path: string | null | undefined,
  type: 'poster' | 'backdrop' | 'profile' = 'poster',
  size: 'small' | 'medium' | 'large' | 'original' = 'medium'
): string | null {
  if (!path) return null
  return `${TMDB_IMAGE_BASE}${imageSizes[type][size]}${path}`
}

// Fetch helper
async function tmdbFetch<T>(endpoint: string, params: Record<string, string> = {}): Promise<T> {
  const url = new URL(`${TMDB_BASE_URL}${endpoint}`)
  url.searchParams.append('api_key', TMDB_API_KEY)

  Object.entries(params).forEach(([key, value]) => {
    url.searchParams.append(key, value)
  })

  const response = await fetch(url.toString())

  if (!response.ok) {
    throw new Error(`TMDB API error: ${response.status}`)
  }

  return response.json()
}

// ============================================
// MOVIE FUNCTIONS
// ============================================

interface TMDBMovieResult {
  id: number
  title: string
  overview: string
  poster_path: string | null
  backdrop_path: string | null
  release_date: string
  vote_average: number
  genre_ids: number[]
  runtime?: number
}

interface TMDBResponse {
  page: number
  results: TMDBMovieResult[]
  total_pages: number
  total_results: number
}

interface TMDBMovieDetails extends TMDBMovieResult {
  runtime: number
  genres: { id: number; name: string }[]
  credits?: {
    cast: { id: number; name: string; character: string; profile_path: string | null }[]
    crew: { id: number; name: string; job: string }[]
  }
  'watch/providers'?: {
    results: Record<string, {
      flatrate?: { provider_id: number; provider_name: string; logo_path: string }[]
    }>
  }
}

function transformMovieResult(movie: TMDBMovieResult | TMDBMovieDetails): Movie {
  return {
    id: movie.id.toString(),
    type: 'movie',
    title: movie.title,
    description: movie.overview,
    posterPath: movie.poster_path ?? undefined,
    backdropPath: movie.backdrop_path ?? undefined,
    releaseDate: movie.release_date,
    rating: movie.vote_average,
    runtime: movie.runtime,
    genres: 'genres' in movie
      ? movie.genres.map((g) => g.name)
      : [],
  }
}

export async function getPopularMovies(page = 1): Promise<Movie[]> {
  const data = await tmdbFetch<TMDBResponse>('/movie/popular', {
    page: page.toString(),
  })
  return data.results.map(transformMovieResult)
}

export async function getTrendingMovies(timeWindow: 'day' | 'week' = 'week'): Promise<Movie[]> {
  const data = await tmdbFetch<TMDBResponse>(`/trending/movie/${timeWindow}`)
  return data.results.map(transformMovieResult)
}

export async function getTopRatedMovies(page = 1): Promise<Movie[]> {
  const data = await tmdbFetch<TMDBResponse>('/movie/top_rated', {
    page: page.toString(),
  })
  return data.results.map(transformMovieResult)
}

export async function getNowPlayingMovies(page = 1): Promise<Movie[]> {
  const data = await tmdbFetch<TMDBResponse>('/movie/now_playing', {
    page: page.toString(),
  })
  return data.results.map(transformMovieResult)
}

export async function getMovieDetails(movieId: string): Promise<Movie> {
  const data = await tmdbFetch<TMDBMovieDetails>(`/movie/${movieId}`, {
    append_to_response: 'credits,watch/providers',
  })
  return transformMovieResult(data)
}

export async function searchMovies(query: string, page = 1): Promise<Movie[]> {
  const data = await tmdbFetch<TMDBResponse>('/search/movie', {
    query,
    page: page.toString(),
  })
  return data.results.map(transformMovieResult)
}

// ============================================
// TV SHOW FUNCTIONS
// ============================================

interface TMDBTVResult {
  id: number
  name: string
  overview: string
  poster_path: string | null
  backdrop_path: string | null
  first_air_date: string
  vote_average: number
  genre_ids: number[]
}

interface TMDBTVDetails extends TMDBTVResult {
  number_of_seasons: number
  episode_run_time: number[]
  genres: { id: number; name: string }[]
}

function transformTVResult(show: TMDBTVResult | TMDBTVDetails): TVShow {
  return {
    id: show.id.toString(),
    type: 'tv',
    title: show.name,
    description: show.overview,
    posterPath: show.poster_path ?? undefined,
    backdropPath: show.backdrop_path ?? undefined,
    releaseDate: show.first_air_date,
    rating: show.vote_average,
    seasons: 'number_of_seasons' in show ? show.number_of_seasons : undefined,
    episodeRuntime: 'episode_run_time' in show ? show.episode_run_time[0] : undefined,
    genres: 'genres' in show
      ? show.genres.map((g) => g.name)
      : [],
  }
}

export async function getPopularTVShows(page = 1): Promise<TVShow[]> {
  const data = await tmdbFetch<{ results: TMDBTVResult[] }>('/tv/popular', {
    page: page.toString(),
  })
  return data.results.map(transformTVResult)
}

export async function getTrendingTVShows(timeWindow: 'day' | 'week' = 'week'): Promise<TVShow[]> {
  const data = await tmdbFetch<{ results: TMDBTVResult[] }>(`/trending/tv/${timeWindow}`)
  return data.results.map(transformTVResult)
}

export async function getTopRatedTVShows(page = 1): Promise<TVShow[]> {
  const data = await tmdbFetch<{ results: TMDBTVResult[] }>('/tv/top_rated', {
    page: page.toString(),
  })
  return data.results.map(transformTVResult)
}

export async function getTVShowDetails(tvId: string): Promise<TVShow> {
  const data = await tmdbFetch<TMDBTVDetails>(`/tv/${tvId}`, {
    append_to_response: 'credits,watch/providers',
  })
  return transformTVResult(data)
}

export async function searchTVShows(query: string, page = 1): Promise<TVShow[]> {
  const data = await tmdbFetch<{ results: TMDBTVResult[] }>('/search/tv', {
    query,
    page: page.toString(),
  })
  return data.results.map(transformTVResult)
}

// ============================================
// COMBINED FUNCTIONS
// ============================================

export async function searchAll(query: string, page = 1): Promise<Content[]> {
  const data = await tmdbFetch<{
    results: (TMDBMovieResult & TMDBTVResult & { media_type: 'movie' | 'tv' | 'person' })[]
  }>('/search/multi', {
    query,
    page: page.toString(),
  })

  return data.results
    .filter((item) => item.media_type === 'movie' || item.media_type === 'tv')
    .map((item) => {
      if (item.media_type === 'movie') {
        return transformMovieResult(item as TMDBMovieResult)
      }
      return transformTVResult(item as TMDBTVResult)
    })
}

export async function getTrending(
  mediaType: 'movie' | 'tv' | 'all' = 'all',
  timeWindow: 'day' | 'week' = 'week'
): Promise<Content[]> {
  const data = await tmdbFetch<{
    results: (TMDBMovieResult & TMDBTVResult & { media_type: 'movie' | 'tv' })[]
  }>(`/trending/${mediaType}/${timeWindow}`)

  return data.results.map((item) => {
    if (item.media_type === 'movie' || 'title' in item) {
      return transformMovieResult(item as TMDBMovieResult)
    }
    return transformTVResult(item as TMDBTVResult)
  })
}

// ============================================
// MOOD-BASED RECOMMENDATIONS
// ============================================

// Genre mappings for moods
const moodGenreMap: Record<string, { movie: number[]; tv: number[] }> = {
  stressed: {
    movie: [35, 16, 10751], // Comedy, Animation, Family
    tv: [35, 16, 10751],
  },
  anxious: {
    movie: [99, 10751, 10402], // Documentary, Family, Music
    tv: [99, 10751, 10762],
  },
  bored: {
    movie: [28, 12, 878, 53], // Action, Adventure, Sci-Fi, Thriller
    tv: [28, 10759, 878],
  },
  sad: {
    movie: [35, 10749, 16], // Comedy, Romance, Animation
    tv: [35, 10749, 16],
  },
  happy: {
    movie: [12, 35, 10751], // Adventure, Comedy, Family
    tv: [12, 35, 10751],
  },
  lonely: {
    movie: [10749, 35, 18], // Romance, Comedy, Drama
    tv: [10749, 35, 18],
  },
  angry: {
    movie: [35, 16, 10402], // Comedy, Animation, Music
    tv: [35, 16, 10762],
  },
  tired: {
    movie: [16, 10751, 99], // Animation, Family, Documentary
    tv: [16, 10751, 99],
  },
  overwhelmed: {
    movie: [16, 10751, 35], // Animation, Family, Comedy
    tv: [16, 10751, 35],
  },
  restless: {
    movie: [28, 53, 878], // Action, Thriller, Sci-Fi
    tv: [28, 10759, 878],
  },
  focused: {
    movie: [99, 36, 10402], // Documentary, History, Music
    tv: [99, 10768, 10764],
  },
  melancholic: {
    movie: [18, 10749, 10402], // Drama, Romance, Music
    tv: [18, 10749, 10766],
  },
}

export async function getMoodBasedRecommendations(
  currentMood: string,
  targetMood: string,
  contentType: 'movie' | 'tv' | 'all' = 'all'
): Promise<Content[]> {
  const genres = moodGenreMap[currentMood] || moodGenreMap.bored
  const results: Content[] = []

  if (contentType === 'movie' || contentType === 'all') {
    const movieData = await tmdbFetch<TMDBResponse>('/discover/movie', {
      with_genres: genres.movie.slice(0, 2).join(','),
      sort_by: 'popularity.desc',
      'vote_count.gte': '100',
    })
    results.push(...movieData.results.map(transformMovieResult))
  }

  if (contentType === 'tv' || contentType === 'all') {
    const tvData = await tmdbFetch<{ results: TMDBTVResult[] }>('/discover/tv', {
      with_genres: genres.tv.slice(0, 2).join(','),
      sort_by: 'popularity.desc',
      'vote_count.gte': '50',
    })
    results.push(...tvData.results.map(transformTVResult))
  }

  // Shuffle and return
  return results.sort(() => Math.random() - 0.5).slice(0, 20)
}

// ============================================
// QUICK HIT - RANDOM RECOMMENDATION
// ============================================

export async function getQuickHitRecommendation(): Promise<Content> {
  // Get a mix of trending content
  const trending = await getTrending('all', 'week')

  // Filter to highly rated content
  const filtered = trending.filter(
    (item) => item.rating && item.rating >= 7.0
  )

  // Return a random one
  const randomIndex = Math.floor(Math.random() * filtered.length)
  return filtered[randomIndex] || trending[0]
}
