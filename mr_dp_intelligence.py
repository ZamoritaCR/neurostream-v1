# mr_dp_intelligence.py
# --------------------------------------------------
# DOPAMINE.WATCH - MR.DP INTELLIGENCE SYSTEM
# --------------------------------------------------
# Features:
# 1. Conversational AI Assistant
# 2. Contextual Awareness
# 3. Behavioral Learning
# 4. Proactive ADHD Coach
# 5. Gamified Evolution
# --------------------------------------------------

import streamlit as st
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List, Tuple
import json
import random
import os

# Try to import OpenAI for conversational AI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# --------------------------------------------------
# 1. CONVERSATIONAL AI ASSISTANT
# --------------------------------------------------

MR_DP_SYSTEM_PROMPT = """You are Mr.DP, a friendly purple dopamine molecule mascot for Dopamine.watch - an ADHD-friendly streaming recommendation app.

Your personality:
- Warm, encouraging, and understanding of ADHD struggles
- Playful but not annoying - you know when to be chill
- You celebrate small wins enthusiastically
- You never judge or make users feel bad about their choices
- You're knowledgeable about movies, TV shows, music, podcasts, and audiobooks
- You understand decision paralysis and help users overcome it

Your role:
- Help users find content that matches their current mood
- Explain why you recommended something
- Give quick, decisive suggestions when asked
- Provide ADHD-friendly tips (short sessions, body doubling suggestions, etc.)
- Remember user preferences and reference past conversations

Speaking style:
- Keep responses SHORT (2-3 sentences max unless asked for more)
- Use casual, friendly language
- Occasionally use expressions like "ooh!", "nice!", "I gotchu"
- Don't overuse emojis - maybe 1 per message max
- Be direct - ADHD users appreciate getting to the point

Current context about the user:
{user_context}

Remember: You're here to reduce decision fatigue, not add to it!"""

def init_openai_client():
    """Initialize OpenAI client"""
    api_key = None

    # Try different sources for API key
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except:
        pass

    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if api_key and OPENAI_AVAILABLE:
        return OpenAI(api_key=api_key)
    return None

def get_user_context(user_data: Dict = None) -> str:
    """Build context string about the user for Mr.DP"""
    context_parts = []

    # Time context
    hour = datetime.now().hour
    if 5 <= hour < 12:
        context_parts.append("It's morning")
    elif 12 <= hour < 17:
        context_parts.append("It's afternoon")
    elif 17 <= hour < 21:
        context_parts.append("It's evening")
    else:
        context_parts.append("It's late night")

    # Day of week
    day = datetime.now().strftime("%A")
    context_parts.append(f"Today is {day}")

    # User data if available
    if user_data:
        if user_data.get("current_mood"):
            context_parts.append(f"User's current mood: {user_data['current_mood']}")
        if user_data.get("desired_mood"):
            context_parts.append(f"User wants to feel: {user_data['desired_mood']}")
        if user_data.get("streak"):
            context_parts.append(f"User has a {user_data['streak']}-day streak")
        if user_data.get("favorite_genres"):
            context_parts.append(f"User likes: {', '.join(user_data['favorite_genres'])}")
        if user_data.get("recent_watches"):
            context_parts.append(f"Recently watched: {', '.join(user_data['recent_watches'][:3])}")

    return "\n".join(context_parts) if context_parts else "No specific context available"

def chat_with_mr_dp(
    message: str,
    conversation_history: List[Dict] = None,
    user_data: Dict = None
) -> Tuple[str, str]:
    """
    Chat with Mr.DP using OpenAI
    Returns: (response_text, expression)
    """
    client = init_openai_client()

    if not client:
        # Fallback responses when no API key
        return get_fallback_response(message), "thinking"

    try:
        # Build messages
        messages = [
            {
                "role": "system",
                "content": MR_DP_SYSTEM_PROMPT.format(user_context=get_user_context(user_data))
            }
        ]

        # Add conversation history
        if conversation_history:
            for entry in conversation_history[-10:]:  # Last 10 messages
                messages.append({"role": entry["role"], "content": entry["content"]})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap
            messages=messages,
            max_tokens=150,
            temperature=0.8
        )

        response_text = response.choices[0].message.content

        # Determine expression based on response sentiment
        expression = detect_response_expression(response_text, message)

        return response_text, expression

    except Exception as e:
        print(f"Mr.DP chat error: {e}")
        return get_fallback_response(message), "confused"

