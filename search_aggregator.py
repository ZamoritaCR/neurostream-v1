# search_aggregator.py
# --------------------------------------------------
# DOPAMINE.WATCH - MULTI-PLATFORM SEARCH AGGREGATOR
# --------------------------------------------------
# Features:
# 1. Unified search across TMDB, Spotify, YouTube
# 2. Mood-based filtering
# 3. Duration filtering for ADHD
# 4. Intelligent ranking
# 5. Streamlit UI Components
# --------------------------------------------------

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os

# --------------------------------------------------
# 1. MOOD-GENRE MAPPING
# --------------------------------------------------

MOOD_GENRE_MAP = {
    "stressed": ["documentary", "nature", "meditation", "ambient", "comedy"],
    "bored": ["action", "comedy", "thriller", "adventure", "mystery"],
    "sad": ["comedy", "animation", "feel-good", "romance", "family"],
    "anxious": ["nature", "cooking", "crafts", "documentary", "lofi"],
    "happy": ["adventure", "comedy", "music", "action", "animation"],
    "tired": ["nature", "documentary", "ambient", "lofi", "romance"],
    "energetic": ["action", "sports", "dance", "electronic", "adventure"],
    "focused": ["documentary", "educational", "ambient", "classical", "thriller"],
    "nostalgic": ["classic", "80s", "90s", "retro", "drama"],
    "curious": ["documentary", "educational", "science", "history", "mystery"]
}


# --------------------------------------------------
# 2. TMDB SEARCH (Movies & TV)
# --------------------------------------------------

def _search_tmdb(query: str, content_type: str = "movie", limit: int = 10) -> List[Dict]:
    """Search TMDB for movies and TV shows."""
    try:
        # Try to use existing TMDB setup from app
        import requests

        api_key = os.environ.get("TMDB_API_KEY") or st.secrets.get("TMDB_API_KEY", "")
        if not api_key:
            return _mock_tmdb_results(query, content_type)

        base_url = "https://api.themoviedb.org/3"
        results = []

        if content_type in ["all", "movie"]:
            response = requests.get(
                f"{base_url}/search/movie",
                params={"api_key": api_key, "query": query, "page": 1},
                timeout=5
            )
            if response.ok:
                data = response.json()
                for item in data.get("results", [])[:limit]:
                    results.append({
                        "id": f"tmdb_movie_{item['id']}",
                        "title": item.get("title", ""),
                        "type": "movie",
                        "platform": "tmdb",
                        "year": item.get("release_date", "")[:4] if item.get("release_date") else "",
                        "rating": item.get("vote_average", 0),
                        "description": item.get("overview", "")[:200],
                        "image_url": f"https://image.tmdb.org/t/p/w300{item['poster_path']}" if item.get("poster_path") else None,
                        "genres": [],  # Would need additional API call
                        "duration_minutes": 120  # Default estimate
                    })

        if content_type in ["all", "tv"]:
            response = requests.get(
                f"{base_url}/search/tv",
                params={"api_key": api_key, "query": query, "page": 1},
                timeout=5
            )
            if response.ok:
                data = response.json()
                for item in data.get("results", [])[:limit]:
                    results.append({
                        "id": f"tmdb_tv_{item['id']}",
                        "title": item.get("name", ""),
                        "type": "tv",
                        "platform": "tmdb",
                        "year": item.get("first_air_date", "")[:4] if item.get("first_air_date") else "",
                        "rating": item.get("vote_average", 0),
                        "description": item.get("overview", "")[:200],
                        "image_url": f"https://image.tmdb.org/t/p/w300{item['poster_path']}" if item.get("poster_path") else None,
                        "genres": [],
                        "duration_minutes": 45  # Episode estimate
                    })

        return results

    except Exception as e:
        print(f"TMDB search error: {e}")
        return _mock_tmdb_results(query, content_type)


def _mock_tmdb_results(query: str, content_type: str) -> List[Dict]:
    """Return mock results when TMDB unavailable."""
    return [
        {
            "id": f"mock_movie_1",
            "title": f"Results for: {query}",
            "type": "movie",
            "platform": "tmdb",
            "year": "2024",
            "rating": 7.5,
            "description": "Connect your TMDB API key to see real results.",
            "image_url": None,
            "genres": ["drama"],
            "duration_minutes": 120
        }
    ]


# --------------------------------------------------
# 3. SPOTIFY SEARCH (Music & Podcasts)
# --------------------------------------------------

