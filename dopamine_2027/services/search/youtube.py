"""
═══════════════════════════════════════════════════════════════════════════════
YOUTUBE SERVICE
Video search and discovery via YouTube Data API.
═══════════════════════════════════════════════════════════════════════════════
"""

import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import logging

from config.settings import YOUTUBE_API_KEY, YOUTUBE_ENABLED

logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service for searching and discovering videos via YouTube Data API.

    Features:
    - Video search with filters
    - Channel information
    - Playlist retrieval
    - Duration parsing
    - ADHD-friendly metadata
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.enabled = YOUTUBE_ENABLED and bool(self.api_key)

    async def _api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make an API request to YouTube."""
        if not self.enabled:
            return None

        params["key"] = self.api_key

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/{endpoint}",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 403:
                        logger.error("YouTube API quota exceeded or key invalid")
                        return None
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"YouTube request error: {e}")
            return None

    # ═══════════════════════════════════════════════════════════════════════════
    # SEARCH METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def search_videos(
        self,
        query: str,
        limit: int = 10,
        order: str = "relevance",
        duration: str = None,
        published_after: datetime = None,
        safe_search: str = "moderate"
    ) -> List[Dict[str, Any]]:
        """
        Search for videos.

        Args:
            query: Search query
            limit: Number of results (max 50)
            order: Sort order (relevance, date, rating, viewCount)
            duration: Filter by duration (short <4min, medium 4-20min, long >20min)
            published_after: Only videos published after this date
            safe_search: Content filter (none, moderate, strict)

        Returns:
            List of video dictionaries
        """
        if not self.enabled:
            return []

        params = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": min(limit, 50),
            "order": order,
            "safeSearch": safe_search
        }

        if duration:
            params["videoDuration"] = duration

        if published_after:
            params["publishedAfter"] = published_after.isoformat() + "Z"

        data = await self._api_request("search", params)

        if not data:
            return []

        # Get video IDs for additional details
        video_ids = [item["id"]["videoId"] for item in data.get("items", [])]

        if video_ids:
            # Fetch additional details (duration, view count, etc.)
            details = await self._get_video_details(video_ids)
            return [
                self._transform_video(item, details.get(item["id"]["videoId"], {}))
                for item in data.get("items", [])
            ]

        return [self._transform_video(item, {}) for item in data.get("items", [])]

    async def search_channels(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for YouTube channels."""
        if not self.enabled:
            return []

        params = {
            "part": "snippet",
            "type": "channel",
            "q": query,
            "maxResults": min(limit, 50)
        }

        data = await self._api_request("search", params)

        if not data:
            return []

        return [self._transform_channel(item) for item in data.get("items", [])]

    async def search_playlists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for YouTube playlists."""
        if not self.enabled:
            return []

        params = {
            "part": "snippet",
            "type": "playlist",
            "q": query,
            "maxResults": min(limit, 50)
        }

        data = await self._api_request("search", params)

        if not data:
            return []

        return [self._transform_playlist(item) for item in data.get("items", [])]

    async def _get_video_details(self, video_ids: List[str]) -> Dict[str, Dict]:
        """Get detailed information for multiple videos."""
        if not video_ids:
            return {}

        params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids)
        }

        data = await self._api_request("videos", params)

        if not data:
            return {}

        return {
            item["id"]: {
                "duration": item.get("contentDetails", {}).get("duration"),
                "view_count": item.get("statistics", {}).get("viewCount"),
                "like_count": item.get("statistics", {}).get("likeCount"),
                "comment_count": item.get("statistics", {}).get("commentCount")
            }
            for item in data.get("items", [])
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # DETAIL METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed video information."""
        if not self.enabled:
            return None

        params = {
            "part": "snippet,contentDetails,statistics",
            "id": video_id
        }

        data = await self._api_request("videos", params)

        if not data or not data.get("items"):
            return None

        item = data["items"][0]
        return self._transform_video_full(item)

    async def get_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed channel information."""
        if not self.enabled:
            return None

        params = {
            "part": "snippet,statistics,brandingSettings",
            "id": channel_id
        }

        data = await self._api_request("channels", params)

        if not data or not data.get("items"):
            return None

        return self._transform_channel_full(data["items"][0])

    async def get_playlist_videos(
        self,
        playlist_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get videos from a playlist."""
        if not self.enabled:
            return []

        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": min(limit, 50)
        }

        data = await self._api_request("playlistItems", params)

        if not data:
            return []

        videos = []
        for item in data.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                videos.append({
                    "id": f"youtube_{video_id}",
                    "youtube_id": video_id,
                    "title": item["snippet"].get("title", "Unknown"),
                    "description": item["snippet"].get("description", ""),
                    "thumbnail_url": self._get_best_thumbnail(item["snippet"].get("thumbnails", {})),
                    "channel_title": item["snippet"].get("channelTitle"),
                    "position": item["snippet"].get("position", 0),
                    "published_at": item["snippet"].get("publishedAt")
                })

        return videos

    # ═══════════════════════════════════════════════════════════════════════════
    # DISCOVERY METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_trending(
        self,
        category_id: str = None,
        region_code: str = "US",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get trending videos."""
        if not self.enabled:
            return []

        params = {
            "part": "snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": min(limit, 50)
        }

        if category_id:
            params["videoCategoryId"] = category_id

        data = await self._api_request("videos", params)

        if not data:
            return []

        return [self._transform_video_full(item) for item in data.get("items", [])]

    async def get_related_videos(self, video_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get videos related to a specific video."""
        # Note: Related videos endpoint was deprecated, using search instead
        video = await self.get_video(video_id)
        if not video:
            return []

        # Search for similar content using title keywords
        title_words = video.get("title", "").split()[:5]
        query = " ".join(title_words)

        return await self.search_videos(query, limit=limit)

    async def get_channel_videos(
        self,
        channel_id: str,
        limit: int = 10,
        order: str = "date"
    ) -> List[Dict[str, Any]]:
        """Get videos from a specific channel."""
        if not self.enabled:
            return []

        params = {
            "part": "snippet",
            "type": "video",
            "channelId": channel_id,
            "maxResults": min(limit, 50),
            "order": order
        }

        data = await self._api_request("search", params)

        if not data:
            return []

        video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
        details = await self._get_video_details(video_ids) if video_ids else {}

        return [
            self._transform_video(item, details.get(item["id"]["videoId"], {}))
            for item in data.get("items", [])
        ]

    # ═══════════════════════════════════════════════════════════════════════════
    # ADHD-FRIENDLY FEATURES
    # ═══════════════════════════════════════════════════════════════════════════

    async def search_by_duration(
        self,
        query: str,
        max_minutes: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for videos under a specific duration.
        Perfect for ADHD users who need time-limited content.
        """
        # Determine duration category
        if max_minutes <= 4:
            duration = "short"
        elif max_minutes <= 20:
            duration = "medium"
        else:
            duration = "long"

        videos = await self.search_videos(query, limit=limit * 2, duration=duration)

        # Further filter by exact duration
        filtered = [
            v for v in videos
            if v.get("duration_minutes", 999) <= max_minutes
        ]

        return filtered[:limit]

    async def get_quick_content(
        self,
        query: str,
        max_minutes: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get quick, digestible content for ADHD users.
        Prioritizes shorter, highly-rated videos.
        """
        videos = await self.search_by_duration(query, max_minutes, limit=20)

        # Sort by engagement (view count / duration ratio)
        def engagement_score(v):
            views = int(v.get("view_count", 0) or 0)
            duration = max(v.get("duration_minutes", 1), 0.1)
            return views / duration

        sorted_videos = sorted(videos, key=engagement_score, reverse=True)
        return sorted_videos[:10]

    # ═══════════════════════════════════════════════════════════════════════════
    # TRANSFORMATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════

    def _transform_video(self, data: Dict, details: Dict) -> Dict[str, Any]:
        """Transform YouTube search result to unified format."""
        snippet = data.get("snippet", {})
        video_id = data.get("id", {}).get("videoId")
        duration_iso = details.get("duration", "PT0S")

        return {
            "id": f"youtube_{video_id}",
            "youtube_id": video_id,
            "title": snippet.get("title", "Unknown"),
            "type": "video",
            "platform": "youtube",
            "description": snippet.get("description", ""),
            "thumbnail_url": self._get_best_thumbnail(snippet.get("thumbnails", {})),
            "channel_title": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "duration_iso": duration_iso,
            "duration_minutes": self._parse_duration(duration_iso),
            "view_count": details.get("view_count"),
            "like_count": details.get("like_count"),
            "external_url": f"https://www.youtube.com/watch?v={video_id}"
        }

    def _transform_video_full(self, data: Dict) -> Dict[str, Any]:
        """Transform full video data to unified format."""
        snippet = data.get("snippet", {})
        content_details = data.get("contentDetails", {})
        statistics = data.get("statistics", {})
        video_id = data.get("id")
        duration_iso = content_details.get("duration", "PT0S")

        return {
            "id": f"youtube_{video_id}",
            "youtube_id": video_id,
            "title": snippet.get("title", "Unknown"),
            "type": "video",
            "platform": "youtube",
            "description": snippet.get("description", ""),
            "thumbnail_url": self._get_best_thumbnail(snippet.get("thumbnails", {})),
            "channel_title": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "published_at": snippet.get("publishedAt"),
            "duration_iso": duration_iso,
            "duration_minutes": self._parse_duration(duration_iso),
            "view_count": statistics.get("viewCount"),
            "like_count": statistics.get("likeCount"),
            "comment_count": statistics.get("commentCount"),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId"),
            "definition": content_details.get("definition"),  # hd or sd
            "caption": content_details.get("caption"),  # true if has captions
            "external_url": f"https://www.youtube.com/watch?v={video_id}"
        }

    def _transform_channel(self, data: Dict) -> Dict[str, Any]:
        """Transform channel search result."""
        snippet = data.get("snippet", {})
        channel_id = data.get("id", {}).get("channelId")

        return {
            "id": f"youtube_channel_{channel_id}",
            "youtube_id": channel_id,
            "title": snippet.get("title", "Unknown"),
            "type": "channel",
            "platform": "youtube",
            "description": snippet.get("description", ""),
            "thumbnail_url": self._get_best_thumbnail(snippet.get("thumbnails", {})),
            "external_url": f"https://www.youtube.com/channel/{channel_id}"
        }

    def _transform_channel_full(self, data: Dict) -> Dict[str, Any]:
        """Transform full channel data."""
        snippet = data.get("snippet", {})
        statistics = data.get("statistics", {})
        branding = data.get("brandingSettings", {}).get("channel", {})
        channel_id = data.get("id")

        return {
            "id": f"youtube_channel_{channel_id}",
            "youtube_id": channel_id,
            "title": snippet.get("title", "Unknown"),
            "type": "channel",
            "platform": "youtube",
            "description": snippet.get("description", ""),
            "thumbnail_url": self._get_best_thumbnail(snippet.get("thumbnails", {})),
            "subscriber_count": statistics.get("subscriberCount"),
            "video_count": statistics.get("videoCount"),
            "view_count": statistics.get("viewCount"),
            "keywords": branding.get("keywords", ""),
            "banner_url": data.get("brandingSettings", {}).get("image", {}).get("bannerExternalUrl"),
            "external_url": f"https://www.youtube.com/channel/{channel_id}"
        }

    def _transform_playlist(self, data: Dict) -> Dict[str, Any]:
        """Transform playlist search result."""
        snippet = data.get("snippet", {})
        playlist_id = data.get("id", {}).get("playlistId")

        return {
            "id": f"youtube_playlist_{playlist_id}",
            "youtube_id": playlist_id,
            "title": snippet.get("title", "Unknown"),
            "type": "playlist",
            "platform": "youtube",
            "description": snippet.get("description", ""),
            "thumbnail_url": self._get_best_thumbnail(snippet.get("thumbnails", {})),
            "channel_title": snippet.get("channelTitle"),
            "channel_id": snippet.get("channelId"),
            "external_url": f"https://www.youtube.com/playlist?list={playlist_id}"
        }

    def _get_best_thumbnail(self, thumbnails: Dict) -> Optional[str]:
        """Get the best quality thumbnail available."""
        for quality in ["maxres", "high", "medium", "default"]:
            if quality in thumbnails:
                return thumbnails[quality].get("url")
        return None

    def _parse_duration(self, iso_duration: str) -> float:
        """Parse ISO 8601 duration to minutes."""
        if not iso_duration:
            return 0

        # Parse PT#H#M#S format
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, iso_duration)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return round(hours * 60 + minutes + seconds / 60, 1)


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def search_videos(query: str, limit: int = 10) -> List[Dict]:
    """Quick video search."""
    service = YouTubeService()
    return await service.search_videos(query, limit)


async def get_trending_videos(limit: int = 10) -> List[Dict]:
    """Get trending videos."""
    service = YouTubeService()
    return await service.get_trending(limit=limit)


async def get_quick_videos(query: str, max_minutes: int = 10) -> List[Dict]:
    """Get quick, ADHD-friendly videos under specified duration."""
    service = YouTubeService()
    return await service.get_quick_content(query, max_minutes)
