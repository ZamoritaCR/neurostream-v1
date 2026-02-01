"""
Analytics Dashboard
Visual mood analytics and usage patterns for users.
"""

import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


def render_analytics_dashboard(user_id: str):
    """Render the main analytics dashboard."""
    st.markdown(get_analytics_styles(), unsafe_allow_html=True)

    st.markdown("""
        <div class="analytics-header">
            <h1>📊 Your Dopamine Analytics</h1>
            <p>Insights into your mood patterns and content journey</p>
        </div>
    """, unsafe_allow_html=True)

    # Summary cards
    render_summary_cards(user_id)

    # Tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs(["Mood Patterns", "Content Stats", "Streaks & Points", "Insights"])

    with tab1:
        render_mood_analytics(user_id)

    with tab2:
        render_content_analytics(user_id)

    with tab3:
        render_gamification_analytics(user_id)

    with tab4:
        render_insights(user_id)


def render_summary_cards(user_id: str):
    """Render summary stat cards."""
    # Get mock data (in production, fetch from services)
    stats = get_user_stats(user_id)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="🔥 Current Streak",
            value=f"{stats['streak']} days",
            delta="+1 today" if stats['streak'] > 0 else None
        )

    with col2:
        st.metric(
            label="💜 Dopamine Points",
            value=f"{stats['points']:,}",
            delta=f"+{stats['points_today']} today"
        )

    with col3:
        st.metric(
            label="📺 Content Watched",
            value=stats['content_count'],
            delta=f"+{stats['content_this_week']} this week"
        )

    with col4:
        st.metric(
            label="🏆 Achievements",
            value=f"{stats['achievements_unlocked']}/{stats['achievements_total']}",
            delta="1 new!" if stats['new_achievement'] else None
        )