def _search_spotify(query: str, content_type: str = "music", limit: int = 10) -> List[Dict]:
    """Search Spotify for music and podcasts."""
    try:
        import requests

        client_id = os.environ.get("SPOTIFY_CLIENT_ID") or st.secrets.get("SPOTIFY_CLIENT_ID", "")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") or st.secrets.get("SPOTIFY_CLIENT_SECRET", "")

        if not client_id or not client_secret:
            return _mock_spotify_results(query, content_type)

        # Get access token
        auth_response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=5
        )

        if not auth_response.ok:
            return _mock_spotify_results(query, content_type)

        token = auth_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        results = []

        if content_type in ["all", "music"]:
            response = requests.get(
                "https://api.spotify.com/v1/search",
                params={"q": query, "type": "track", "limit": limit},
                headers=headers,
                timeout=5
            )
            if response.ok:
                data = response.json()
                for item in data.get("tracks", {}).get("items", []):
                    results.append({
                        "id": f"spotify_track_{item['id']}",
                        "title": item.get("name", ""),
                        "type": "music",
                        "platform": "spotify",
                        "artist": ", ".join([a["name"] for a in item.get("artists", [])]),
                        "album": item.get("album", {}).get("name", ""),
                        "image_url": item.get("album", {}).get("images", [{}])[0].get("url") if item.get("album", {}).get("images") else None,
                        "duration_minutes": round(item.get("duration_ms", 0) / 60000, 1),
                        "spotify_url": item.get("external_urls", {}).get("spotify")
                    })

        if content_type in ["all", "podcast"]:
            response = requests.get(
                "https://api.spotify.com/v1/search",
                params={"q": query, "type": "show", "limit": limit},
                headers=headers,
                timeout=5
            )
            if response.ok:
                data = response.json()
                for item in data.get("shows", {}).get("items", []):
                    results.append({
                        "id": f"spotify_podcast_{item['id']}",
                        "title": item.get("name", ""),
                        "type": "podcast",
                        "platform": "spotify",
                        "publisher": item.get("publisher", ""),
                        "description": item.get("description", "")[:200],
                        "image_url": item.get("images", [{}])[0].get("url") if item.get("images") else None,
                        "duration_minutes": 45,  # Episode estimate
                        "spotify_url": item.get("external_urls", {}).get("spotify")
                    })

        return results

    except Exception as e:
        print(f"Spotify search error: {e}")
        return _mock_spotify_results(query, content_type)


def _mock_spotify_results(query: str, content_type: str) -> List[Dict]:
    """Return mock results when Spotify unavailable."""
    return [
        {
            "id": f"mock_music_1",
            "title": f"Results for: {query}",
            "type": "music",
            "platform": "spotify",
            "artist": "Connect Spotify API",
            "album": "API Keys Required",
            "image_url": None,
            "duration_minutes": 3.5
        }
    ]


# --------------------------------------------------
# 4. YOUTUBE SEARCH (Videos)
# --------------------------------------------------

def _search_youtube(query: str, limit: int = 10) -> List[Dict]:
    """Search YouTube for videos."""
    # YouTube API requires OAuth or API key
    # Return search URL for now
    return [
        {
            "id": f"youtube_search",
            "title": f"Search YouTube: {query}",
            "type": "video",
            "platform": "youtube",
            "description": "Click to search on YouTube",
            "image_url": None,
            "duration_minutes": 10,
            "youtube_url": f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        }
    ]


# --------------------------------------------------
# 5. AGGREGATOR FUNCTIONS
# --------------------------------------------------

def search_all_sync(
    query: str,
    content_type: str = "all",
    mood: Optional[str] = None,
    limit: int = 10,
    max_duration_minutes: Optional[int] = None
) -> List[Dict]:
    """
    Search all platforms synchronously (Streamlit-friendly).

    Args:
        query: Search query
        content_type: movie, tv, music, podcast, video, or all
        mood: Current mood for filtering
        limit: Max results to return
        max_duration_minutes: Filter by max duration

    Returns:
        List of unified content items, ranked by relevance
    """
    combined = []

    # Movies & TV
    if content_type in ["all", "movie", "tv"]:
        combined.extend(_search_tmdb(query, content_type, limit))

    # Music & Podcasts
    if content_type in ["all", "music", "podcast"]:
        combined.extend(_search_spotify(query, content_type, limit))

    # Videos
    if content_type in ["all", "video"]:
        combined.extend(_search_youtube(query, limit))

    # Apply mood filtering
    if mood:
        combined = _apply_mood_filter(combined, mood)

    # Apply duration filter
    if max_duration_minutes:
        combined = [r for r in combined if r.get("duration_minutes", 999) <= max_duration_minutes]

    # Rank results
    ranked = _rank_results(combined, query, mood)

    # Add ADHD-friendly metadata
    for item in ranked:
        item["time_estimate"] = format_duration(item.get("duration_minutes", 0))
        item["adhd_friendly"] = is_adhd_friendly(item)

    return ranked[:limit]


def quick_search_sync(query: str, limit: int = 5) -> List[Dict]:
    """Quick search across all platforms with minimal results."""
    return search_all_sync(query, content_type="all", limit=limit)


