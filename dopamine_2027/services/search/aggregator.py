"""
═══════════════════════════════════════════════════════════════════════════════
SEARCH AGGREGATOR
Multi-platform content search across TMDB, Spotify, YouTube.
Parallel execution for speed, intelligent ranking for relevance.
═══════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp

from config.settings import MOODS


class SearchAggregator:
    """
    Searches across multiple platforms simultaneously.
    Returns unified, ranked results with ADHD-friendly metadata.
    """

    def __init__(self):
        self.mood_genre_map = {
            "stressed": ["documentary", "nature", "meditation", "ambient"],
            "bored": ["action", "comedy", "thriller", "adventure"],
            "sad": ["comedy", "animation", "feel-good", "romance"],
            "anxious": ["nature", "cooking", "crafts", "documentary"],
            "happy": ["adventure", "comedy", "music", "action"],
            "tired": ["nature", "documentary", "ambient", "lo-fi"],
            "energetic": ["action", "sports", "dance", "electronic"],
            "focused": ["documentary", "educational", "ambient", "classical"]
        }

    async def search_all(
        self,
        query: str,
        content_type: str = "all",
        mood: str = None,
        limit: int = 10,
        user_id: str = None,
        max_duration_minutes: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search all platforms in parallel.

        Args:
            query: Search query
            content_type: movie, tv, music, podcast, or all
            mood: Current mood for filtering
            limit: Max results to return
            user_id: For personalization
            max_duration_minutes: Filter by max duration

        Returns:
            List of unified content items, ranked by relevance
        """

        tasks = []

        # Movies & TV
        if content_type in ["all", "movie", "tv"]:
            tasks.append(self._search_tmdb(query, content_type, limit))

        # Music & Podcasts
        if content_type in ["all", "music", "podcast"]:
            tasks.append(self._search_spotify(query, content_type, limit))

        # Videos
        if content_type in ["all", "video", "shorts"]:
            tasks.append(self._search_youtube(query, limit))

        # Execute all searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        combined = []
        for result in results:
            if isinstance(result, list):
                combined.extend(result)
            elif isinstance(result, Exception):
                print(f"Search error: {result}")

        # Apply mood filtering
        if mood:
            combined = self._apply_mood_filter(combined, mood)

        # Apply duration filter
        if max_duration_minutes:
            combined = [r for r in combined if r.get("duration_minutes", 999) <= max_duration_minutes]

        # Rank results
        ranked = self._rank_results(combined, query, mood, user_id)

        # Add ADHD-friendly metadata
        for item in ranked:
            item["time_estimate"] = self._format_duration(item.get("duration_minutes", 0))
            item["adhd_friendly"] = self._is_adhd_friendly(item)

        return ranked[:limit]

    async def _search_tmdb(self, query: str, content_type: str, limit: int) -> List[Dict[str, Any]]:
        """Search TMDB for movies and TV shows."""
        try:
            from services.search.tmdb import TMDBService
            tmdb = TMDBService()

            results = []

            if content_type in ["all", "movie"]:
                movies = await tmdb.search_movies(query, limit)
                results.extend(movies)

            if content_type in ["all", "tv"]:
                shows = await tmdb.search_tv(query, limit)
                results.extend(shows)

            return results

        except ImportError:
            # Return mock data if TMDB service not implemented
            return self._mock_tmdb_results(query, content_type)
        except Exception as e:
            print(f"TMDB search error: {e}")
            return []

    async def _search_spotify(self, query: str, content_type: str, limit: int) -> List[Dict[str, Any]]:
        """Search Spotify for music and podcasts."""
        try:
            from services.search.spotify import SpotifyService
            spotify = SpotifyService()

            results = []

            if content_type in ["all", "music"]:
                tracks = await spotify.search_tracks(query, limit)
                results.extend(tracks)

            if content_type in ["all", "podcast"]:
                podcasts = await spotify.search_podcasts(query, limit)
                results.extend(podcasts)

            return results

        except ImportError:
            return self._mock_spotify_results(query, content_type)
        except Exception as e:
            print(f"Spotify search error: {e}")
            return []

    async def _search_youtube(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search YouTube for videos."""
        try:
            from services.search.youtube import YouTubeService
            youtube = YouTubeService()
            return await youtube.search(query, limit)

        except ImportError:
            return self._mock_youtube_results(query)
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []

    def _apply_mood_filter(self, results: List[Dict], mood: str) -> List[Dict]:
        """Filter results based on mood preferences."""
        preferred_genres = self.mood_genre_map.get(mood, [])

        if not preferred_genres:
            return results

        # Boost items matching mood genres
        for item in results:
            item_genres = item.get("genres", [])
            mood_match = any(g.lower() in [pg.lower() for pg in preferred_genres] for g in item_genres)
            item["mood_boost"] = 20 if mood_match else 0

        return results

    def _rank_results(
        self,
        results: List[Dict],
        query: str,
        mood: str = None,
        user_id: str = None
    ) -> List[Dict]:
        """
        Rank results by relevance.

        Scoring factors:
        - Query match: 30 points
        - Mood match: 25 points
        - Rating: 20 points
        - Recency: 15 points
        - ADHD friendly: 10 points
        """

        query_lower = query.lower()

        for item in results:
            score = 0

            # Query match (title contains query)
            title = item.get("title", "").lower()
            if query_lower in title:
                score += 30
            elif any(word in title for word in query_lower.split()):
                score += 20

            # Mood boost
            score += item.get("mood_boost", 0)

            # Rating (normalize to 0-20)
            rating = item.get("rating", 0)
            score += (rating / 10) * 20

            # Recency (newer = better, max 15 points)
            year = item.get("release_year", 2020)
            years_old = 2027 - year
            if years_old <= 1:
                score += 15
            elif years_old <= 3:
                score += 10
            elif years_old <= 5:
                score += 5

            # ADHD friendly bonus
            duration = item.get("duration_minutes", 120)
            if duration <= 30:
                score += 10
            elif duration <= 60:
                score += 5

            item["relevance_score"] = score

        # Sort by score
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return results

    def _format_duration(self, minutes: int) -> str:
        """Format duration as human-readable string."""
        if not minutes:
            return "Unknown"
        if minutes < 5:
            return "Under 5 min"
        if minutes < 15:
            return "~15 min"
        if minutes < 30:
            return "~30 min"
        if minutes < 60:
            return "~1 hour"
        if minutes < 90:
            return "~1.5 hours"
        if minutes < 120:
            return "~2 hours"
        hours = minutes // 60
        return f"~{hours} hours"

    def _is_adhd_friendly(self, item: Dict) -> bool:
        """Determine if content is ADHD-friendly."""
        # Short duration is good
        duration = item.get("duration_minutes", 999)
        if duration <= 30:
            return True

        # Highly rated is good
        rating = item.get("rating", 0)
        if rating >= 8.0:
            return True

        # Certain genres are engaging
        adhd_genres = ["comedy", "action", "animation", "documentary"]
        genres = item.get("genres", [])
        if any(g.lower() in adhd_genres for g in genres):
            return True

        return False

    # ═══════════════════════════════════════════════════════════════════════════
    # MOCK DATA (for when services aren't fully implemented)
    # ═══════════════════════════════════════════════════════════════════════════

    def _mock_tmdb_results(self, query: str, content_type: str) -> List[Dict]:
        """Mock TMDB results."""
        movies = [
            {
                "id": "tmdb_1",
                "title": "Spider-Man: Into the Spider-Verse",
                "type": "movie",
                "platform": "tmdb",
                "poster_url": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg",
                "rating": 8.4,
                "release_year": 2018,
                "duration_minutes": 117,
                "genres": ["Animation", "Action", "Adventure"],
                "description": "Miles Morales becomes Spider-Man and must save the multiverse."
            },
            {
                "id": "tmdb_2",
                "title": "Everything Everywhere All at Once",
                "type": "movie",
                "platform": "tmdb",
                "poster_url": "https://image.tmdb.org/t/p/w500/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
                "rating": 8.0,
                "release_year": 2022,
                "duration_minutes": 139,
                "genres": ["Action", "Adventure", "Comedy"],
                "description": "A woman discovers she can access parallel universes."
            },
            {
                "id": "tmdb_3",
                "title": "Paddington 2",
                "type": "movie",
                "platform": "tmdb",
                "poster_url": "https://image.tmdb.org/t/p/w500/egjg7C67sC0rLUZ3gVJSjlsC9dK.jpg",
                "rating": 7.8,
                "release_year": 2017,
                "duration_minutes": 103,
                "genres": ["Comedy", "Family", "Adventure"],
                "description": "Paddington tries to get a gift for his aunt's birthday."
            }
        ]

        shows = [
            {
                "id": "tmdb_tv_1",
                "title": "Ted Lasso",
                "type": "tv",
                "platform": "tmdb",
                "poster_url": "https://image.tmdb.org/t/p/w500/5fhZdwP1DVJ0FyVH6vrFdHwpXIn.jpg",
                "rating": 8.8,
                "release_year": 2020,
                "duration_minutes": 30,
                "genres": ["Comedy", "Drama"],
                "description": "An American football coach moves to England to manage a soccer team."
            },
            {
                "id": "tmdb_tv_2",
                "title": "Our Planet",
                "type": "tv",
                "platform": "tmdb",
                "poster_url": "https://image.tmdb.org/t/p/w500/gk5TCN4R9FXH6BcAJfXIWdDTdMT.jpg",
                "rating": 9.3,
                "release_year": 2019,
                "duration_minutes": 50,
                "genres": ["Documentary", "Nature"],
                "description": "David Attenborough explores the wonders of our planet."
            }
        ]

        results = []
        if content_type in ["all", "movie"]:
            results.extend(movies)
        if content_type in ["all", "tv"]:
            results.extend(shows)

        # Filter by query
        query_lower = query.lower()
        results = [r for r in results if query_lower in r["title"].lower() or
                   any(query_lower in g.lower() for g in r.get("genres", []))]

        return results if results else movies[:2] + shows[:1]

    def _mock_spotify_results(self, query: str, content_type: str) -> List[Dict]:
        """Mock Spotify results."""
        tracks = [
            {
                "id": "spotify_1",
                "title": "Lofi Hip Hop Radio",
                "type": "music",
                "platform": "spotify",
                "artist": "ChilledCow",
                "album": "Lofi Beats",
                "duration_minutes": 60,
                "genres": ["Lo-fi", "Chill"],
                "preview_url": None
            },
            {
                "id": "spotify_2",
                "title": "Weightless",
                "type": "music",
                "platform": "spotify",
                "artist": "Marconi Union",
                "album": "Ambient Collection",
                "duration_minutes": 8,
                "genres": ["Ambient", "Relaxation"],
                "description": "Scientifically proven to reduce anxiety"
            }
        ]

        podcasts = [
            {
                "id": "spotify_pod_1",
                "title": "ADHD Experts Podcast",
                "type": "podcast",
                "platform": "spotify",
                "host": "ADDitude Magazine",
                "duration_minutes": 45,
                "genres": ["Health", "Education"],
                "description": "Expert insights on living with ADHD"
            }
        ]

        results = []
        if content_type in ["all", "music"]:
            results.extend(tracks)
        if content_type in ["all", "podcast"]:
            results.extend(podcasts)

        return results

    def _mock_youtube_results(self, query: str) -> List[Dict]:
        """Mock YouTube results."""
        return [
            {
                "id": "yt_1",
                "title": "Relaxing Nature Sounds - 8 Hours",
                "type": "video",
                "platform": "youtube",
                "channel": "Relaxing Sounds",
                "duration_minutes": 480,
                "views": 10000000,
                "thumbnail_url": None
            },
            {
                "id": "yt_2",
                "title": "Study With Me - 2 Hour Pomodoro",
                "type": "video",
                "platform": "youtube",
                "channel": "Study Vibes",
                "duration_minutes": 120,
                "views": 5000000,
                "thumbnail_url": None
            }
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK SEARCH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def quick_search(query: str, limit: int = 5) -> List[Dict]:
    """Quick search across all platforms."""
    aggregator = SearchAggregator()
    return await aggregator.search_all(query, limit=limit)


async def mood_based_search(mood: str, content_type: str = "all", limit: int = 5) -> List[Dict]:
    """Search based on mood."""
    aggregator = SearchAggregator()

    # Convert mood to search query
    mood_queries = {
        "stressed": "relaxing calming nature",
        "bored": "exciting action adventure",
        "sad": "feel good comedy uplifting",
        "anxious": "calming meditation peaceful",
        "happy": "fun adventure comedy",
        "tired": "peaceful ambient relaxing",
        "energetic": "upbeat exciting action"
    }

    query = mood_queries.get(mood, "popular trending")
    return await aggregator.search_all(query, content_type=content_type, mood=mood, limit=limit)
