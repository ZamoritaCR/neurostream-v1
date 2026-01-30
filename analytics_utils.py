# analytics_utils.py
# --------------------------------------------------
# DOPAMINE.WATCH - ANALYTICS TRACKING SYSTEM
# --------------------------------------------------

import streamlit as st
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List
import json

# Track analytics in session state and optionally to Supabase
def init_analytics_session():
    """Initialize analytics tracking for the session"""
    if "analytics" not in st.session_state:
        st.session_state.analytics = {
            "session_start": datetime.now().isoformat(),
            "page_views": [],
            "clicks": [],
            "mood_selections": [],
            "content_interactions": [],
            "feature_usage": {},
            "scroll_depth": 0
        }

def track_page_view(page_name: str, user_id: Optional[str] = None):
    """Track page view"""
    init_analytics_session()
    st.session_state.analytics["page_views"].append({
        "page": page_name,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    })

def track_click(element: str, context: Optional[Dict] = None, user_id: Optional[str] = None):
    """Track click event"""
    init_analytics_session()
    st.session_state.analytics["clicks"].append({
        "element": element,
        "context": context or {},
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    })

def track_mood_selection(current_mood: str, desired_mood: str, user_id: Optional[str] = None):
    """Track mood selection"""
    init_analytics_session()
    st.session_state.analytics["mood_selections"].append({
        "current": current_mood,
        "desired": desired_mood,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    })

def track_content_interaction(content_id: str, content_type: str, action: str,
                              user_id: Optional[str] = None, metadata: Optional[Dict] = None):
    """Track content interaction (view, save, click, etc.)"""
    init_analytics_session()
    st.session_state.analytics["content_interactions"].append({
        "content_id": content_id,
        "content_type": content_type,
        "action": action,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id
    })

def track_feature_usage(feature: str, user_id: Optional[str] = None):
    """Track feature usage count"""
    init_analytics_session()
    if feature not in st.session_state.analytics["feature_usage"]:
        st.session_state.analytics["feature_usage"][feature] = 0
    st.session_state.analytics["feature_usage"][feature] += 1

def get_session_duration() -> float:
    """Get current session duration in minutes"""
    init_analytics_session()
    start = datetime.fromisoformat(st.session_state.analytics["session_start"])
    return (datetime.now() - start).total_seconds() / 60

def get_session_stats() -> Dict[str, Any]:
    """Get session statistics"""
    init_analytics_session()
    return {
        "duration_minutes": round(get_session_duration(), 2),
        "page_views": len(st.session_state.analytics["page_views"]),
        "clicks": len(st.session_state.analytics["clicks"]),
        "mood_selections": len(st.session_state.analytics["mood_selections"]),
        "content_interactions": len(st.session_state.analytics["content_interactions"]),
        "feature_usage": st.session_state.analytics["feature_usage"]
    }

# Supabase Analytics Functions
def save_session_analytics(supabase_client, user_id: str):
    """Save session analytics to Supabase"""
    if not supabase_client or not user_id:
        return False

    try:
        stats = get_session_stats()
        analytics_data = {
            "user_id": user_id,
            "session_start": st.session_state.analytics["session_start"],
            "session_end": datetime.now().isoformat(),
            "duration_minutes": stats["duration_minutes"],
            "page_views_count": stats["page_views"],
            "clicks_count": stats["clicks"],
            "mood_selections_count": stats["mood_selections"],
            "content_interactions_count": stats["content_interactions"],
            "feature_usage": json.dumps(stats["feature_usage"]),
            "created_at": datetime.now().isoformat()
        }

        supabase_client.table("user_analytics").insert(analytics_data).execute()
        return True
    except Exception as e:
        print(f"Analytics save error: {e}")
        return False

def get_aggregate_analytics(supabase_client, days: int = 7) -> Dict[str, Any]:
    """Get aggregate analytics for admin dashboard"""
    if not supabase_client:
        return {}

    try:
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Total users active
        users = supabase_client.table("user_analytics")\
            .select("user_id")\
            .gte("created_at", since_date)\
            .execute()
        unique_users = len(set(u["user_id"] for u in users.data)) if users.data else 0

        # Total sessions
        sessions = supabase_client.table("user_analytics")\
            .select("*")\
            .gte("created_at", since_date)\
            .execute()
        total_sessions = len(sessions.data) if sessions.data else 0

        # Average session duration
        if sessions.data:
            durations = [s.get("duration_minutes", 0) for s in sessions.data]
            avg_duration = sum(durations) / len(durations) if durations else 0
        else:
            avg_duration = 0

        # Total page views
        total_page_views = sum(s.get("page_views_count", 0) for s in (sessions.data or []))

        # Total content interactions
        total_interactions = sum(s.get("content_interactions_count", 0) for s in (sessions.data or []))

        # Feature usage aggregation
        feature_totals = {}
        for s in (sessions.data or []):
            usage = json.loads(s.get("feature_usage", "{}"))
            for feature, count in usage.items():
                feature_totals[feature] = feature_totals.get(feature, 0) + count

        return {
            "period_days": days,
            "unique_users": unique_users,
            "total_sessions": total_sessions,
            "avg_session_duration": round(avg_duration, 2),
            "total_page_views": total_page_views,
            "total_content_interactions": total_interactions,
            "feature_usage": feature_totals
        }
    except Exception as e:
        print(f"Analytics aggregation error: {e}")
        return {}

