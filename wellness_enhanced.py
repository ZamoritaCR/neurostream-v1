# wellness_enhanced.py
# --------------------------------------------------
# DOPAMINE.WATCH - ENHANCED WELLNESS SYSTEM
# --------------------------------------------------
# Features:
# 1. Structured Breathing Exercises with Timing
# 2. 5-4-3-2-1 Grounding Technique
# 3. Mood-Specific Affirmations
# 4. Calming Video Suggestions
# 5. Streamlit UI Components with Animations
# --------------------------------------------------

import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import random
import time

# --------------------------------------------------
# 1. BREATHING EXERCISES
# --------------------------------------------------

@dataclass
class BreathingExercise:
    """Breathing exercise configuration."""
    id: str
    name: str
    description: str
    icon: str
    inhale_seconds: int
    hold_seconds: int
    exhale_seconds: int
    hold_after_exhale: int = 0
    cycles: int = 4
    instructions: List[str] = field(default_factory=list)


BREATHING_EXERCISES: Dict[str, BreathingExercise] = {
    "box_breathing": BreathingExercise(
        id="box_breathing",
        name="Box Breathing",
        description="Navy SEAL technique for instant calm",
        icon="📦",
        inhale_seconds=4,
        hold_seconds=4,
        exhale_seconds=4,
        hold_after_exhale=4,
        cycles=4,
        instructions=[
            "Sit comfortably with your back straight",
            "Breathe in slowly through your nose for 4 seconds",
            "Hold your breath for 4 seconds",
            "Exhale slowly through your mouth for 4 seconds",
            "Hold empty for 4 seconds",
            "Repeat 4 times"
        ]
    ),
    "breathing_478": BreathingExercise(
        id="breathing_478",
        name="4-7-8 Breathing",
        description="Dr. Weil's relaxing breath technique",
        icon="🌙",
        inhale_seconds=4,
        hold_seconds=7,
        exhale_seconds=8,
        cycles=4,
        instructions=[
            "Place the tip of your tongue behind your upper front teeth",
            "Exhale completely through your mouth, making a whoosh sound",
            "Close your mouth and inhale quietly through your nose for 4 seconds",
            "Hold your breath for 7 seconds",
            "Exhale completely through your mouth for 8 seconds",
            "Repeat 4 times"
        ]
    ),
    "deep_breathing": BreathingExercise(
        id="deep_breathing",
        name="Simple Deep Breathing",
        description="Easy and effective for beginners",
        icon="🌬️",
        inhale_seconds=4,
        hold_seconds=2,
        exhale_seconds=6,
        cycles=6,
        instructions=[
            "Find a comfortable position",
            "Place one hand on your chest, one on your belly",
            "Breathe in slowly through your nose for 4 seconds",
            "Feel your belly rise (not your chest)",
            "Hold briefly for 2 seconds",
            "Exhale slowly through your mouth for 6 seconds",
            "Repeat 6 times"
        ]
    )
}


def get_breathing_exercise(exercise_id: str) -> Optional[Dict]:
    """Get a specific breathing exercise."""
    exercise = BREATHING_EXERCISES.get(exercise_id)
    if not exercise:
        return None

    total_cycle = (
        exercise.inhale_seconds +
        exercise.hold_seconds +
        exercise.exhale_seconds +
        exercise.hold_after_exhale
    )

    return {
        "id": exercise.id,
        "name": exercise.name,
        "description": exercise.description,
        "icon": exercise.icon,
        "timing": {
            "inhale": exercise.inhale_seconds,
            "hold": exercise.hold_seconds,
            "exhale": exercise.exhale_seconds,
            "hold_after_exhale": exercise.hold_after_exhale,
            "cycles": exercise.cycles,
            "total_seconds": total_cycle * exercise.cycles,
            "cycle_seconds": total_cycle
        },
        "instructions": exercise.instructions
    }


def get_all_breathing_exercises() -> List[Dict]:
    """Get all available breathing exercises."""
    return [get_breathing_exercise(eid) for eid in BREATHING_EXERCISES.keys()]


# --------------------------------------------------
# 2. GROUNDING TECHNIQUE (5-4-3-2-1)
# --------------------------------------------------

