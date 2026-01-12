import streamlit as st
import requests

# CONSTANTS
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_URL = "https://image.tmdb.org/t/p/w500"

def get_api_key():
    """Retrives API key safely from Streamlit secrets."""
    return st.secrets["tmdb"]["api_key"]

@st.cache_data(ttl=3600)  # Cache results for 1 hour to save API calls
def search_global(query):
    """
    Searches for Movies and TV Shows.
    Returns a clean list of dictionaries with title, poster, and id.
    """
    if not query:
        return []

    url = f"{BASE_URL}/search/multi"
    params = {
        "api_key": get_api_key(),
        "query": query,
        "include_adult": False,
        "language": "en-US"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        # Filter and clean data immediately
        clean_results = []
        for item in results:
            # We only want Movies and TV, not 'people'
            if item.get("media_type") in ["movie", "tv"]:
                clean_results.append({
                    "id": item.get("id"),
                    "type": item.get("media_type"),
                    "title": item.get("title") or item.get("name"),
                    "overview": item.get("overview"),
                    # Handle missing posters gracefully
                    "poster": f"{IMAGE_URL}{item.get('poster_path')}" if item.get('poster_path') else None,
                    "release_date": item.get("release_date") or item.get("first_air_date") or "Unknown"
                })
        return clean_results
    except Exception as e:
        # Fail silently in UI, log to console
        print(f"TMDB Search Error: {e}")
        return []

@st.cache_data(ttl=86400)  # Cache for 24 hours (streaming rights rarely change)
def get_streaming_providers(tmdb_id, media_type="movie"):
    """
    Finds where a specific title is streaming in the US.
    """
    url = f"{BASE_URL}/{media_type}/{tmdb_id}/watch/providers"
    params = {"api_key": get_api_key()}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # Default to US providers
        us_providers = data.get("results", {}).get("US", {})
        
        # Extract flatrate (subscription) providers like Netflix/Disney+
        flatrate = us_providers.get("flatrate", [])
        
        # Return just the names for the UI
        provider_names = [p["provider_name"] for p in flatrate]
        return provider_names
    except Exception as e:
        print(f"Provider Error: {e}")
        return []