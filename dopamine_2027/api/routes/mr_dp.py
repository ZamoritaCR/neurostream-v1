"""
═══════════════════════════════════════════════════════════════════════════════
MR.DP AI API ROUTES
AI chatbot endpoints for personalized recommendations.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
import json

from services.mr_dp.agent import MrDPAgent
from services.mr_dp.learning import get_learning_service, EventType

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    mood: Optional[str] = None
    history: Optional[List[ChatMessage]] = None
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    expression: str
    suggestions: Optional[List[dict]] = None
    mood_detected: Optional[str] = None


class QuickSuggestionRequest(BaseModel):
    user_id: Optional[str] = None
    mood: Optional[str] = None
    content_type: Optional[str] = None
    max_duration: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════════════════
# CHAT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/chat", response_model=ChatResponse)
async def chat_with_mr_dp(request: ChatRequest):
    """
    Chat with Mr.DP for personalized recommendations.

    Mr.DP understands:
    - Mood and emotional state
    - Time constraints ("I have 20 minutes")
    - Content preferences
    - ADHD-specific needs
    """
    agent = MrDPAgent()

    # Build conversation history
    history = []
    if request.history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]

    # Get user context if available
    context = {}
    if request.user_id:
        learning = get_learning_service()
        context = learning.get_mrdp_context(request.user_id)

    # Get response
    response = await agent.chat(
        message=request.message,
        user_id=request.user_id,
        mood=request.mood,
        history=history,
        context=context
    )

    # Track interaction
    if request.user_id:
        learning = get_learning_service()
        await learning.track_event(
            request.user_id,
            EventType.MRDP_CHAT,
            {"message_length": len(request.message)}
        )

    return ChatResponse(
        response=response.get("content", ""),
        expression=response.get("expression", "happy"),
        suggestions=response.get("suggestions"),
        mood_detected=response.get("mood_detected")
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat response from Mr.DP.

    Returns Server-Sent Events for real-time streaming.
    """
    agent = MrDPAgent()

    history = []
    if request.history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.history
        ]

    async def generate():
        async for chunk in agent.chat_stream(
            message=request.message,
            user_id=request.user_id,
            mood=request.mood,
            history=history
        ):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK ACTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/quick-suggestion")
async def get_quick_suggestion(request: QuickSuggestionRequest):
    """
    Get a quick content suggestion without full chat.

    Perfect for "Quick Dope Hit" button.
    """
    agent = MrDPAgent()

    suggestion = await agent.quick_suggestion(
        user_id=request.user_id,
        mood=request.mood,
        content_type=request.content_type,
        max_duration=request.max_duration
    )

    # Track if user_id provided
    if request.user_id:
        learning = get_learning_service()
        await learning.track_event(
            request.user_id,
            EventType.MRDP_CHAT,
            {"action": "quick_suggestion", "mood": request.mood}
        )

    return suggestion


@router.get("/quick-dope-hit")
async def quick_dope_hit(
    user_id: Optional[str] = None,
    mood: Optional[str] = None,
    max_minutes: int = 30
):
    """
    Instant dopamine hit - get a quick recommendation.

    ADHD-optimized for immediate gratification.
    """
    agent = MrDPAgent()

    return await agent.quick_suggestion(
        user_id=user_id,
        mood=mood,
        max_duration=max_minutes
    )


@router.get("/marathon-mode")
async def marathon_mode(
    user_id: Optional[str] = None,
    mood: Optional[str] = None,
    hours: float = 3
):
    """
    Get a curated marathon session.

    Perfect for hyperfocus sessions.
    """
    agent = MrDPAgent()

    return await agent.marathon_mode(
        user_id=user_id,
        mood=mood,
        hours=hours
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MOOD & EXPRESSION
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/expressions")
async def get_expressions():
    """Get all available Mr.DP expressions."""
    return {
        "expressions": [
            {"id": "happy", "emoji": "😊", "description": "Default happy state"},
            {"id": "excited", "emoji": "🤩", "description": "Found something great"},
            {"id": "thinking", "emoji": "🤔", "description": "Processing request"},
            {"id": "curious", "emoji": "🧐", "description": "Wants to know more"},
            {"id": "empathetic", "emoji": "🥺", "description": "Understanding feelings"},
            {"id": "encouraging", "emoji": "💪", "description": "Motivating user"},
            {"id": "playful", "emoji": "😜", "description": "Fun mood"},
            {"id": "wise", "emoji": "🦉", "description": "Sharing wisdom"},
            {"id": "sleepy", "emoji": "😴", "description": "Late night mode"},
            {"id": "celebrating", "emoji": "🎉", "description": "Achievement unlocked"},
            {"id": "concerned", "emoji": "😟", "description": "Checking in on user"},
            {"id": "loving", "emoji": "🥰", "description": "Showing appreciation"}
        ]
    }


@router.get("/mood-suggestions/{mood}")
async def mood_suggestions(mood: str):
    """Get Mr.DP's suggestions based on specific mood."""
    mood_responses = {
        "happy": {
            "expression": "excited",
            "message": "You're feeling great! Let's find something to keep that energy going!",
            "content_types": ["comedy", "adventure", "feel-good"]
        },
        "sad": {
            "expression": "empathetic",
            "message": "I'm here for you. Want something comforting or something to lift your spirits?",
            "content_types": ["comfort", "heartwarming", "inspiring"]
        },
        "anxious": {
            "expression": "concerned",
            "message": "Take a deep breath. I've got some calming content that might help.",
            "content_types": ["calming", "nature", "meditation"]
        },
        "bored": {
            "expression": "playful",
            "message": "Boredom? Not on my watch! Let's find something exciting!",
            "content_types": ["thriller", "mystery", "documentary"]
        },
        "tired": {
            "expression": "sleepy",
            "message": "Feeling tired? How about something easy to watch?",
            "content_types": ["comfort", "familiar", "light"]
        },
        "energetic": {
            "expression": "celebrating",
            "message": "I love that energy! Let's match it with something exciting!",
            "content_types": ["action", "music", "adventure"]
        },
        "focused": {
            "expression": "wise",
            "message": "Focus mode activated! I've got some great recommendations.",
            "content_types": ["documentary", "educational", "ambient"]
        }
    }

    response = mood_responses.get(mood.lower(), {
        "expression": "curious",
        "message": f"Tell me more about feeling {mood}!",
        "content_types": ["varied"]
    })

    return response


# ═══════════════════════════════════════════════════════════════════════════════
# FEEDBACK
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/feedback/suggestion")
async def suggestion_feedback(
    user_id: str,
    content_id: str,
    accepted: bool,
    content_type: Optional[str] = None,
    genres: Optional[List[str]] = None
):
    """
    Track whether user accepted or rejected a suggestion.

    This helps Mr.DP learn user preferences.
    """
    learning = get_learning_service()

    event_type = (
        EventType.MRDP_SUGGESTION_ACCEPT if accepted
        else EventType.MRDP_SUGGESTION_REJECT
    )

    await learning.track_event(
        user_id,
        event_type,
        {
            "content_id": content_id,
            "content_type": content_type,
            "genres": genres or []
        }
    )

    return {
        "status": "recorded",
        "message": "Thanks for the feedback! I'm learning your preferences."
    }
