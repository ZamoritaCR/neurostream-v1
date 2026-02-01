"""
Onboarding Flow
4-step onboarding for new users.
"""

import streamlit as st
from typing import Dict, List, Optional


# Onboarding steps
ONBOARDING_STEPS = [
    {
        "id": "welcome",
        "title": "Welcome to dopamine.watch!",
        "subtitle": "Let's personalize your experience",
        "icon": "🧠"
    },
    {
        "id": "mood_calibration",
        "title": "How are you feeling right now?",
        "subtitle": "This helps us understand your starting point",
        "icon": "🎭"
    },
    {
        "id": "preferences",
        "title": "What do you enjoy?",
        "subtitle": "Select your favorite content types and genres",
        "icon": "🎬"
    },
    {
        "id": "meet_mrdp",
        "title": "Meet Mr.DP",
        "subtitle": "Your personal dopamine curator",
        "icon": "🤖"
    }
]

# Mood options for calibration
MOOD_OPTIONS = [
    {"id": "relaxed", "label": "Relaxed", "emoji": "😌", "color": "#10b981"},
    {"id": "stressed", "label": "Stressed", "emoji": "😰", "color": "#ef4444"},
    {"id": "tired", "label": "Tired", "emoji": "😴", "color": "#8b5cf6"},
    {"id": "energetic", "label": "Energetic", "emoji": "⚡", "color": "#f59e0b"},
    {"id": "bored", "label": "Bored", "emoji": "😐", "color": "#6b7280"},
    {"id": "happy", "label": "Happy", "emoji": "😊", "color": "#06b6d4"},
    {"id": "sad", "label": "Sad", "emoji": "😢", "color": "#3b82f6"},
    {"id": "anxious", "label": "Anxious", "emoji": "😟", "color": "#ec4899"},
]

# Content type options
CONTENT_TYPES = [
    {"id": "movies", "label": "Movies", "emoji": "🎬"},
    {"id": "tv", "label": "TV Shows", "emoji": "📺"},
    {"id": "music", "label": "Music", "emoji": "🎵"},
    {"id": "podcasts", "label": "Podcasts", "emoji": "🎙️"},
    {"id": "audiobooks", "label": "Audiobooks", "emoji": "📚"},
    {"id": "shorts", "label": "Short Videos", "emoji": "📱"},
]

# Genre options
GENRE_OPTIONS = [
    {"id": "comedy", "label": "Comedy", "emoji": "😂"},
    {"id": "drama", "label": "Drama", "emoji": "🎭"},
    {"id": "action", "label": "Action", "emoji": "💥"},
    {"id": "scifi", "label": "Sci-Fi", "emoji": "🚀"},
    {"id": "horror", "label": "Horror", "emoji": "👻"},
    {"id": "romance", "label": "Romance", "emoji": "💕"},
    {"id": "documentary", "label": "Documentary", "emoji": "🎥"},
    {"id": "animation", "label": "Animation", "emoji": "🎨"},
    {"id": "thriller", "label": "Thriller", "emoji": "🔪"},
    {"id": "fantasy", "label": "Fantasy", "emoji": "🧙"},
]


def should_show_onboarding() -> bool:
    """Check if user should see onboarding."""
    if "onboarding_completed" not in st.session_state:
        st.session_state.onboarding_completed = False

    return not st.session_state.onboarding_completed


def complete_onboarding():
    """Mark onboarding as completed."""
    st.session_state.onboarding_completed = True
    st.session_state.onboarding_step = 0


def get_onboarding_data() -> Dict:
    """Get data collected during onboarding."""
    return {
        "initial_mood": st.session_state.get("onboarding_mood"),
        "content_types": st.session_state.get("onboarding_content_types", []),
        "genres": st.session_state.get("onboarding_genres", []),
        "streaming_services": st.session_state.get("onboarding_services", [])
    }


