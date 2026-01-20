# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v32.0 - FULL EXPERIENCE 🚀
# Landing Page + Auth + All Tabs Functional
# --------------------------------------------------
# FEATURES:
# ✅ Stunning landing page with auth
# ✅ Login / Sign Up / Guest mode
# ✅ Movies tab (emotion-driven TMDB)
# ✅ Music tab (Spotify integration)
# ✅ Podcasts tab (curated + search)
# ✅ Audiobooks tab (multi-provider)
# ✅ Shorts tab (YouTube)
# ✅ Gamification (DP, streaks, levels)
# ✅ Mr.DP NLP search
# ✅ Premium tier ready
# --------------------------------------------------

import streamlit as st
import os
import requests
import json
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from openai import OpenAI
import html as html_lib
import random
from datetime import datetime, timedelta
import hashlib
import re

# --------------------------------------------------
# 1. CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Dopamine.watch | Feel Better, Watch Better",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

APP_NAME = "Dopamine.watch"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_URL = "https://image.tmdb.org/t/p/original"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"

# --------------------------------------------------
# 2. SERVICE MAPS
# --------------------------------------------------
MOVIE_SERVICES = {
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Amazon Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Disney Plus": "https://www.disneyplus.com/search?q={title}",
    "Max": "https://play.max.com/search?q={title}",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "Peacock": "https://www.peacocktv.com/search?q={title}",
    "Paramount Plus": "https://www.paramountplus.com/search?q={title}",
    "Apple TV Plus": "https://tv.apple.com/search?term={title}",
    "Apple TV": "https://tv.apple.com/search?term={title}",
    "Tubi": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details/{title}",
    "Plex": "https://watch.plex.tv/search?q={title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",
    "MUBI": "https://mubi.com/search?query={title}",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Fandango At Home": "https://www.vudu.com/content/movies/search?searchString={title}",
}

MUSIC_SERVICES = {
    "Spotify": {"url": "https://open.spotify.com/search/{query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg", "color": "#1DB954"},
    "Apple Music": {"url": "https://music.apple.com/search?term={query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Apple_Music_icon.svg", "color": "#FA243C"},
    "YouTube Music": {"url": "https://music.youtube.com/search?q={query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Youtube_Music_icon.svg", "color": "#FF0000"},
    "Amazon Music": {"url": "https://music.amazon.com/search/{query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/7/79/Amazon_Music_logo.svg", "color": "#00A8E1"},
    "Tidal": {"url": "https://tidal.com/search?q={query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/e/e6/TIDAL_Logo.svg", "color": "#000000"},
    "SoundCloud": {"url": "https://soundcloud.com/search?q={query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Antu_soundcloud.svg", "color": "#FF5500"},
}