GROUNDING_54321 = {
    "name": "5-4-3-2-1 Grounding",
    "description": "Engage all your senses to ground yourself in the present moment",
    "icon": "🌍",
    "steps": [
        {
            "count": 5,
            "sense": "see",
            "emoji": "👀",
            "prompt": "Name 5 things you can SEE",
            "examples": ["the color of the wall", "your hands", "a plant", "the ceiling", "your phone"]
        },
        {
            "count": 4,
            "sense": "touch",
            "emoji": "✋",
            "prompt": "Name 4 things you can TOUCH",
            "examples": ["the texture of your clothes", "your chair", "the floor", "your hair"]
        },
        {
            "count": 3,
            "sense": "hear",
            "emoji": "👂",
            "prompt": "Name 3 things you can HEAR",
            "examples": ["traffic outside", "your breathing", "a fan humming"]
        },
        {
            "count": 2,
            "sense": "smell",
            "emoji": "👃",
            "prompt": "Name 2 things you can SMELL",
            "examples": ["coffee", "fresh air", "laundry detergent"]
        },
        {
            "count": 1,
            "sense": "taste",
            "emoji": "👅",
            "prompt": "Name 1 thing you can TASTE",
            "examples": ["your morning coffee", "toothpaste", "water"]
        }
    ]
}


def get_grounding_exercise() -> Dict:
    """Get the 5-4-3-2-1 grounding exercise."""
    return GROUNDING_54321


# --------------------------------------------------
# 3. CALMING VIDEOS
# --------------------------------------------------

CALMING_VIDEOS = [
    {
        "id": "rain",
        "name": "Gentle Rain",
        "description": "Soft rain sounds for relaxation",
        "icon": "🌧️",
        "youtube_search": "relaxing rain sounds for sleep",
        "duration_minutes": 30
    },
    {
        "id": "ocean",
        "name": "Ocean Waves",
        "description": "Peaceful ocean wave sounds",
        "icon": "🌊",
        "youtube_search": "ocean waves sounds for relaxation",
        "duration_minutes": 30
    },
    {
        "id": "fireplace",
        "name": "Cozy Fireplace",
        "description": "Crackling fire for comfort",
        "icon": "🔥",
        "youtube_search": "cozy fireplace crackling sounds",
        "duration_minutes": 60
    },
    {
        "id": "forest",
        "name": "Forest Ambience",
        "description": "Peaceful forest sounds with birds",
        "icon": "🌲",
        "youtube_search": "forest nature sounds birds",
        "duration_minutes": 45
    },
    {
        "id": "thunderstorm",
        "name": "Distant Thunder",
        "description": "Gentle thunderstorm for relaxation",
        "icon": "⛈️",
        "youtube_search": "gentle thunderstorm sounds sleep",
        "duration_minutes": 60
    },
    {
        "id": "meditation",
        "name": "Guided Meditation",
        "description": "Calming guided meditation",
        "icon": "🧘",
        "youtube_search": "5 minute guided meditation anxiety",
        "duration_minutes": 5
    }
]


def get_calming_videos() -> List[Dict]:
    """Get list of calming video suggestions."""
    return CALMING_VIDEOS


# --------------------------------------------------
# 4. AFFIRMATIONS
# --------------------------------------------------

AFFIRMATIONS_BY_MOOD = {
    "anxious": [
        "This feeling is temporary. It will pass.",
        "I am safe in this moment.",
        "I can handle this, one breath at a time.",
        "My feelings are valid, but they don't define me.",
        "I've survived every hard moment before this one."
    ],
    "overwhelmed": [
        "I don't have to do everything right now.",
        "It's okay to take a break.",
        "One step at a time is enough.",
        "I give myself permission to rest.",
        "Not everything is urgent."
    ],
    "sad": [
        "It's okay to feel sad. This is part of being human.",
        "I am worthy of love and kindness.",
        "Tomorrow is a new day.",
        "I am doing the best I can.",
        "This sadness will lift."
    ],
    "stressed": [
        "I release what I cannot control.",
        "I am capable and resilient.",
        "Stress does not define my worth.",
        "I choose calm over chaos.",
        "I can only do what I can do."
    ],
    "tired": [
        "Rest is productive.",
        "My body deserves care.",
        "It's okay to slow down.",
        "I don't have to earn rest.",
        "Tomorrow I can try again."
    ],
    "general": [
        "You're doing better than you think.",
        "It's okay to not be okay.",
        "You matter.",
        "Take it one moment at a time.",
        "Be gentle with yourself.",
        "You are enough, just as you are.",
        "Your brain works differently, and that's okay.",
        "Small steps still move you forward."
    ]
}


def get_affirmation(mood: Optional[str] = None) -> str:
    """Get a random affirmation for the given mood."""
    mood_key = mood.lower() if mood and mood.lower() in AFFIRMATIONS_BY_MOOD else "general"
    return random.choice(AFFIRMATIONS_BY_MOOD[mood_key])