def render_mood_analytics(user_id: str):
    """Render mood pattern analytics."""
    st.markdown("### 🎭 Your Mood Journey")

    # Weekly mood chart
    st.markdown("#### This Week's Moods")

    # Mock mood data for visualization
    mood_data = get_mood_history(user_id)

    # Simple text-based visualization
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    moods = ["😌 Relaxed", "😰 Stressed", "😊 Happy", "😴 Tired", "⚡ Energetic", "😊 Happy", "😌 Relaxed"]

    st.markdown('<div class="mood-week">', unsafe_allow_html=True)
    cols = st.columns(7)
    for i, (day, mood) in enumerate(zip(days, moods)):
        with cols[i]:
            st.markdown(f"""
                <div class="mood-day">
                    <div class="day-label">{day}</div>
                    <div class="mood-emoji">{mood.split()[0]}</div>
                    <div class="mood-label">{mood.split()[1]}</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Mood breakdown
    st.markdown("#### Mood Distribution (Last 30 Days)")

    mood_counts = {
        "Relaxed": 8,
        "Happy": 12,
        "Stressed": 4,
        "Tired": 3,
        "Energetic": 3
    }

    for mood, count in mood_counts.items():
        percentage = count / 30 * 100
        st.markdown(f"""
            <div class="mood-bar-container">
                <span class="mood-bar-label">{mood}</span>
                <div class="mood-bar-bg">
                    <div class="mood-bar-fill" style="width: {percentage}%"></div>
                </div>
                <span class="mood-bar-count">{count} days</span>
            </div>
        """, unsafe_allow_html=True)

    # Time patterns
    st.markdown("#### When You're Most Active")

    peak_hours = {
        "Morning (6-12)": 15,
        "Afternoon (12-6)": 25,
        "Evening (6-10)": 45,
        "Night (10-6)": 15
    }

    for period, percentage in peak_hours.items():
        st.markdown(f"**{period}**: {'█' * (percentage // 5)} {percentage}%")


def render_content_analytics(user_id: str):
    """Render content consumption analytics."""
    st.markdown("### 📺 Content Stats")

    # Content type breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Content Types")
        content_types = {
            "Movies": 45,
            "TV Shows": 30,
            "Music": 15,
            "Podcasts": 7,
            "Shorts": 3
        }

        for ctype, percentage in content_types.items():
            st.markdown(f"""
                <div class="content-type-row">
                    <span>{ctype}</span>
                    <span>{percentage}%</span>
                </div>
            """, unsafe_allow_html=True)
            st.progress(percentage / 100)

    with col2:
        st.markdown("#### Top Genres")
        genres = [
            ("Comedy", "😂", 28),
            ("Drama", "🎭", 22),
            ("Sci-Fi", "🚀", 18),
            ("Documentary", "🎥", 15),
            ("Action", "💥", 12)
        ]

        for genre, emoji, count in genres:
            st.markdown(f"{emoji} **{genre}**: {count} items watched")

    # Watch time
    st.markdown("#### Watch Time This Month")
    total_hours = 47
    avg_per_day = total_hours / 30

    st.markdown(f"""
        <div class="watch-time-card">
            <div class="watch-time-big">{total_hours} hours</div>
            <div class="watch-time-sub">Average: {avg_per_day:.1f} hours/day</div>
        </div>
    """, unsafe_allow_html=True)


def render_gamification_analytics(user_id: str):
    """Render gamification stats."""
    st.markdown("### 🏆 Your Progress")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Level Progress")
        level = 7
        xp = 2450
        next_level_xp = 3600

        progress = (xp - (level - 1) ** 2 * 100) / ((level ** 2 * 100) - (level - 1) ** 2 * 100)

        st.markdown(f"""
            <div class="level-card">
                <div class="level-number">Level {level}</div>
                <div class="level-title">Content Curator</div>
            </div>
        """, unsafe_allow_html=True)

        st.progress(min(1.0, progress))
        st.markdown(f"**{xp:,} / {next_level_xp:,} XP** to Level {level + 1}")

        st.markdown("#### Streak History")
        st.markdown("""
            - 🔥 Current: **12 days**
            - 🏆 Longest: **45 days**
            - 📅 Total active days: **156**
        """)

    with col2:
        st.markdown("#### Recent Achievements")
        achievements = [
            ("🎬", "Binge Master", "Watched 100 items", "2 days ago"),
            ("🔥", "Week Warrior", "7 day streak", "5 days ago"),
            ("💬", "Chatty", "10 Mr.DP conversations", "1 week ago"),
        ]

        for icon, name, desc, when in achievements:
            st.markdown(f"""
                <div class="achievement-row">
                    <span class="achievement-icon">{icon}</span>
                    <div class="achievement-info">
                        <div class="achievement-name">{name}</div>
                        <div class="achievement-desc">{desc}</div>
                    </div>
                    <span class="achievement-when">{when}</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Points Breakdown")
        point_sources = [
            ("Content watched", 1200),
            ("Daily logins", 450),
            ("Mr.DP chats", 350),
            ("Achievements", 400),
            ("Streaks", 250)
        ]

        for source, points in point_sources:
            st.markdown(f"- **{source}**: {points:,} DP")


def render_insights(user_id: str):
    """Render personalized insights."""
    st.markdown("### 💡 Personalized Insights")

    insights = [
        {
            "icon": "🌙",
            "title": "Night Owl Detected",
            "description": "You're most active between 8-11 PM. Consider setting up watch reminders for this time!",
            "type": "pattern"
        },
        {
            "icon": "😌",
            "title": "Comfort Content Works",
            "description": "When you're stressed, comedies improve your mood 78% of the time. Keep it up!",
            "type": "mood"
        },
        {
            "icon": "⏱️",
            "title": "Perfect Watch Length",
            "description": "You finish content under 45 minutes 90% of the time. Your attention span sweet spot!",
            "type": "adhd"
        },
        {
            "icon": "🎭",
            "title": "Genre Variety Alert",
            "description": "You've been watching a lot of drama lately. Try some comedy for a mood boost?",
            "type": "suggestion"
        }
    ]

    for insight in insights:
        st.markdown(f"""
            <div class="insight-card insight-{insight['type']}">
                <span class="insight-icon">{insight['icon']}</span>
                <div class="insight-content">
                    <div class="insight-title">{insight['title']}</div>
                    <div class="insight-desc">{insight['description']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ADHD-specific tips
    st.markdown("### 🧠 ADHD Tips Based on Your Patterns")

    tips = [
        "Your focus time peaks at 45 minutes - try the Pomodoro technique!",
        "You skip content most often at the 15-minute mark - look for shorter content when low energy",
        "Music helps you focus - try our focus playlists before work sessions"
    ]

    for tip in tips:
        st.info(tip)


def get_user_stats(user_id: str) -> Dict:
    """Get user statistics (mock data for now)."""
    return {
        "streak": 12,
        "points": 2450,
        "points_today": 75,
        "content_count": 156,
        "content_this_week": 8,
        "achievements_unlocked": 12,
        "achievements_total": 25,
        "new_achievement": True
    }


def get_mood_history(user_id: str) -> List[Dict]:
    """Get mood history (mock data for now)."""
    moods = ["relaxed", "stressed", "happy", "tired", "energetic"]
    return [
        {"mood": random.choice(moods), "date": (datetime.now() - timedelta(days=i)).isoformat()}
        for i in range(30)
    ]


def get_analytics_styles() -> str:
    """Get analytics dashboard CSS styles."""
    return """
    <style>
    .analytics-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .analytics-header h1 {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }

    .analytics-header p {
        color: #6b7280;
    }

    .mood-week {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }

    .mood-day {
        text-align: center;
        padding: 1rem;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 12px;
    }

    .day-label {
        font-size: 0.8rem;
        color: #6b7280;
    }

    .mood-emoji {
        font-size: 2rem;
        margin: 0.5rem 0;
    }

    .mood-label {
        font-size: 0.75rem;
    }

    .mood-bar-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0.5rem 0;
    }

    .mood-bar-label {
        width: 80px;
        font-size: 0.9rem;
    }

    .mood-bar-bg {
        flex: 1;
        height: 20px;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 10px;
        overflow: hidden;
    }

    .mood-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #8b5cf6, #06b6d4);
        border-radius: 10px;
    }

    .mood-bar-count {
        width: 60px;
        text-align: right;
        font-size: 0.85rem;
        color: #6b7280;
    }

    .content-type-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.25rem;
    }

    .watch-time-card {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(6, 182, 212, 0.1));
        border-radius: 16px;
        margin: 1rem 0;
    }

    .watch-time-big {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .watch-time-sub {
        color: #6b7280;
    }

    .level-card {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        border-radius: 16px;
        color: white;
        margin-bottom: 1rem;
    }

    .level-number {
        font-size: 2rem;
        font-weight: 700;
    }

    .level-title {
        opacity: 0.9;
    }

    .achievement-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: rgba(139, 92, 246, 0.05);
        border-radius: 12px;
        margin-bottom: 0.5rem;
    }

    .achievement-icon {
        font-size: 1.5rem;
    }

    .achievement-info {
        flex: 1;
    }

    .achievement-name {
        font-weight: 600;
    }

    .achievement-desc {
        font-size: 0.85rem;
        color: #6b7280;
    }

    .achievement-when {
        font-size: 0.8rem;
        color: #9ca3af;
    }

    .insight-card {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
    }

    .insight-pattern { background: rgba(139, 92, 246, 0.1); }
    .insight-mood { background: rgba(16, 185, 129, 0.1); }
    .insight-adhd { background: rgba(245, 158, 11, 0.1); }
    .insight-suggestion { background: rgba(6, 182, 212, 0.1); }

    .insight-icon {
        font-size: 2rem;
    }

    .insight-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .insight-desc {
        color: #4b5563;
        font-size: 0.95rem;
    }
    </style>
    """