PODCAST_SERVICES = {
    "Spotify": {"url": "https://open.spotify.com/search/{query}/podcasts", "icon": "https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg", "color": "#1DB954"},
    "Apple Podcasts": {"url": "https://podcasts.apple.com/search?term={query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Apple_Podcasts_%28iOS%29.svg", "color": "#9933CC"},
    "YouTube": {"url": "https://www.youtube.com/results?search_query={query}+podcast", "icon": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg", "color": "#FF0000"},
    "Pocket Casts": {"url": "https://pocketcasts.com/search/{query}", "icon": "https://www.pocketcasts.com/assets/images/roundel.svg", "color": "#F43E37"},
    "Overcast": {"url": "https://overcast.fm/search?q={query}", "icon": "https://overcast.fm/img/logo.svg", "color": "#FC7E0F"},
}

AUDIOBOOK_SERVICES = {
    "Audible": {"url": "https://www.audible.com/search?keywords={query}", "icon": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Audible_logo.svg", "color": "#F8991D"},
    "Libro.fm": {"url": "https://libro.fm/search?q={query}", "icon": "https://libro.fm/images/libro-logo.svg", "color": "#00A651"},
    "Google Play Books": {"url": "https://play.google.com/store/search?q={query}&c=audiobooks", "icon": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Google_Play_Books_icon_%282016%29.svg", "color": "#4285F4"},
    "Kobo": {"url": "https://www.kobo.com/search?query={query}&fcsearchfield=Audiobook", "icon": "https://upload.wikimedia.org/wikipedia/commons/2/2e/Kobo_logo.svg", "color": "#BF0000"},
    "Chirp": {"url": "https://www.chirpbooks.com/search?query={query}", "icon": "https://www.chirpbooks.com/images/chirp-logo.svg", "color": "#FF6B6B"},
}

# --------------------------------------------------
# 3. API CLIENTS
# --------------------------------------------------
@st.cache_data
def get_tmdb_key():
    try:
        return st.secrets["tmdb"]["api_key"]
    except:
        return None

try:
    openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])
except:
    openai_client = None

# --------------------------------------------------
# 4. EMOTION MAPPINGS
# --------------------------------------------------
CURRENT_FEELINGS = ["Sad", "Lonely", "Anxious", "Overwhelmed", "Angry", "Stressed", "Bored", "Tired", "Numb", "Confused", "Restless", "Focused", "Calm", "Happy", "Excited", "Curious"]
DESIRED_FEELINGS = ["Comforted", "Calm", "Relaxed", "Focused", "Energized", "Stimulated", "Happy", "Entertained", "Inspired", "Grounded", "Curious", "Sleepy", "Connected"]

MOOD_EMOJIS = {
    "Sad": "🌧️", "Lonely": "🥺", "Anxious": "😰", "Overwhelmed": "😵‍💫",
    "Angry": "😡", "Stressed": "😫", "Bored": "😐", "Tired": "😴",
    "Numb": "🫥", "Confused": "🤔", "Restless": "😬", "Focused": "🎯",
    "Calm": "😌", "Happy": "😊", "Excited": "⚡", "Curious": "🧐",
    "Comforted": "🫶", "Relaxed": "🛋️", "Energized": "🔥", "Stimulated": "🚀",
    "Entertained": "🍿", "Inspired": "✨", "Grounded": "🌱", "Sleepy": "🌙", "Connected": "❤️"
}

FEELING_TO_GENRES = {
    "Sad": {"avoid": [18, 10752], "prefer": [35, 10751, 16]},
    "Lonely": {"prefer": [10749, 35, 18]},
    "Anxious": {"avoid": [27, 53], "prefer": [35, 16, 10751, 99]},
    "Overwhelmed": {"avoid": [28, 53, 27], "prefer": [99, 10402, 16]},
    "Angry": {"prefer": [28, 53, 80]},
    "Stressed": {"avoid": [53, 27], "prefer": [35, 16, 10751]},
    "Bored": {"prefer": [12, 878, 14, 28]},
    "Tired": {"prefer": [35, 10749, 16]},
    "Numb": {"prefer": [28, 12, 53]},
    "Confused": {"prefer": [99, 36]},
    "Restless": {"prefer": [28, 12, 878]},
    "Focused": {"prefer": [99, 9648, 36]},
    "Calm": {"prefer": [99, 10402, 36]},
    "Happy": {"prefer": [35, 10751, 12]},
    "Excited": {"prefer": [28, 12, 878]},
    "Curious": {"prefer": [99, 878, 9648, 14]},
    "Comforted": {"prefer": [10751, 16, 35, 10749]},
    "Relaxed": {"prefer": [10749, 35, 99]},
    "Energized": {"prefer": [28, 12, 878]},
    "Stimulated": {"prefer": [878, 14, 53, 9648]},
    "Entertained": {"prefer": [12, 28, 35, 14]},
    "Inspired": {"prefer": [18, 36, 99, 10752]},
    "Grounded": {"prefer": [99, 36, 10751]},
    "Sleepy": {"prefer": [16, 10751, 10749]},
    "Connected": {"prefer": [10749, 18, 10751]},
}

# Music mood mappings
FEELING_TO_MUSIC = {
    "Sad": {"query": "sad songs comfort", "playlist": "37i9dQZF1DX7qK8ma5wgG1", "genres": ["acoustic", "piano", "indie folk"]},
    "Lonely": {"query": "comfort songs lonely", "playlist": "37i9dQZF1DX3YSRoSdA634", "genres": ["indie", "acoustic", "soul"]},
    "Anxious": {"query": "calm relaxing anxiety relief", "playlist": "37i9dQZF1DWXe9gFZP0gtP", "genres": ["ambient", "classical", "new age"]},
    "Overwhelmed": {"query": "peaceful ambient stress relief", "playlist": "37i9dQZF1DWZqd5JICZI0u", "genres": ["ambient", "meditation", "nature sounds"]},
    "Angry": {"query": "angry workout metal", "playlist": "37i9dQZF1DX1tyCD9QhIWF", "genres": ["metal", "hard rock", "punk"]},
    "Stressed": {"query": "meditation spa relaxation", "playlist": "37i9dQZF1DWU0ScTcjJBdj", "genres": ["spa", "meditation", "ambient"]},
    "Bored": {"query": "upbeat pop hits energy", "playlist": "37i9dQZF1DXcBWIGoYBM5M", "genres": ["pop", "dance", "electronic"]},
    "Tired": {"query": "acoustic chill coffee", "playlist": "37i9dQZF1DX4WYpdgoIcn6", "genres": ["acoustic", "indie folk", "chill"]},
    "Numb": {"query": "intense electronic bass", "playlist": "37i9dQZF1DX4dyzvuaRJ0n", "genres": ["electronic", "dubstep", "bass"]},
    "Confused": {"query": "lo-fi study beats", "playlist": "37i9dQZF1DWWQRwui0ExPn", "genres": ["lo-fi", "chillhop", "jazz"]},
    "Restless": {"query": "high energy dance workout", "playlist": "37i9dQZF1DX76Wlfdnj7AP", "genres": ["edm", "dance", "house"]},
    "Focused": {"query": "deep focus concentration", "playlist": "37i9dQZF1DWZeKCadgRdKQ", "genres": ["classical", "ambient", "electronic"]},
    "Calm": {"query": "nature sounds peaceful", "playlist": "37i9dQZF1DX4sWSpwq3LiO", "genres": ["nature", "ambient", "classical"]},
    "Happy": {"query": "feel good happy hits", "playlist": "37i9dQZF1DX3rxVfibe1L0", "genres": ["pop", "dance", "funk"]},
    "Excited": {"query": "party anthems hype", "playlist": "37i9dQZF1DXa2PvUpywmrr", "genres": ["edm", "pop", "hip-hop"]},
    "Curious": {"query": "experimental indie discover", "playlist": "37i9dQZF1DX2sUQwD7tbmL", "genres": ["experimental", "indie", "alternative"]},
    "Comforted": {"query": "warm acoustic cozy", "playlist": "37i9dQZF1DX4E3UdUs7fUx", "genres": ["acoustic", "folk", "singer-songwriter"]},
    "Relaxed": {"query": "sunday morning chill", "playlist": "37i9dQZF1DX6VdMW310YC7", "genres": ["chill", "acoustic", "jazz"]},
    "Energized": {"query": "workout motivation pump", "playlist": "37i9dQZF1DX76Wlfdnj7AP", "genres": ["hip-hop", "edm", "rock"]},
    "Stimulated": {"query": "electronic bass intense", "playlist": "37i9dQZF1DX0pH2SQMRXnC", "genres": ["electronic", "techno", "trance"]},
    "Entertained": {"query": "viral hits trending", "playlist": "37i9dQZF1DXcBWIGoYBM5M", "genres": ["pop", "hip-hop", "dance"]},
    "Inspired": {"query": "epic orchestral motivation", "playlist": "37i9dQZF1DX3rxVfibe1L0", "genres": ["orchestral", "cinematic", "classical"]},
    "Grounded": {"query": "folk roots acoustic", "playlist": "37i9dQZF1DX4E3UdUs7fUx", "genres": ["folk", "americana", "acoustic"]},
    "Sleepy": {"query": "sleep sounds rain", "playlist": "37i9dQZF1DWZd79rJ6a7lp", "genres": ["sleep", "ambient", "nature"]},
    "Connected": {"query": "love songs romance", "playlist": "37i9dQZF1DX50QitC6Oqtn", "genres": ["r&b", "soul", "pop"]},
}

# Podcast mood mappings
FEELING_TO_PODCASTS = {
    "Sad": {"query": "mental health comfort healing", "shows": [("The Happiness Lab", "Learn the science of happiness"), ("Unlocking Us", "Brené Brown on emotions"), ("On Being", "Deep conversations on life")]},
    "Lonely": {"query": "friendship connection stories", "shows": [("This American Life", "Human connection stories"), ("Modern Love", "Stories of love & connection"), ("Dear Sugars", "Advice & comfort")]},
    "Anxious": {"query": "anxiety meditation calm", "shows": [("The Calm App", "Guided meditations"), ("Ten Percent Happier", "Meditation for skeptics"), ("Anxiety Slayer", "Tips for anxiety")]},
    "Overwhelmed": {"query": "minimalism simple living", "shows": [("The Minimalists", "Less is more"), ("Optimal Living Daily", "Curated self-help"), ("How to Be a Better Human", "Small improvements")]},
    "Bored": {"query": "true crime mystery thriller", "shows": [("Serial", "Investigative journalism"), ("My Favorite Murder", "True crime comedy"), ("Casefile", "True crime deep dives")]},
    "Curious": {"query": "science explained learning", "shows": [("Radiolab", "Science & philosophy"), ("Stuff You Should Know", "Learn anything"), ("Hidden Brain", "Psychology insights")]},
    "Focused": {"query": "productivity business success", "shows": [("Deep Work", "Cal Newport on focus"), ("The Tim Ferriss Show", "World-class performers"), ("How I Built This", "Entrepreneur stories")]},
    "Inspired": {"query": "motivation success stories", "shows": [("The School of Greatness", "Lewis Howes"), ("Impact Theory", "Tom Bilyeu"), ("The Tony Robbins Podcast", "Personal development")]},
    "Happy": {"query": "comedy funny laugh", "shows": [("Conan O'Brien Needs A Friend", "Comedy interviews"), ("SmartLess", "Jason Bateman & friends"), ("My Dad Wrote A Porno", "Hilarious readings")]},
    "Relaxed": {"query": "chill conversations stories", "shows": [("Nothing Much Happens", "Bedtime stories"), ("Sleep With Me", "Boring stories for sleep"), ("The Moth", "True stories")]},
}

# Audiobook mood mappings
FEELING_TO_AUDIOBOOKS = {
    "Sad": {"query": "comfort healing memoir", "genres": ["Self-Help", "Memoir", "Fiction"], "picks": [("It's OK That You're Not OK", "Megan Devine"), ("Maybe You Should Talk to Someone", "Lori Gottlieb"), ("A Man Called Ove", "Fredrik Backman")]},
    "Anxious": {"query": "anxiety calm mindfulness", "genres": ["Self-Help", "Mindfulness", "Psychology"], "picks": [("Dare", "Barry McDonagh"), ("The Anxiety Toolkit", "Alice Boyes"), ("Breath", "James Nestor")]},
    "Bored": {"query": "thriller mystery page turner", "genres": ["Thriller", "Mystery", "Suspense"], "picks": [("The Silent Patient", "Alex Michaelides"), ("Gone Girl", "Gillian Flynn"), ("The Girl on the Train", "Paula Hawkins")]},
    "Curious": {"query": "science history fascinating", "genres": ["Science", "History", "Biography"], "picks": [("Sapiens", "Yuval Noah Harari"), ("The Code Breaker", "Walter Isaacson"), ("Outliers", "Malcolm Gladwell")]},
    "Inspired": {"query": "motivation biography success", "genres": ["Biography", "Business", "Self-Help"], "picks": [("Atomic Habits", "James Clear"), ("Can't Hurt Me", "David Goggins"), ("Shoe Dog", "Phil Knight")]},
    "Focused": {"query": "productivity business focus", "genres": ["Business", "Self-Help", "Psychology"], "picks": [("Deep Work", "Cal Newport"), ("The 4-Hour Workweek", "Tim Ferriss"), ("Thinking, Fast and Slow", "Daniel Kahneman")]},
    "Happy": {"query": "feel good comedy romance", "genres": ["Romance", "Comedy", "Fiction"], "picks": [("Beach Read", "Emily Henry"), ("The House in the Cerulean Sea", "TJ Klune"), ("Anxious People", "Fredrik Backman")]},
    "Sleepy": {"query": "fantasy fiction adventure", "genres": ["Fantasy", "Fiction", "Classic"], "picks": [("The Hobbit", "J.R.R. Tolkien"), ("Harry Potter", "J.K. Rowling"), ("The Night Circus", "Erin Morgenstern")]},
    "Connected": {"query": "romance love stories", "genres": ["Romance", "Contemporary", "Fiction"], "picks": [("The Notebook", "Nicholas Sparks"), ("Me Before You", "Jojo Moyes"), ("Outlander", "Diana Gabaldon")]},
}

# --------------------------------------------------
# 5. DATA ENGINE - MOVIES
# --------------------------------------------------
def _clean_movie_results(results):
    clean = []
    for item in results:
        media_type = item.get("media_type", "movie")
        if media_type not in ["movie", "tv"]:
            continue
        title = item.get("title") or item.get("name")
        if not title or not item.get("poster_path"):
            continue
        clean.append({
            "id": item.get("id"), "type": media_type, "title": title,
            "overview": item.get("overview", "")[:150] + "..." if len(item.get("overview", "")) > 150 else item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "backdrop": f"{TMDB_BACKDROP_URL}{item.get('backdrop_path', '')}" if item.get('backdrop_path') else None,
            "release_date": item.get("release_date") or item.get("first_air_date") or "",
            "vote_average": item.get("vote_average", 0),
        })
    return clean

@st.cache_data(ttl=3600)
def discover_movies(page=1, current_feeling=None, desired_feeling=None):
    api_key = get_tmdb_key()
    if not api_key: return []
    genre_ids, avoid_genres = [], []
    if desired_feeling and desired_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[desired_feeling]
        genre_ids.extend(prefs.get("prefer", [])[:3])
        avoid_genres.extend(prefs.get("avoid", []))
    if current_feeling and current_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[current_feeling]
        avoid_genres.extend(prefs.get("avoid", []))
    try:
        params = {"api_key": api_key, "sort_by": "popularity.desc", "watch_region": "US",
                  "with_watch_monetization_types": "flatrate|rent", "page": page, "include_adult": "false"}
        if genre_ids: params["with_genres"] = "|".join(map(str, list(set(genre_ids))[:3]))
        if avoid_genres: params["without_genres"] = ",".join(map(str, list(set(avoid_genres))))
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        return _clean_movie_results(r.json().get("results", []))
    except: return []

@st.cache_data(ttl=3600)
def search_movies(query, page=1):
    api_key = get_tmdb_key()
    if not api_key or not query: return []
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/multi", params={"api_key": api_key, "query": query, "include_adult": "false", "page": page}, timeout=8)
        r.raise_for_status()
        results = [item for item in r.json().get("results", []) if item.get("media_type") in ["movie", "tv"]]
        return _clean_movie_results(results)
    except: return []

@st.cache_data(ttl=86400)
def get_movie_providers(tmdb_id, media_type):
    api_key = get_tmdb_key()
    if not api_key: return []
    try:
        r = requests.get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers", params={"api_key": api_key}, timeout=8)
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return (data.get("flatrate", []) + data.get("rent", []))[:8]
    except: return []

def get_movie_deep_link(provider_name, title):
    provider = (provider_name or "").strip()
    safe_title = quote_plus(title)
    if provider in MOVIE_SERVICES: return MOVIE_SERVICES[provider].format(title=safe_title)
    for key, template in MOVIE_SERVICES.items():
        if key.lower() in provider.lower() or provider.lower() in key.lower():
            return template.format(title=safe_title)
    return None

# --------------------------------------------------
# 6. NLP ENGINE
# --------------------------------------------------
def nlp_infer_feelings(prompt):
    t = (prompt or "").lower()
    current, desired = None, None
    if any(k in t for k in ["bore", "boring", "nothing", "meh"]): current = "Bored"
    elif any(k in t for k in ["stress", "burnout"]): current = "Stressed"
    elif any(k in t for k in ["anxious", "anxiety", "panic"]): current = "Anxious"
    elif any(k in t for k in ["sad", "down", "depressed"]): current = "Sad"
    elif any(k in t for k in ["lonely", "alone"]): current = "Lonely"
    elif any(k in t for k in ["angry", "mad"]): current = "Angry"
    elif any(k in t for k in ["tired", "exhaust"]): current = "Tired"
    if any(k in t for k in ["comfort", "cozy"]): desired = "Comforted"
    elif any(k in t for k in ["relax", "chill", "easy"]): desired = "Relaxed"
    elif any(k in t for k in ["action", "energy", "hype"]): desired = "Energized"
    elif any(k in t for k in ["fun", "funny", "laugh"]): desired = "Entertained"
    elif any(k in t for k in ["inspir", "motivat"]): desired = "Inspired"
    elif any(k in t for k in ["curious", "learn"]): desired = "Curious"
    elif any(k in t for k in ["sleep"]): desired = "Sleepy"
    elif any(k in t for k in ["happy", "joy"]): desired = "Happy"
    return current, desired

@st.cache_data(ttl=3600)
def nlp_search(prompt, page=1):
    if not prompt: return []
    h_current, h_desired = nlp_infer_feelings(prompt)
    if h_current or h_desired:
        return discover_movies(page=page, current_feeling=h_current, desired_feeling=h_desired)
    return search_movies(prompt, page=page)

# --------------------------------------------------
# 7. GAMIFICATION
# --------------------------------------------------
def get_dp(): return st.session_state.get("dopamine_points", 0)
def add_dp(amount, reason=""):
    st.session_state.dopamine_points = st.session_state.get("dopamine_points", 0) + amount
    if reason: st.toast(f"+{amount} DP: {reason}", icon="⚡")

def get_streak(): return st.session_state.get("streak_days", 0)

def update_streak():
    today = datetime.now().strftime("%Y-%m-%d")
    last = st.session_state.get("last_visit_date", "")
    if last != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last == yesterday:
            st.session_state.streak_days = st.session_state.get("streak_days", 0) + 1
            add_dp(10 * st.session_state.streak_days, f"{st.session_state.streak_days} day streak!")
        else:
            st.session_state.streak_days = 1
        st.session_state.last_visit_date = today

def get_level():
    p = get_dp()
    if p < 100: return ("Newbie", 1, 100)
    elif p < 500: return ("Explorer", 2, 500)
    elif p < 1500: return ("Curator", 3, 1500)
    elif p < 5000: return ("Connoisseur", 4, 5000)
    return ("Dopamine Master", 5, 999999)

def get_achievements():
    ach = []
    if get_streak() >= 3: ach.append(("🔥", "Hot Streak"))
    if get_streak() >= 7: ach.append(("💎", "Week Warrior"))
    if st.session_state.get("quick_hit_count", 0) >= 10: ach.append(("⚡", "Quick Draw"))
    if get_dp() >= 100: ach.append(("🌟", "Rising Star"))
    if get_dp() >= 1000: ach.append(("👑", "Royalty"))
    return ach

# --------------------------------------------------
# 8. STATE INIT
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "user": None, "auth_step": "landing", "is_premium": False,
        "current_feeling": "Bored", "desired_feeling": "Entertained",
        "movies_feed": [], "feed_page": 1, "last_emotion_key": None,
        "quick_hit": None, "quick_hit_count": 0,
        "dopamine_points": 0, "streak_days": 0, "last_visit_date": "",
        "nlp_prompt": "", "nlp_results": [], "nlp_page": 1,
        "referral_code": hashlib.md5(str(random.random()).encode()).hexdigest()[:8].upper(),
        "active_tab": "movies",
    })
    st.session_state.init = True