def render_onboarding():
    """Render the onboarding flow."""
    # Initialize state
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 0

    current_step = st.session_state.onboarding_step
    total_steps = len(ONBOARDING_STEPS)

    # Inject onboarding styles
    st.markdown(get_onboarding_styles(), unsafe_allow_html=True)

    # Container
    st.markdown('<div class="onboarding-container">', unsafe_allow_html=True)

    # Progress bar
    progress = (current_step + 1) / total_steps
    st.progress(progress)
    st.markdown(f"<p class='step-counter'>Step {current_step + 1} of {total_steps}</p>", unsafe_allow_html=True)

    # Render current step
    step = ONBOARDING_STEPS[current_step]

    st.markdown(f"""
        <div class="step-header">
            <span class="step-icon">{step['icon']}</span>
            <h1 class="step-title">{step['title']}</h1>
            <p class="step-subtitle">{step['subtitle']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Step content
    if step["id"] == "welcome":
        render_welcome_step()
    elif step["id"] == "mood_calibration":
        render_mood_step()
    elif step["id"] == "preferences":
        render_preferences_step()
    elif step["id"] == "meet_mrdp":
        render_mrdp_step()

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_step > 0:
            if st.button("← Back", key="onboarding_back"):
                st.session_state.onboarding_step -= 1
                st.rerun()

    with col3:
        if current_step < total_steps - 1:
            if st.button("Next →", key="onboarding_next", type="primary"):
                st.session_state.onboarding_step += 1
                st.rerun()
        else:
            if st.button("Get Started! 🚀", key="onboarding_finish", type="primary"):
                complete_onboarding()
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_welcome_step():
    """Render the welcome step."""
    st.markdown("""
        <div class="welcome-content">
            <div class="welcome-features">
                <div class="welcome-feature">
                    <span class="feature-emoji">🎯</span>
                    <span>Mood-based content discovery</span>
                </div>
                <div class="welcome-feature">
                    <span class="feature-emoji">🤖</span>
                    <span>AI-powered recommendations</span>
                </div>
                <div class="welcome-feature">
                    <span class="feature-emoji">⚡</span>
                    <span>Zero decision fatigue</span>
                </div>
                <div class="welcome-feature">
                    <span class="feature-emoji">🧠</span>
                    <span>Built for ADHD brains</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_mood_step():
    """Render the mood calibration step."""
    st.markdown('<div class="mood-grid">', unsafe_allow_html=True)

    # Get current selection
    selected_mood = st.session_state.get("onboarding_mood")

    # Display mood options in a grid
    cols = st.columns(4)
    for i, mood in enumerate(MOOD_OPTIONS):
        with cols[i % 4]:
            is_selected = selected_mood == mood["id"]
            btn_type = "primary" if is_selected else "secondary"

            if st.button(
                f"{mood['emoji']} {mood['label']}",
                key=f"mood_{mood['id']}",
                type=btn_type,
                use_container_width=True
            ):
                st.session_state.onboarding_mood = mood["id"]
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    if selected_mood:
        mood_data = next((m for m in MOOD_OPTIONS if m["id"] == selected_mood), None)
        if mood_data:
            st.success(f"You're feeling {mood_data['label'].lower()} - got it! We'll remember this.")


def render_preferences_step():
    """Render the preferences step."""
    # Content types
    st.markdown("### What do you like to watch/listen to?")

    selected_types = st.session_state.get("onboarding_content_types", [])

    type_cols = st.columns(3)
    for i, ct in enumerate(CONTENT_TYPES):
        with type_cols[i % 3]:
            is_selected = ct["id"] in selected_types
            if st.checkbox(
                f"{ct['emoji']} {ct['label']}",
                value=is_selected,
                key=f"type_{ct['id']}"
            ):
                if ct["id"] not in selected_types:
                    selected_types.append(ct["id"])
            else:
                if ct["id"] in selected_types:
                    selected_types.remove(ct["id"])

    st.session_state.onboarding_content_types = selected_types

    st.markdown("---")

    # Genres
    st.markdown("### Pick your favorite genres")

    selected_genres = st.session_state.get("onboarding_genres", [])

    genre_cols = st.columns(5)
    for i, genre in enumerate(GENRE_OPTIONS):
        with genre_cols[i % 5]:
            is_selected = genre["id"] in selected_genres
            if st.checkbox(
                f"{genre['emoji']} {genre['label']}",
                value=is_selected,
                key=f"genre_{genre['id']}"
            ):
                if genre["id"] not in selected_genres:
                    selected_genres.append(genre["id"])
            else:
                if genre["id"] in selected_genres:
                    selected_genres.remove(genre["id"])

    st.session_state.onboarding_genres = selected_genres

    if selected_types and selected_genres:
        st.info(f"Great choices! {len(selected_types)} content types and {len(selected_genres)} genres selected.")


def render_mrdp_step():
    """Render the Meet Mr.DP step."""
    st.markdown("""
        <div class="mrdp-intro">
            <div class="mrdp-avatar-large">🧠</div>
            <div class="mrdp-speech">
                <p><strong>Hey there! I'm Mr.DP (Mr. Dopamine)!</strong></p>
                <p>I'm your personal content curator. I understand that ADHD brains work differently - and that's totally okay!</p>
                <p>Here's what I can do for you:</p>
                <ul>
                    <li>💬 Tell me how you feel in plain language</li>
                    <li>🎯 I'll give you max 3 suggestions - no decision paralysis!</li>
                    <li>🧠 I learn your preferences over time</li>
                    <li>💚 I never judge, always support</li>
                </ul>
                <p>Ready to find your perfect content? Let's go!</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Quick try
    st.markdown("### Try asking me something:")
    user_input = st.text_input(
        "What would you like to watch?",
        placeholder="e.g., I'm stressed and need something calming",
        key="onboarding_mrdp_input"
    )

    if user_input:
        st.markdown("""
            <div class="mrdp-response">
                <span class="mrdp-emoji">🤔</span>
                <span>I'll remember that! Once you finish onboarding, I'll have the perfect suggestions ready for you!</span>
            </div>
        """, unsafe_allow_html=True)


def get_onboarding_styles() -> str:
    """Get onboarding CSS styles."""
    return """
    <style>
    .onboarding-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }

    .step-counter {
        text-align: center;
        color: #6b7280;
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }

    .step-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .step-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 1rem;
    }

    .step-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #1f2937;
    }

    .step-subtitle {
        font-size: 1.1rem;
        color: #6b7280;
    }

    .welcome-features {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        max-width: 400px;
        margin: 2rem auto;
    }

    .welcome-feature {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 12px;
        font-size: 1.1rem;
    }

    .feature-emoji {
        font-size: 1.5rem;
    }

    .mood-grid {
        margin: 2rem 0;
    }

    .mrdp-intro {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        text-align: center;
    }

    .mrdp-avatar-large {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        box-shadow: 0 10px 40px rgba(139, 92, 246, 0.3);
    }

    .mrdp-speech {
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        max-width: 500px;
        text-align: left;
    }

    .mrdp-speech ul {
        margin: 1rem 0;
        padding-left: 1.5rem;
    }

    .mrdp-speech li {
        margin-bottom: 0.5rem;
    }

    .mrdp-response {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: rgba(16, 185, 129, 0.1);
        border-radius: 12px;
        margin-top: 1rem;
    }

    .mrdp-emoji {
        font-size: 1.5rem;
    }
    </style>
    """