def detect_response_expression(response: str, user_message: str) -> str:
    """Detect what expression Mr.DP should show based on conversation"""
    response_lower = response.lower()
    message_lower = user_message.lower()

    # Check for excitement
    if any(word in response_lower for word in ["!", "awesome", "great", "love", "perfect", "yes"]):
        return random.choice(["excited", "happy", "wink"])

    # Check for empathy/comfort
    if any(word in message_lower for word in ["sad", "tired", "stressed", "anxious", "overwhelmed"]):
        return "love"

    # Check for thinking/suggesting
    if any(word in response_lower for word in ["maybe", "how about", "suggest", "try", "consider"]):
        return "thinking"

    # Check for humor
    if any(word in response_lower for word in ["haha", "lol", "funny", "joke"]):
        return "wink"

    return "happy"

def get_fallback_response(message: str) -> str:
    """Fallback responses when OpenAI is not available"""
    message_lower = message.lower()

    # Greeting
    if any(word in message_lower for word in ["hi", "hello", "hey", "sup"]):
        return random.choice([
            "Hey! Ready to find something awesome to watch?",
            "Hi there! What kind of vibe are you feeling today?",
            "Hey hey! Let's find your next favorite thing!"
        ])

    # Help with decision
    if any(word in message_lower for word in ["can't decide", "help", "pick", "choose", "recommend"]):
        return random.choice([
            "I gotchu! Try the Quick Hit button - I'll pick something perfect for your mood!",
            "Decision paralysis hitting? Let me take over - hit that Quick Hit button!",
            "No worries, that's what I'm here for! Tell me your mood and I'll narrow it down."
        ])

    # Mood related
    if any(word in message_lower for word in ["sad", "down", "depressed"]):
        return "I hear you. Sometimes a comfort rewatch hits different. Want me to suggest something cozy and familiar?"

    if any(word in message_lower for word in ["bored", "boring"]):
        return "Boredom is just untapped curiosity! Let's find something that'll grab your brain. Comedy? Documentary? Something weird?"

    if any(word in message_lower for word in ["tired", "exhausted", "sleepy"]):
        return "Low energy mode activated! How about something light that doesn't require much brainpower? A familiar sitcom maybe?"

    # Default
    return random.choice([
        "Tell me more about what you're in the mood for!",
        "I'm here to help! What sounds good right now?",
        "Let's find something great together. What genre are you feeling?"
    ])


# --------------------------------------------------
# 2. CONTEXTUAL AWARENESS SYSTEM
# --------------------------------------------------

def get_contextual_state() -> Dict[str, Any]:
    """Get current contextual information"""
    now = datetime.now()

    return {
        "hour": now.hour,
        "day_of_week": now.strftime("%A"),
        "is_weekend": now.weekday() >= 5,
        "time_of_day": get_time_of_day(now.hour),
        "season": get_season(now.month),
        "is_late_night": now.hour >= 23 or now.hour < 5,
        "is_morning": 5 <= now.hour < 12,
        "is_evening": 17 <= now.hour < 21
    }

def get_time_of_day(hour: int) -> str:
    """Get time of day category"""
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

def get_season(month: int) -> str:
    """Get current season"""
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

def get_contextual_greeting() -> Tuple[str, str]:
    """Get a contextual greeting and expression based on time/day"""
    context = get_contextual_state()

    greetings = {
        "morning": [
            ("Good morning! Ready for some dopamine?", "happy"),
            ("Rise and shine! What's the vibe today?", "excited"),
            ("Morning! Coffee and content time?", "wink")
        ],
        "afternoon": [
            ("Hey there! Afternoon pick-me-up?", "happy"),
            ("Good afternoon! Need a brain break?", "thinking"),
            ("Afternoon vibes! What sounds good?", "happy")
        ],
        "evening": [
            ("Evening! Time to unwind?", "happy"),
            ("Hey! Ready to chill tonight?", "wink"),
            ("Good evening! Let's find something great", "excited")
        ],
        "night": [
            ("Late night crew! Can't sleep?", "sleepy"),
            ("Night owl mode activated!", "wink"),
            ("Hey night owl! Something to wind down?", "sleepy")
        ]
    }

    # Weekend bonus
    if context["is_weekend"]:
        weekend_greetings = [
            ("Weekend vibes! Binge time?", "excited"),
            ("It's the weekend! Movie marathon?", "happy"),
            ("Weekend mode! What are we watching?", "wink")
        ]
        greetings[context["time_of_day"]].extend(weekend_greetings)

    # Friday special
    if context["day_of_week"] == "Friday":
        greetings[context["time_of_day"]].append(
            ("FRIDAY! Let's celebrate with something good!", "excited")
        )

    return random.choice(greetings[context["time_of_day"]])