# --------------------------------------------------
# 9. CSS - COMPLETE STYLING
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #050508;
    --bg-secondary: #0a0a10;
    --accent-primary: #8b5cf6;
    --accent-secondary: #06b6d4;
    --accent-gradient: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
    --accent-gradient-2: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.6);
    --glass: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.08);
}

* { font-family: 'Outfit', sans-serif; }
h1, h2, h3, .stat-value { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: var(--bg-primary);
    background-image: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 100% 100%, rgba(6, 182, 212, 0.1) 0%, transparent 50%);
}

#MainMenu, footer, header, div[data-testid="stToolbar"] {visibility: hidden; display: none;}

/* Landing Page Styles */
.landing-hero {
    text-align: center;
    padding: 60px 20px;
    max-width: 900px;
    margin: 0 auto;
}

.landing-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
    line-height: 1.1;
}

.landing-subtitle {
    font-size: 1.5rem;
    color: var(--text-secondary);
    margin-bottom: 40px;
    line-height: 1.5;
}

.landing-tagline {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 32px;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin: 48px 0;
}

.feature-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    transition: all 0.3s;
}

.feature-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-4px);
}

.feature-icon { font-size: 2.5rem; margin-bottom: 16px; }
.feature-title { font-weight: 600; font-size: 1.1rem; margin-bottom: 8px; color: var(--text-primary); }
.feature-desc { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; }

