"""
═══════════════════════════════════════════════════════════════════════════════
TMDB SERVICE
Movie and TV show search via The Movie Database API.
═══════════════════════════════════════════════════════════════════════════════
"""

import aiohttp
from typing import List, Dict, Any, Optional
from config.settings import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE, TMDB_ENABLED


class TMDBService:
    """Service for searching movies and TV shows via TMDB API."""

    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.image_base = TMDB_IMAGE_BASE
        self.enabled = TMDB_ENABLED

    async def search_movies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for movies."""
        if not self.enabled:
            return []

        url = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": query,
            "include_adult": False,
            "language": "en-US",
            "page": 1
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [self._transform_movie(m) for m in data.get("results", [])[:limit]]
                    return []
        except Exception as e:
            print(f"TMDB movie search error: {e}")
            return []

    async def search_tv(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for TV shows."""
        if not self.enabled:
            return []

        url = f"{self.base_url}/search/tv"
        params = {
            "api_key": self.api_key,
            "query": query,
            "include_adult": False,
            "language": "en-US",
            "page": 1
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [self._transform_tv(t) for t in data.get("results", [])[:limit]]
                    return []
        except Exception as e:
            print(f"TMDB TV search error: {e}")
            return []

    async def get_movie_details(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed movie information."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "append_to_response": "watch/providers,credits"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._transform_movie_details(data)
                    return None
        except Exception as e:
            print(f"TMDB movie details error: {e}")
            return None

    async def get_trending(self, media_type: str = "all", time_window: str = "week", limit: int = 10) -> List[Dict]:
        """Get trending content."""
        if not self.enabled:
            return []

        url = f"{self.base_url}/trending/{media_type}/{time_window}"
        params = {"api_key": self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        for item in data.get("results", [])[:limit]:
                            if item.get("media_type") == "movie":
                                results.append(self._transform_movie(item))
                            else:
                                results.append(self._transform_tv(item))
                        return results
                    return []
        except Exception as e:
            print(f"TMDB trending error: {e}")
            return []

    async def get_recommendations(self, movie_id: int, limit: int = 10) -> List[Dict]:
        """Get movie recommendations based on a movie."""
        if not self.enabled:
            return []

        url = f"{self.base_url}/movie/{movie_id}/recommendations"
        params = {"api_key": self.api_key}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [self._transform_movie(m) for m in data.get("results", [])[:limit]]
                    return []
        except Exception as e:
            print(f"TMDB recommendations error: {e}")
            return []

    def _transform_movie(self, data: Dict) -> Dict[str, Any]:
        """Transform TMDB movie response to unified format."""
        return {
            "id": f"tmdb_movie_{data.get('id')}",
            "tmdb_id": data.get("id"),
            "title": data.get("title", "Unknown"),
            "type": "movie",
            "platform": "tmdb",
            "poster_url": f"{self.image_base}/w500{data.get('poster_path')}" if data.get("poster_path") else None,
            "backdrop_url": f"{self.image_base}/w1280{data.get('backdrop_path')}" if data.get("backdrop_path") else None,
            "rating": round(data.get("vote_average", 0), 1),
            "vote_count": data.get("vote_count", 0),
            "release_year": int(data.get("release_date", "2000")[:4]) if data.get("release_date") else None,
            "description": data.get("overview", ""),
            "genres": [],  # Would need separate call to get genre names
            "duration_minutes": None,  # Not in search results
            "popularity": data.get("popularity", 0)
        }

    def _transform_tv(self, data: Dict) -> Dict[str, Any]:
        """Transform TMDB TV response to unified format."""
        return {
            "id": f"tmdb_tv_{data.get('id')}",
            "tmdb_id": data.get("id"),
            "title": data.get("name", "Unknown"),
            "type": "tv",
            "platform": "tmdb",
            "poster_url": f"{self.image_base}/w500{data.get('poster_path')}" if data.get("poster_path") else None,
            "backdrop_url": f"{self.image_base}/w1280{data.get('backdrop_path')}" if data.get("backdrop_path") else None,
            "rating": round(data.get("vote_average", 0), 1),
            "vote_count": data.get("vote_count", 0),
            "release_year": int(data.get("first_air_date", "2000")[:4]) if data.get("first_air_date") else None,
            "description": data.get("overview", ""),
            "genres": [],
            "duration_minutes": 45,  # Typical episode length
            "popularity": data.get("popularity", 0)
        }

    def _transform_movie_details(self, data: Dict) -> Dict[str, Any]:
        """Transform detailed movie response."""
        genres = [g.get("name") for g in data.get("genres", [])]

        # Get streaming providers (US)
        watch_providers = data.get("watch/providers", {}).get("results", {}).get("US", {})
        streaming = [p.get("provider_name") for p in watch_providers.get("flatrate", [])]

        return {
            "id": f"tmdb_movie_{data.get('id')}",
            "tmdb_id": data.get("id"),
            "title": data.get("title", "Unknown"),
            "type": "movie",
            "platform": "tmdb",
            "poster_url": f"{self.image_base}/w500{data.get('poster_path')}" if data.get("poster_path") else None,
            "backdrop_url": f"{self.image_base}/w1280{data.get('backdrop_path')}" if data.get("backdrop_path") else None,
            "rating": round(data.get("vote_average", 0), 1),
            "vote_count": data.get("vote_count", 0),
            "release_year": int(data.get("release_date", "2000")[:4]) if data.get("release_date") else None,
            "description": data.get("overview", ""),
            "genres": genres,
            "duration_minutes": data.get("runtime"),
            "tagline": data.get("tagline"),
            "budget": data.get("budget"),
            "revenue": data.get("revenue"),
            "streaming_on": streaming,
            "imdb_id": data.get("imdb_id")
        }


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK ACCESS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def search_movies(query: str, limit: int = 10) -> List[Dict]:
    """Quick movie search."""
    service = TMDBService()
    return await service.search_movies(query, limit)


async def search_tv(query: str, limit: int = 10) -> List[Dict]:
    """Quick TV search."""
    service = TMDBService()
    return await service.search_tv(query, limit)


async def get_trending(limit: int = 10) -> List[Dict]:
    """Get trending content."""
    service = TMDBService()
    return await service.get_trending(limit=limit)


# ═══════════════════════════════════════════════════════════════════════════════
# STREAMING DEEP LINKS
# ═══════════════════════════════════════════════════════════════════════════════

# Deep link URL templates for streaming services
STREAMING_DEEP_LINKS = {
    "Netflix": {
        "web": "https://www.netflix.com/title/{id}",
        "app": "nflx://www.netflix.com/title/{id}",
        "search": "https://www.netflix.com/search?q={title}"
    },
    "Disney Plus": {
        "web": "https://www.disneyplus.com/movies/{slug}/{id}",
        "app": "disneyplus://movies/{id}",
        "search": "https://www.disneyplus.com/search?q={title}"
    },
    "Amazon Prime Video": {
        "web": "https://www.amazon.com/gp/video/detail/{id}",
        "app": "aiv://aiv/resume?gti={id}",
        "search": "https://www.amazon.com/s?k={title}&i=instant-video"
    },
    "Hulu": {
        "web": "https://www.hulu.com/movie/{slug}",
        "app": "hulu://movie/{id}",
        "search": "https://www.hulu.com/search?q={title}"
    },
    "Max": {
        "web": "https://play.max.com/movie/{id}",
        "app": "hbomax://movie/{id}",
        "search": "https://play.max.com/search?q={title}"
    },
    "HBO Max": {
        "web": "https://play.max.com/movie/{id}",
        "app": "hbomax://movie/{id}",
        "search": "https://play.max.com/search?q={title}"
    },
    "Peacock": {
        "web": "https://www.peacocktv.com/watch/asset/movies/{slug}/{id}",
        "app": "peacocktv://movie/{id}",
        "search": "https://www.peacocktv.com/search?q={title}"
    },
    "Paramount Plus": {
        "web": "https://www.paramountplus.com/movies/{slug}/",
        "app": "paramountplus://movie/{id}",
        "search": "https://www.paramountplus.com/search/?q={title}"
    },
    "Apple TV Plus": {
        "web": "https://tv.apple.com/movie/{slug}/{id}",
        "app": "videos://movie/{id}",
        "search": "https://tv.apple.com/search?term={title}"
    },
    "YouTube": {
        "web": "https://www.youtube.com/results?search_query={title}+full+movie",
        "app": "youtube://results?search_query={title}",
        "search": "https://www.youtube.com/results?search_query={title}"
    },
    "Tubi": {
        "web": "https://tubitv.com/movies/{id}/{slug}",
        "app": "tubi://movies/{id}",
        "search": "https://tubitv.com/search/{title}"
    },
    "Crunchyroll": {
        "web": "https://www.crunchyroll.com/watch/{id}",
        "app": "crunchyroll://watch/{id}",
        "search": "https://www.crunchyroll.com/search?q={title}"
    }
}


def get_streaming_deep_link(
    provider_name: str,
    title: str,
    content_id: str = None,
    slug: str = None,
    link_type: str = "search"
) -> Optional[str]:
    """
    Get deep link URL for a streaming service.

    Args:
        provider_name: Name of the streaming provider
        title: Content title (for search links)
        content_id: Provider-specific content ID
        slug: URL-friendly content slug
        link_type: "web", "app", or "search"

    Returns:
        Deep link URL or None if provider not supported
    """
    import urllib.parse

    provider = STREAMING_DEEP_LINKS.get(provider_name)
    if not provider:
        # Try to find by partial match
        for name, links in STREAMING_DEEP_LINKS.items():
            if name.lower() in provider_name.lower() or provider_name.lower() in name.lower():
                provider = links
                break

    if not provider:
        return None

    # Prefer search if no ID available
    if not content_id and link_type != "search":
        link_type = "search"

    url_template = provider.get(link_type, provider.get("search"))
    if not url_template:
        return None

    # Create URL-safe versions
    safe_title = urllib.parse.quote_plus(title)
    safe_slug = slug or title.lower().replace(" ", "-").replace(":", "")

    try:
        return url_template.format(
            id=content_id or "",
            title=safe_title,
            slug=safe_slug
        )
    except Exception:
        return url_template.format(title=safe_title)


async def get_movie_watch_links(movie_id: int) -> Dict[str, Any]:
    """
    Get watch links for a movie across streaming services.

    Returns dictionary with available providers and their deep links.
    """
    service = TMDBService()
    details = await service.get_movie_details(movie_id)

    if not details:
        return {"providers": [], "links": []}

    title = details.get("title", "")
    streaming_providers = details.get("streaming_on", [])

    links = []
    for provider in streaming_providers:
        deep_link = get_streaming_deep_link(
            provider_name=provider,
            title=title,
            link_type="search"  # Use search since we don't have provider-specific IDs
        )

        if deep_link:
            links.append({
                "provider": provider,
                "web_url": deep_link,
                "app_url": get_streaming_deep_link(provider, title, link_type="app")
            })

    # Always add YouTube as fallback for trailers
    links.append({
        "provider": "YouTube",
        "web_url": f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(title)}+trailer",
        "type": "trailer"
    })

    return {
        "movie_id": movie_id,
        "title": title,
        "providers": streaming_providers,
        "links": links,
        "total_providers": len(streaming_providers)
    }


import urllib.parse
