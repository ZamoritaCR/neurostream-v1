"""
Dopamine.watch 2027 - Discover Page
Mood-based content discovery with modern UI.
"""

import streamlit as st
from core.session import set_mood, get_state
from config.settings import MOODS


def render_discover():
    """Render the discover/mood selection page."""

    st.markdown("""
    <div class="discover-header animate-fade-in">
        <h1>Discover</h1>
        <p>Tell us how you're feeling and we'll find the perfect content.</p>
    </div>
    """, unsafe_allow_html=True)

    # Current mood selection
    render_mood_selector("current", "How are you feeling right now?")

    # Desired mood selection
    render_mood_selector("desired", "How do you want to feel?")

    # Find content button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Find My Dopamine", type="primary", use_container_width=True):
            current = get_state("selected_current_mood")
            desired = get_state("selected_desired_mood")
            if current:
                set_mood(current, desired)
                st.session_state.current_page = "home"
                st.rerun()
            else:
                st.warning("Please select how you're feeling first!")


def render_mood_selector(mood_type: str, title: str):
    """Render a mood selection grid."""

    st.markdown(f"""
    <div class="mood-selector-section">
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (mood_key, mood_data) in enumerate(MOODS.items()):
        with cols[i % 4]:
            selected = get_state(f"selected_{mood_type}_mood") == mood_key

            # Style the button
            btn_class = "mood-chip selected" if selected else "mood-chip"

            if st.button(
                f"{mood_data['emoji']} {mood_key.title()}",
                key=f"{mood_type}_{mood_key}",
                use_container_width=True
            ):
                st.session_state[f"selected_{mood_type}_mood"] = mood_key
                st.rerun()
