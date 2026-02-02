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

CRITICAL - Content Type Prefixes (MANDATORY FORMAT - NEVER SKIP):
Every single recommendation MUST use this exact format: [type] "Title"
- [movie] "Title" - for films
- [tv] "Title" - for TV shows/series
- [podcast] "Title" - for podcast shows
- [audiobook] "Title" - for audiobooks
- [music] "Title" - for songs, albums, playlists, or any music to listen to

NEVER recommend content without the [type] prefix. Examples of CORRECT format:
- ✅ [music] "Weightless by Marconi Union"
- ✅ [movie] "Inside Out"
- ❌ "Future Nostalgia" by Dua Lipa (WRONG - missing prefix!)
- ❌ check out "Lo-fi Beats" (WRONG - missing prefix!)

IMPORTANT - MUSIC vs MOVIES ABOUT MUSIC:
- When user asks for MUSIC → recommend [music] "actual songs/albums"
- Example: "I want music to relax" → [music] "Weightless by Marconi Union" or [music] "Lo-Fi Beats"
- NOT [movie] "The Greatest Showman" - that's a movie, not music!
- Artists like Dua Lipa, Taylor Swift, etc. = [music], not movies

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

// Detect content type from context around the title
function detectTypeFromContext(text: string, title: string): ContentType {
  const lowerText = text.toLowerCase()
  const titleIndex = lowerText.indexOf(title.toLowerCase())

  // Get surrounding context (100 chars before and after)
  const start = Math.max(0, titleIndex - 100)
  const end = Math.min(text.length, titleIndex + title.length + 100)
  const context = lowerText.slice(start, end)

  // Music indicators: "by Artist", "listen to", "song", "album", "music", "track"
  if (/\bby\s+[a-z]/i.test(context) ||
      /listen(ing)?\s+to/i.test(context) ||
      /\b(music|song|album|track|playlist|artist|band)\b/i.test(context)) {
    return 'music'
  }

  // Podcast indicators
  if (/\b(podcast|episode|show|series)\b/i.test(context) &&
      !/\b(tv|television)\s+(show|series)\b/i.test(context)) {
    return 'podcast'
  }

  // Audiobook indicators
  if (/\b(audiobook|audio\s*book|narrat|listen.*book)\b/i.test(context)) {
    return 'audiobook'
  }

  // TV show indicators
  if (/\b(tv|television|series|season|episode)\b/i.test(context)) {
    return 'tv'
  }

  // Default to movie
  return 'movie'
}

// Extract content with type prefixes: [movie] "Title", [podcast] "Title", etc.
// Also detects type from context when prefix is missing
function extractContent(text: string): ExtractedContent[] {
  const results: ExtractedContent[] = []

  // Pattern: [type] "title" or just "title"
  const typedPattern = /\[(movie|tv|podcast|audiobook|music)\]\s*"([^"]+)"/gi
  const simplePattern = /"([^"]+)"/g
  // Also match "Title" by Artist pattern for music
  const musicByArtistPattern = /"([^"]+)"\s+by\s+([^.!?,]+)/gi

  let match
  const foundTitles = new Set<string>()

  // First extract explicitly typed content
  while ((match = typedPattern.exec(text)) !== null) {
    const type = match[1].toLowerCase() as ContentType
    const title = match[2]
    if (!foundTitles.has(title.toLowerCase())) {
      foundTitles.add(title.toLowerCase())
      results.push({ type, title })
    }
  }

  // Extract "Title" by Artist pattern as music
  while ((match = musicByArtistPattern.exec(text)) !== null) {
    const title = match[1]
    const artist = match[2].trim()
    const fullTitle = `${title} ${artist}`.trim()
    if (!foundTitles.has(title.toLowerCase())) {
      foundTitles.add(title.toLowerCase())
      results.push({ type: 'music', title: fullTitle })
    }
  }

  // Then extract untyped content and detect type from context
  while ((match = simplePattern.exec(text)) !== null) {
    const title = match[1]
    if (!foundTitles.has(title.toLowerCase())) {
      foundTitles.add(title.toLowerCase())
      const detectedType = detectTypeFromContext(text, title)
      results.push({ type: detectedType, title })
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

// Search iTunes for podcasts with platform links
async function searchPodcast(query: string): Promise<any | null> {
  try {
    const url = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&media=podcast&limit=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    const searchQuery = encodeURIComponent(query)
    return {
      id: `podcast-${result.collectionId}`,
      type: 'podcast' as const,
      title: result.collectionName,
      posterPath: result.artworkUrl600 || result.artworkUrl100,
      artist: result.artistName,
      feedUrl: result.feedUrl,
      trackCount: result.trackCount,
      // Platform links for user choice
      platforms: {
        applePodcasts: result.collectionViewUrl || `https://podcasts.apple.com/search?term=${searchQuery}`,
        spotify: `https://open.spotify.com/search/${searchQuery}/shows`,
        youtube: `https://www.youtube.com/results?search_query=${searchQuery}+podcast`,
        googlePodcasts: `https://podcasts.google.com/search/${searchQuery}`,
      },
    }
  } catch (error) {
    console.error('Podcast search error:', error)
    return null
  }
}

// Search iTunes for audiobooks with platform links (including Audible)
async function searchAudiobook(query: string): Promise<any | null> {
  try {
    const url = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&media=audiobook&limit=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    const searchQuery = encodeURIComponent(query)
    return {
      id: `audiobook-${result.collectionId}`,
      type: 'audiobook' as const,
      title: result.collectionName,
      posterPath: result.artworkUrl600 || result.artworkUrl100,
      artist: result.artistName,
      description: result.description,
      previewUrl: result.previewUrl,
      // Platform links for user choice
      platforms: {
        audible: `https://www.audible.com/search?keywords=${searchQuery}`,
        appleBooks: result.collectionViewUrl || `https://books.apple.com/search?term=${searchQuery}`,
        spotify: `https://open.spotify.com/search/${searchQuery}/audiobooks`,
        googlePlayBooks: `https://play.google.com/store/search?q=${searchQuery}&c=audiobooks`,
      },
    }
  } catch (error) {
    console.error('Audiobook search error:', error)
    return null
  }
}

// Search iTunes for music (albums/songs) with platform links
async function searchMusic(query: string): Promise<any | null> {
  try {
    const url = `https://itunes.apple.com/search?term=${encodeURIComponent(query)}&media=music&entity=album&limit=1`
    const response = await fetch(url)
    if (!response.ok) return null

    const data = await response.json()
    const result = data.results?.[0]
    if (!result) return null

    const searchQuery = encodeURIComponent(query)
    return {
      id: `music-${result.collectionId}`,
      type: 'music' as const,
      title: result.collectionName,
      posterPath: result.artworkUrl600 || result.artworkUrl100,
      artist: result.artistName,
      trackCount: result.trackCount,
      releaseDate: result.releaseDate,
      // Platform links for user choice
      platforms: {
        spotify: `https://open.spotify.com/search/${searchQuery}`,
        appleMusic: result.collectionViewUrl || `https://music.apple.com/search?term=${searchQuery}`,
        youtubeMusic: `https://music.youtube.com/search?q=${searchQuery}`,
        amazonMusic: `https://music.amazon.com/search/${searchQuery}`,
      },
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
