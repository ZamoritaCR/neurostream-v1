"""
Dopamine.watch SOS Calm Mode
Feature: Emergency Calm-Down Overlay (Phase 2)

For when ADHD overwhelm hits hard - a one-click escape to calm.
"""
import streamlit as st
import streamlit.components.v1 as components
import random


# Calming content collections
CALM_VIDEOS = [
    {"title": "Rain Sounds", "url": "https://www.youtube.com/watch?v=mPZkdNFkNps", "duration": "3 hours"},
    {"title": "Fireplace Ambience", "url": "https://www.youtube.com/watch?v=L_LUpnjgPso", "duration": "10 hours"},
    {"title": "Ocean Waves", "url": "https://www.youtube.com/watch?v=bn9F19Hi1Lk", "duration": "8 hours"},
    {"title": "Forest Sounds", "url": "https://www.youtube.com/watch?v=xNN7iTA57jM", "duration": "3 hours"},
    {"title": "Thunderstorm", "url": "https://www.youtube.com/watch?v=nDq6TstdEi8", "duration": "2 hours"},
]

BREATHING_EXERCISES = [
    {
        "name": "Box Breathing",
        "steps": ["Breathe in for 4 seconds", "Hold for 4 seconds", "Breathe out for 4 seconds", "Hold for 4 seconds"],
        "cycles": 4,
        "emoji": "🔲"
    },
    {
        "name": "4-7-8 Breathing",
        "steps": ["Breathe in for 4 seconds", "Hold for 7 seconds", "Breathe out for 8 seconds"],
        "cycles": 3,
        "emoji": "🌊"
    },
    {
        "name": "Simple Deep Breath",
        "steps": ["Breathe in slowly", "Hold gently", "Breathe out completely"],
        "cycles": 5,
        "emoji": "🍃"
    }
]

GROUNDING_PROMPTS = [
    "Name 5 things you can see right now",
    "Name 4 things you can touch",
    "Name 3 things you can hear",
    "Name 2 things you can smell",
    "Name 1 thing you can taste",
]

AFFIRMATIONS = [
    "This feeling will pass. You've gotten through this before.",
    "You are safe right now. Take it one breath at a time.",
    "It's okay to feel overwhelmed. You're doing your best.",
    "Your brain is just working differently right now. That's okay.",
    "You don't have to figure everything out right now.",
    "Small steps count. You're making progress.",
    "It's okay to take a break. Rest is productive too.",
    "You are more than your thoughts. You are whole.",
]

# STOP Skill (Research: Brain 6, Section 2 - DBT Distress Tolerance)
# Prevents impulsive reactions during emotional overwhelm
STOP_SKILL = [
    {
        "letter": "S",
        "title": "Stop",
        "description": "Don't react. Freeze for a moment.",
        "emoji": "🛑"
    },
    {
        "letter": "T",
        "title": "Take a step back",
        "description": "Remove yourself from the situation. Take a breath.",
        "emoji": "👣"
    },
    {
        "letter": "O",
        "title": "Observe",
        "description": "Notice what's happening inside and around you without judgment.",
        "emoji": "👁️"
    },
    {
        "letter": "P",
        "title": "Proceed mindfully",
        "description": "Think before you act. What will help right now?",
        "emoji": "🧠"
    }
]