/* Auth Card */
.auth-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 40px;
    max-width: 420px;
    margin: 0 auto;
}

.auth-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 8px;
}

.auth-subtitle {
    text-align: center;
    color: var(--text-secondary);
    margin-bottom: 24px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}

/* Stats Bar */
.stats-bar {
    display: flex;
    gap: 16px;
    padding: 16px 20px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    justify-content: center;
}

.stat-item { text-align: center; min-width: 80px; }
.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }

@keyframes fireGlow {
    0%, 100% { filter: drop-shadow(0 0 4px #ff6b35); transform: scale(1); }
    50% { filter: drop-shadow(0 0 12px #ff9f1c); transform: scale(1.1); }
}
.streak-fire { animation: fireGlow 1.5s ease-in-out infinite; font-size: 1.5rem; }

.level-bar { height: 6px; background: var(--glass); border-radius: 3px; margin-top: 6px; }
.level-progress { height: 100%; background: var(--accent-gradient); border-radius: 3px; }

/* Content Cards */
.content-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 16px;
}

.content-card:hover {
    transform: scale(1.03) translateY(-6px);
    border-color: var(--accent-primary);
    box-shadow: 0 20px 40px rgba(139, 92, 246, 0.2);
}

.content-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
}

.content-cover {
    width: 100%;
    aspect-ratio: 1/1;
    object-fit: cover;
    border-radius: 12px;
}

.content-info { padding: 14px; }
.content-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.content-meta { font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px; }

/* Provider Grid */
.provider-grid { display: flex; flex-wrap: wrap; gap: 6px; padding: 10px 14px; border-top: 1px solid var(--glass-border); }
.provider-btn {
    width: 32px; height: 32px;
    border-radius: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    text-decoration: none;
}
.provider-btn:hover { transform: scale(1.15); border-color: var(--accent-primary); }
.provider-icon { width: 22px; height: 22px; border-radius: 5px; }

/* Service Button */
.service-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    text-decoration: none;
    color: var(--text-primary);
    transition: all 0.2s;
    margin-bottom: 10px;
}
.service-btn:hover {
    border-color: var(--accent-primary);
    transform: translateX(4px);
    background: var(--glass);
}
.service-icon { width: 36px; height: 36px; border-radius: 10px; }
.service-name { font-weight: 600; font-size: 0.95rem; }
.service-desc { font-size: 0.8rem; color: var(--text-secondary); }

/* Buttons */
.stButton > button {
    background: var(--accent-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 12px 24px;
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    background: var(--accent-gradient);
    border-color: transparent;
    color: white;
}

/* Section Header */
.section-header { display: flex; align-items: center; gap: 10px; margin: 24px 0 16px 0; }
.section-title { font-family: 'Space Grotesk'; font-size: 1.3rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.section-icon { font-size: 1.4rem; }

/* Glass Card */
.glass-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-primary) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent-primary); border-radius: 3px; }

