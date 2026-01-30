"""
Dopamine.watch Focus Session Timer
Feature: Watch Time Tracking with Break Reminders (Phase 2)

Helps ADHD brains track watch time and remember to take breaks.
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta


# Preset session lengths (in minutes)
SESSION_PRESETS = [
    {"label": "Quick Watch", "minutes": 25, "break": 5, "emoji": "⚡"},
    {"label": "Standard", "minutes": 45, "break": 10, "emoji": "🎬"},
    {"label": "Movie Mode", "minutes": 90, "break": 15, "emoji": "🍿"},
    {"label": "Binge Mode", "minutes": 120, "break": 20, "emoji": "🛋️"},
]

# Break activity suggestions
BREAK_ACTIVITIES = [
    {"activity": "Stretch your body", "emoji": "🧘", "duration": "2-3 min"},
    {"activity": "Get some water", "emoji": "💧", "duration": "1 min"},
    {"activity": "Look at something far away", "emoji": "👁️", "duration": "20 sec"},
    {"activity": "Walk around the room", "emoji": "🚶", "duration": "2 min"},
    {"activity": "Do 10 jumping jacks", "emoji": "🏃", "duration": "1 min"},
    {"activity": "Deep breathing", "emoji": "🫁", "duration": "1 min"},
    {"activity": "Check in with yourself", "emoji": "🧠", "duration": "30 sec"},
    {"activity": "Snack break", "emoji": "🍎", "duration": "5 min"},
]


def init_focus_session_state():
    """Initialize session state for focus timer."""
    if 'focus_session' not in st.session_state:
        st.session_state.focus_session = {
            'active': False,
            'start_time': None,
            'duration_minutes': 45,
            'break_reminder_minutes': 10,
            'total_watch_time_today': 0,
            'sessions_completed_today': 0,
            'last_break_reminder': None,
        }


def start_focus_session(duration_minutes: int = 45, break_every: int = 10):
    """Start a new focus session."""
    init_focus_session_state()
    st.session_state.focus_session.update({
        'active': True,
        'start_time': datetime.now(),
        'duration_minutes': duration_minutes,
        'break_reminder_minutes': break_every,
        'last_break_reminder': datetime.now(),
    })


def end_focus_session():
    """End the current focus session and log time."""
    init_focus_session_state()
    session = st.session_state.focus_session

    if session['active'] and session['start_time']:
        elapsed = (datetime.now() - session['start_time']).total_seconds() / 60
        session['total_watch_time_today'] += elapsed
        session['sessions_completed_today'] += 1

    session['active'] = False
    session['start_time'] = None


def get_session_status() -> dict:
    """Get current session status and stats."""
    init_focus_session_state()
    session = st.session_state.focus_session

    if not session['active'] or not session['start_time']:
        return {
            'active': False,
            'elapsed_minutes': 0,
            'remaining_minutes': 0,
            'needs_break': False,
            'total_today': session['total_watch_time_today'],
            'sessions_today': session['sessions_completed_today'],
        }

    now = datetime.now()
    elapsed = (now - session['start_time']).total_seconds() / 60
    remaining = max(0, session['duration_minutes'] - elapsed)

    # Check if break reminder needed
    time_since_break = (now - session['last_break_reminder']).total_seconds() / 60
    needs_break = time_since_break >= session['break_reminder_minutes']

    return {
        'active': True,
        'elapsed_minutes': round(elapsed, 1),
        'remaining_minutes': round(remaining, 1),
        'needs_break': needs_break,
        'break_interval': session['break_reminder_minutes'],
        'total_today': session['total_watch_time_today'] + elapsed,
        'sessions_today': session['sessions_completed_today'],
        'progress_percent': min(100, (elapsed / session['duration_minutes']) * 100),
    }


def acknowledge_break():
    """Mark that user acknowledged the break reminder."""
    init_focus_session_state()
    st.session_state.focus_session['last_break_reminder'] = datetime.now()


def render_focus_timer_sidebar():
    """
    Render focus timer controls in sidebar.
    Call this in your sidebar rendering.
    """
    init_focus_session_state()
    status = get_session_status()

    st.markdown("#### ⏱️ Focus Session")

    if status['active']:
        # Active session display
        progress = status['progress_percent'] / 100
        st.progress(progress, text=f"{int(status['elapsed_minutes'])} / {int(status['elapsed_minutes'] + status['remaining_minutes'])} min")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Elapsed", f"{int(status['elapsed_minutes'])}m")
        with col2:
            st.metric("Remaining", f"{int(status['remaining_minutes'])}m")

        if st.button("⏹️ End Session", key="end_focus", use_container_width=True):
            end_focus_session()
            st.toast("Session ended! Great job staying focused!")
            st.rerun()

        # Break reminder check
        if status['needs_break']:
            st.warning("🧘 Time for a quick break!")
            import random
            activity = random.choice(BREAK_ACTIVITIES)
            st.info(f"{activity['emoji']} {activity['activity']} ({activity['duration']})")
            if st.button("✓ I took a break", key="break_ack"):
                acknowledge_break()
                st.toast("Great job taking care of yourself!")
                st.rerun()
    else:
        # Not in session - show start options
        st.caption("Track your watch time")

        preset_options = [f"{p['emoji']} {p['label']} ({p['minutes']}min)" for p in SESSION_PRESETS]
        selected = st.selectbox("Session length:", preset_options, key="session_preset")

        # Parse selection
        idx = preset_options.index(selected)
        preset = SESSION_PRESETS[idx]

        if st.button("▶️ Start Session", key="start_focus", use_container_width=True, type="primary"):
            start_focus_session(preset['minutes'], preset['break'])
            st.toast(f"Focus session started! {preset['minutes']} minutes, breaks every {preset['break']}min")
            st.rerun()

    # Today's stats
    st.markdown("---")
    st.caption("Today's Stats")
    st.write(f"📺 Watch time: {int(status['total_today'])} min")
    st.write(f"🎯 Sessions: {status['sessions_today']}")


def render_break_reminder_overlay():
    """
    Render a full break reminder overlay when it's time for a break.

    Call this at the top of your main render function.
    Returns True if overlay is showing (to skip normal content).
    """
    init_focus_session_state()
    status = get_session_status()

    if not status['active'] or not status['needs_break']:
        return False

    # Check if we should show full overlay (been 2+ min since reminder)
    session = st.session_state.focus_session
    time_since = (datetime.now() - session['last_break_reminder']).total_seconds() / 60

    if time_since < 2:
        # Just show toast, not full overlay
        return False

    # Full overlay after ignoring for 2+ minutes
    import random
    activity = random.choice(BREAK_ACTIVITIES)

    st.markdown("""
    <style>
    .break-overlay {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        max-width: 500px;
        margin: 50px auto;
        border: 2px solid rgba(6, 182, 212, 0.3);
    }
    .break-title {
        font-size: 2rem;
        color: #06b6d4;
        margin-bottom: 20px;
    }
    .break-activity {
        font-size: 1.5rem;
        color: #e2e8f0;
        margin: 20px 0;
    }
    .break-reason {
        color: #94a3b8;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="break-overlay">
        <div class="break-title">🧘 Break Time!</div>
        <div class="break-activity">{activity['emoji']} {activity['activity']}</div>
        <div class="break-reason">
            You've been watching for a while. Taking short breaks helps your ADHD brain
            stay fresh and engaged. This will only take {activity['duration']}!
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✓ I took my break!", key="break_done", use_container_width=True, type="primary"):
            acknowledge_break()
            st.toast("Awesome! Back to watching!")
            st.rerun()

        if st.button("⏭️ Skip this time", key="skip_break", use_container_width=True):
            acknowledge_break()
            st.toast("Okay, but try to take a break soon!")
            st.rerun()

    return True


def log_focus_session(supabase_client, user_id: str, duration_minutes: float,
                      content_watched: list = None):
    """
    Log a completed focus session to database.

    Args:
        duration_minutes: How long the session lasted
        content_watched: Optional list of content IDs watched during session
    """
    try:
        session_data = {
            'user_id': user_id,
            'duration_minutes': round(duration_minutes, 1),
            'content_watched': content_watched or [],
            'completed_at': datetime.now().isoformat()
        }
        supabase_client.table('focus_sessions').insert(session_data).execute()
        return True
    except Exception as e:
        print(f"Error logging focus session: {e}")
        return False


def get_focus_stats(supabase_client, user_id: str, days: int = 7) -> dict:
    """
    Get user's focus session statistics.

    Returns dict with:
        - total_sessions: Number of sessions
        - total_minutes: Total watch time
        - avg_session_length: Average session duration
        - longest_session: Longest session
    """
    try:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        result = supabase_client.table('focus_sessions')\
            .select('duration_minutes')\
            .eq('user_id', user_id)\
            .gte('completed_at', since)\
            .execute()

        if not result.data:
            return {
                'total_sessions': 0,
                'total_minutes': 0,
                'avg_session_length': 0,
                'longest_session': 0
            }

        durations = [r['duration_minutes'] for r in result.data]
        return {
            'total_sessions': len(durations),
            'total_minutes': round(sum(durations), 1),
            'avg_session_length': round(sum(durations) / len(durations), 1),
            'longest_session': max(durations)
        }
    except Exception as e:
        print(f"Error getting focus stats: {e}")
        return {}
