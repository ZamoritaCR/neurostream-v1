import streamlit as st
import requests

# CONSTANTS
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

def get_api_key():
    return st.secrets["tmdb"]["api_key"]

def _clean_results(results):
    """Helper to format TMDB data consistently."""
    clean = []
    for item in results:
        if item.get("media_type", "movie") in ["movie", "tv"]:
            clean.append({
                "id": item.get("id"),
                "type": item.get("media_type", "movie"),
                "title": item.get("title") or item.get("name"),
                "overview": item.get("overview", ""),
                "poster": f"{IMAGE_URL}{item.get('poster_path')}" if item.get('poster_path') else None,
                "release_date": item.get("release_date") or item.get("first_air_date") or "Unknown"
            })
    return clean

@st.cache_data(ttl=3600)
def search_global(query):
    if not query: return []
    url = f"{BASE_URL}/search/multi"
    params = {"api_key": get_api_key(), "query": query, "include_adult": "false", "language": "en-US"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except Exception:
        return []

@st.cache_data(ttl=1800)
def get_popular_movies():
    """THE AGGREGATOR: Fetches trending content for the lobby."""
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": get_api_key(),
        "include_adult": "false",
        "sort_by": "popularity.desc",
        "watch_region": "US",
        "with_watch_monetization_types": "flatrate|rent"
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except Exception:
        return []

@st.cache_data(ttl=86400)
def get_streaming_providers(tmdb_id, media_type="movie"):
    """Returns detailed provider info (name + logo) for buttons."""
    url = f"{BASE_URL}/{media_type}/{tmdb_id}/watch/providers"
    params = {"api_key": get_api_key()}
    try:
        r = requests.get(url, params=params)
        data = r.json().get("results", {}).get("US", {})
        return {
            "flatrate": data.get("flatrate", []),
            "rent": data.get("rent", [])
        }
    except Exception:
        return {"flatrate": [], "rent": []}