def mood_based_search_sync(
    mood: str,
    content_type: str = "all",
    limit: int = 10
) -> List[Dict]:
    """Search based on mood rather than query."""
    genres = MOOD_GENRE_MAP.get(mood.lower(), ["comedy", "drama"])
    query = " ".join(genres[:2])  # Use top 2 genres as search query
    return search_all_sync(query, content_type, mood=mood, limit=limit)


# --------------------------------------------------
# 6. FILTERING & RANKING
# --------------------------------------------------

def _apply_mood_filter(results: List[Dict], mood: str) -> List[Dict]:
    """Filter results based on mood preference."""
    preferred_genres = set(MOOD_GENRE_MAP.get(mood.lower(), []))
    if not preferred_genres:
        return results

    # Score each result based on genre match
    for result in results:
        result_genres = set(g.lower() for g in result.get("genres", []))
        overlap = len(result_genres & preferred_genres)
        result["mood_score"] = overlap

    # Sort by mood score but don't filter out non-matching
    return sorted(results, key=lambda x: x.get("mood_score", 0), reverse=True)


def _rank_results(
    results: List[Dict],
    query: str,
    mood: Optional[str] = None
) -> List[Dict]:
    """Rank results by relevance."""
    query_lower = query.lower()

    for result in results:
        score = 0

        # Title match
        if query_lower in result.get("title", "").lower():
            score += 10

        # High rating
        if result.get("rating", 0) >= 7.5:
            score += 5

        # ADHD-friendly duration
        duration = result.get("duration_minutes", 0)
        if 20 <= duration <= 45:
            score += 3  # Ideal episode length
        elif duration <= 90:
            score += 2

        # Mood match
        score += result.get("mood_score", 0) * 2

        result["relevance_score"] = score

    return sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)


# --------------------------------------------------
# 7. HELPERS
# --------------------------------------------------

def format_duration(minutes: float) -> str:
    """Format duration for display."""
    if minutes <= 0:
        return "Unknown"
    elif minutes < 1:
        return f"{int(minutes * 60)}s"
    elif minutes < 60:
        return f"{int(minutes)}m"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"


def is_adhd_friendly(item: Dict) -> bool:
    """Check if content is ADHD-friendly based on duration."""
    duration = item.get("duration_minutes", 0)
    content_type = item.get("type", "")

    if content_type == "music":
        return True  # Music is always friendly (short)
    elif content_type == "tv":
        return duration <= 45  # Episodes under 45 min
    elif content_type == "movie":
        return duration <= 100  # Movies under 100 min
    elif content_type == "podcast":
        return duration <= 30  # Short podcasts
    else:
        return duration <= 30


# --------------------------------------------------
# 8. STREAMLIT UI COMPONENTS
# --------------------------------------------------

def render_unified_search_bar():
    """Render a unified search bar with filters."""
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        query = st.text_input("🔍 Search everything...", key="unified_search_query")

    with col2:
        content_type = st.selectbox(
            "Type",
            ["all", "movie", "tv", "music", "podcast"],
            key="unified_search_type"
        )

    with col3:
        max_duration = st.selectbox(
            "Max time",
            [None, 30, 60, 90, 120],
            format_func=lambda x: "Any" if x is None else f"{x}m",
            key="unified_search_duration"
        )

    return query, content_type, max_duration


def render_search_results_grid(results: List[Dict]):
    """Render search results in a responsive grid."""
    if not results:
        st.info("No results found. Try a different search!")
        return

    # Platform icons
    platform_icons = {
        "tmdb": "🎬",
        "spotify": "🎵",
        "youtube": "📺"
    }

    # Type icons
    type_icons = {
        "movie": "🎬",
        "tv": "📺",
        "music": "🎵",
        "podcast": "🎙️",
        "video": "📹"
    }

    cols = st.columns(4)
    for i, item in enumerate(results[:12]):
        with cols[i % 4]:
            type_icon = type_icons.get(item.get("type", ""), "📄")
            adhd_badge = "⚡" if item.get("adhd_friendly") else ""

            st.markdown(f"""
            <div style="background: rgba(168, 85, 247, 0.1); padding: 12px;
                        border-radius: 12px; margin: 8px 0; min-height: 200px;">
                <div style="font-size: 2rem; text-align: center;">
                    {type_icon}
                </div>
                <div style="font-weight: bold; margin: 8px 0; font-size: 0.9rem;
                            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {item.get('title', 'Untitled')[:30]}
                </div>
                <div style="font-size: 0.75rem; color: #888;">
                    {item.get('artist', item.get('year', ''))}
                </div>
                <div style="font-size: 0.75rem; margin-top: 8px;">
                    ⏱️ {item.get('time_estimate', 'N/A')} {adhd_badge}
                </div>
                <div style="font-size: 0.75rem; color: #a855f7;">
                    ⭐ {item.get('rating', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_mood_quick_picks(mood: str):
    """Render quick picks based on current mood."""
    st.markdown(f"### 🎯 Quick Picks for {mood.title()} Mood")

    results = mood_based_search_sync(mood, limit=8)
    render_search_results_grid(results)
