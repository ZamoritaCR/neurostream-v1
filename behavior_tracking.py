"""
Dopamine.watch Behavior Tracking Utilities
Feature: User Behavior Analytics (Phase 1)
"""
from datetime import datetime, timedelta


def log_user_action(supabase_client, user_id: str, action_type: str, content_id: str = None,
                    content_type: str = None, metadata: dict = None):
    """
    Log a user action for behavior tracking.

    Args:
        supabase_client: Supabase client instance
        user_id: User's unique ID
        action_type: Type of action ('view', 'click', 'save', 'watch', 'search', 'mr_dp_chat', 'quick_hit')
        content_id: ID of content interacted with (if applicable)
        content_type: Type of content ('movie', 'tv', 'podcast', 'music', 'audiobook')
        metadata: Additional data (e.g., search query, mood at time of action)
    """
    try:
        action_data = {
            'user_id': user_id,
            'action_type': action_type,
            'content_id': content_id,
            'content_type': content_type,
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat()
        }
        supabase_client.table('user_behavior').insert(action_data).execute()
        return True
    except Exception as e:
        print(f"Error logging action: {e}")
        return False


def get_user_activity(supabase_client, user_id: str, days: int = 7, action_type: str = None) -> list:
    """
    Get user's activity history.

    Args:
        days: How many days to look back
        action_type: Filter by specific action type (optional)

    Returns list of activity entries.
    """
    try:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        query = supabase_client.table('user_behavior')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', since)\
            .order('created_at', desc=True)

        if action_type:
            query = query.eq('action_type', action_type)

        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting user activity: {e}")
        return []


def get_favorite_content_types(supabase_client, user_id: str, days: int = 30) -> list:
    """
    Get user's most engaged content types.

    Returns list of tuples: [(content_type, count), ...]
    """
    try:
        activity = get_user_activity(supabase_client, user_id, days)
        if not activity:
            return []

        # Count by content type
        counts = {}
        for entry in activity:
            ctype = entry.get('content_type')
            if ctype:
                counts[ctype] = counts.get(ctype, 0) + 1

        return sorted(counts.items(), key=lambda x: x[1], reverse=True)
    except Exception as e:
        print(f"Error getting favorite content types: {e}")
        return []


def get_peak_usage_hours(supabase_client, user_id: str, days: int = 30) -> dict:
    """
    Analyze when user is most active.

    Returns dict with hour -> activity count.
    """
    try:
        activity = get_user_activity(supabase_client, user_id, days)
        if not activity:
            return {}

        hours = {}
        for entry in activity:
            try:
                created = entry.get('created_at', '')
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                hour = dt.hour
                hours[hour] = hours.get(hour, 0) + 1
            except:
                pass

        return hours
    except Exception as e:
        print(f"Error getting peak usage hours: {e}")
        return {}


def get_engagement_score(supabase_client, user_id: str, days: int = 7) -> dict:
    """
    Calculate user engagement metrics.

    Returns dict with:
        - total_actions: Total number of actions
        - unique_days: Number of unique days with activity
        - avg_daily_actions: Average actions per active day
        - most_common_action: Most frequent action type
        - engagement_level: 'low', 'medium', 'high'
    """
    try:
        activity = get_user_activity(supabase_client, user_id, days)
        if not activity:
            return {
                'total_actions': 0,
                'unique_days': 0,
                'avg_daily_actions': 0,
                'most_common_action': None,
                'engagement_level': 'low'
            }

        # Count unique days
        unique_days = set()
        action_counts = {}

        for entry in activity:
            try:
                created = entry.get('created_at', '')
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                unique_days.add(dt.date())
            except:
                pass

            action = entry.get('action_type')
            if action:
                action_counts[action] = action_counts.get(action, 0) + 1

        total = len(activity)
        days_active = len(unique_days)
        avg_daily = total / days_active if days_active > 0 else 0

        # Determine engagement level
        if avg_daily >= 10:
            level = 'high'
        elif avg_daily >= 3:
            level = 'medium'
        else:
            level = 'low'

        most_common = max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None

        return {
            'total_actions': total,
            'unique_days': days_active,
            'avg_daily_actions': round(avg_daily, 1),
            'most_common_action': most_common,
            'engagement_level': level
        }
    except Exception as e:
        print(f"Error calculating engagement: {e}")
        return {}


def get_content_recommendations_from_behavior(supabase_client, user_id: str) -> dict:
    """
    Analyze behavior to suggest content preferences.

    Returns dict with insights for personalization.
    """
    try:
        # Get recent behavior
        activity = get_user_activity(supabase_client, user_id, days=30)
        if not activity:
            return {}

        # Analyze patterns
        favorite_types = get_favorite_content_types(supabase_client, user_id, 30)
        peak_hours = get_peak_usage_hours(supabase_client, user_id, 30)

        # Find time of day preference
        morning = sum(peak_hours.get(h, 0) for h in range(5, 12))  # 5am-12pm
        afternoon = sum(peak_hours.get(h, 0) for h in range(12, 17))  # 12pm-5pm
        evening = sum(peak_hours.get(h, 0) for h in range(17, 22))  # 5pm-10pm
        night = sum(peak_hours.get(h, 0) for h in range(22, 24)) + sum(peak_hours.get(h, 0) for h in range(0, 5))

        time_preference = 'evening'  # default
        max_time = max(morning, afternoon, evening, night)
        if max_time == morning:
            time_preference = 'morning'
        elif max_time == afternoon:
            time_preference = 'afternoon'
        elif max_time == night:
            time_preference = 'night'

        return {
            'favorite_content_types': favorite_types[:3],
            'time_preference': time_preference,
            'peak_hours': sorted(peak_hours.items(), key=lambda x: x[1], reverse=True)[:3],
            'total_activity_count': len(activity)
        }
    except Exception as e:
        print(f"Error generating behavior recommendations: {e}")
        return {}