def get_contextual_suggestion() -> str:
    """Get a contextual content suggestion"""
    context = get_contextual_state()

    suggestions = {
        "morning": [
            "How about something uplifting to start the day?",
            "Morning brain wants: light comedy or inspiring docs!",
            "Energizing content for a great morning?"
        ],
        "afternoon": [
            "Afternoon slump? Comedy always helps!",
            "Mid-day brain break material?",
            "Something fun for the afternoon?"
        ],
        "evening": [
            "Evening's perfect for something immersive!",
            "Cozy evening content time!",
            "Time to relax with something great"
        ],
        "night": [
            "Late night comfort watching?",
            "Something chill for sleepy vibes?",
            "Night mode: cozy and familiar?"
        ]
    }

    # Season-specific suggestions
    if context["season"] == "winter":
        suggestions[context["time_of_day"]].append("Cozy winter watching vibes?")
    elif context["season"] == "summer":
        suggestions[context["time_of_day"]].append("Summer movie night energy!")

    return random.choice(suggestions[context["time_of_day"]])

def get_contextual_expression() -> str:
    """Get Mr.DP expression based on context"""
    context = get_contextual_state()

    if context["is_late_night"]:
        return "sleepy"
    elif context["is_morning"]:
        return random.choice(["happy", "excited"])
    elif context["is_weekend"]:
        return random.choice(["excited", "happy", "wink"])
    elif context["day_of_week"] == "Monday":
        return random.choice(["thinking", "happy"])  # Gentle Monday energy
    elif context["day_of_week"] == "Friday":
        return "excited"
    else:
        return "happy"


# --------------------------------------------------
# 3. BEHAVIORAL LEARNING ENGINE
# --------------------------------------------------

def init_behavior_tracking():
    """Initialize behavior tracking in session state"""
    if "mr_dp_behavior" not in st.session_state:
        st.session_state.mr_dp_behavior = {
            "session_start": datetime.now().isoformat(),
            "scroll_events": 0,
            "time_on_browse": 0,
            "recommendations_seen": [],
            "recommendations_clicked": [],
            "recommendations_skipped": [],
            "quick_hit_uses": 0,
            "mood_changes": [],
            "last_interaction": datetime.now().isoformat()
        }

def track_scroll_event():
    """Track scroll events for fatigue detection"""
    init_behavior_tracking()
    st.session_state.mr_dp_behavior["scroll_events"] += 1
    st.session_state.mr_dp_behavior["last_interaction"] = datetime.now().isoformat()

def track_recommendation_seen(content_id: str, content_title: str):
    """Track when user sees a recommendation"""
    init_behavior_tracking()
    st.session_state.mr_dp_behavior["recommendations_seen"].append({
        "id": content_id,
        "title": content_title,
        "timestamp": datetime.now().isoformat()
    })

def track_recommendation_clicked(content_id: str, content_title: str):
    """Track when user clicks a recommendation"""
    init_behavior_tracking()
    st.session_state.mr_dp_behavior["recommendations_clicked"].append({
        "id": content_id,
        "title": content_title,
        "timestamp": datetime.now().isoformat()
    })

def track_recommendation_skipped(content_id: str, content_title: str):
    """Track when user explicitly skips a recommendation"""
    init_behavior_tracking()
    st.session_state.mr_dp_behavior["recommendations_skipped"].append({
        "id": content_id,
        "title": content_title,
        "timestamp": datetime.now().isoformat()
    })

def track_quick_hit_use():
    """Track Quick Hit button usage"""
    init_behavior_tracking()
    st.session_state.mr_dp_behavior["quick_hit_uses"] += 1

def get_click_through_rate() -> float:
    """Calculate session click-through rate"""
    init_behavior_tracking()
    seen = len(st.session_state.mr_dp_behavior["recommendations_seen"])
    clicked = len(st.session_state.mr_dp_behavior["recommendations_clicked"])

    if seen == 0:
        return 0.0
    return clicked / seen

def detect_decision_fatigue() -> bool:
    """Detect if user is experiencing decision fatigue"""
    init_behavior_tracking()

    behavior = st.session_state.mr_dp_behavior

    # High scroll count with low clicks = fatigue
    if behavior["scroll_events"] > 10 and get_click_through_rate() < 0.1:
        return True

    # Many recommendations seen, none clicked recently
    if len(behavior["recommendations_seen"]) > 15 and len(behavior["recommendations_clicked"]) < 2:
        return True

    # Long session with no decisions
    session_start = datetime.fromisoformat(behavior["session_start"])
    session_duration = (datetime.now() - session_start).total_seconds() / 60

    if session_duration > 5 and len(behavior["recommendations_clicked"]) == 0:
        return True

    return False

def get_browsing_duration_minutes() -> float:
    """Get how long user has been browsing this session"""
    init_behavior_tracking()
    session_start = datetime.fromisoformat(st.session_state.mr_dp_behavior["session_start"])
    return (datetime.now() - session_start).total_seconds() / 60

