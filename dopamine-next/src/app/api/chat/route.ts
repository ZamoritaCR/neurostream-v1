import { NextRequest, NextResponse } from 'next/server'

const OPENAI_API_KEY = process.env.OPENAI_API_KEY
const TMDB_API_KEY = process.env.TMDB_API_KEY || process.env.NEXT_PUBLIC_TMDB_API_KEY

// CORS headers for cross-origin requests from landing page
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
}

// Mr.DP system prompt - ADHD-optimized AI assistant
const SYSTEM_PROMPT = `You are Mr.DP (Mr. Dopamine), a friendly and understanding AI assistant for dopamine.watch - an ADHD-friendly streaming recommendation app.

Your personality:
- Warm, supportive, and non-judgmental
- Understanding of ADHD struggles like decision fatigue and analysis paralysis
- Brief and to-the-point (ADHD users appreciate concise responses)
- Enthusiastic about helping find the perfect content
- Uses casual, friendly language (but not overly cheesy)

Your role:
- Help users find movies, TV shows, podcasts, audiobooks, and ACTUAL MUSIC (songs/albums) based on their mood
- Understand that users often can't decide what to watch/listen to (decision fatigue)
- Offer specific, confident recommendations rather than long lists
- Ask clarifying questions if needed, but keep it simple

CRITICAL - Content Type Prefixes (YOU MUST USE THESE):
- [movie] "Title" - for films
- [tv] "Title" - for TV shows/series
- [podcast] "Title" - for podcast shows
- [audiobook] "Title" - for audiobooks
- [music] "Artist - Song" or [music] "Album by Artist" - for ACTUAL SONGS/ALBUMS to listen to

IMPORTANT DISTINCTION:
- When user asks for MUSIC, recommend actual SONGS or ALBUMS (music to listen to), NOT movies about music!
- Example: If user says "I want music" → recommend [music] "Chill Vibes by Lo-Fi Beats" NOT [movie] "The Greatest Showman"
- Movies about musicians are MOVIES, not MUSIC

Key guidelines:
- Keep responses SHORT (2-3 sentences max unless asked for more)
- Give 1-2 specific recommendations, not overwhelming lists
- ALWAYS use the [type] prefix before quoted titles
- Acknowledge the user's feelings before suggesting content
- If they seem stressed or overwhelmed, suggest calming content
- You can use occasional emoji but don't overdo it

Content examples by type:
- MUSIC (actual songs/albums): [music] "Weightless by Marconi Union", [music] "Lo-Fi Hip Hop Radio", [music] "Chill Hits playlist"
- PODCASTS: [podcast] "The Daily", [podcast] "Stuff You Should Know", [podcast] "Crime Junkie"
- AUDIOBOOKS: [audiobook] "Atomic Habits", [audiobook] "Harry Potter"
- MOVIES: [movie] "Soul", [movie] "Inside Out"
- TV: [tv] "Ted Lasso", [tv] "The Office"

Remember: You're helping ADHD brains find content without the doom-scrolling. Match the content TYPE to what they're asking for!`

// Content types we support
type ContentType = 'movie' | 'tv' | 'podcast' | 'audiobook' | 'music'

interface ExtractedContent {
  type: ContentType
  title: string
}

// Extract content with type prefixes: [movie] "Title", [podcast] "Title", etc.
function extractContent(text: string): ExtractedContent[] {
  const results: ExtractedContent[] = []

  // Pattern: [type] "title" or just "title" (defaults to movie/tv)
  const typedPattern = /\[(movie|tv|podcast|audiobook|music)\]\s*"([^"]+)"/gi
  const simplePattern = /"([^"]+)"/g

  // First extract typed content
  let match
  const foundTitles = new Set<string>()

  while ((match = typedPattern.exec(text)) !== null) {
    const type = match[1].toLowerCase() as ContentType
    const title = match[2]
    if (!foundTitles.has(title.toLowerCase())) {
      foundTitles.add(title.toLowerCase())
      results.push({ type, title })
    }
  }

  // Then extract untyped content (treat as movie/tv)
  while ((match = simplePattern.exec(text)) !== null) {
    const title = match[1]
    if (!foundTitles.has(title.toLowerCase())) {
      foundTitles.add(title.toLowerCase())
      results.push({ type: 'movie', title }) // Default to movie, TMDB will search multi
    }
  }

  return results.slice(0, 4) // Max 4 items
}

