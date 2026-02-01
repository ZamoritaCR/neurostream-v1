"""
Dopamine.watch 2027 - Profile View
User profile page with stats and achievements.
"""

import streamlit as st
from core.session import get_user, get_state


def render_profile():
    """Render the user profile page."""

    user = get_user()
    if not user:
        st.error("Please log in to view your profile.")
        return

    # Profile header
    st.markdown(f"""
    <div class="profile-header animate-fade-in">
        <div class="profile-avatar">{user.get('display_name', 'U')[0].upper()}</div>
        <div class="profile-info">
            <h1>{user.get('display_name', 'User')}</h1>
            <p class="profile-email">{user.get('email', '')}</p>
            <div class="profile-badges">
                {'<span class="badge premium">Premium</span>' if user.get('is_premium') else ''}
                <span class="badge level">Level {get_state('level', 1)}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    render_stats()

    # Achievements
    render_achievements()


def render_stats():
    """Render user statistics."""

    st.markdown("""
    <div class="stats-section">
        <h3>Your Stats</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Dopamine Points", get_state("dopamine_points", 0))

    with col2:
        st.metric("Mood Streak", f"{get_state('mood_streak', 0)} days")

    with col3:
        st.metric("Queue Size", len(get_state("user_queue", [])))

    with col4:
        st.metric("Mr.DP Chats", get_state("mr_dp_uses_today", 0))


def render_achievements():
    """Render user achievements."""

    achievements = get_state("achievements", [])

    st.markdown("""
    <div class="achievements-section">
        <h3>Achievements</h3>
    </div>
    """, unsafe_allow_html=True)

    if achievements:
        cols = st.columns(4)
        for i, achievement in enumerate(achievements[:8]):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="achievement-card">
                    <span class="achievement-icon">🏆</span>
                    <span class="achievement-title">{achievement.get('title', 'Achievement')}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Start using dopamine.watch to unlock achievements!")
