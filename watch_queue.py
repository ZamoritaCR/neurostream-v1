"""
Dopamine.watch Watch Queue / Watch Later Utilities
Feature: Content Queue (Phase 1)
"""
from datetime import datetime


def add_to_queue(supabase_client, user_id: str, content_id: str, content_type: str,
                 title: str, poster_path: str = None, mood_context: dict = None) -> bool:
    """
    Add content to user's watch queue.

    Args:
        supabase_client: Supabase client instance
        user_id: User's unique ID
        content_id: TMDB ID or unique identifier
        content_type: 'movie', 'tv', 'podcast', 'music', 'audiobook'
        title: Display title
        poster_path: TMDB poster path (optional)
        mood_context: Dict with current_feeling, desired_feeling at time of save

    Returns True if added successfully.
    """
    try:
        # Check if already in queue
        existing = supabase_client.table('watch_queue')\
            .select('id')\
            .eq('user_id', user_id)\
            .eq('content_id', content_id)\
            .eq('content_type', content_type)\
            .execute()

        if existing.data:
            return False  # Already in queue

        queue_item = {
            'user_id': user_id,
            'content_id': content_id,
            'content_type': content_type,
            'title': title,
            'poster_path': poster_path,
            'mood_when_saved': mood_context or {},
            'status': 'queued',  # 'queued', 'watching', 'watched'
            'added_at': datetime.now().isoformat()
        }
        supabase_client.table('watch_queue').insert(queue_item).execute()
        return True
    except Exception as e:
        print(f"Error adding to queue: {e}")
        return False


def remove_from_queue(supabase_client, user_id: str, content_id: str, content_type: str) -> bool:
    """Remove content from user's watch queue."""
    try:
        supabase_client.table('watch_queue')\
            .delete()\
            .eq('user_id', user_id)\
            .eq('content_id', content_id)\
            .eq('content_type', content_type)\
            .execute()
        return True
    except Exception as e:
        print(f"Error removing from queue: {e}")
        return False


def update_queue_status(supabase_client, user_id: str, content_id: str, content_type: str,
                        new_status: str) -> bool:
    """
    Update queue item status.

    Args:
        new_status: 'queued', 'watching', 'watched'
    """
    try:
        update_data = {
            'status': new_status,
            'updated_at': datetime.now().isoformat()
        }
        if new_status == 'watched':
            update_data['watched_at'] = datetime.now().isoformat()

        supabase_client.table('watch_queue')\
            .update(update_data)\
            .eq('user_id', user_id)\
            .eq('content_id', content_id)\
            .eq('content_type', content_type)\
            .execute()
        return True
    except Exception as e:
        print(f"Error updating queue status: {e}")
        return False


def get_watch_queue(supabase_client, user_id: str, status: str = None,
                    content_type: str = None, limit: int = 50) -> list:
    """
    Get user's watch queue.

    Args:
        status: Filter by status ('queued', 'watching', 'watched') - None for all
        content_type: Filter by content type - None for all
        limit: Max items to return

    Returns list of queue items sorted by added_at (most recent first).
    """
    try:
        query = supabase_client.table('watch_queue')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('added_at', desc=True)\
            .limit(limit)

        if status:
            query = query.eq('status', status)
        if content_type:
            query = query.eq('content_type', content_type)

        result = query.execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting watch queue: {e}")
        return []


def is_in_queue(supabase_client, user_id: str, content_id: str, content_type: str) -> bool:
    """Check if content is already in user's queue."""
    try:
        result = supabase_client.table('watch_queue')\
            .select('id')\
            .eq('user_id', user_id)\
            .eq('content_id', content_id)\
            .eq('content_type', content_type)\
            .execute()
        return len(result.data) > 0 if result.data else False
    except:
        return False


def get_queue_stats(supabase_client, user_id: str) -> dict:
    """
    Get statistics about user's watch queue.

    Returns dict with:
        - total: Total items in queue
        - queued: Items waiting to watch
        - watching: Items currently watching
        - watched: Completed items
        - by_type: Count by content type
    """
    try:
        result = supabase_client.table('watch_queue')\
            .select('status, content_type')\
            .eq('user_id', user_id)\
            .execute()

        if not result.data:
            return {
                'total': 0,
                'queued': 0,
                'watching': 0,
                'watched': 0,
                'by_type': {}
            }

        stats = {
            'total': len(result.data),
            'queued': 0,
            'watching': 0,
            'watched': 0,
            'by_type': {}
        }

        for item in result.data:
            status = item.get('status', 'queued')
            ctype = item.get('content_type', 'unknown')

            if status in stats:
                stats[status] += 1

            stats['by_type'][ctype] = stats['by_type'].get(ctype, 0) + 1

        return stats
    except Exception as e:
        print(f"Error getting queue stats: {e}")
        return {}


def get_queue_by_mood(supabase_client, user_id: str, desired_feeling: str) -> list:
    """
    Get queue items that were saved when user wanted a specific feeling.

    Useful for "What did I save for when I want to feel X?"
    """
    try:
        result = supabase_client.table('watch_queue')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('status', 'queued')\
            .order('added_at', desc=True)\
            .execute()

        if not result.data:
            return []

        # Filter by mood context
        matching = []
        for item in result.data:
            mood = item.get('mood_when_saved', {})
            if mood.get('desired_feeling') == desired_feeling:
                matching.append(item)

        return matching
    except Exception as e:
        print(f"Error getting queue by mood: {e}")
        return []


def render_queue_button(st, supabase_client, user_id: str, content_id: str, content_type: str,
                        title: str, poster_path: str = None, current_feeling: str = None,
                        desired_feeling: str = None, button_key: str = None):
    """
    Render a Watch Later button for a piece of content.

    Call this in your content card rendering.
    """
    in_queue = is_in_queue(supabase_client, user_id, str(content_id), content_type)
    key = button_key or f"queue_{content_type}_{content_id}"

    if in_queue:
        if st.button("✓ In Queue", key=key, disabled=True):
            pass
    else:
        if st.button("+ Watch Later", key=key):
            mood_context = {}
            if current_feeling:
                mood_context['current_feeling'] = current_feeling
            if desired_feeling:
                mood_context['desired_feeling'] = desired_feeling

            if add_to_queue(supabase_client, user_id, str(content_id), content_type,
                            title, poster_path, mood_context):
                st.toast(f"Added '{title}' to your queue!")
                st.rerun()
            else:
                st.toast("Already in your queue!")