/* Pricing */
.pricing-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 32px;
    text-align: center;
    transition: all 0.3s;
}
.pricing-card.featured {
    border-color: var(--accent-primary);
    transform: scale(1.05);
    box-shadow: 0 20px 60px rgba(139, 92, 246, 0.3);
}
.pricing-name { font-weight: 700; font-size: 1.3rem; margin-bottom: 8px; }
.pricing-price { font-size: 2.5rem; font-weight: 700; }
.pricing-period { color: var(--text-secondary); }

/* About Section */
.about-section {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 40px;
    margin: 40px 0;
}

/* Testimonial */
.testimonial {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.testimonial-text { font-style: italic; color: var(--text-secondary); margin-bottom: 12px; }
.testimonial-author { font-weight: 600; color: var(--text-primary); }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 10. LANDING PAGE
# --------------------------------------------------
def render_landing():
    # Hero
    st.markdown("""
    <div class="landing-hero">
        <h1 class="landing-title">🧠 Dopamine.watch</h1>
        <p class="landing-subtitle">The first streaming guide designed for <strong>ADHD & neurodivergent brains</strong>.</p>
        <p class="landing-tagline">Tell us how you feel. We'll find the perfect content to match your mood.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Get Started Free", use_container_width=True, key="cta_signup"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button("🔑 Log In", use_container_width=True, key="cta_login"):
                st.session_state.auth_step = "login"
                st.rerun()
    
    # Features
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Mood-Driven Discovery</div>
            <div class="feature-desc">Select how you feel now and how you want to feel. We'll curate content that takes you there.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧾</div>
            <div class="feature-title">Mr.DP - AI Curator</div>
            <div class="feature-desc">Just type what you want in plain English. "Something funny for a stressed day" — done.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Quick Dope Hit</div>
            <div class="feature-desc">Can't decide? One button gives you the perfect match. No scrolling required.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎬</div>
            <div class="feature-title">Movies & TV</div>
            <div class="feature-desc">Emotion-filtered recommendations from Netflix, Disney+, Max, and 20+ streaming services.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎵</div>
            <div class="feature-title">Music & Playlists</div>
            <div class="feature-desc">Mood-matched music from Spotify, Apple Music, and more. Perfect vibes, every time.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <div class="feature-title">Podcasts & Books</div>
            <div class="feature-desc">Curated podcasts and audiobooks based on your current headspace.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Social Proof
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>💬</span><h2 class='section-title'>What People Are Saying</h2></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"Finally an app that understands my ADHD brain. No more endless scrolling!"</div>
            <div class="testimonial-author">— Sarah K., Designer</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"The Quick Dope Hit button is a game changer. Decision fatigue? Gone."</div>
            <div class="testimonial-author">— Marcus T., Developer</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"I love that it asks how I WANT to feel. So thoughtful."</div>
            <div class="testimonial-author">— Jamie L., Teacher</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Pricing
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>💎</span><h2 class='section-title'>Simple Pricing</h2></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-name">Free</div>
            <div class="pricing-price">$0</div>
            <div class="pricing-period">forever</div>
            <hr style="border-color: var(--glass-border); margin: 20px 0;">
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                ✓ Mood-based discovery<br>
                ✓ Quick Dope Hit<br>
                ✓ All content types<br>
                ✓ Basic Mr.DP
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="pricing-card featured">
            <div style="background: var(--accent-gradient); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; display: inline-block; margin-bottom: 12px;">MOST POPULAR</div>
            <div class="pricing-name">Plus</div>
            <div class="pricing-price">$4.99</div>
            <div class="pricing-period">/month</div>
            <hr style="border-color: var(--glass-border); margin: 20px 0;">
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                ✓ Everything in Free<br>
                ✓ Advanced AI curation<br>
                ✓ No ads<br>
                ✓ 2x Dopamine Points<br>
                ✓ Mood analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-name">Pro</div>
            <div class="pricing-price">$9.99</div>
            <div class="pricing-period">/month</div>
            <hr style="border-color: var(--glass-border); margin: 20px 0;">
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                ✓ Everything in Plus<br>
                ✓ Priority support<br>
                ✓ Early features<br>
                ✓ Custom triggers<br>
                ✓ API access
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # About
    st.markdown("---")
    st.markdown("""
    <div class="about-section">
        <h2 style="text-align: center; margin-bottom: 24px;">About Dopamine.watch</h2>
        <p style="color: var(--text-secondary); text-align: center; max-width: 700px; margin: 0 auto; line-height: 1.8;">
            We built Dopamine.watch because we know the struggle. Spending 45 minutes scrolling through Netflix, 
            only to give up and rewatch The Office again. Decision fatigue is real, especially for neurodivergent brains.
            <br><br>
            Our mission is simple: <strong>help you feel better, faster</strong>. By understanding your current emotional 
            state and where you want to be, we cut through the noise and deliver exactly what you need.
            <br><br>
            Built with ❤️ for ADHD brains, by ADHD brains.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer CTA
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>Ready to feel better?</h3>", unsafe_allow_html=True)
        if st.button("🚀 Start Free — No Credit Card Required", use_container_width=True, key="footer_cta"):
            st.session_state.auth_step = "signup"
            st.rerun()

# --------------------------------------------------
# 11. AUTH SCREENS
# --------------------------------------------------
def render_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🧠</h1>
            <div class="auth-title">Welcome Back</div>
            <div class="auth-subtitle">Log in to your dopamine engine</div>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
        
        if st.button("🔑 Log In", use_container_width=True, key="login_btn"):
            if email:
                st.session_state.user = {"email": email, "name": email.split("@")[0]}
                update_streak()
                add_dp(25, "Welcome back!")
                st.rerun()
            else:
                st.error("Please enter your email")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create Account", use_container_width=True, key="to_signup"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button("👤 Guest Mode", use_container_width=True, key="guest_login"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()
        
        if st.button("← Back to Home", key="back_login"):
            st.session_state.auth_step = "landing"
            st.rerun()

def render_signup():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🧠</h1>
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Start your dopamine journey</div>
        </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input("Name", key="signup_name", placeholder="Your name")
        email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="signup_pass", placeholder="••••••••")
        
        if st.button("🚀 Create Account", use_container_width=True, key="signup_btn"):
            if email and name:
                st.session_state.user = {"email": email, "name": name}
                update_streak()
                add_dp(50, "Welcome to Dopamine.watch!")
                st.balloons()
                st.rerun()
            else:
                st.error("Please fill in all fields")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Have Account? Log In", use_container_width=True, key="to_login"):
                st.session_state.auth_step = "login"
                st.rerun()
        with c2:
            if st.button("👤 Guest Mode", use_container_width=True, key="guest_signup"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()
        
        if st.button("← Back to Home", key="back_signup"):
            st.session_state.auth_step = "landing"
            st.rerun()

# --------------------------------------------------
# 12. HELPER FUNCTIONS
# --------------------------------------------------
def safe(s): return html_lib.escape(s or "")

def render_stats_bar():
    level_name, level_num, next_level = get_level()
    points, streak = get_dp(), get_streak()
    progress = min(100, (points / next_level) * 100)
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item"><div class="stat-value">{points}</div><div class="stat-label">Dopamine Points</div></div>
        <div class="stat-item"><span class="streak-fire">🔥</span><div class="stat-value">{streak}</div><div class="stat-label">Day Streak</div></div>
        <div class="stat-item"><div class="stat-value">Lv.{level_num}</div><div class="stat-label">{level_name}</div><div class="level-bar"><div class="level-progress" style="width:{progress}%"></div></div></div>
        <div class="stat-item"><div class="stat-value">{st.session_state.get('quick_hit_count', 0)}</div><div class="stat-label">Dope Hits</div></div>
    </div>
    """, unsafe_allow_html=True)

def render_movie_card(item):
    title, year = item.get("title", ""), item.get("release_date", "")[:4]
    rating, poster = item.get("vote_average", 0), item.get("poster")
    providers = get_movie_providers(item.get("id"), item.get("type", "movie"))
    icons = ""
    for p in providers[:6]:
        name, logo = p.get("provider_name", ""), p.get("logo_path")
        if not logo: continue
        link = get_movie_deep_link(name, title)
        if link: icons += f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='{safe(name)}'><img src='{TMDB_LOGO_URL}{logo}' class='provider-icon'></a>"
    providers_html = f"<div class='provider-grid'>{icons}</div>" if icons else ""
    rating_html = f"<span style='background:rgba(255,215,0,0.2);padding:2px 8px;border-radius:6px;font-size:0.7rem;color:#ffd700;'>⭐ {rating:.1f}</span>" if rating else ""
    st.markdown(f"""
    <div class="content-card">
        <img src="{safe(poster)}" class="content-poster" loading="lazy">
        <div class="content-info">
            <div class="content-title">{safe(title)}</div>
            <div class="content-meta">{year} {rating_html}</div>
        </div>
        {providers_html}
    </div>
    """, unsafe_allow_html=True)

def render_music_card(title, artist, image, query):
    st.markdown(f"""
    <div class="content-card">
        <img src="{safe(image)}" class="content-cover" loading="lazy">
        <div class="content-info">
            <div class="content-title">{safe(title)}</div>
            <div class="content-meta">{safe(artist)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_service_buttons(services, query):
    for name, data in services.items():
        url = data["url"].format(query=quote_plus(query))
        color = data.get("color", "#8b5cf6")
        st.markdown(f"""
        <a href="{url}" target="_blank" class="service-btn">
            <div style="width:36px;height:36px;background:{color};border-radius:10px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">{name[0]}</div>
            <div>
                <div class="service-name">{name}</div>
                <div class="service-desc">Search for "{query[:30]}..."</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

def get_quick_hit():
    movies = discover_movies(page=random.randint(1, 3), current_feeling=st.session_state.current_feeling, desired_feeling=st.session_state.desired_feeling)
    if movies:
        add_dp(15, "Quick Hit!")
        st.session_state.quick_hit_count = st.session_state.get("quick_hit_count", 0) + 1
        return random.choice(movies[:5])
    return None

# --------------------------------------------------
# 13. SIDEBAR
# --------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <h1 style="font-family:'Space Grotesk';font-size:1.4rem;margin-bottom:4px;">
            🧠 Dopamine<span style="background:var(--accent-gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">.watch</span>
        </h1>
        <p style="color:var(--text-secondary);font-size:0.8rem;margin-bottom:16px;">Hey, {st.session_state.user.get('name', 'Friend')}! 👋</p>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎯 How do you feel?")
        
        current_options = [f"{MOOD_EMOJIS.get(f, '😊')} {f}" for f in CURRENT_FEELINGS]
        current_idx = CURRENT_FEELINGS.index(st.session_state.current_feeling) if st.session_state.current_feeling in CURRENT_FEELINGS else 6
        current_choice = st.selectbox("Right now I feel...", current_options, index=current_idx, key="current_sel")
        new_current = current_choice.split(" ", 1)[1]
        if new_current != st.session_state.current_feeling:
            st.session_state.current_feeling = new_current
            st.session_state.movies_feed = []
            add_dp(5, "Mood check!")
        
        desired_options = [f"{MOOD_EMOJIS.get(f, '✨')} {f}" for f in DESIRED_FEELINGS]
        desired_idx = DESIRED_FEELINGS.index(st.session_state.desired_feeling) if st.session_state.desired_feeling in DESIRED_FEELINGS else 7
        desired_choice = st.selectbox("I want to feel...", desired_options, index=desired_idx, key="desired_sel")
        new_desired = desired_choice.split(" ", 1)[1]
        if new_desired != st.session_state.desired_feeling:
            st.session_state.desired_feeling = new_desired
            st.session_state.movies_feed = []
            add_dp(5, "Mood updated!")
        
        st.markdown("---")
        if st.button("⚡ QUICK DOPE HIT", use_container_width=True):
            st.session_state.quick_hit = get_quick_hit()
            st.session_state.nlp_results = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🧾 Mr.DP")
        nlp = st.text_area("Ask anything...", placeholder="'90s sci-fi' or 'I'm stressed'", height=80, key="nlp_in", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔮 Ask", use_container_width=True):
                if nlp.strip():
                    st.session_state.nlp_prompt = nlp
                    st.session_state.nlp_results = nlp_search(nlp)
                    st.session_state.quick_hit = None
                    add_dp(10, "Asked Mr.DP!")
                    st.rerun()
        with c2:
            if st.button("✕ Clear", use_container_width=True):
                st.session_state.nlp_results = []
                st.session_state.nlp_prompt = ""
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"<p style='text-align:center;'><span style='font-family:Space Grotesk;font-size:1.2rem;letter-spacing:2px;background:var(--accent-gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{st.session_state.referral_code}</span></p>", unsafe_allow_html=True)
        st.caption("Share for bonus DP!")
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.session_state.auth_step = "landing"
            st.rerun()

# --------------------------------------------------
# 14. MAIN APP TABS
# --------------------------------------------------
def render_main():
    render_stats_bar()
    
    # Quick Hit Display
    if st.session_state.quick_hit:
        st.markdown("<div class='section-header'><span class='section-icon'>🎬</span><h2 class='section-title'>Your Perfect Match</h2></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            render_movie_card(st.session_state.quick_hit)
            if st.button("🔄 Another Hit", use_container_width=True):
                st.session_state.quick_hit = get_quick_hit()
                st.rerun()
        st.markdown("---")
    
    # NLP Results
    if st.session_state.nlp_results:
        st.markdown(f"<div class='section-header'><span class='section-icon'>🧾</span><h2 class='section-title'>Mr.DP: \"{safe(st.session_state.nlp_prompt[:50])}...\"</h2></div>", unsafe_allow_html=True)
        cols = st.columns(6)
        for i, m in enumerate(st.session_state.nlp_results[:18]):
            with cols[i % 6]: render_movie_card(m)
        st.markdown("---")
    
    # Main Tabs
    tab_movies, tab_music, tab_pods, tab_books, tab_shorts = st.tabs(["🎬 Movies", "🎵 Music", "🎙️ Podcasts", "📚 Audiobooks", "⚡ Shorts"])
    
    # MOVIES TAB
    with tab_movies:
        st.markdown(f"<p style='color:var(--text-secondary);'>Curated for: {MOOD_EMOJIS.get(st.session_state.current_feeling,'')} → {MOOD_EMOJIS.get(st.session_state.desired_feeling,'')}</p>", unsafe_allow_html=True)
        ek = f"{st.session_state.current_feeling}_{st.session_state.desired_feeling}"
        if st.session_state.get("last_emotion_key") != ek:
            st.session_state.movies_feed = discover_movies(page=1, current_feeling=st.session_state.current_feeling, desired_feeling=st.session_state.desired_feeling)
            st.session_state.last_emotion_key = ek
            st.session_state.feed_page = 1
        if not st.session_state.movies_feed:
            st.session_state.movies_feed = discover_movies(page=1)
        cols = st.columns(6)
        for i, m in enumerate(st.session_state.movies_feed[:24]):
            with cols[i % 6]: render_movie_card(m)
        if st.button("Load More Movies", use_container_width=True, key="more_movies"):
            st.session_state.feed_page += 1
            more = discover_movies(page=st.session_state.feed_page, current_feeling=st.session_state.current_feeling, desired_feeling=st.session_state.desired_feeling)
            st.session_state.movies_feed.extend(more)
            add_dp(5, "Exploring!")
            st.rerun()
    
    # MUSIC TAB
    with tab_music:
        mood_music = FEELING_TO_MUSIC.get(st.session_state.desired_feeling, FEELING_TO_MUSIC["Happy"])
        st.markdown(f"### 🎵 Music for {st.session_state.desired_feeling}")
        st.markdown(f"<p style='color:var(--text-secondary);'>Genres: {', '.join(mood_music['genres'])}</p>", unsafe_allow_html=True)
        
        # Spotify Embed
        st.markdown("#### 🎧 Curated Playlist")
        components.iframe(f"https://open.spotify.com/embed/playlist/{mood_music['playlist']}?theme=0", height=380)
        
        st.markdown("#### 🔍 Search on Your Platform")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(MUSIC_SERVICES.items())[:3]), mood_music["query"])
        with c2:
            render_service_buttons(dict(list(MUSIC_SERVICES.items())[3:]), mood_music["query"])
        
        st.markdown("#### 🎹 Custom Search")
        music_query = st.text_input("Search for music...", placeholder="Artist, song, or mood", key="music_search")
        if music_query:
            render_service_buttons(MUSIC_SERVICES, music_query)
    
    # PODCASTS TAB
    with tab_pods:
        mood_pods = FEELING_TO_PODCASTS.get(st.session_state.desired_feeling, FEELING_TO_PODCASTS.get("Curious"))
        st.markdown(f"### 🎙️ Podcasts for {st.session_state.desired_feeling}")
        
        st.markdown("#### ⭐ Recommended Shows")
        for show, desc in mood_pods["shows"]:
            st.markdown(f"""
            <div class="glass-card" style="display:flex;align-items:center;gap:16px;">
                <div style="font-size:2rem;">🎙️</div>
                <div>
                    <div style="font-weight:600;">{show}</div>
                    <div style="color:var(--text-secondary);font-size:0.85rem;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### 🔍 Search Podcasts")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(PODCAST_SERVICES.items())[:3]), mood_pods["query"])
        with c2:
            render_service_buttons(dict(list(PODCAST_SERVICES.items())[3:]), mood_pods["query"])
        
        st.markdown("#### 🎤 Custom Search")
        pod_query = st.text_input("Search for podcasts...", placeholder="Topic or show name", key="pod_search")
        if pod_query:
            render_service_buttons(PODCAST_SERVICES, pod_query)
    
    # AUDIOBOOKS TAB
    with tab_books:
        mood_books = FEELING_TO_AUDIOBOOKS.get(st.session_state.desired_feeling, FEELING_TO_AUDIOBOOKS.get("Curious"))
        st.markdown(f"### 📚 Audiobooks for {st.session_state.desired_feeling}")
        st.markdown(f"<p style='color:var(--text-secondary);'>Genres: {', '.join(mood_books['genres'])}</p>", unsafe_allow_html=True)
        
        st.markdown("#### ⭐ Top Picks")
        cols = st.columns(3)
        for i, (title, author) in enumerate(mood_books["picks"]):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center;padding:24px;">
                    <div style="font-size:3rem;margin-bottom:12px;">📖</div>
                    <div style="font-weight:600;">{title}</div>
                    <div style="color:var(--text-secondary);font-size:0.85rem;">{author}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("#### 🔍 Search Audiobooks")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[:3]), mood_books["query"])
        with c2:
            render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[3:]), mood_books["query"])
        
        st.markdown("#### 📕 Custom Search")
        book_query = st.text_input("Search for audiobooks...", placeholder="Title, author, or genre", key="book_search")
        if book_query:
            render_service_buttons(AUDIOBOOK_SERVICES, book_query)
        
        st.info("💡 **Tip:** Check if your local library offers free audiobooks through Libby or Hoopla!")
    
    # SHORTS TAB
    with tab_shorts:
        videos_map = {
            "Sad": "wholesome animals cute", "Anxious": "satisfying oddly calming", "Bored": "mind blowing facts",
            "Stressed": "meditation guided relaxing", "Tired": "asmr relaxing", "Happy": "funny comedy viral",
            "Energized": "workout motivation hype", "Curious": "science experiments cool", "Relaxed": "nature scenery peaceful"
        }
        vq = videos_map.get(st.session_state.desired_feeling, "trending viral shorts")
        st.markdown(f"### ⚡ Quick Dopamine Hits")
        st.markdown(f"<p style='color:var(--text-secondary);'>Perfect for: {st.session_state.desired_feeling}</p>", unsafe_allow_html=True)
        
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(vq)}+shorts"
        st.markdown(f"<a href='{yt_url}' target='_blank' style='display:block;text-align:center;padding:24px;background:var(--accent-gradient);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;'>🎥 Watch {vq.title()} Shorts on YouTube →</a>", unsafe_allow_html=True)
        
        tt_url = f"https://www.tiktok.com/search?q={quote_plus(vq)}"
        st.markdown(f"<a href='{tt_url}' target='_blank' style='display:block;text-align:center;padding:24px;background:linear-gradient(135deg,#ff0050,#00f2ea);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-top:12px;'>📱 Browse on TikTok →</a>", unsafe_allow_html=True)

# --------------------------------------------------
# 15. MAIN ROUTER
# --------------------------------------------------
if not st.session_state.get("user"):
    if st.session_state.get("auth_step") == "login":
        render_login()
    elif st.session_state.get("auth_step") == "signup":
        render_signup()
    else:
        render_landing()
else:
    render_sidebar()
    render_main()
