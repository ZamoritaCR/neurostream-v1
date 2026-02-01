import { NextRequest, NextResponse } from 'next/server'

// Use server-side env var first, fall back to public
const TMDB_API_KEY = process.env.TMDB_API_KEY || process.env.NEXT_PUBLIC_TMDB_API_KEY
const TMDB_BASE_URL = 'https://api.themoviedb.org/3'

// Allowed endpoints for security
const ALLOWED_ENDPOINTS = [
  '/trending/',
  '/movie/popular',
  '/movie/top_rated',
  '/movie/now_playing',
  '/movie/',  // For movie details and watch/providers
  '/tv/popular',
  '/tv/top_rated',
  '/tv/',     // For TV details and watch/providers
  '/discover/movie',
  '/discover/tv',
  '/search/movie',
  '/search/tv',
  '/search/multi',
]

export async function GET(request: NextRequest) {
  try {
    if (!TMDB_API_KEY) {
      console.error('TMDB API key not configured')
      return NextResponse.json(
        { error: 'TMDB API key not configured' },
        { status: 500 }
      )
    }

    const { searchParams } = new URL(request.url)
    const endpoint = searchParams.get('endpoint')

    if (!endpoint) {
      return NextResponse.json(
        { error: 'Endpoint is required' },
        { status: 400 }
      )
    }

    // Security check - only allow specific endpoints
    const isAllowed = ALLOWED_ENDPOINTS.some(allowed => endpoint.startsWith(allowed))
    if (!isAllowed) {
      return NextResponse.json(
        { error: 'Endpoint not allowed' },
        { status: 403 }
      )
    }

    // Build TMDB URL
    const url = new URL(`${TMDB_BASE_URL}${endpoint}`)
    url.searchParams.append('api_key', TMDB_API_KEY)

    // Forward other query params
    searchParams.forEach((value, key) => {
      if (key !== 'endpoint') {
        url.searchParams.append(key, value)
      }
    })

    const response = await fetch(url.toString())

    if (!response.ok) {
      console.error('TMDB API error:', response.status)
      return NextResponse.json(
        { error: `TMDB API error: ${response.status}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('TMDB proxy error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