def render_sos_button():
    """
    Render the SOS button that appears in sidebar.
    Call this in your sidebar rendering.
    """
    st.markdown("""
    <style>
    .sos-button {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        font-weight: bold !important;
        animation: pulse-sos 2s infinite;
    }
    @keyframes pulse-sos {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("🆘 SOS Calm Mode", key="sos_button", use_container_width=True, type="secondary"):
        st.session_state.sos_mode = True
        st.rerun()


def render_sos_overlay():
    """
    Render the full SOS Calm Mode overlay.
    Call this at the top of your main render function.
    """
    if not st.session_state.get('sos_mode', False):
        return False

    # Full-screen calming overlay
    st.markdown("""
    <style>
    /* Dark calming overlay */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    }
    .calm-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        text-align: center;
    }
    .calm-header {
        font-size: 2.5rem;
        color: #a78bfa;
        margin-bottom: 10px;
    }
    .calm-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 30px;
    }
    .breathing-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        margin: 30px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: breathe 8s ease-in-out infinite;
        box-shadow: 0 0 60px rgba(139, 92, 246, 0.3);
    }
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
    }
    .breathing-text {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .affirmation-card {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        color: #e2e8f0;
        font-size: 1.2rem;
        line-height: 1.6;
    }
    .grounding-step {
        background: rgba(6, 182, 212, 0.15);
        border: 1px solid rgba(6, 182, 212, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        color: #e2e8f0;
        text-align: left;
    }
    .calm-section {
        margin: 30px 0;
    }
    .section-title {
        font-size: 1.3rem;
        color: #a78bfa;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Exit button at top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✕ Exit Calm Mode", key="exit_sos", use_container_width=True):
            st.session_state.sos_mode = False
            st.rerun()

    st.markdown("---")

    # Header
    st.markdown("""
    <div class="calm-container">
        <div class="calm-header">🌙 Take a Breath</div>
        <div class="calm-subtitle">Everything is okay. Let's slow down together.</div>
    </div>
    """, unsafe_allow_html=True)

    # Breathing animation
    st.markdown("""
    <div class="breathing-circle">
        <span class="breathing-text">Breathe</span>
    </div>
    """, unsafe_allow_html=True)

    # Affirmation
    affirmation = random.choice(AFFIRMATIONS)
    st.markdown(f"""
    <div class="affirmation-card">
        "{affirmation}"
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Grounding exercise (5-4-3-2-1)
    st.markdown("<div class='section-title'>🌿 5-4-3-2-1 Grounding</div>", unsafe_allow_html=True)

    for i, prompt in enumerate(GROUNDING_PROMPTS):
        emoji = ["👁️", "✋", "👂", "👃", "👅"][i]
        st.markdown(f"""
        <div class="grounding-step">
            {emoji} {prompt}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # STOP Skill (Research: Brain 6, Section 2 - DBT Distress Tolerance)
    st.markdown("<div class='section-title'>🛑 STOP Skill</div>", unsafe_allow_html=True)
    st.caption("A DBT technique to pause before reacting")

    for step in STOP_SKILL:
        st.markdown(f"""
        <div class="grounding-step" style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.5rem;">{step['emoji']}</span>
            <div>
                <strong style="color: #a78bfa;">{step['letter']}</strong> - {step['title']}
                <br><span style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{step['description']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Breathing exercise selector
    st.markdown("<div class='section-title'>🫁 Guided Breathing</div>", unsafe_allow_html=True)

    exercise = st.selectbox(
        "Choose a breathing exercise:",
        options=[ex["name"] for ex in BREATHING_EXERCISES],
        key="breathing_select"
    )

    selected = next((ex for ex in BREATHING_EXERCISES if ex["name"] == exercise), BREATHING_EXERCISES[0])

    st.info(f"{selected['emoji']} **{selected['name']}** - Do {selected['cycles']} cycles")
    for step in selected["steps"]:
        st.write(f"  • {step}")

    st.markdown("---")

    # Calming sounds
    st.markdown("<div class='section-title'>🎧 Calming Sounds</div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, video in enumerate(CALM_VIDEOS[:3]):
        with cols[i]:
            st.markdown(f"**{video['title']}**")
            st.caption(video['duration'])
            st.link_button("Play ▶️", video['url'], use_container_width=True)

    st.markdown("---")

    # Timer option
    st.markdown("<div class='section-title'>⏱️ Set a Calm Timer</div>", unsafe_allow_html=True)
    st.caption("Step away and come back when you're ready")

    timer_cols = st.columns(4)
    timer_options = [("2 min", 2), ("5 min", 5), ("10 min", 10), ("15 min", 15)]

    for col, (label, mins) in zip(timer_cols, timer_options):
        with col:
            if st.button(label, key=f"timer_{mins}", use_container_width=True):
                st.session_state.calm_timer_end = mins
                st.toast(f"Take {mins} minutes. We'll be here when you're back. 💜")

    st.markdown("---")

    # Gentle reminder
    st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 20px;">
        <p>💜 It's okay to stay here as long as you need.</p>
        <p>When you're ready, click "Exit Calm Mode" above.</p>
    </div>
    """, unsafe_allow_html=True)

    return True  # Indicates we rendered the overlay (skip normal content)


def log_sos_usage(supabase_client, user_id: str):
    """Log when user activates SOS mode for analytics."""
    try:
        from datetime import datetime
        supabase_client.table('user_behavior').insert({
            'user_id': user_id,
            'action_type': 'sos_calm_mode',
            'metadata': {'activated': True},
            'created_at': datetime.now().isoformat()
        }).execute()
    except:
        pass
