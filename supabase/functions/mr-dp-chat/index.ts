// Supabase Edge Function for Mr.DP AI Chat
// Deploy: supabase functions deploy mr-dp-chat
// Set secret: supabase secrets set OPENAI_API_KEY=your-key

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

const SYSTEM_PROMPT_EN = `You are Mr.DP (Mr. Dopamine Partner), a friendly, empathetic AI assistant for dopamine.watch - a mood-based content recommendation app designed for ADHD and neurodivergent minds.

Your personality:
- Warm, supportive, and understanding
- You use casual, friendly language (not corporate)
- You understand ADHD struggles: decision fatigue, overwhelm, understimulation, hyperfocus
- You occasionally use emojis but don't overdo it
- You're knowledgeable about how different content affects mood and dopamine

Your job on the landing page:
- Welcome visitors and explain what dopamine.watch does
- Help them understand how mood-based recommendations work
- Encourage them to sign up (it's free!)
- Answer questions about the app, pricing, features
- If they share how they're feeling, empathize and tease what kind of content might help

Key features to mention:
- Mood-based discovery: tell us how you feel NOW and how you WANT to feel
- Quick Dope Hit: one button for instant perfect recommendations
- Mr.DP (you!) in the full app can find specific content
- Movies, TV, music, podcasts, audiobooks, shorts - all in one place
- Free tier with 5 Mr.DP chats, Premium ($4.99/mo) unlimited

Keep responses SHORT (2-3 sentences max). You're a chat widget, not an essay writer.
If they ask something you can't help with, suggest they sign up to explore the full app.`