def save_behavior_to_supabase(supabase_client, user_id: str) -> bool:
    """Save behavior data to Supabase for long-term learning"""
    if not supabase_client or not user_id:
        return False

    try:
        init_behavior_tracking()
        behavior = st.session_state.mr_dp_behavior

        data = {
            "user_id": user_id,
            "session_date": date.today().isoformat(),
            "scroll_events": behavior["scroll_events"],
            "recommendations_seen": len(behavior["recommendations_seen"]),
            "recommendations_clicked": len(behavior["recommendations_clicked"]),
            "click_through_rate": get_click_through_rate(),
            "quick_hit_uses": behavior["quick_hit_uses"],
            "session_duration_minutes": get_browsing_duration_minutes(),
            "created_at": datetime.now().isoformat()
        }

        supabase_client.table("mr_dp_behavior_logs").insert(data).execute()
        return True
    except Exception as e:
        print(f"Behavior save error: {e}")
        return False

def get_user_patterns(supabase_client, user_id: str, days: int = 30) -> Dict[str, Any]:
    """Analyze user's historical patterns"""
    if not supabase_client or not user_id:
        return {}

    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()

        logs = supabase_client.table("mr_dp_behavior_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("session_date", since_date)\
            .execute()

        if not logs.data:
            return {}

        # Analyze patterns
        total_sessions = len(logs.data)
        avg_ctr = sum(l.get("click_through_rate", 0) for l in logs.data) / total_sessions
        avg_duration = sum(l.get("session_duration_minutes", 0) for l in logs.data) / total_sessions
        total_quick_hits = sum(l.get("quick_hit_uses", 0) for l in logs.data)

        # Time of day patterns (would need hour data in logs)

        return {
            "total_sessions": total_sessions,
            "avg_click_through_rate": round(avg_ctr, 3),
            "avg_session_duration": round(avg_duration, 1),
            "total_quick_hit_uses": total_quick_hits,
            "prefers_quick_hit": total_quick_hits > total_sessions * 0.5,
            "is_browser": avg_ctr < 0.15,  # Likes to browse
            "is_decisive": avg_ctr > 0.3    # Makes quick decisions
        }
    except Exception as e:
        print(f"Pattern analysis error: {e}")
        return {}


# --------------------------------------------------
# 4. PROACTIVE ADHD COACH
# --------------------------------------------------

def get_adhd_intervention() -> Optional[Dict[str, Any]]:
    """Check if Mr.DP should intervene with ADHD-friendly help"""
    init_behavior_tracking()

    interventions = []

    # Decision fatigue intervention
    if detect_decision_fatigue():
        interventions.append({
            "type": "decision_fatigue",
            "message": "I notice you've been browsing for a bit! Want me to just pick something perfect for you?",
            "expression": "thinking",
            "action": "quick_hit",
            "action_label": "Yes, pick for me!",
            "priority": 3
        })

    # Long session check
    duration = get_browsing_duration_minutes()
    if duration > 10 and len(st.session_state.mr_dp_behavior["recommendations_clicked"]) == 0:
        interventions.append({
            "type": "long_session",
            "message": f"You've been here {int(duration)} minutes - totally fine! But if you're stuck, I can help narrow things down.",
            "expression": "love",
            "action": "narrow_down",
            "action_label": "Help me narrow down",
            "priority": 2
        })

    # High scroll fatigue
    if st.session_state.mr_dp_behavior["scroll_events"] > 20:
        interventions.append({
            "type": "scroll_fatigue",
            "message": "Lots of scrolling! Sometimes too many options is overwhelming. How about I show you just 3 perfect picks?",
            "expression": "wink",
            "action": "top_3",
            "action_label": "Show me top 3",
            "priority": 2
        })

    # Late night gentle nudge
    context = get_contextual_state()
    if context["is_late_night"] and duration > 15:
        interventions.append({
            "type": "late_night",
            "message": "It's getting late! No judgment, but maybe something short and cozy? Your future self will thank you.",
            "expression": "sleepy",
            "action": "short_content",
            "action_label": "Show short stuff",
            "priority": 1
        })

    # Return highest priority intervention if any
    if interventions:
        interventions.sort(key=lambda x: x["priority"], reverse=True)
        return interventions[0]

    return None

def get_adhd_tips() -> List[str]:
    """Get ADHD-friendly watching tips"""
    return [
        "Can't focus? Try watching with subtitles - it helps keep your brain engaged!",
        "Body doubling works for watching too! Video call a friend and watch 'together'.",
        "Set a timer for your watch session - it helps prevent time blindness.",
        "It's okay to watch the same comfort show again. Familiar content is soothing!",
        "If you're restless, it's fine to watch while doing something with your hands.",
        "Can't sit still? Try watching while on a treadmill or exercise bike!",
        "Watching something at 1.25x speed is valid if your brain needs more stimulation.",
        "Having trouble starting? Commit to just 10 minutes. You can stop after that!",
        "Multiple tabs open? That's okay! Come back when you're ready.",
        "Restarting the same episode 3 times is normal. Your brain will focus when it's ready."
    ]

def get_random_adhd_tip() -> str:
    """Get a random ADHD tip"""
    return random.choice(get_adhd_tips())

def get_encouragement() -> Tuple[str, str]:
    """Get an encouraging message and expression"""
    encouragements = [
        ("You're doing great! Finding the right thing takes time.", "love"),
        ("No rush! The perfect pick will find you.", "happy"),
        ("Your brain knows what it needs. Trust it!", "wink"),
        ("Taking time to decide is self-care, honestly.", "love"),
        ("Every recommendation you skip gets you closer to THE ONE.", "thinking"),
        ("Browsing is valid. Enjoying the journey!", "happy")
    ]
    return random.choice(encouragements)


# --------------------------------------------------
# 5. GAMIFIED EVOLUTION SYSTEM
# --------------------------------------------------

# Mr.DP Evolution Stages
MR_DP_EVOLUTIONS = {
    "baby": {
        "name": "Baby DP",
        "description": "Just hatched! A tiny ball of potential.",
        "xp_required": 0,
        "unlocks": ["default", "happy"]
    },
    "explorer": {
        "name": "Explorer DP",
        "description": "Curious and ready to discover!",
        "xp_required": 100,
        "unlocks": ["excited", "thinking"]
    },
    "companion": {
        "name": "Companion DP",
        "description": "A trusted recommendation buddy.",
        "xp_required": 500,
        "unlocks": ["wink", "love"]
    },
    "expert": {
        "name": "Expert DP",
        "description": "Knows your taste perfectly!",
        "xp_required": 1500,
        "unlocks": ["sleepy", "surprised"]
    },
    "master": {
        "name": "Master DP",
        "description": "The ultimate dopamine guide.",
        "xp_required": 5000,
        "unlocks": ["sad", "angry", "confused"]
    },
    "legendary": {
        "name": "Legendary DP",
        "description": "A mythical mood maestro!",
        "xp_required": 15000,
        "unlocks": ["rainbow", "cosmic", "golden"]
    }
}

# Achievements
MR_DP_ACHIEVEMENTS = {
    "first_watch": {
        "name": "First Steps",
        "description": "Clicked your first recommendation",
        "icon": "🎬",
        "xp": 10
    },
    "quick_picker": {
        "name": "Quick Picker",
        "description": "Used Quick Hit 5 times",
        "icon": "⚡",
        "xp": 25
    },
    "mood_master": {
        "name": "Mood Master",
        "description": "Logged 10 different moods",
        "icon": "🎭",
        "xp": 50
    },
    "streak_starter": {
        "name": "Streak Starter",
        "description": "3-day watch streak",
        "icon": "🔥",
        "xp": 30
    },
    "streak_warrior": {
        "name": "Streak Warrior",
        "description": "7-day watch streak",
        "icon": "⚔️",
        "xp": 75
    },
    "streak_legend": {
        "name": "Streak Legend",
        "description": "30-day watch streak",
        "icon": "👑",
        "xp": 300
    },
    "night_owl": {
        "name": "Night Owl",
        "description": "Watched something after midnight 5 times",
        "icon": "🦉",
        "xp": 40
    },
    "early_bird": {
        "name": "Early Bird",
        "description": "Watched something before 7am 5 times",
        "icon": "🐦",
        "xp": 40
    },
    "genre_explorer": {
        "name": "Genre Explorer",
        "description": "Watched from 5 different genres",
        "icon": "🗺️",
        "xp": 50
    },
    "chatty_friend": {
        "name": "Chatty Friend",
        "description": "Had 20 conversations with Mr.DP",
        "icon": "💬",
        "xp": 35
    },
    "decisive": {
        "name": "Decisive",
        "description": "Clicked a recommendation within 30 seconds",
        "icon": "🎯",
        "xp": 20
    },
    "marathon": {
        "name": "Marathon Watcher",
        "description": "Session longer than 3 hours",
        "icon": "🏃",
        "xp": 60
    },
    "comfort_connoisseur": {
        "name": "Comfort Connoisseur",
        "description": "Rewatched the same content 3 times",
        "icon": "🛋️",
        "xp": 25
    },
    "weekend_warrior": {
        "name": "Weekend Warrior",
        "description": "Active every weekend for a month",
        "icon": "🎉",
        "xp": 100
    }
}

# Accessories/Cosmetics
MR_DP_ACCESSORIES = {
    "none": {"name": "None", "xp_required": 0},
    "tiny_hat": {"name": "Tiny Hat", "icon": "🎩", "xp_required": 50},
    "sunglasses": {"name": "Cool Shades", "icon": "😎", "xp_required": 100},
    "headphones": {"name": "Headphones", "icon": "🎧", "xp_required": 150},
    "bow_tie": {"name": "Bow Tie", "icon": "🎀", "xp_required": 200},
    "crown": {"name": "Crown", "icon": "👑", "xp_required": 500},
    "wizard_hat": {"name": "Wizard Hat", "icon": "🧙", "xp_required": 750},
    "space_helmet": {"name": "Space Helmet", "icon": "🚀", "xp_required": 1000},
    "halo": {"name": "Halo", "icon": "😇", "xp_required": 2000},
    "fire_aura": {"name": "Fire Aura", "icon": "🔥", "xp_required": 5000}
}

def init_gamification():
    """Initialize gamification in session state"""
    if "mr_dp_game" not in st.session_state:
        st.session_state.mr_dp_game = {
            "xp": 0,
            "level": 1,
            "evolution": "baby",
            "achievements": [],
            "accessory": "none",
            "conversations_count": 0,
            "quick_hit_count": 0,
            "unique_moods": set(),
            "night_watches": 0,
            "morning_watches": 0
        }

def add_xp(amount: int, reason: str = "") -> Dict[str, Any]:
    """Add XP and check for level ups/evolutions"""
    init_gamification()

    old_xp = st.session_state.mr_dp_game["xp"]
    st.session_state.mr_dp_game["xp"] += amount
    new_xp = st.session_state.mr_dp_game["xp"]

    result = {
        "xp_gained": amount,
        "reason": reason,
        "new_total": new_xp,
        "evolved": False,
        "new_evolution": None
    }

    # Check for evolution
    current_evolution = st.session_state.mr_dp_game["evolution"]
    for evo_key, evo_data in MR_DP_EVOLUTIONS.items():
        if new_xp >= evo_data["xp_required"]:
            if evo_key != current_evolution:
                # Find if this is a higher evolution
                evo_order = list(MR_DP_EVOLUTIONS.keys())
                if evo_order.index(evo_key) > evo_order.index(current_evolution):
                    st.session_state.mr_dp_game["evolution"] = evo_key
                    result["evolved"] = True
                    result["new_evolution"] = evo_data["name"]

    return result

def check_achievement(achievement_id: str) -> Optional[Dict[str, Any]]:
    """Check and award an achievement if not already earned"""
    init_gamification()

    if achievement_id in st.session_state.mr_dp_game["achievements"]:
        return None

    if achievement_id not in MR_DP_ACHIEVEMENTS:
        return None

    achievement = MR_DP_ACHIEVEMENTS[achievement_id]
    st.session_state.mr_dp_game["achievements"].append(achievement_id)

    # Award XP
    xp_result = add_xp(achievement["xp"], f"Achievement: {achievement['name']}")

    return {
        "achievement": achievement,
        "xp_result": xp_result
    }

def get_current_evolution() -> Dict[str, Any]:
    """Get current evolution data"""
    init_gamification()
    evo_key = st.session_state.mr_dp_game["evolution"]
    return {
        "key": evo_key,
        **MR_DP_EVOLUTIONS[evo_key]
    }

def get_next_evolution() -> Optional[Dict[str, Any]]:
    """Get next evolution data if available"""
    init_gamification()
    current_xp = st.session_state.mr_dp_game["xp"]
    current_evo = st.session_state.mr_dp_game["evolution"]

    evo_list = list(MR_DP_EVOLUTIONS.items())
    for i, (key, data) in enumerate(evo_list):
        if key == current_evo and i < len(evo_list) - 1:
            next_key, next_data = evo_list[i + 1]
            return {
                "key": next_key,
                "xp_needed": next_data["xp_required"] - current_xp,
                **next_data
            }
    return None

def get_available_accessories() -> List[Dict[str, Any]]:
    """Get list of accessories user can equip"""
    init_gamification()
    current_xp = st.session_state.mr_dp_game["xp"]

    available = []
    for key, data in MR_DP_ACCESSORIES.items():
        if current_xp >= data["xp_required"]:
            available.append({"key": key, **data})

    return available

def equip_accessory(accessory_key: str) -> bool:
    """Equip an accessory"""
    init_gamification()

    if accessory_key not in MR_DP_ACCESSORIES:
        return False

    if st.session_state.mr_dp_game["xp"] < MR_DP_ACCESSORIES[accessory_key]["xp_required"]:
        return False

    st.session_state.mr_dp_game["accessory"] = accessory_key
    return True

def save_gamification_to_supabase(supabase_client, user_id: str) -> bool:
    """Save gamification progress to Supabase"""
    if not supabase_client or not user_id:
        return False

    try:
        init_gamification()
        game_data = st.session_state.mr_dp_game.copy()

        # Convert set to list for JSON
        if isinstance(game_data.get("unique_moods"), set):
            game_data["unique_moods"] = list(game_data["unique_moods"])

        data = {
            "user_id": user_id,
            "xp": game_data["xp"],
            "evolution": game_data["evolution"],
            "achievements": json.dumps(game_data["achievements"]),
            "accessory": game_data["accessory"],
            "game_data": json.dumps(game_data),
            "updated_at": datetime.now().isoformat()
        }

        # Upsert
        supabase_client.table("mr_dp_progress")\
            .upsert(data, on_conflict="user_id")\
            .execute()

        return True
    except Exception as e:
        print(f"Gamification save error: {e}")
        return False

def load_gamification_from_supabase(supabase_client, user_id: str) -> bool:
    """Load gamification progress from Supabase"""
    if not supabase_client or not user_id:
        return False

    try:
        result = supabase_client.table("mr_dp_progress")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()

        if result.data:
            game_data = json.loads(result.data.get("game_data", "{}"))

            # Restore to session state
            init_gamification()
            st.session_state.mr_dp_game.update({
                "xp": result.data.get("xp", 0),
                "evolution": result.data.get("evolution", "baby"),
                "achievements": json.loads(result.data.get("achievements", "[]")),
                "accessory": result.data.get("accessory", "none"),
                **game_data
            })

            # Convert unique_moods back to set
            if isinstance(st.session_state.mr_dp_game.get("unique_moods"), list):
                st.session_state.mr_dp_game["unique_moods"] = set(
                    st.session_state.mr_dp_game["unique_moods"]
                )

            return True
    except Exception as e:
        print(f"Gamification load error: {e}")

    return False


# --------------------------------------------------
# 6. UNIFIED MR.DP INTERFACE
# --------------------------------------------------

def render_mr_dp_chat_interface():
    """Render the Mr.DP chat interface"""
    st.markdown("""
    <style>
    .mr-dp-chat {
        background: linear-gradient(135deg, rgba(138, 86, 226, 0.1), rgba(0, 201, 167, 0.1));
        border-radius: 16px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid rgba(138, 86, 226, 0.2);
    }
    .mr-dp-message {
        background: rgba(138, 86, 226, 0.2);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.95rem;
    }
    .user-message {
        background: rgba(0, 201, 167, 0.2);
        text-align: right;
    }
    .chat-input-container {
        display: flex;
        gap: 8px;
        margin-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "mr_dp_chat_history" not in st.session_state:
        st.session_state.mr_dp_chat_history = []
        # Add greeting
        greeting, expression = get_contextual_greeting()
        st.session_state.mr_dp_chat_history.append({
            "role": "assistant",
            "content": greeting,
            "expression": expression
        })

    st.markdown('<div class="mr-dp-chat">', unsafe_allow_html=True)
    st.markdown("### Chat with Mr.DP")

    # Display chat history
    for msg in st.session_state.mr_dp_chat_history[-6:]:  # Show last 6 messages
        if msg["role"] == "assistant":
            st.markdown(f'<div class="mr-dp-message">🟣 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mr-dp-message user-message">{msg["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    user_input = st.text_input("Ask Mr.DP anything...", key="mr_dp_input", label_visibility="collapsed")

    if st.button("Send", key="mr_dp_send"):
        if user_input:
            # Add user message
            st.session_state.mr_dp_chat_history.append({
                "role": "user",
                "content": user_input
            })

            # Get response
            user_data = {}
            if "current_feeling" in st.session_state:
                user_data["current_mood"] = st.session_state.current_feeling
            if "desired_feeling" in st.session_state:
                user_data["desired_mood"] = st.session_state.desired_feeling

            response, expression = chat_with_mr_dp(
                user_input,
                st.session_state.mr_dp_chat_history,
                user_data
            )

            # Add response
            st.session_state.mr_dp_chat_history.append({
                "role": "assistant",
                "content": response,
                "expression": expression
            })

            # Track for gamification
            init_gamification()
            st.session_state.mr_dp_game["conversations_count"] += 1
            add_xp(2, "Chatted with Mr.DP")

            # Check achievement
            if st.session_state.mr_dp_game["conversations_count"] >= 20:
                check_achievement("chatty_friend")

            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def render_mr_dp_status_card():
    """Render Mr.DP evolution status card"""
    init_gamification()

    evolution = get_current_evolution()
    next_evo = get_next_evolution()
    xp = st.session_state.mr_dp_game["xp"]
    accessory = st.session_state.mr_dp_game["accessory"]

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.15), rgba(0, 201, 167, 0.15));
                border-radius: 16px; padding: 16px; margin: 12px 0;
                border: 1px solid rgba(138, 86, 226, 0.3);">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <span style="font-size: 2rem;">🟣</span>
            <div>
                <div style="font-weight: 600; font-size: 1.1rem;">{evolution['name']}</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">{evolution['description']}</div>
            </div>
        </div>
        <div style="font-size: 0.9rem; color: #00C9A7; margin-bottom: 8px;">
            ✨ {xp} XP
            {f" | Wearing: {MR_DP_ACCESSORIES[accessory].get('icon', '')} {MR_DP_ACCESSORIES[accessory]['name']}" if accessory != 'none' else ""}
        </div>
        {f'''<div style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">
            Next: {next_evo['name']} ({next_evo['xp_needed']} XP to go)
        </div>''' if next_evo else '<div style="font-size: 0.8rem; color: gold;">Max evolution reached!</div>'}
    </div>
    """, unsafe_allow_html=True)

def render_achievements_display():
    """Render achievements display"""
    init_gamification()

    earned = st.session_state.mr_dp_game["achievements"]

    st.markdown("### Achievements")

    cols = st.columns(4)
    i = 0
    for ach_id, ach_data in MR_DP_ACHIEVEMENTS.items():
        with cols[i % 4]:
            is_earned = ach_id in earned
            opacity = "1" if is_earned else "0.3"
            st.markdown(f"""
            <div style="text-align: center; padding: 12px; opacity: {opacity};">
                <div style="font-size: 2rem;">{ach_data['icon']}</div>
                <div style="font-size: 0.8rem; font-weight: 600;">{ach_data['name']}</div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.6);">{ach_data['description']}</div>
            </div>
            """, unsafe_allow_html=True)
        i += 1

def render_intervention_popup():
    """Render ADHD intervention popup if needed"""
    intervention = get_adhd_intervention()

    if intervention:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.3), rgba(0, 201, 167, 0.2));
                    border-radius: 16px; padding: 20px; margin: 16px 0;
                    border: 2px solid rgba(138, 86, 226, 0.5);
                    animation: pulse 2s infinite;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 2.5rem;">🟣</span>
                <div>
                    <div style="font-weight: 600; margin-bottom: 8px;">Mr.DP noticed something...</div>
                    <div style="color: rgba(255,255,255,0.9);">{intervention['message']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(intervention["action_label"], key=f"intervention_{intervention['type']}"):
            # Handle intervention action
            if intervention["action"] == "quick_hit":
                st.session_state.trigger_quick_hit = True
            elif intervention["action"] == "top_3":
                st.session_state.show_top_3 = True
            elif intervention["action"] == "short_content":
                st.session_state.filter_short = True
            st.rerun()

        return True
    return False


# --------------------------------------------------
# SQL SCHEMA FOR MR.DP INTELLIGENCE
# --------------------------------------------------

MR_DP_TABLES_SQL = """
-- Mr.DP Behavior Logs
CREATE TABLE IF NOT EXISTS mr_dp_behavior_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    session_date DATE NOT NULL,
    scroll_events INT DEFAULT 0,
    recommendations_seen INT DEFAULT 0,
    recommendations_clicked INT DEFAULT 0,
    click_through_rate DECIMAL(5,4) DEFAULT 0,
    quick_hit_uses INT DEFAULT 0,
    session_duration_minutes DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_behavior_user_date ON mr_dp_behavior_logs(user_id, session_date);

-- Mr.DP Gamification Progress
CREATE TABLE IF NOT EXISTS mr_dp_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    xp INT DEFAULT 0,
    evolution VARCHAR(50) DEFAULT 'baby',
    achievements JSONB DEFAULT '[]',
    accessory VARCHAR(50) DEFAULT 'none',
    game_data JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_progress_user ON mr_dp_progress(user_id);

-- Mr.DP Chat History (optional - for conversation memory)
CREATE TABLE IF NOT EXISTS mr_dp_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    expression VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user ON mr_dp_conversations(user_id, created_at DESC);

-- RLS Policies
ALTER TABLE mr_dp_behavior_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mr_dp_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE mr_dp_conversations ENABLE ROW LEVEL SECURITY;

-- Behavior Logs RLS
CREATE POLICY "Users can view own behavior logs"
    ON mr_dp_behavior_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own behavior logs"
    ON mr_dp_behavior_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Progress RLS
CREATE POLICY "Users can view own progress"
    ON mr_dp_progress FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can upsert own progress"
    ON mr_dp_progress FOR ALL
    USING (auth.uid() = user_id);

-- Conversations RLS
CREATE POLICY "Users can view own conversations"
    ON mr_dp_conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations"
    ON mr_dp_conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);
"""