// Search TMDB for movies/TV shows
async function searchTMDB(query: string): Promise<any | null> {
  if (!TMDB_API_KEY) return null

  try {
    const url = `https://api.themoviedb.org/3/search/multi?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(query)}&page=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    // Only return movies and TV shows
    if (result.media_type !== 'movie' && result.media_type !== 'tv') return null

    return {
      id: result.id.toString(),
      type: result.media_type,
      title: result.title || result.name,
      posterPath: result.poster_path,
      rating: result.vote_average,
      releaseDate: result.release_date || result.first_air_date,
    }
  } catch (error) {
    console.error('TMDB search error:', error)
    return null
  }
}

// Search iTunes for podcasts
async function searchPodcast(query: string): Promise<any | null> {
  try {
    const url = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&media=podcast&limit=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    return {
      id: `podcast-${result.collectionId}`,
      type: 'podcast' as const,
      title: result.collectionName,
      posterPath: result.artworkUrl600 || result.artworkUrl100,
      artist: result.artistName,
      feedUrl: result.feedUrl,
      trackCount: result.trackCount,
    }
  } catch (error) {
    console.error('Podcast search error:', error)
    return null
  }
}

// Search iTunes for audiobooks
async function searchAudiobook(query: string): Promise<any | null> {
  try {
    const url = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&media=audiobook&limit=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    return {
      id: `audiobook-${result.collectionId}`,
      type: 'audiobook' as const,
      title: result.collectionName,
      posterPath: result.artworkUrl600 || result.artworkUrl100,
      artist: result.artistName,
      description: result.description,
      previewUrl: result.previewUrl,
    }
  } catch (error) {
    console.error('Audiobook search error:', error)
    return null
  }
}

// Search iTunes for music (albums/songs)
async function searchMusic(query: string): Promise<any | null> {
  try {
    const url = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&media=music&entity=album&limit=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    return {
      id: `music-${result.collectionId}`,
      type: 'music' as const,
      title: result.collectionName,
      posterPath: result.artworkUrl600 || result.artworkUrl100,
      artist: result.artistName,
      trackCount: result.trackCount,
      releaseDate: result.releaseDate,
    }
  } catch (error) {
    console.error('Music search error:', error)
    return null
  }
}

// Search for content based on type
async function searchContent(item: ExtractedContent): Promise<any | null> {
  switch (item.type) {
    case 'movie':
    case 'tv':
      return searchTMDB(item.title)
    case 'podcast':
      return searchPodcast(item.title)
    case 'audiobook':
      return searchAudiobook(item.title)
    case 'music':
      return searchMusic(item.title)
    default:
      return searchTMDB(item.title)
  }
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

// Handle OPTIONS preflight request for CORS
export async function OPTIONS() {
  return NextResponse.json({}, { headers: corsHeaders })
}

export async function POST(request: NextRequest) {
  try {
    if (!OPENAI_API_KEY) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500, headers: corsHeaders }
      )
    }

    const body = await request.json()
    const { messages, mood } = body as { messages: ChatMessage[]; mood?: string }

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400, headers: corsHeaders }
      )
    }

    // Build conversation with system prompt
    const conversationMessages: ChatMessage[] = [
      { role: 'system', content: SYSTEM_PROMPT },
      // Add mood context if provided
      ...(mood ? [{ role: 'system' as const, content: `The user's current mood is: ${mood}. Keep this in mind when making recommendations.` }] : []),
      // Add user conversation
      ...messages.slice(-10), // Keep last 10 messages to avoid token limits
    ]

    // Call OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: conversationMessages,
        temperature: 0.7,
        max_tokens: 300,
        presence_penalty: 0.1,
        frequency_penalty: 0.1,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      console.error('OpenAI API error:', error)
      return NextResponse.json(
        { error: 'Failed to get response from AI' },
        { status: 500, headers: corsHeaders }
      )
    }

    const data = await response.json()
    const assistantMessage = data.choices[0]?.message?.content

    if (!assistantMessage) {
      return NextResponse.json(
        { error: 'No response from AI' },
        { status: 500, headers: corsHeaders }
      )
    }

    // Extract content (movies, podcasts, audiobooks, music) and search
    const extractedContent = extractContent(assistantMessage)
    const contentPromises = extractedContent.map(item => searchContent(item))
    const contentResults = await Promise.all(contentPromises)
    const recommendations = contentResults.filter(Boolean)

    return NextResponse.json({
      message: assistantMessage,
      movies: recommendations, // Keep 'movies' key for backward compatibility
      recommendations, // Also provide as 'recommendations' for clarity
      usage: data.usage,
    }, { headers: corsHeaders })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500, headers: corsHeaders }
    )
  }
}
