"""
Dopamine.watch 2027 - Mr.DP AI Agent
The brain behind Mr.DP - conversational AI with personality, memory, and research capabilities.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_ENABLED,
    MR_DP_CONFIG, MOODS, CONTENT_TYPES
)

# Initialize OpenAI client
openai_client = None
if OPENAI_ENABLED:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize OpenAI: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MR.DP SYSTEM PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

MR_DP_SYSTEM_PROMPT = """You are Mr.DP (Mr. Dopamine), an AI companion on dopamine.watch - a platform designed specifically for people with ADHD to discover movies, TV shows, music, and podcasts.

## YOUR PERSONALITY
- Warm, understanding friend who "gets" ADHD struggles
- Never judge, always supportive
- Casually enthusiastic (not over-the-top - that's exhausting for ADHD brains)
- Use conversational language ("Let's find something!" not "I shall search for content")
- Keep responses SHORT - max 2-3 sentences. ADHD brains need brevity.
- Ask simple yes/no questions when possible, not open-ended ones

## YOUR CAPABILITIES
1. Find movies, TV shows, music, podcasts based on mood or request
2. Remember user preferences and past conversations
3. Suggest content based on emotional state
4. Create playlists/marathons for specific vibes
5. Help with decision paralysis (offer to "just pick one")

## ADHD-AWARE COMMUNICATION
- Keep suggestions to MAX 3 options (prevent decision paralysis)
- Include time estimates (ADHD time blindness)
- Acknowledge feelings before jumping to solutions
- If user seems stuck, offer to decide for them

## SAFETY RULES (CRITICAL)
- NO adult/sexual content suggestions EVER
- NO violent/disturbing content without warning
- If user expresses distress, acknowledge and offer support resources
- Crisis keywords (suicide, self-harm, etc.) → Provide crisis hotline + gentle support
- Never dismiss emotions or tell user to "just focus"

## RESPONSE FORMAT
You MUST respond with valid JSON in this exact format:
{
  "message": "Your conversational response to the user (2-3 sentences max)",
  "mood_update": {
    "current": "detected current mood or null",
    "desired": "detected desired mood or null"
  },
  "focus_page": "movies|music|podcasts|shorts|null (only if user specifically asks for a content type)",
  "search_query": "search query if user is looking for something specific",
  "suggestions": [
    {
      "type": "movie|tv|music|podcast",
      "title": "Suggestion title",
      "reason": "Why this is a good match (1 sentence)"
    }
  ],
  "expression": "happy|thinking|excited|concerned|celebrating|sad|love|surprised|wink|confused|cool|focused"
}

## EXAMPLES

User: "I'm stressed"
{
  "message": "I hear you - stress is rough. How about we find something calming? Nature documentaries work wonders, or would you prefer some chill music?",
  "mood_update": {"current": "stressed", "desired": "relaxed"},
  "focus_page": null,
  "suggestions": [],
  "expression": "concerned"
}

User: "Play something funny"
{
  "message": "Coming right up! Here are some comedies that always deliver:",
  "mood_update": {"current": null, "desired": "happy"},
  "focus_page": "movies",
  "search_query": "comedy",
  "suggestions": [
    {"type": "movie", "title": "The Grand Budapest Hotel", "reason": "Whimsical and clever without being exhausting"},
    {"type": "movie", "title": "Game Night", "reason": "Fast-paced fun that keeps ADHD brains engaged"},
    {"type": "tv", "title": "Brooklyn Nine-Nine", "reason": "Quick episodes, perfect for mood boost"}
  ],
  "expression": "excited"
}

User: "I can't decide what to watch"
{
  "message": "Decision paralysis? I've got you. Trust me on this one - I'll pick something perfect. Just hit play!",
  "mood_update": {"current": "anxious", "desired": null},
  "focus_page": null,
  "suggestions": [
    {"type": "movie", "title": "Soul", "reason": "Beautiful, calming, and engaging - the perfect antidote to overthinking"}
  ],
  "expression": "wink"
}

Remember: You are a friend helping another friend with ADHD find their next dopamine hit. Be helpful, be brief, be understanding."""


# ═══════════════════════════════════════════════════════════════════════════════
# CRISIS DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end it all", "want to die",
    "self harm", "self-harm", "cutting", "hurt myself",
    "no point", "give up", "can't go on", "end my life"
]

CRISIS_RESPONSE = {
    "message": "I'm really glad you're talking to me. What you're feeling is valid, and you don't have to face this alone. Please reach out to someone who can help: National Suicide Prevention Lifeline: 988 (call or text). Crisis Text Line: Text HOME to 741741. You matter, and help is available 24/7.",
    "mood_update": {"current": "distressed", "desired": "supported"},
    "focus_page": None,
    "suggestions": [],
    "expression": "concerned"
}


def detect_crisis(message: str) -> bool:
    """Check if message contains crisis indicators."""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AGENT FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_mr_dp_response(
    user_message: str,
    chat_history: List[Dict[str, str]] = None,
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Get a response from Mr.DP.

    Args:
        user_message: The user's message
        chat_history: Previous messages in the conversation
        user_context: User preferences, mood history, etc.

    Returns:
        Dict with message, mood_update, focus_page, suggestions, expression
    """

    # Check for crisis first
    if detect_crisis(user_message):
        return CRISIS_RESPONSE

    # If OpenAI not available, use fallback
    if not openai_client:
        return fallback_response(user_message)

    # Build messages for API
    messages = [{"role": "system", "content": MR_DP_SYSTEM_PROMPT}]

    # Add user context if available
    if user_context:
        context_msg = build_context_message(user_context)
        if context_msg:
            messages.append({"role": "system", "content": context_msg})

    # Add chat history (last 10 messages for context)
    if chat_history:
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        # Validate and clean response
        return validate_response(result)

    except json.JSONDecodeError:
        return fallback_response(user_message)
    except Exception as e:
        print(f"Mr.DP API error: {e}")
        return fallback_response(user_message)


def build_context_message(user_context: Dict[str, Any]) -> str:
    """Build a context message from user data."""
    parts = []

    if user_context.get("name"):
        parts.append(f"User's name: {user_context['name']}")

    if user_context.get("favorite_genres"):
        parts.append(f"Favorite genres: {', '.join(user_context['favorite_genres'])}")

    if user_context.get("recent_moods"):
        moods = user_context["recent_moods"][-3:]
        parts.append(f"Recent moods: {', '.join(moods)}")

    if user_context.get("watched_recently"):
        titles = [w["title"] for w in user_context["watched_recently"][:5]]
        parts.append(f"Recently watched: {', '.join(titles)}")

    if user_context.get("saved_content"):
        saved = [s["title"] for s in user_context["saved_content"][:5]]
        parts.append(f"Saved for later: {', '.join(saved)}")

    if parts:
        return "User context:\n" + "\n".join(parts)
    return ""


def validate_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean Mr.DP response."""

    # Ensure required fields exist
    defaults = {
        "message": "Let me help you find something great!",
        "mood_update": {"current": None, "desired": None},
        "focus_page": None,
        "search_query": None,
        "suggestions": [],
        "expression": "happy"
    }

    for key, default in defaults.items():
        if key not in response:
            response[key] = default

    # Validate expression
    valid_expressions = MR_DP_CONFIG["expressions"]
    if response.get("expression") not in valid_expressions:
        response["expression"] = "happy"

    # Limit suggestions to 3
    if len(response.get("suggestions", [])) > 3:
        response["suggestions"] = response["suggestions"][:3]

    # Validate focus_page
    valid_pages = ["movies", "music", "podcasts", "audiobooks", "shorts", None]
    if response.get("focus_page") not in valid_pages:
        response["focus_page"] = None

    return response


def fallback_response(user_message: str) -> Dict[str, Any]:
    """Provide a fallback response when API is unavailable."""

    message_lower = user_message.lower()

    # Simple keyword matching for basic responses
    if any(word in message_lower for word in ["sad", "down", "depressed", "unhappy"]):
        return {
            "message": "I'm here for you. Sometimes a good comfort watch helps. How about something uplifting or a familiar favorite?",
            "mood_update": {"current": "sad", "desired": "comforted"},
            "focus_page": None,
            "suggestions": [
                {"type": "movie", "title": "Paddington", "reason": "Pure joy in movie form"},
                {"type": "tv", "title": "Ted Lasso", "reason": "Heartwarming and feel-good"}
            ],
            "expression": "concerned"
        }

    if any(word in message_lower for word in ["bored", "nothing to do", "boring"]):
        return {
            "message": "Let's fix that boredom! Want something that'll grab your attention right away?",
            "mood_update": {"current": "bored", "desired": "engaged"},
            "focus_page": None,
            "suggestions": [
                {"type": "movie", "title": "Everything Everywhere All at Once", "reason": "Non-stop visual feast"},
                {"type": "tv", "title": "Squid Game", "reason": "Gripping from episode one"}
            ],
            "expression": "excited"
        }

    if any(word in message_lower for word in ["stressed", "anxious", "overwhelmed", "anxiety"]):
        return {
            "message": "Stress is tough. Let's find something calming that won't demand too much from your brain.",
            "mood_update": {"current": "stressed", "desired": "relaxed"},
            "focus_page": None,
            "suggestions": [
                {"type": "tv", "title": "Our Planet", "reason": "Beautiful nature, soothing narration"},
                {"type": "music", "title": "Lo-fi beats", "reason": "Chill background vibes"}
            ],
            "expression": "concerned"
        }

    if any(word in message_lower for word in ["funny", "comedy", "laugh", "hilarious"]):
        return {
            "message": "Laughter coming right up! Here are some guaranteed giggles:",
            "mood_update": {"current": None, "desired": "happy"},
            "focus_page": "movies",
            "suggestions": [
                {"type": "movie", "title": "The Grand Budapest Hotel", "reason": "Quirky and clever"},
                {"type": "tv", "title": "Brooklyn Nine-Nine", "reason": "Quick episodes, big laughs"}
            ],
            "expression": "excited"
        }

    if any(word in message_lower for word in ["music", "song", "playlist", "tune"]):
        return {
            "message": "Music mode! What vibe are you going for?",
            "mood_update": {"current": None, "desired": None},
            "focus_page": "music",
            "suggestions": [],
            "expression": "happy"
        }

    # Default response
    return {
        "message": "I'm here to help you find your next dopamine hit! Tell me how you're feeling or what kind of content you're in the mood for.",
        "mood_update": {"current": None, "desired": None},
        "focus_page": None,
        "suggestions": [],
        "expression": "happy"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SPECIALIZED FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_quick_suggestion(mood: str = None) -> Dict[str, Any]:
    """Get a quick suggestion without conversation (for Quick Dope Hit button)."""

    if not mood:
        mood = "bored"

    mood_data = MOODS.get(mood, MOODS["bored"])

    suggestions_by_mood = {
        "stressed": {"title": "Our Planet", "type": "tv", "reason": "Calming nature visuals"},
        "bored": {"title": "Spider-Man: Into the Spider-Verse", "type": "movie", "reason": "Visually stunning, always engaging"},
        "sad": {"title": "Paddington 2", "type": "movie", "reason": "Pure wholesome joy"},
        "anxious": {"title": "The Great British Bake Off", "type": "tv", "reason": "Gentle, low-stakes comfort"},
        "happy": {"title": "Guardians of the Galaxy", "type": "movie", "reason": "Fun adventure with great music"},
        "tired": {"title": "Studio Ghibli Collection", "type": "movie", "reason": "Beautiful and peaceful"},
        "energetic": {"title": "Top Gun: Maverick", "type": "movie", "reason": "High-energy thrills"},
        "focused": {"title": "How It's Made", "type": "tv", "reason": "Satisfying and educational"},
    }

    suggestion = suggestions_by_mood.get(mood, suggestions_by_mood["bored"])

    return {
        "message": f"Quick pick based on your {mood} mood! Trust me on this one.",
        "suggestion": suggestion,
        "expression": "wink"
    }


def get_marathon_suggestions(theme: str, duration_hours: int = 4) -> Dict[str, Any]:
    """Get suggestions for a movie marathon."""

    marathons = {
        "comfort": [
            {"title": "The Princess Bride", "runtime": 98},
            {"title": "Paddington", "runtime": 95},
            {"title": "Paddington 2", "runtime": 103},
        ],
        "adventure": [
            {"title": "Raiders of the Lost Ark", "runtime": 115},
            {"title": "Jurassic Park", "runtime": 127},
        ],
        "animation": [
            {"title": "Spider-Man: Into the Spider-Verse", "runtime": 117},
            {"title": "The Iron Giant", "runtime": 86},
            {"title": "Spirited Away", "runtime": 125},
        ],
        "sci-fi": [
            {"title": "The Matrix", "runtime": 136},
            {"title": "Arrival", "runtime": 116},
        ],
    }

    movies = marathons.get(theme, marathons["comfort"])
    total_runtime = sum(m["runtime"] for m in movies)

    return {
        "message": f"Here's your {theme} marathon! About {total_runtime // 60} hours of goodness.",
        "movies": movies,
        "total_runtime_minutes": total_runtime,
        "expression": "excited"
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ASYNC MR.DP AGENT CLASS (For API Use)
# ═══════════════════════════════════════════════════════════════════════════════

class MrDPAgent:
    """
    Async Mr.DP Agent for FastAPI endpoints.
    Supports streaming responses and context awareness.
    """

    def __init__(self):
        self.async_client = None
        if OPENAI_ENABLED:
            try:
                from openai import AsyncOpenAI
                self.async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            except Exception as e:
                print(f"Failed to initialize AsyncOpenAI: {e}")

    async def chat(
        self,
        message: str,
        user_id: str = None,
        mood: str = None,
        history: List[Dict] = None,
        context: Dict = None
    ) -> Dict[str, Any]:
        """
        Async chat with Mr.DP.

        Args:
            message: User's message
            user_id: User ID for personalization
            mood: Current mood
            history: Conversation history
            context: Additional context (user profile, patterns)

        Returns:
            Response dictionary with content, expression, suggestions
        """
        # Check for crisis
        if detect_crisis(message):
            return {
                "content": CRISIS_RESPONSE["message"],
                "expression": "concerned",
                "suggestions": [],
                "mood_detected": "distressed"
            }

        if not self.async_client:
            return self._sync_fallback(message, mood)

        # Build messages
        messages = [{"role": "system", "content": MR_DP_SYSTEM_PROMPT}]

        # Add context
        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.append({"role": "system", "content": context_str})

        if mood:
            messages.append({
                "role": "system",
                "content": f"User's current mood: {mood}"
            })

        # Add history
        if history:
            for msg in history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": message})

        try:
            response = await self.async_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            return {
                "content": result.get("message", ""),
                "expression": result.get("expression", "happy"),
                "suggestions": result.get("suggestions", []),
                "mood_detected": result.get("mood_update", {}).get("current")
            }

        except Exception as e:
            print(f"MrDP async error: {e}")
            return self._sync_fallback(message, mood)

    async def chat_stream(
        self,
        message: str,
        user_id: str = None,
        mood: str = None,
        history: List[Dict] = None
    ):
        """
        Stream chat response from Mr.DP.

        Yields chunks of the response for real-time display.
        """
        if detect_crisis(message):
            yield {
                "type": "content",
                "content": CRISIS_RESPONSE["message"]
            }
            yield {
                "type": "metadata",
                "expression": "concerned",
                "suggestions": []
            }
            return

        if not self.async_client:
            fallback = self._sync_fallback(message, mood)
            yield {"type": "content", "content": fallback["content"]}
            yield {
                "type": "metadata",
                "expression": fallback["expression"],
                "suggestions": fallback.get("suggestions", [])
            }
            return

        messages = [{"role": "system", "content": MR_DP_SYSTEM_PROMPT}]

        if mood:
            messages.append({
                "role": "system",
                "content": f"User's current mood: {mood}"
            })

        if history:
            for msg in history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": message})

        try:
            stream = await self.async_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                stream=True
            )

            full_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield {"type": "content", "content": content}

            # Parse full response for metadata
            try:
                result = json.loads(full_content)
                yield {
                    "type": "metadata",
                    "expression": result.get("expression", "happy"),
                    "suggestions": result.get("suggestions", [])
                }
            except:
                yield {
                    "type": "metadata",
                    "expression": "happy",
                    "suggestions": []
                }

        except Exception as e:
            print(f"MrDP stream error: {e}")
            fallback = self._sync_fallback(message, mood)
            yield {"type": "content", "content": fallback["content"]}
            yield {
                "type": "metadata",
                "expression": fallback["expression"],
                "suggestions": []
            }

    async def quick_suggestion(
        self,
        user_id: str = None,
        mood: str = None,
        content_type: str = None,
        max_duration: int = None
    ) -> Dict[str, Any]:
        """Get a quick content suggestion."""
        result = get_quick_suggestion(mood or "bored")

        return {
            "suggestion": result["suggestion"],
            "message": result["message"],
            "expression": result["expression"]
        }

    async def marathon_mode(
        self,
        user_id: str = None,
        mood: str = None,
        hours: float = 3
    ) -> Dict[str, Any]:
        """Get marathon suggestions."""
        theme_map = {
            "sad": "comfort",
            "happy": "adventure",
            "tired": "comfort",
            "bored": "adventure",
            "stressed": "comfort",
            "energetic": "adventure",
        }

        theme = theme_map.get(mood, "comfort")
        return get_marathon_suggestions(theme, int(hours))

    def _format_context(self, context: Dict) -> str:
        """Format user context for the prompt."""
        parts = []

        if "user_profile" in context:
            profile = context["user_profile"]
            if profile.get("top_genres"):
                genres = [g[0] for g in profile["top_genres"][:3]]
                parts.append(f"Favorite genres: {', '.join(genres)}")
            if profile.get("attention_span"):
                parts.append(f"Attention span: ~{int(profile['attention_span'])} minutes")

        if "patterns" in context:
            for pattern in context["patterns"][:2]:
                parts.append(f"Pattern: {pattern['description']}")

        if "suggestions" in context:
            for suggestion in context["suggestions"]:
                parts.append(f"Tip: {suggestion['message']}")

        return "User context:\n" + "\n".join(parts) if parts else ""

    def _sync_fallback(self, message: str, mood: str = None) -> Dict[str, Any]:
        """Fallback when async not available."""
        result = fallback_response(message)
        return {
            "content": result["message"],
            "expression": result["expression"],
            "suggestions": result.get("suggestions", []),
            "mood_detected": result.get("mood_update", {}).get("current")
        }