const SYSTEM_PROMPT_ES = `Eres Mr.DP (Mr. Dopamine Partner), un asistente de IA amigable y empático para dopamine.watch - una app de recomendaciones de contenido basadas en el estado de ánimo, diseñada para mentes con TDAH y neurodivergentes.

Tu personalidad:
- Cálido, comprensivo y solidario
- Usas lenguaje casual y amigable (no corporativo)
- Entiendes las luchas del TDAH: fatiga de decisión, agobio, falta de estimulación, hiperfoco
- Usas emojis ocasionalmente pero sin exagerar
- Conoces cómo diferentes tipos de contenido afectan el ánimo y la dopamina

Tu trabajo en la landing page:
- Dar la bienvenida y explicar qué hace dopamine.watch
- Ayudarles a entender cómo funcionan las recomendaciones por ánimo
- Animarles a registrarse (¡es gratis!)
- Responder preguntas sobre la app, precios, funciones
- Si comparten cómo se sienten, empatiza y menciona qué tipo de contenido podría ayudar

Funciones clave a mencionar:
- Descubrimiento por ánimo: dinos cómo te sientes AHORA y cómo QUIERES sentirte
- Chute Rápido: un botón para recomendaciones perfectas instantáneas
- Mr.DP (¡tú!) en la app completa puede encontrar contenido específico
- Películas, series, música, podcasts, audiolibros, shorts - todo en un lugar
- Plan gratis con 5 chats de Mr.DP, Premium ($4.99/mes) ilimitado

Mantén las respuestas CORTAS (2-3 oraciones máximo). Eres un widget de chat, no un escritor de ensayos.
IMPORTANTE: Responde SIEMPRE en español.`

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { message, history = [], lang = 'en' } = await req.json()

    if (!message) {
      return new Response(
        JSON.stringify({ error: 'Message is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const isSpanish = lang === 'es'
    const OPENAI_API_KEY = Deno.env.get('OPENAI_API_KEY')

    if (!OPENAI_API_KEY) {
      // Fallback to smart canned responses if no API key
      return new Response(
        JSON.stringify({
          response: isSpanish ? getFallbackResponseES(message) : getFallbackResponse(message),
          fallback: true
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Build messages array with appropriate language prompt
    const systemPrompt = isSpanish ? SYSTEM_PROMPT_ES : SYSTEM_PROMPT_EN
    const messages = [
      { role: 'system', content: systemPrompt },
      ...history.slice(-6), // Keep last 6 messages for context
      { role: 'user', content: message }
    ]

    // Call OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: messages,
        max_tokens: 150,
        temperature: 0.8,
      }),
    })

    if (!response.ok) {
      const error = await response.text()
      console.error('OpenAI API error:', error)
      return new Response(
        JSON.stringify({
          response: isSpanish ? getFallbackResponseES(message) : getFallbackResponse(message),
          fallback: true
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const data = await response.json()
    const fallbackFn = isSpanish ? getFallbackResponseES : getFallbackResponse
    const aiResponse = data.choices[0]?.message?.content || fallbackFn(message)

    return new Response(
      JSON.stringify({ response: aiResponse }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

// Smart fallback responses based on keywords
function getFallbackResponse(message: string): string {
  const msg = message.toLowerCase()

  // Greetings
  if (msg.match(/^(hi|hello|hey|hola|sup|yo)/)) {
    return "Hey there! 👋 I'm Mr.DP, your dopamine buddy. What brings you here today? Feeling stuck in scroll-land?"
  }

  // Feeling states
  if (msg.match(/(anxious|stressed|overwhelmed|panic)/)) {
    return "I hear you - that anxious energy is rough. 💜 The full app can find you calming content that actually helps. Want to sign up and let me work my magic?"
  }

  if (msg.match(/(bored|tired|exhausted|drained|unmotivated)/)) {
    return "Ugh, that understimulated feeling is the worst! I'm great at finding content that hits just right - not too much, not too little. Sign up free and I'll help you out! 🎯"
  }

  if (msg.match(/(sad|depressed|down|lonely)/)) {
    return "Sending you good vibes 💜 Sometimes the right movie or music can really help shift things. Sign up and I can find something comforting for you."
  }

  if (msg.match(/(happy|excited|good|great|amazing)/)) {
    return "Love that energy! 🎉 Let's keep it going - I can find content that matches your vibe perfectly. Sign up and let's roll!"
  }

  // Questions about the app
  if (msg.match(/(what|how).*(work|do|app)/)) {
    return "Simple! Tell me how you feel NOW and how you WANT to feel. I find movies, music, podcasts that bridge that gap. No more endless scrolling! Sign up free to try it 🚀"
  }

  if (msg.match(/(price|cost|free|pay|premium)/)) {
    return "Free tier gets you everything + 5 chats with me daily. Premium ($4.99/mo) = unlimited Mr.DP chats + no ads + priority recommendations. Pretty sweet deal! 💎"
  }

  if (msg.match(/(adhd|neurodivergent|autism)/)) {
    return "Built BY neurodivergent folks FOR neurodivergent folks! We get decision fatigue, we get overwhelm. That's why one button = perfect content. No thinking required 🧠✨"
  }

  if (msg.match(/(movie|film|show|tv|netflix)/)) {
    return "I've got movies & shows from Netflix, Disney+, Max, Prime, and 20+ services - all filtered by the emotion you need. Sign up and tell me what you're in the mood for! 🎬"
  }

  if (msg.match(/(music|song|playlist|spotify)/)) {
    return "Mood-matched music is my jam! 🎵 I connect to Spotify and Apple Music to find the perfect vibe. Sign up and let's get those good sounds flowing!"
  }

  if (msg.match(/(podcast|audiobook)/)) {
    return "Podcasts and audiobooks curated by vibe - perfect for when you need background brain food! Sign up and I'll match you with something good 🎙️"
  }

  // Default
  const defaults = [
    "Interesting! In the full app, I can really dig into that and find you perfect content. Want to sign up free and let me help? 🎯",
    "I'd love to help more! Sign up (it's free) and I can access my full powers to find you exactly what you need 💜",
    "That's what I'm here for! Create a free account and let's find your perfect content match 🚀",
  ]

  return defaults[Math.floor(Math.random() * defaults.length)]
}

// Spanish fallback responses
function getFallbackResponseES(message: string): string {
  const msg = message.toLowerCase()

  // Saludos
  if (msg.match(/^(hola|hey|buenas|qué tal|saludos)/)) {
    return "¡Hola! 👋 Soy Mr.DP, tu amigo de dopamina. ¿Qué te trae por aquí? ¿Atrapado en el scroll infinito?"
  }

  // Estados emocionales
  if (msg.match(/(ansioso|ansiedad|estresado|abrumado|pánico)/)) {
    return "Te escucho - esa energía ansiosa es difícil. 💜 La app completa puede encontrarte contenido relajante que realmente ayuda. ¿Quieres registrarte y dejarme trabajar mi magia?"
  }

  if (msg.match(/(aburrido|cansado|agotado|sin energía|desmotivado)/)) {
    return "¡Ugh, esa falta de estimulación es lo peor! Soy muy bueno encontrando contenido que pega justo - ni mucho, ni poco. ¡Regístrate gratis y te ayudo! 🎯"
  }

  if (msg.match(/(triste|deprimido|bajón|solo)/)) {
    return "Te envío buenas vibras 💜 A veces la película o música correcta puede cambiar las cosas. Regístrate y puedo encontrar algo reconfortante."
  }

  if (msg.match(/(feliz|emocionado|bien|genial|increíble)/)) {
    return "¡Me encanta esa energía! 🎉 Mantengámosla - puedo encontrar contenido que combine perfecto con tu vibra. ¡Regístrate y a rodar!"
  }

  // Preguntas sobre la app
  if (msg.match(/(qué|cómo).*(funciona|hace|app)/)) {
    return "¡Simple! Dime cómo te sientes AHORA y cómo QUIERES sentirte. Encuentro películas, música, podcasts que cierran esa brecha. ¡Sin más scroll infinito! Regístrate gratis 🚀"
  }

  if (msg.match(/(precio|costo|gratis|pagar|premium)/)) {
    return "El plan gratis incluye todo + 5 chats conmigo al día. Premium ($4.99/mes) = Mr.DP ilimitado + sin anuncios + recomendaciones prioritarias. ¡Buen trato! 💎"
  }

  if (msg.match(/(tdah|neurodivergente|autismo)/)) {
    return "¡Hecho POR neurodivergentes PARA neurodivergentes! Entendemos la fatiga de decisión, el agobio. Por eso un botón = contenido perfecto. Sin pensar 🧠✨"
  }

  if (msg.match(/(película|peli|serie|tv|netflix)/)) {
    return "Tengo pelis y series de Netflix, Disney+, Max, Prime y +20 servicios - todo filtrado por la emoción que necesitas. ¡Regístrate y dime qué te apetece! 🎬"
  }

  if (msg.match(/(música|canción|playlist|spotify)/)) {
    return "¡La música por ánimo es mi especialidad! 🎵 Conecto con Spotify y Apple Music para encontrar la vibra perfecta. ¡Regístrate y hagamos sonar lo bueno!"
  }

  if (msg.match(/(podcast|audiolibro)/)) {
    return "Podcasts y audiolibros curados por vibra - perfecto para cuando necesitas alimento cerebral de fondo. ¡Regístrate y te combino algo bueno! 🎙️"
  }

  // Default
  const defaults = [
    "¡Interesante! En la app completa puedo profundizar y encontrarte contenido perfecto. ¿Quieres registrarte gratis y dejarme ayudar? 🎯",
    "¡Me encantaría ayudar más! Regístrate (es gratis) y puedo acceder a mis poderes completos para encontrarte justo lo que necesitas 💜",
    "¡Para eso estoy! Crea una cuenta gratis y encontremos tu contenido perfecto 🚀",
  ]

  return defaults[Math.floor(Math.random() * defaults.length)]
}
