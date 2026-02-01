import { NextRequest, NextResponse } from 'next/server'

const OPENAI_API_KEY = process.env.OPENAI_API_KEY

// Mr.DP system prompt - ADHD-optimized AI assistant
const SYSTEM_PROMPT = `You are Mr.DP (Mr. Dopamine), a friendly and understanding AI assistant for dopamine.watch - an ADHD-friendly streaming recommendation app.

Your personality:
- Warm, supportive, and non-judgmental
- Understanding of ADHD struggles like decision fatigue and analysis paralysis
- Brief and to-the-point (ADHD users appreciate concise responses)
- Enthusiastic about helping find the perfect content
- Uses casual, friendly language (but not overly cheesy)

Your role:
- Help users find movies, TV shows, and other content based on their mood
- Understand that users often can't decide what to watch (decision fatigue)
- Offer specific, confident recommendations rather than long lists
- Ask clarifying questions if needed, but keep it simple

Key guidelines:
- Keep responses SHORT (2-3 sentences max unless asked for more)
- Give 1-2 specific recommendations, not overwhelming lists
- Acknowledge the user's feelings before suggesting content
- If they seem stressed or overwhelmed, suggest calming/comfort content
- Be encouraging about their content choices
- You can use occasional emoji but don't overdo it

Content knowledge:
- You know popular movies and TV shows
- You understand mood-to-content matching (sad → comfort shows, bored → action/thriller, anxious → calming content)
- You can suggest content for different vibes: cozy, exciting, thought-provoking, funny, emotional, etc.

Remember: You're helping ADHD brains find content without the doom-scrolling. Be their friendly decision-making assistant!`

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export async function POST(request: NextRequest) {
  try {
    if (!OPENAI_API_KEY) {
      return NextResponse.json(
        { error: 'OpenAI API key not configured' },
        { status: 500 }
      )
    }

    const body = await request.json()
    const { messages, mood } = body as { messages: ChatMessage[]; mood?: string }

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
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
        { status: 500 }
      )
    }

    const data = await response.json()
    const assistantMessage = data.choices[0]?.message?.content

    if (!assistantMessage) {
      return NextResponse.json(
        { error: 'No response from AI' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      message: assistantMessage,
      usage: data.usage,
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
