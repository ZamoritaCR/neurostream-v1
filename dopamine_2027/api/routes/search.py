"""
═══════════════════════════════════════════════════════════════════════════════
SEARCH API ROUTES
Unified search across TMDB, Spotify, and YouTube.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from services.search.aggregator import SearchAggregator
from services.search.tmdb import TMDBService
from services.search.spotify import SpotifyService
from services.search.youtube import YouTubeService

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SearchResult(BaseModel):
    id: str
    title: str
    type: str
    platform: str
    poster_url: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    duration_minutes: Optional[float] = None
    release_year: Optional[int] = None


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]
    platforms_searched: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/", response_model=SearchResponse)
async def search_all(
    q: str = Query(..., min_length=1, description="Search query"),
    type: Optional[str] = Query(None, description="Content type: movie, tv, music, podcast, video, all"),
    mood: Optional[str] = Query(None, description="Current mood for filtering"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results per platform"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in minutes (ADHD-friendly)")
):
    """
    Search across all platforms (TMDB, Spotify, YouTube).

    ADHD-Friendly Features:
    - Filter by max duration for manageable content
    - Mood-based filtering for emotional state matching
    - Unified results ranked by relevance
    """
    aggregator = SearchAggregator()

    results = await aggregator.search_all(
        query=q,
        content_type=type or "all",
        mood=mood,
        limit=limit,
        max_duration_minutes=max_duration
    )

    return SearchResponse(
        query=q,
        total_results=len(results),
        results=results,
        platforms_searched=["tmdb", "spotify", "youtube"]
    )


@router.get("/quick")
async def quick_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20)
):
    """
    Quick search for autocomplete/suggestions.
    Returns minimal data for fast response.
    """
    aggregator = SearchAggregator()
    results = await aggregator.search_all(query=q, limit=limit)

    return {
        "results": [
            {
                "id": r.get("id"),
                "title": r.get("title"),
                "type": r.get("type"),
                "platform": r.get("platform"),
                "poster_url": r.get("poster_url")
            }
            for r in results
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PLATFORM-SPECIFIC SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/movies")
async def search_movies(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search movies via TMDB."""
    service = TMDBService()
    results = await service.search_movies(q, limit)
    return {"results": results, "total": len(results)}


@router.get("/tv")
async def search_tv_shows(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Search TV shows via TMDB."""
    service = TMDBService()
    results = await service.search_tv(q, limit)
    return {"results": results, "total": len(results)}


@router.get("/music")
async def search_music(
    q: str = Query(..., min_length=1),
    type: str = Query("track", description="track, album, playlist, podcast"),
    limit: int = Query(10, ge=1, le=50)
):
    """Search music/audio via Spotify."""
    service = SpotifyService()

    if type == "track":
        results = await service.search_tracks(q, limit)
    elif type == "album":
        results = await service.search_albums(q, limit)
    elif type == "playlist":
        results = await service.search_playlists(q, limit)
    elif type == "podcast":
        results = await service.search_podcasts(q, limit)
    else:
        results = await service.search_all(q, limit // 4)
        # Flatten results
        flat_results = []
        for category in results.values():
            flat_results.extend(category)
        results = flat_results

    return {"results": results, "total": len(results)}


@router.get("/videos")
async def search_videos(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    max_duration: Optional[int] = Query(None, description="Max duration in minutes")
):
    """Search videos via YouTube."""
    service = YouTubeService()

    if max_duration:
        results = await service.search_by_duration(q, max_duration, limit)
    else:
        results = await service.search_videos(q, limit)

    return {"results": results, "total": len(results)}


# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/trending")
async def get_trending(
    type: str = Query("all", description="movie, tv, music, video, all"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending content across platforms."""
    results = []

    if type in ["all", "movie", "tv"]:
        tmdb = TMDBService()
        trending = await tmdb.get_trending(media_type=type if type != "all" else "all", limit=limit)
        results.extend(trending)

    if type in ["all", "video"]:
        youtube = YouTubeService()
        trending = await youtube.get_trending(limit=limit)
        results.extend(trending)

    return {"results": results[:limit], "total": len(results)}


@router.get("/mood/{mood}")
async def get_by_mood(
    mood: str,
    type: str = Query("all"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get content recommendations based on mood.

    Supported moods:
    - happy, sad, anxious, calm, energetic, tired, bored, focused
    """
    aggregator = SearchAggregator()

    # Map moods to search strategies
    mood_queries = {
        "happy": "uplifting feel good comedy",
        "sad": "comforting heartwarming emotional",
        "anxious": "calming relaxing peaceful",
        "calm": "chill ambient relaxing",
        "energetic": "action exciting adventure",
        "tired": "cozy comfort easy watch",
        "bored": "exciting thriller surprising",
        "focused": "documentary educational interesting"
    }

    query = mood_queries.get(mood.lower(), mood)
    results = await aggregator.search_all(
        query=query,
        content_type=type,
        mood=mood,
        limit=limit
    )

    return {
        "mood": mood,
        "results": results,
        "total": len(results),
        "suggestion": f"Based on your {mood} mood, here's what might help!"
    }


@router.get("/adhd-friendly")
async def get_adhd_friendly(
    max_duration: int = Query(30, description="Max duration in minutes"),
    mood: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get ADHD-friendly content recommendations.

    Features:
    - Short duration content
    - High engagement scores
    - Quick dopamine hits
    """
    aggregator = SearchAggregator()

    # Search for engaging, short content
    results = await aggregator.search_all(
        query="popular trending top rated",
        content_type="all",
        mood=mood,
        limit=limit * 2,
        max_duration_minutes=max_duration
    )

    # Filter and sort by ADHD-friendliness
    adhd_results = [
        r for r in results
        if r.get("duration_minutes", 999) <= max_duration
    ]

    return {
        "results": adhd_results[:limit],
        "total": len(adhd_results),
        "max_duration": max_duration,
        "tip": f"All content under {max_duration} minutes - perfect for ADHD brains!"
    }
