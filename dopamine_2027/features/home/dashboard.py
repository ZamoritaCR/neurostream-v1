"""
Dopamine.watch 2027 - Home Dashboard
The main dashboard after login - personalized content, continue watching, mood check.
"""

import streamlit as st
from core.session import get_user, get_state


def render_home():
    """Render the home dashboard."""

    user = get_user()
    name = user.get("display_name", "friend") if user else "friend"

    # Welcome header
    st.markdown(f"""
    <div class="home-header animate-fade-in">
        <h1>Welcome back, {name}! 👋</h1>
        <p>What are you in the mood for today?</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick mood check
    render_mood_check()

    # Continue watching
    render_continue_watching()

    # Recommendations
    render_recommendations()


def render_mood_check():
    """Render quick mood selection."""

    st.markdown("""
    <div class="mood-check-section">
        <h3>How are you feeling?</h3>
    </div>
    """, unsafe_allow_html=True)

    moods = ["😌 Relaxed", "😤 Stressed", "😴 Tired", "⚡ Energetic", "😢 Sad", "😊 Happy"]

    cols = st.columns(6)
    for i, mood in enumerate(moods):
        with cols[i]:
            if st.button(mood, key=f"mood_{i}", use_container_width=True):
                st.session_state.current_mood = mood.split()[1].lower()
                st.rerun()


def render_continue_watching():
    """Render continue watching section."""

    continue_watching = get_state("continue_watching", [])

    if continue_watching:
        st.markdown("""
        <div class="section-header">
            <h3>Continue Watching</h3>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(4)
        for i, item in enumerate(continue_watching[:4]):
            with cols[i]:
                st.image(item.get("poster_url", ""), use_container_width=True)
                st.caption(item.get("title", ""))


def render_recommendations():
    """Render personalized recommendations."""

    st.markdown("""
    <div class="section-header">
        <h3>Recommended for You</h3>
        <p>Based on your mood and preferences</p>
    </div>
    """, unsafe_allow_html=True)

    # Placeholder cards
    st.info("Your personalized recommendations will appear here. Try talking to Mr.DP!")