def get_affirmations(mood: Optional[str] = None, count: int = 3) -> List[str]:
    """Get multiple affirmations for the given mood."""
    mood_key = mood.lower() if mood and mood.lower() in AFFIRMATIONS_BY_MOOD else "general"
    available = AFFIRMATIONS_BY_MOOD[mood_key]
    return random.sample(available, min(count, len(available)))


# --------------------------------------------------
# 5. SOS CONTENT PACKAGE
# --------------------------------------------------

def get_sos_content_package(mood: Optional[str] = None) -> Dict:
    """Get complete SOS mode content package."""
    return {
        "breathing_exercises": get_all_breathing_exercises(),
        "grounding": get_grounding_exercise(),
        "calming_videos": get_calming_videos(),
        "affirmations": get_affirmations(mood, count=3),
        "quick_tips": [
            "Put one hand on your heart and one on your belly",
            "Splash cold water on your face",
            "Hold an ice cube in your hand",
            "Step outside for fresh air if possible",
            "Name 5 things around you that are blue"
        ],
        "crisis_resources": {
            "text": "If you're in crisis, you're not alone.",
            "hotline": "988",
            "hotline_name": "Suicide & Crisis Lifeline",
            "chat": "988lifeline.org/chat"
        }
    }


# --------------------------------------------------
# 6. USAGE TRACKING
# --------------------------------------------------

def log_wellness_usage(
    user_id: str,
    technique: str,
    duration_seconds: int = 0,
    mood_before: Optional[str] = None,
    mood_after: Optional[str] = None
) -> Dict:
    """Log wellness feature usage."""
    if 'wellness_usage' not in st.session_state:
        st.session_state.wellness_usage = []

    usage = {
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "technique": technique,
        "duration_seconds": duration_seconds,
        "mood_before": mood_before,
        "mood_after": mood_after
    }
    st.session_state.wellness_usage.append(usage)

    return {"logged": True, "timestamp": usage["timestamp"]}


def get_wellness_stats(user_id: str) -> Dict:
    """Get user's wellness usage statistics."""
    if 'wellness_usage' not in st.session_state:
        return {"total_uses": 0, "techniques": {}, "total_minutes": 0}

    user_usage = [
        u for u in st.session_state.wellness_usage
        if u.get("user_id") == user_id
    ]

    technique_counts = {}
    total_seconds = 0
    for u in user_usage:
        tech = u.get("technique", "unknown")
        technique_counts[tech] = technique_counts.get(tech, 0) + 1
        total_seconds += u.get("duration_seconds", 0)

    return {
        "total_uses": len(user_usage),
        "techniques": technique_counts,
        "total_minutes": round(total_seconds / 60, 1),
        "most_used": max(technique_counts.items(), key=lambda x: x[1])[0] if technique_counts else None
    }


# --------------------------------------------------
# 7. STREAMLIT UI COMPONENTS
# --------------------------------------------------

def render_breathing_animation(exercise_id: str = "box_breathing"):
    """Render an animated breathing exercise."""
    exercise = get_breathing_exercise(exercise_id)
    if not exercise:
        st.error("Exercise not found")
        return

    timing = exercise["timing"]

    st.markdown(f"### {exercise['icon']} {exercise['name']}")
    st.caption(exercise['description'])

    # CSS for breathing animation
    total_cycle = timing['cycle_seconds']
    inhale_pct = (timing['inhale'] / total_cycle) * 100
    hold_pct = (timing['hold'] / total_cycle) * 100
    exhale_pct = (timing['exhale'] / total_cycle) * 100
    hold2_pct = (timing['hold_after_exhale'] / total_cycle) * 100

    st.markdown(f"""
    <style>
    @keyframes breathe {{
        0%, 100% {{ transform: scale(1); background: #7c3aed; }}
        {inhale_pct:.0f}% {{ transform: scale(1.3); background: #a855f7; }}
        {inhale_pct + hold_pct:.0f}% {{ transform: scale(1.3); background: #a855f7; }}
        {inhale_pct + hold_pct + exhale_pct:.0f}% {{ transform: scale(1); background: #7c3aed; }}
    }}
    .breathing-circle {{
        width: 200px;
        height: 200px;
        border-radius: 50%;
        margin: 40px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        animation: breathe {total_cycle}s ease-in-out infinite;
    }}
    </style>
    <div class="breathing-circle">
        Breathe
    </div>
    """, unsafe_allow_html=True)

    # Instructions
    with st.expander("Instructions", expanded=False):
        for i, instruction in enumerate(exercise['instructions'], 1):
            st.markdown(f"{i}. {instruction}")

    # Timing info
    st.caption(f"⏱️ {timing['cycles']} cycles • {timing['total_seconds']} seconds total")


