"""
Dopamine.watch Mood History Utilities
Feature: Mood History Logging (Phase 1)
"""
from datetime import datetime, timedelta


def log_mood_selection(supabase_client, user_id: str, current_feeling: str, desired_feeling: str, source: str = "manual"):
    """
    Log a mood selection to the database.

    Args:
        supabase_client: Supabase client instance
        user_id: User's unique ID
        current_feeling: How the user currently feels
        desired_feeling: How the user wants to feel
        source: Where the mood was set from ('manual', 'mr_dp', 'quick_hit')
    """
    try:
        mood_data = {
            'user_id': user_id,
            'current_feeling': current_feeling,
            'desired_feeling': desired_feeling,
            'source': source,
            'created_at': datetime.now().isoformat()
        }
        supabase_client.table('mood_history').insert(mood_data).execute()
        return True
    except Exception as e:
        print(f"Error logging mood: {e}")
        return False


def get_mood_history(supabase_client, user_id: str, days: int = 7) -> list:
    """
    Get user's mood history for the past N days.

    Returns list of mood entries sorted by most recent first.
    """
    try:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        result = supabase_client.table('mood_history')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', since)\
            .order('created_at', desc=True)\
            .execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting mood history: {e}")
        return []


def get_top_moods(supabase_client, user_id: str, mood_type: str = 'current', days: int = 30, limit: int = 5) -> list:
    """
    Get user's most frequent moods.

    Args:
        mood_type: 'current' or 'desired'
        days: How many days to look back
        limit: Max number of moods to return

    Returns list of tuples: [(mood, count), ...]
    """
    try:
        history = get_mood_history(supabase_client, user_id, days)
        if not history:
            return []

        # Count occurrences
        field = 'current_feeling' if mood_type == 'current' else 'desired_feeling'
        counts = {}
        for entry in history:
            mood = entry.get(field)
            if mood:
                counts[mood] = counts.get(mood, 0) + 1

        # Sort by count descending
        sorted_moods = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_moods[:limit]
    except Exception as e:
        print(f"Error getting top moods: {e}")
        return []


def get_mood_patterns(supabase_client, user_id: str, days: int = 30) -> dict:
    """
    Analyze mood patterns for insights.

    Returns dict with:
        - top_current: Most frequent current feelings
        - top_desired: Most frequent desired feelings
        - common_transitions: Most common current->desired pairs
        - mood_by_hour: Which moods appear at which hours
    """
    try:
        history = get_mood_history(supabase_client, user_id, days)
        if not history:
            return {}

        # Count transitions
        transitions = {}
        hour_moods = {}

        for entry in history:
            current = entry.get('current_feeling')
            desired = entry.get('desired_feeling')
            created_at = entry.get('created_at', '')

            # Count transition
            if current and desired:
                key = f"{current} → {desired}"
                transitions[key] = transitions.get(key, 0) + 1

            # Track hour (if we can parse the timestamp)
            try:
                hour = datetime.fromisoformat(created_at.replace('Z', '+00:00')).hour
                if current:
                    if hour not in hour_moods:
                        hour_moods[hour] = {}
                    hour_moods[hour][current] = hour_moods[hour].get(current, 0) + 1
            except:
                pass

        return {
            'top_current': get_top_moods(supabase_client, user_id, 'current', days, 5),
            'top_desired': get_top_moods(supabase_client, user_id, 'desired', days, 5),
            'common_transitions': sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:5],
            'mood_by_hour': hour_moods,
            'total_entries': len(history)
        }
    except Exception as e:
        print(f"Error analyzing mood patterns: {e}")
        return {}


def get_mood_streak(supabase_client, user_id: str) -> int:
    """
    Get the user's consecutive days of mood logging.
    """
    try:
        # Get all mood history
        result = supabase_client.table('mood_history')\
            .select('created_at')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()

        if not result.data:
            return 0

        # Get unique dates
        dates = set()
        for entry in result.data:
            try:
                dt = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
                dates.add(dt.date())
            except:
                pass

        if not dates:
            return 0

        # Count consecutive days from today
        today = datetime.now().date()
        streak = 0
        check_date = today

        while check_date in dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak
    except Exception as e:
        print(f"Error getting mood streak: {e}")
        return 0
