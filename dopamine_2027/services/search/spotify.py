"""
═══════════════════════════════════════════════════════════════════════════════
SPOTIFY SERVICE
Music, podcast, and playlist search via Spotify Web API.
═══════════════════════════════════════════════════════════════════════════════
"""

import aiohttp
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

from config.settings import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_ENABLED
)

logger = logging.getLogger(__name__)


@dataclass
class SpotifyToken:
    """Spotify API access token."""
    access_token: str
    expires_at: datetime


class SpotifyService:
    """
    Service for searching music, podcasts, and playlists via Spotify API.

    Uses client credentials flow for server-side access.
    """

    BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self):
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self.enabled = SPOTIFY_ENABLED and self.client_id and self.client_secret
        self._token: Optional[SpotifyToken] = None

    async def _get_token(self) -> Optional[str]:
        """Get or refresh the access token."""
        if not self.enabled:
            return None

        # Check if current token is still valid
        if self._token and datetime.utcnow() < self._token.expires_at:
            return self._token.access_token

        # Get new token
        try:
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.AUTH_URL,
                    headers={
                        "Authorization": f"Basic {credentials}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    data={"grant_type": "client_credentials"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        expires_in = data.get("expires_in", 3600)
                        self._token = SpotifyToken(
                            access_token=data["access_token"],
                            expires_at=datetime.utcnow() + timedelta(seconds=expires_in - 60)
                        )
                        return self._token.access_token
                    else:
                        logger.error(f"Spotify auth failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Spotify token error: {e}")
            return None

    async def _api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make an authenticated API request."""
        token = await self._get_token()
        if not token:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/{endpoint}",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Rate limited
                        retry_after = response.headers.get("Retry-After", 1)
                        logger.warning(f"Spotify rate limited, retry after {retry_after}s")
                        return None
                    else:
                        logger.error(f"Spotify API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Spotify request error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════════════════
    # SEARCH METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for music tracks."""
        if not self.enabled:
            return []

        data = await self._api_request("search", {
            "q": query,
            "type": "track",
            "limit": limit,
            "market": "US"
        })

        if not data:
            return []

        tracks = data.get("tracks", {}).get("items", [])
        return [self._transform_track(t) for t in tracks]

    async def search_albums(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for albums."""
        if not self.enabled:
            return []

        data = await self._api_request("search", {
            "q": query,
            "type": "album",
            "limit": limit,
            "market": "US"
        })

        if not data:
            return []

        albums = data.get("albums", {}).get("items", [])
        return [self._transform_album(a) for a in albums]

    async def search_playlists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for playlists."""
        if not self.enabled:
            return []

        data = await self._api_request("search", {
            "q": query,
            "type": "playlist",
            "limit": limit
        })

        if not data:
            return []

        playlists = data.get("playlists", {}).get("items", [])
        return [self._transform_playlist(p) for p in playlists if p]

    async def search_podcasts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for podcasts/shows."""
        if not self.enabled:
            return []

        data = await self._api_request("search", {
            "q": query,
            "type": "show",
            "limit": limit,
            "market": "US"
        })

        if not data:
            return []

        shows = data.get("shows", {}).get("items", [])
        return [self._transform_podcast(s) for s in shows if s]

    async def search_episodes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for podcast episodes."""
        if not self.enabled:
            return []

        data = await self._api_request("search", {
            "q": query,
            "type": "episode",
            "limit": limit,
            "market": "US"
        })

        if not data:
            return []

        episodes = data.get("episodes", {}).get("items", [])
        return [self._transform_episode(e) for e in episodes if e]

    async def search_all(self, query: str, limit: int = 5) -> Dict[str, List[Dict]]:
        """Search all content types at once."""
        if not self.enabled:
            return {"tracks": [], "albums": [], "playlists": [], "podcasts": []}

        data = await self._api_request("search", {
            "q": query,
            "type": "track,album,playlist,show",
            "limit": limit,
            "market": "US"
        })

        if not data:
            return {"tracks": [], "albums": [], "playlists": [], "podcasts": []}

        return {
            "tracks": [self._transform_track(t) for t in data.get("tracks", {}).get("items", [])],
            "albums": [self._transform_album(a) for a in data.get("albums", {}).get("items", [])],
            "playlists": [self._transform_playlist(p) for p in data.get("playlists", {}).get("items", []) if p],
            "podcasts": [self._transform_podcast(s) for s in data.get("shows", {}).get("items", []) if s]
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # DETAIL METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_track(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed track information."""
        data = await self._api_request(f"tracks/{track_id}")
        return self._transform_track(data) if data else None

    async def get_album(self, album_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed album information with tracks."""
        data = await self._api_request(f"albums/{album_id}")
        if not data:
            return None

        album = self._transform_album(data)
        album["tracks"] = [
            self._transform_track(t)
            for t in data.get("tracks", {}).get("items", [])
        ]
        return album

    async def get_playlist(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed playlist information with tracks."""
        data = await self._api_request(f"playlists/{playlist_id}")
        if not data:
            return None

        playlist = self._transform_playlist(data)
        playlist["tracks"] = [
            self._transform_track(item.get("track"))
            for item in data.get("tracks", {}).get("items", [])
            if item.get("track")
        ]
        return playlist

    async def get_podcast(self, show_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed podcast/show information."""
        data = await self._api_request(f"shows/{show_id}", {"market": "US"})
        if not data:
            return None

        podcast = self._transform_podcast(data)
        podcast["episodes"] = [
            self._transform_episode(e)
            for e in data.get("episodes", {}).get("items", [])
            if e
        ]
        return podcast

    # ═══════════════════════════════════════════════════════════════════════════
    # DISCOVERY METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_featured_playlists(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Spotify's featured playlists."""
        data = await self._api_request("browse/featured-playlists", {
            "limit": limit,
            "country": "US"
        })

        if not data:
            return []

        playlists = data.get("playlists", {}).get("items", [])
        return [self._transform_playlist(p) for p in playlists if p]

    async def get_new_releases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get new album releases."""
        data = await self._api_request("browse/new-releases", {
            "limit": limit,
            "country": "US"
        })

        if not data:
            return []

        albums = data.get("albums", {}).get("items", [])
        return [self._transform_album(a) for a in albums]

    async def get_recommendations(
        self,
        seed_tracks: List[str] = None,
        seed_artists: List[str] = None,
        seed_genres: List[str] = None,
        limit: int = 10,
        **audio_features
    ) -> List[Dict[str, Any]]:
        """
        Get track recommendations based on seeds.

        Audio features can include:
        - target_energy (0-1)
        - target_valence (0-1, happiness)
        - target_danceability (0-1)
        - target_tempo (BPM)
        """
        if not self.enabled:
            return []

        params = {"limit": limit, "market": "US"}

        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:5])

        # Add audio feature targets
        for key, value in audio_features.items():
            if key.startswith("target_") or key.startswith("min_") or key.startswith("max_"):
                params[key] = value

        data = await self._api_request("recommendations", params)

        if not data:
            return []

        tracks = data.get("tracks", [])
        return [self._transform_track(t) for t in tracks]

    async def get_mood_playlist(self, mood: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get playlists matching a mood."""
        # Map moods to search queries
        mood_queries = {
            "happy": "happy upbeat feel good",
            "sad": "sad melancholy emotional",
            "energetic": "energy workout pump up",
            "calm": "calm relaxing chill peaceful",
            "focused": "focus concentration study",
            "romantic": "romantic love songs",
            "angry": "angry intense aggressive",
            "nostalgic": "throwback nostalgia classics"
        }

        query = mood_queries.get(mood.lower(), mood)
        return await self.search_playlists(query, limit)

    # ═══════════════════════════════════════════════════════════════════════════
    # TRANSFORMATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _transform_track(self, data: Dict) -> Dict[str, Any]:
        """Transform Spotify track to unified format."""
        if not data:
            return {}

        artists = data.get("artists", [])
        album = data.get("album", {})
        images = album.get("images", [])

        return {
            "id": f"spotify_track_{data.get('id')}",
            "spotify_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "type": "track",
            "platform": "spotify",
            "artists": [a.get("name") for a in artists],
            "artist_ids": [a.get("id") for a in artists],
            "album": album.get("name"),
            "album_id": album.get("id"),
            "poster_url": images[0].get("url") if images else None,
            "duration_ms": data.get("duration_ms"),
            "duration_minutes": round(data.get("duration_ms", 0) / 60000, 1),
            "explicit": data.get("explicit", False),
            "popularity": data.get("popularity", 0),
            "preview_url": data.get("preview_url"),
            "external_url": data.get("external_urls", {}).get("spotify"),
            "release_date": album.get("release_date")
        }

    def _transform_album(self, data: Dict) -> Dict[str, Any]:
        """Transform Spotify album to unified format."""
        if not data:
            return {}

        artists = data.get("artists", [])
        images = data.get("images", [])

        return {
            "id": f"spotify_album_{data.get('id')}",
            "spotify_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "type": "album",
            "platform": "spotify",
            "artists": [a.get("name") for a in artists],
            "poster_url": images[0].get("url") if images else None,
            "total_tracks": data.get("total_tracks"),
            "release_date": data.get("release_date"),
            "album_type": data.get("album_type"),  # album, single, compilation
            "external_url": data.get("external_urls", {}).get("spotify")
        }

    def _transform_playlist(self, data: Dict) -> Dict[str, Any]:
        """Transform Spotify playlist to unified format."""
        if not data:
            return {}

        images = data.get("images", [])
        owner = data.get("owner", {})

        return {
            "id": f"spotify_playlist_{data.get('id')}",
            "spotify_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "type": "playlist",
            "platform": "spotify",
            "description": data.get("description", ""),
            "poster_url": images[0].get("url") if images else None,
            "owner": owner.get("display_name"),
            "owner_id": owner.get("id"),
            "track_count": data.get("tracks", {}).get("total", 0),
            "public": data.get("public", True),
            "collaborative": data.get("collaborative", False),
            "external_url": data.get("external_urls", {}).get("spotify")
        }

    def _transform_podcast(self, data: Dict) -> Dict[str, Any]:
        """Transform Spotify podcast/show to unified format."""
        if not data:
            return {}

        images = data.get("images", [])

        return {
            "id": f"spotify_podcast_{data.get('id')}",
            "spotify_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "type": "podcast",
            "platform": "spotify",
            "publisher": data.get("publisher"),
            "description": data.get("description", ""),
            "poster_url": images[0].get("url") if images else None,
            "total_episodes": data.get("total_episodes"),
            "explicit": data.get("explicit", False),
            "languages": data.get("languages", []),
            "external_url": data.get("external_urls", {}).get("spotify")
        }

    def _transform_episode(self, data: Dict) -> Dict[str, Any]:
        """Transform Spotify podcast episode to unified format."""
        if not data:
            return {}

        images = data.get("images", [])

        return {
            "id": f"spotify_episode_{data.get('id')}",
            "spotify_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "type": "episode",
            "platform": "spotify",
            "description": data.get("description", ""),
            "poster_url": images[0].get("url") if images else None,
            "duration_ms": data.get("duration_ms"),
            "duration_minutes": round(data.get("duration_ms", 0) / 60000, 1),
            "explicit": data.get("explicit", False),
            "release_date": data.get("release_date"),
            "external_url": data.get("external_urls", {}).get("spotify")
        }


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def search_music(query: str, limit: int = 10) -> List[Dict]:
    """Quick music track search."""
    service = SpotifyService()
    return await service.search_tracks(query, limit)


async def search_podcasts(query: str, limit: int = 10) -> List[Dict]:
    """Quick podcast search."""
    service = SpotifyService()
    return await service.search_podcasts(query, limit)


async def get_mood_music(mood: str, limit: int = 10) -> List[Dict]:
    """Get music for a specific mood."""
    service = SpotifyService()
    return await service.get_mood_playlist(mood, limit)


async def get_recommendations_for_adhd(energy_level: str = "medium") -> List[Dict]:
    """
    Get music recommendations optimized for ADHD focus.

    Energy levels:
    - "low": Calm, ambient music for relaxation
    - "medium": Balanced music for steady focus
    - "high": Upbeat music for motivation
    """
    service = SpotifyService()

    energy_settings = {
        "low": {"target_energy": 0.3, "target_valence": 0.4, "min_instrumentalness": 0.5},
        "medium": {"target_energy": 0.5, "target_valence": 0.5, "target_tempo": 100},
        "high": {"target_energy": 0.8, "target_valence": 0.7, "target_tempo": 130}
    }

    settings = energy_settings.get(energy_level, energy_settings["medium"])

    # Use focus/study genre as seed
    return await service.get_recommendations(
        seed_genres=["study", "chill", "ambient"],
        limit=20,
        **settings
    )