def render_grounding_guided_exercise():
    """Render interactive grounding exercise."""
    grounding = get_grounding_exercise()

    st.markdown(f"### {grounding['icon']} {grounding['name']}")
    st.caption(grounding['description'])

    if 'grounding_step' not in st.session_state:
        st.session_state.grounding_step = 0

    step_idx = st.session_state.grounding_step
    steps = grounding['steps']

    if step_idx < len(steps):
        step = steps[step_idx]

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
                    padding: 30px; border-radius: 16px; text-align: center; color: white;">
            <div style="font-size: 3rem;">{step['emoji']}</div>
            <div style="font-size: 1.5rem; font-weight: bold; margin: 16px 0;">
                {step['prompt']}
            </div>
            <div style="opacity: 0.8;">
                Examples: {', '.join(step['examples'][:3])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Previous", disabled=step_idx == 0):
                st.session_state.grounding_step -= 1
                st.rerun()
        with col2:
            if st.button("Next ➡️"):
                st.session_state.grounding_step += 1
                st.rerun()
    else:
        st.success("🎉 You've completed the grounding exercise!")
        st.markdown("Take a moment to notice how you feel now.")
        if st.button("Start Over"):
            st.session_state.grounding_step = 0
            st.rerun()


def render_calming_video_picker():
    """Render calming video selection."""
    videos = get_calming_videos()

    st.markdown("### 🎬 Calming Videos")
    st.caption("Choose a soundscape to help you relax")

    cols = st.columns(3)
    for i, video in enumerate(videos):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: rgba(168, 85, 247, 0.1); padding: 16px;
                        border-radius: 12px; text-align: center; margin: 8px 0;">
                <div style="font-size: 2rem;">{video['icon']}</div>
                <div style="font-weight: bold;">{video['name']}</div>
                <div style="font-size: 0.8rem; color: #888;">{video['duration_minutes']} min</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Play {video['name']}", key=f"video_{video['id']}"):
                search_url = f"https://www.youtube.com/results?search_query={video['youtube_search'].replace(' ', '+')}"
                st.markdown(f"[Open on YouTube]({search_url})")


def render_affirmation_card(mood: Optional[str] = None):
    """Render an affirmation card."""
    affirmation = get_affirmation(mood)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #7c3aed 0%, #ec4899 100%);
                padding: 40px; border-radius: 20px; text-align: center; color: white;">
        <div style="font-size: 1.5rem; font-style: italic; line-height: 1.6;">
            "{affirmation}"
        </div>
        <div style="margin-top: 20px; opacity: 0.8;">
            💜 Take a deep breath 💜
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_enhanced_sos_overlay():
    """Render the complete SOS calm mode overlay."""
    st.markdown("""
    <style>
    .sos-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border-radius: 16px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sos-header">
        <div style="font-size: 3rem;">🆘</div>
        <h1>SOS Calm Mode</h1>
        <p style="opacity: 0.8;">Take a moment. You're safe here.</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for different techniques
    tab1, tab2, tab3, tab4 = st.tabs(["🫁 Breathing", "🌍 Grounding", "💜 Affirmations", "🎬 Videos"])

    with tab1:
        exercise_choice = st.selectbox(
            "Choose a breathing exercise:",
            ["box_breathing", "breathing_478", "deep_breathing"],
            format_func=lambda x: BREATHING_EXERCISES[x].name
        )
        render_breathing_animation(exercise_choice)

    with tab2:
        render_grounding_guided_exercise()

    with tab3:
        mood = st.selectbox(
            "How are you feeling?",
            ["general", "anxious", "overwhelmed", "sad", "stressed", "tired"]
        )
        render_affirmation_card(mood)
        if st.button("New Affirmation"):
            st.rerun()

    with tab4:
        render_calming_video_picker()

    # Crisis resources
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 16px; background: rgba(239, 68, 68, 0.1); border-radius: 12px;">
        <p><strong>If you're in crisis, you're not alone.</strong></p>
        <p>📞 <strong>988</strong> - Suicide & Crisis Lifeline (US)</p>
        <p>💬 <a href="https://988lifeline.org/chat">988lifeline.org/chat</a></p>
    </div>
    """, unsafe_allow_html=True)