def get_mood_analytics(supabase_client, days: int = 7) -> Dict[str, Any]:
    """Get mood selection analytics"""
    if not supabase_client:
        return {}

    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()

        # Get mood history
        moods = supabase_client.table("mood_history")\
            .select("current_feeling, desired_feeling")\
            .gte("created_at", since_date)\
            .execute()

        if not moods.data:
            return {"current_moods": {}, "desired_moods": {}, "transitions": []}

        # Count current moods
        current_counts = {}
        desired_counts = {}
        transitions = []

        for m in moods.data:
            current = m.get("current_feeling", "Unknown")
            desired = m.get("desired_feeling", "Unknown")

            current_counts[current] = current_counts.get(current, 0) + 1
            desired_counts[desired] = desired_counts.get(desired, 0) + 1
            transitions.append(f"{current} -> {desired}")

        # Sort by frequency
        current_sorted = dict(sorted(current_counts.items(), key=lambda x: x[1], reverse=True))
        desired_sorted = dict(sorted(desired_counts.items(), key=lambda x: x[1], reverse=True))

        # Top transitions
        transition_counts = {}
        for t in transitions:
            transition_counts[t] = transition_counts.get(t, 0) + 1
        top_transitions = dict(sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        return {
            "current_moods": current_sorted,
            "desired_moods": desired_sorted,
            "top_transitions": top_transitions,
            "total_selections": len(moods.data)
        }
    except Exception as e:
        print(f"Mood analytics error: {e}")
        return {}

def get_content_analytics(supabase_client, days: int = 7) -> Dict[str, Any]:
    """Get content interaction analytics"""
    if not supabase_client:
        return {}

    try:
        since_date = (date.today() - timedelta(days=days)).isoformat()

        # Get behavior data
        behavior = supabase_client.table("user_behavior")\
            .select("action_type, content_type")\
            .gte("created_at", since_date)\
            .execute()

        if not behavior.data:
            return {"actions": {}, "content_types": {}}

        # Count actions
        action_counts = {}
        content_type_counts = {}

        for b in behavior.data:
            action = b.get("action_type", "Unknown")
            content_type = b.get("content_type", "Unknown")

            action_counts[action] = action_counts.get(action, 0) + 1
            if content_type:
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1

        return {
            "actions": dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)),
            "content_types": dict(sorted(content_type_counts.items(), key=lambda x: x[1], reverse=True)),
            "total_interactions": len(behavior.data)
        }
    except Exception as e:
        print(f"Content analytics error: {e}")
        return {}

def render_analytics_dashboard(supabase_client, is_admin: bool = False):
    """Render analytics dashboard (admin view)"""
    if not is_admin:
        st.warning("Admin access required")
        return

    st.markdown("## Analytics Dashboard")

    # Time period selector
    period = st.selectbox("Time Period", [7, 14, 30, 90], index=0, format_func=lambda x: f"Last {x} days")

    # Main metrics
    col1, col2, col3, col4 = st.columns(4)

    aggregate = get_aggregate_analytics(supabase_client, days=period)

    with col1:
        st.metric("Active Users", aggregate.get("unique_users", 0))
    with col2:
        st.metric("Total Sessions", aggregate.get("total_sessions", 0))
    with col3:
        st.metric("Avg Session (min)", aggregate.get("avg_session_duration", 0))
    with col4:
        st.metric("Content Interactions", aggregate.get("total_content_interactions", 0))

    st.markdown("---")

    # Mood Analytics
    st.markdown("### Mood Analytics")
    mood_data = get_mood_analytics(supabase_client, days=period)

    if mood_data:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top Current Moods**")
            for mood, count in list(mood_data.get("current_moods", {}).items())[:5]:
                st.markdown(f"- {mood}: {count}")

        with col2:
            st.markdown("**Top Desired Moods**")
            for mood, count in list(mood_data.get("desired_moods", {}).items())[:5]:
                st.markdown(f"- {mood}: {count}")

        st.markdown("**Top Mood Transitions**")
        for transition, count in list(mood_data.get("top_transitions", {}).items())[:5]:
            st.markdown(f"- {transition}: {count}")
    else:
        st.info("No mood data available")

    st.markdown("---")

    # Content Analytics
    st.markdown("### Content Analytics")
    content_data = get_content_analytics(supabase_client, days=period)

    if content_data:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Actions**")
            for action, count in list(content_data.get("actions", {}).items())[:5]:
                st.markdown(f"- {action}: {count}")

        with col2:
            st.markdown("**Content Types**")
            for ctype, count in list(content_data.get("content_types", {}).items())[:5]:
                st.markdown(f"- {ctype}: {count}")
    else:
        st.info("No content data available")

    st.markdown("---")

    # Feature Usage
    st.markdown("### Feature Usage")
    feature_usage = aggregate.get("feature_usage", {})

    if feature_usage:
        for feature, count in sorted(feature_usage.items(), key=lambda x: x[1], reverse=True):
            st.markdown(f"- **{feature}**: {count} uses")
    else:
        st.info("No feature usage data available")

# SQL for analytics table (run in Supabase)
ANALYTICS_TABLE_SQL = """
-- User Analytics Table
CREATE TABLE IF NOT EXISTS user_analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    session_start TIMESTAMPTZ NOT NULL,
    session_end TIMESTAMPTZ,
    duration_minutes DECIMAL(10,2),
    page_views_count INT DEFAULT 0,
    clicks_count INT DEFAULT 0,
    mood_selections_count INT DEFAULT 0,
    content_interactions_count INT DEFAULT 0,
    feature_usage JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_analytics_user_id ON user_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_analytics_created_at ON user_analytics(created_at DESC);

-- RLS
ALTER TABLE user_analytics ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own analytics" ON user_analytics;
DROP POLICY IF EXISTS "Users can insert own analytics" ON user_analytics;

CREATE POLICY "Users can view own analytics"
    ON user_analytics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analytics"
    ON user_analytics FOR INSERT
    WITH CHECK (auth.uid() = user_id);
"""
