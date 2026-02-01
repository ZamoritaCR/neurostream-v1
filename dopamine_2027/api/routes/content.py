"""
═══════════════════════════════════════════════════════════════════════════════
CONTENT API ROUTES
Content details, recommendations, and management.
═══════════════════════════════════════════════════════════════════════════════
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from services.search.tmdb import TMDBService
from services.search.spotify import SpotifyService
from services.search.youtube import YouTubeService

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT DETAILS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/movie/{movie_id}")
async def get_movie_details(movie_id: int):
    """Get detailed movie information from TMDB."""
    service = TMDBService()

    details = await service.get_movie_details(movie_id)
    if not details:
        raise HTTPException(status_code=404, detail="Movie not found")

    return details


@router.get("/movie/{movie_id}/recommendations")
async def get_movie_recommendations(movie_id: int, limit: int = Query(10, ge=1, le=50)):
    """Get movie recommendations based on a movie."""
    service = TMDBService()

    recommendations = await service.get_recommendations(movie_id, limit)

    return {
        "based_on": movie_id,
        "recommendations": recommendations,
        "total": len(recommendations)
    }


@router.get("/spotify/track/{track_id}")
async def get_track_details(track_id: str):
    """Get detailed track information from Spotify."""
    service = SpotifyService()

    details = await service.get_track(track_id)
    if not details:
        raise HTTPException(status_code=404, detail="Track not found")

    return details


@router.get("/spotify/album/{album_id}")
async def get_album_details(album_id: str):
    """Get detailed album information from Spotify."""
    service = SpotifyService()

    details = await service.get_album(album_id)
    if not details:
        raise HTTPException(status_code=404, detail="Album not found")

    return details


@router.get("/spotify/playlist/{playlist_id}")
async def get_playlist_details(playlist_id: str):
    """Get detailed playlist information from Spotify."""
    service = SpotifyService()

    details = await service.get_playlist(playlist_id)
    if not details:
        raise HTTPException(status_code=404, detail="Playlist not found")

    return details


@router.get("/spotify/podcast/{show_id}")
async def get_podcast_details(show_id: str):
    """Get detailed podcast/show information from Spotify."""
    service = SpotifyService()

    details = await service.get_podcast(show_id)
    if not details:
        raise HTTPException(status_code=404, detail="Podcast not found")

    return details


@router.get("/youtube/video/{video_id}")
async def get_video_details(video_id: str):
    """Get detailed video information from YouTube."""
    service = YouTubeService()

    details = await service.get_video(video_id)
    if not details:
        raise HTTPException(status_code=404, detail="Video not found")

    return details


@router.get("/youtube/channel/{channel_id}")
async def get_channel_details(channel_id: str):
    """Get detailed channel information from YouTube."""
    service = YouTubeService()

    details = await service.get_channel(channel_id)
    if not details:
        raise HTTPException(status_code=404, detail="Channel not found")

    return details


@router.get("/youtube/playlist/{playlist_id}")
async def get_youtube_playlist(playlist_id: str, limit: int = Query(50, ge=1, le=50)):
    """Get videos from a YouTube playlist."""
    service = YouTubeService()

    videos = await service.get_playlist_videos(playlist_id, limit)

    return {
        "playlist_id": playlist_id,
        "videos": videos,
        "total": len(videos)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY & FEATURED
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/featured/playlists")
async def get_featured_playlists(limit: int = Query(10, ge=1, le=50)):
    """Get Spotify's featured playlists."""
    service = SpotifyService()

    playlists = await service.get_featured_playlists(limit)

    return {
        "playlists": playlists,
        "total": len(playlists)
    }


@router.get("/featured/new-releases")
async def get_new_releases(limit: int = Query(10, ge=1, le=50)):
    """Get new album releases from Spotify."""
    service = SpotifyService()

    albums = await service.get_new_releases(limit)

    return {
        "albums": albums,
        "total": len(albums)
    }


@router.get("/featured/trending-videos")
async def get_trending_videos(
    category: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending YouTube videos."""
    service = YouTubeService()

    videos = await service.get_trending(category_id=category, limit=limit)

    return {
        "videos": videos,
        "total": len(videos)
    }


@router.get("/featured/trending-movies")
async def get_trending_movies(
    time_window: str = Query("week", description="day or week"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending movies from TMDB."""
    service = TMDBService()

    movies = await service.get_trending(
        media_type="movie",
        time_window=time_window,
        limit=limit
    )

    return {
        "movies": movies,
        "total": len(movies),
        "time_window": time_window
    }


@router.get("/featured/trending-tv")
async def get_trending_tv(
    time_window: str = Query("week", description="day or week"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending TV shows from TMDB."""
    service = TMDBService()

    shows = await service.get_trending(
        media_type="tv",
        time_window=time_window,
        limit=limit
    )

    return {
        "shows": shows,
        "total": len(shows),
        "time_window": time_window
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ADHD-FRIENDLY CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/adhd/quick-videos")
async def get_quick_videos(
    query: str = Query("popular"),
    max_minutes: int = Query(10, ge=1, le=30)
):
    """Get short, ADHD-friendly videos."""
    service = YouTubeService()

    videos = await service.get_quick_content(query, max_minutes)

    return {
        "videos": videos,
        "max_duration_minutes": max_minutes,
        "tip": f"All videos under {max_minutes} minutes!"
    }


@router.get("/adhd/focus-music")
async def get_focus_music(
    energy: str = Query("medium", description="low, medium, high")
):
    """Get music for ADHD focus sessions."""
    service = SpotifyService()

    from services.search.spotify import get_recommendations_for_adhd

    tracks = await get_recommendations_for_adhd(energy)

    return {
        "tracks": tracks,
        "energy_level": energy,
        "tip": {
            "low": "Calm ambient music for relaxation",
            "medium": "Balanced beats for steady focus",
            "high": "Upbeat music for motivation"
        }.get(energy, "Music for focus")
    }


@router.get("/adhd/mood-playlist")
async def get_mood_playlist(
    mood: str = Query(..., description="happy, sad, calm, energetic, etc."),
    limit: int = Query(10, ge=1, le=50)
):
    """Get playlist matching current mood."""
    service = SpotifyService()

    playlists = await service.get_mood_playlist(mood, limit)

    return {
        "mood": mood,
        "playlists": playlists,
        "total": len(playlists)
    }


@router.get("/adhd/channel-binge")
async def get_channel_for_binge(
    channel_id: str,
    limit: int = Query(20, ge=1, le=50)
):
    """Get videos from a channel optimized for binge-watching."""
    service = YouTubeService()

    videos = await service.get_channel_videos(channel_id, limit, order="viewCount")

    # Sort by popularity for best binge experience
    sorted_videos = sorted(
        videos,
        key=lambda v: int(v.get("view_count", 0) or 0),
        reverse=True
    )

    return {
        "channel_id": channel_id,
        "videos": sorted_videos,
        "tip": "Start with the most popular videos!"
    }
