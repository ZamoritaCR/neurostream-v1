# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v29.0 - VIRAL EDITION 🚀
# --------------------------------------------------
# UI/UX inspired by: Netflix, Disney+, TikTok, Duolingo
# Viral mechanics: Streaks, badges, social sharing, referrals
# ADHD-optimized: Minimal decisions, instant dopamine
# Target: 15k users by April, $10k MRR by June
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
LOGO_PATH = "logo.gif" if os.path.exists("logo.gif") else "logo.png"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_IMAGE_URL_HD = "https://image.tmdb.org/t/p/original"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"

# --------------------------------------------------
# 2. SERVICE MAP - WORKING DEEP LINKS
# --------------------------------------------------
SERVICE_MAP = {
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
    "Tubi TV": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details/{title}",
    "Plex": "https://watch.plex.tv/search?q={title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",
    "MUBI": "https://mubi.com/search?query={title}",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Fandango At Home": "https://www.vudu.com/content/movies/search?searchString={title}",
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

FEELING_TO_MUSIC = {
    "Sad": "sad piano", "Lonely": "comfort songs", "Anxious": "calm relaxing",
    "Overwhelmed": "peaceful ambient", "Angry": "heavy metal workout", "Stressed": "meditation spa",
    "Bored": "upbeat pop", "Tired": "acoustic chill", "Numb": "intense electronic",
    "Confused": "lo-fi study", "Restless": "high energy dance", "Focused": "deep focus",
    "Calm": "nature sounds", "Happy": "feel good hits", "Excited": "party anthems",
    "Curious": "experimental indie", "Comforted": "warm acoustic", "Relaxed": "sunday morning",
    "Energized": "workout motivation", "Stimulated": "electronic bass", "Entertained": "viral hits",
    "Inspired": "epic orchestral", "Grounded": "folk roots", "Sleepy": "sleep sounds", "Connected": "love songs",
}

FEELING_TO_VIDEOS = {
    "Sad": "wholesome animals", "Lonely": "heartwarming stories", "Anxious": "satisfying oddly",
    "Overwhelmed": "calming nature", "Angry": "epic fails funny", "Stressed": "meditation guided",
    "Bored": "mind blowing facts", "Tired": "asmr relaxing", "Numb": "extreme sports",
    "Confused": "explained simply", "Restless": "action parkour", "Focused": "productivity hacks",
    "Calm": "ocean waves", "Happy": "funny moments", "Excited": "epic moments",
    "Curious": "science experiments", "Comforted": "cozy vibes", "Relaxed": "coffee shop",
    "Energized": "hype motivation", "Stimulated": "wtf moments", "Entertained": "viral comedy",
    "Inspired": "success stories", "Grounded": "minimalist living", "Sleepy": "rain sounds", "Connected": "friendship goals",
}

# Gamification badges
BADGES = {
    "first_hit": {"icon": "🎯", "name": "First Hit", "desc": "Got your first Dope Hit"},
    "streak_3": {"icon": "🔥", "name": "On Fire", "desc": "3-day streak"},
    "streak_7": {"icon": "⚡", "name": "Unstoppable", "desc": "7-day streak"},
    "explorer": {"icon": "🧭", "name": "Explorer", "desc": "Tried all 5 content types"},
    "mood_master": {"icon": "🎭", "name": "Mood Master", "desc": "Used 10 different moods"},
    "share_first": {"icon": "📤", "name": "Spreader", "desc": "Shared with a friend"},
}

# --------------------------------------------------
# 5. DATA ENGINE
# --------------------------------------------------
def _clean_results(results):
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
            "overview": item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "backdrop": f"{TMDB_IMAGE_URL_HD}{item.get('backdrop_path', '')}" if item.get('backdrop_path') else None,
            "release_date": item.get("release_date") or item.get("first_air_date") or "",
            "vote_average": item.get("vote_average", 0),
        })
    return clean

@st.cache_data(ttl=3600)
def discover_movies_by_emotion(page=1, current_feeling=None, desired_feeling=None):
    api_key = get_tmdb_key()
    if not api_key:
        return []
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
        if genre_ids:
            params["with_genres"] = "|".join(map(str, list(set(genre_ids))[:3]))
        if avoid_genres:
            params["without_genres"] = ",".join(map(str, list(set(avoid_genres))))
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except:
        return []

@st.cache_data(ttl=3600)
def search_movies(query, page=1):
    api_key = get_tmdb_key()
    if not api_key or not query:
        return []
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/multi",
                         params={"api_key": api_key, "query": query, "include_adult": "false", "page": page}, timeout=8)
        r.raise_for_status()
        results = [item for item in r.json().get("results", []) if item.get("media_type") in ["movie", "tv"]]
        return _clean_results(results)
    except:
        return []

@st.cache_data(ttl=86400)
def get_streaming_providers(tmdb_id, media_type):
    api_key = get_tmdb_key()
    if not api_key:
        return {"flatrate": [], "rent": []}
    try:
        r = requests.get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
                         params={"api_key": api_key}, timeout=8)
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return {"flatrate": data.get("flatrate", [])[:6], "rent": data.get("rent", [])[:4]}
    except:
        return {"flatrate": [], "rent": []}

@st.cache_data(ttl=3600)
def get_trending():
    api_key = get_tmdb_key()
    if not api_key:
        return []
    try:
        r = requests.get(f"{TMDB_BASE_URL}/trending/movie/week", params={"api_key": api_key}, timeout=8)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))[:10]
    except:
        return []

def get_deep_link(provider_name, title):
    provider = (provider_name or "").strip()
    safe_title = quote_plus(title)
    if provider in SERVICE_MAP:
        return SERVICE_MAP[provider].format(title=safe_title)
    for key, template in SERVICE_MAP.items():
        if key.lower() in provider.lower() or provider.lower() in key.lower():
            return template.format(title=safe_title)
    return None

def safe(s):
    return html_lib.escape(s or "")

# --------------------------------------------------
# 6. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "user": None,
        "view": "landing",  # landing, onboarding, home
        "current_feeling": "Bored",
        "desired_feeling": "Entertained",
        "movies_feed": [],
        "movies_page": 1,
        "quick_hit": None,
        "dope_hits": 0,
        "streak": 0,
        "last_visit": None,
        "badges": [],
        "tabs_explored": set(),
        "moods_used": set(),
        "search_query": "",
        "search_results": [],
        "hero_movie": None,
        "show_share_modal": False,
    })
    st.session_state.init = True

# Update streak
today = datetime.now().date()
if st.session_state.last_visit:
    last = st.session_state.last_visit
    if isinstance(last, str):
        last = datetime.fromisoformat(last).date()
    diff = (today - last).days
    if diff == 1:
        st.session_state.streak += 1
    elif diff > 1:
        st.session_state.streak = 1
st.session_state.last_visit = today.isoformat()

# Check badges
def check_badges():
    badges = st.session_state.badges
    if st.session_state.dope_hits >= 1 and "first_hit" not in badges:
        badges.append("first_hit")
    if st.session_state.streak >= 3 and "streak_3" not in badges:
        badges.append("streak_3")
    if st.session_state.streak >= 7 and "streak_7" not in badges:
        badges.append("streak_7")
    if len(st.session_state.tabs_explored) >= 5 and "explorer" not in badges:
        badges.append("explorer")
    if len(st.session_state.moods_used) >= 10 and "mood_master" not in badges:
        badges.append("mood_master")

check_badges()

# --------------------------------------------------
# 7. VIRAL CSS - NETFLIX/TIKTOK INSPIRED
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-card: #1a1a28;
    --accent-primary: #00d4aa;
    --accent-secondary: #ff6b6b;
    --accent-tertiary: #ffd93d;
    --text-primary: #ffffff;
    --text-secondary: rgba(255,255,255,0.7);
    --text-muted: rgba(255,255,255,0.5);
    --gradient-primary: linear-gradient(135deg, #00d4aa 0%, #00a3ff 100%);
    --gradient-fire: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
    --gradient-hero: linear-gradient(180deg, transparent 0%, var(--bg-primary) 100%);
}

* { font-family: 'Outfit', sans-serif !important; }
.stApp { background: var(--bg-primary); }

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
[data-testid="stSidebar"] { background: var(--bg-secondary); }

/* Landing Hero */
.landing-hero {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 2rem;
    background: radial-gradient(ellipse at top, #1a1a35 0%, var(--bg-primary) 70%);
    position: relative;
    overflow: hidden;
}

.landing-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(from 0deg, transparent, var(--accent-primary), transparent 30%);
    animation: rotate 20s linear infinite;
    opacity: 0.1;
}

@keyframes rotate {
    100% { transform: rotate(360deg); }
}

.hero-logo {
    font-size: 4rem;
    font-weight: 900;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.hero-tagline {
    font-size: 1.5rem;
    color: var(--text-secondary);
    max-width: 600px;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.hero-cta {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 18px 48px;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--bg-primary);
    background: var(--gradient-primary);
    border: none;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    box-shadow: 0 8px 32px rgba(0, 212, 170, 0.3);
}

.hero-cta:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 16px 48px rgba(0, 212, 170, 0.4);
}

.social-proof {
    margin-top: 3rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--text-muted);
}

.avatars {
    display: flex;
}

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid var(--bg-primary);
    margin-left: -12px;
    background: var(--gradient-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

/* Mood Selector */
.mood-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    max-width: 600px;
    margin: 0 auto;
}

.mood-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 12px;
    background: var(--bg-card);
    border: 2px solid transparent;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
}

.mood-btn:hover {
    background: var(--bg-secondary);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
}

.mood-btn.active {
    background: var(--accent-primary);
    border-color: var(--accent-primary);
}

.mood-btn.active .mood-label {
    color: var(--bg-primary);
}

.mood-emoji { font-size: 2rem; margin-bottom: 8px; }
.mood-label { font-size: 0.85rem; color: var(--text-secondary); font-weight: 500; }

/* Hero Banner (Netflix style) */
.hero-banner {
    position: relative;
    height: 70vh;
    min-height: 500px;
    margin: -1rem -1rem 2rem -1rem;
    background-size: cover;
    background-position: center top;
    display: flex;
    align-items: flex-end;
}

.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(0deg, var(--bg-primary) 0%, transparent 50%, rgba(0,0,0,0.3) 100%);
}

.hero-content {
    position: relative;
    z-index: 2;
    padding: 3rem;
    max-width: 600px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 1rem;
    line-height: 1.1;
}

.hero-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: var(--text-secondary);
}

.hero-rating {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--accent-tertiary);
}

.hero-desc {
    font-size: 1rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

.hero-actions {
    display: flex;
    gap: 12px;
}

.btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 32px;
    font-size: 1rem;
    font-weight: 600;
    color: var(--bg-primary);
    background: var(--text-primary);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary:hover { transform: scale(1.05); }

.btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 14px 32px;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-secondary:hover { background: rgba(255,255,255,0.3); }

/* Quick Dope Hit Button */
.dope-hit-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    padding: 20px;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--bg-primary);
    background: var(--gradient-fire);
    border: none;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
    animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
    0%, 100% { box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3); }
    50% { box-shadow: 0 8px 48px rgba(255, 107, 107, 0.5); }
}

.dope-hit-btn:hover {
    transform: scale(1.02);
}

/* Stats Bar */
.stats-bar {
    display: flex;
    justify-content: space-around;
    padding: 16px;
    background: var(--bg-card);
    border-radius: 16px;
    margin-bottom: 24px;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Content Row */
.content-row {
    margin-bottom: 32px;
}

.row-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.row-scroll {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding-bottom: 16px;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
}

.row-scroll::-webkit-scrollbar { height: 4px; }
.row-scroll::-webkit-scrollbar-track { background: var(--bg-secondary); border-radius: 4px; }
.row-scroll::-webkit-scrollbar-thumb { background: var(--accent-primary); border-radius: 4px; }

/* Movie Card */
.movie-card {
    flex-shrink: 0;
    width: 180px;
    scroll-snap-align: start;
    background: var(--bg-card);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.movie-card:hover {
    transform: scale(1.08);
    z-index: 10;
    box-shadow: 0 16px 48px rgba(0,0,0,0.5);
}

.movie-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
}

.movie-info {
    padding: 12px;
}

.movie-title {
    font-size: 0.9rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 4px;
}

.movie-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 8px;
}

.movie-rating {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--accent-tertiary);
}

/* Provider Grid */
.provider-grid {
    display: flex;
    gap: 8px;
    padding: 8px 12px;
    flex-wrap: wrap;
}

.provider-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    object-fit: contain;
    background: var(--bg-secondary);
    padding: 4px;
    transition: transform 0.2s;
}

.provider-icon:hover { transform: scale(1.15); }

/* Badges */
.badges-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 16px;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: var(--bg-card);
    border-radius: 20px;
    font-size: 0.8rem;
}

.badge.earned {
    background: var(--gradient-primary);
    color: var(--bg-primary);
}

.badge.locked {
    opacity: 0.4;
}

/* Share Modal */
.share-modal {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.share-content {
    background: var(--bg-card);
    padding: 32px;
    border-radius: 24px;
    max-width: 400px;
    text-align: center;
}

.share-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.share-subtitle {
    color: var(--text-secondary);
    margin-bottom: 24px;
}

.share-buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
}

.share-btn {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    transition: transform 0.2s;
}

.share-btn:hover { transform: scale(1.1); }
.share-btn.twitter { background: #1DA1F2; }
.share-btn.facebook { background: #4267B2; }
.share-btn.whatsapp { background: #25D366; }
.share-btn.copy { background: var(--accent-primary); }

/* Tabs */
.tab-bar {
    display: flex;
    gap: 8px;
    padding: 8px;
    background: var(--bg-secondary);
    border-radius: 16px;
    margin-bottom: 24px;
}

.tab-item {
    flex: 1;
    padding: 12px 16px;
    text-align: center;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
    color: var(--text-secondary);
}

.tab-item:hover { background: var(--bg-card); }
.tab-item.active {
    background: var(--gradient-primary);
    color: var(--bg-primary);
}

/* Search */
.search-box {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: var(--bg-card);
    border-radius: 16px;
    margin-bottom: 24px;
}

.search-input {
    flex: 1;
    background: none;
    border: none;
    color: var(--text-primary);
    font-size: 1rem;
    outline: none;
}

.search-input::placeholder { color: var(--text-muted); }

/* Responsive */
@media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
    .hero-content { padding: 1.5rem; }
    .movie-card { width: 140px; }
    .mood-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 8. LANDING PAGE
# --------------------------------------------------
def render_landing():
    st.markdown("""
    <div class="landing-hero">
        <div class="hero-logo">🧠 Dopamine.watch</div>
        <div class="hero-tagline">
            Stop scrolling forever. Tell us how you feel, and we'll find the perfect movie, music, or video to match your mood — in seconds.
        </div>
        <div class="social-proof">
            <div class="avatars">
                <div class="avatar">😊</div>
                <div class="avatar">🎯</div>
                <div class="avatar">⚡</div>
                <div class="avatar">🔥</div>
                <div class="avatar">+2k</div>
            </div>
            <span>Join 2,000+ neurodivergent users finding their perfect content</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚡ Start Finding Your Vibe", use_container_width=True, type="primary"):
            st.session_state.view = "onboarding"
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("🧠 Built for ADHD & neurodivergent brains"):
            st.markdown("""
            - **Decision paralysis?** We decide for you
            - **Can't focus?** Quick dopamine hits on demand
            - **Mood-driven** - not algorithm-driven
            - **Zero overwhelm** - clean, simple, fast
            """)

# --------------------------------------------------
# 9. ONBOARDING
# --------------------------------------------------
def render_onboarding():
    st.markdown("<h1 style='text-align:center;margin-bottom:0'>How do you feel right now?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:var(--text-secondary);margin-bottom:2rem'>Pick one. We'll handle the rest.</p>", unsafe_allow_html=True)
    
    feelings = [
        ("😐", "Bored"), ("😫", "Stressed"), ("😰", "Anxious"), ("😴", "Tired"),
        ("🌧️", "Sad"), ("😡", "Angry"), ("🥺", "Lonely"), ("😵‍💫", "Overwhelmed"),
    ]
    
    cols = st.columns(4)
    for i, (emoji, feeling) in enumerate(feelings):
        with cols[i % 4]:
            if st.button(f"{emoji}\n{feeling}", key=f"feel_{feeling}", use_container_width=True):
                st.session_state.current_feeling = feeling
                st.session_state.moods_used.add(feeling)
                
    st.markdown("<br><h2 style='text-align:center'>What do you want to feel?</h2>", unsafe_allow_html=True)
    
    desired = [
        ("🍿", "Entertained"), ("🔥", "Energized"), ("😌", "Relaxed"), ("✨", "Inspired"),
        ("😊", "Happy"), ("🚀", "Stimulated"), ("🫶", "Comforted"), ("🌙", "Sleepy"),
    ]
    
    cols = st.columns(4)
    for i, (emoji, feeling) in enumerate(desired):
        with cols[i % 4]:
            if st.button(f"{emoji}\n{feeling}", key=f"want_{feeling}", use_container_width=True):
                st.session_state.desired_feeling = feeling
                st.session_state.moods_used.add(feeling)
                st.session_state.view = "home"
                st.session_state.movies_feed = discover_movies_by_emotion(
                    current_feeling=st.session_state.current_feeling,
                    desired_feeling=feeling
                )
                if st.session_state.movies_feed:
                    st.session_state.hero_movie = st.session_state.movies_feed[0]
                st.rerun()

# --------------------------------------------------
# 10. HOME SCREEN
# --------------------------------------------------
def render_home():
    # Stats bar
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">🔥 {st.session_state.streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">⚡ {st.session_state.dope_hits}</div>
            <div class="stat-label">Dope Hits</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">🏆 {len(st.session_state.badges)}</div>
            <div class="stat-label">Badges</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Dope Hit Button
    if st.button("⚡ QUICK DOPE HIT ⚡", use_container_width=True, type="primary"):
        movies = discover_movies_by_emotion(
            page=random.randint(1, 3),
            current_feeling=st.session_state.current_feeling,
            desired_feeling=st.session_state.desired_feeling
        )
        if movies:
            st.session_state.quick_hit = random.choice(movies[:5])
            st.session_state.dope_hits += 1
            check_badges()
            st.rerun()
    
    # Show Quick Hit Result
    if st.session_state.quick_hit:
        movie = st.session_state.quick_hit
        st.markdown(f"### 🎯 Your Perfect Match")
        
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(movie["poster"], use_container_width=True)
        with cols[1]:
            st.markdown(f"## {movie['title']}")
            if movie.get("vote_average"):
                st.markdown(f"⭐ {movie['vote_average']:.1f}/10")
            st.markdown(movie.get("overview", "")[:200] + "...")
            
            # Providers
            provs = get_streaming_providers(movie["id"], movie["type"])
            if provs["flatrate"]:
                st.markdown("**Watch on:**")
                provider_html = ""
                for p in provs["flatrate"][:4]:
                    link = get_deep_link(p.get("provider_name", ""), movie["title"])
                    if link and p.get("logo_path"):
                        logo = f"{TMDB_LOGO_URL}{p['logo_path']}"
                        provider_html += f"<a href='{link}' target='_blank'><img src='{logo}' class='provider-icon'></a>"
                st.markdown(f"<div class='provider-grid'>{provider_html}</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Try Another", use_container_width=True):
                    st.session_state.quick_hit = None
                    st.rerun()
            with col2:
                if st.button("📤 Share", use_container_width=True):
                    st.session_state.show_share_modal = True
        
        st.markdown("---")
    
    # Search
    search = st.text_input("🔍 Search movies, shows, actors...", key="search_input")
    if search:
        results = search_movies(search)
        if results:
            st.markdown(f"### Results for '{search}'")
            cols = st.columns(6)
            for i, movie in enumerate(results[:12]):
                with cols[i % 6]:
                    render_movie_card(movie)
            return
    
    # Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎬 Movies", "⚡ Shots", "🎵 Music", "🎙️ Podcasts"])
    
    with tab1:
        st.session_state.tabs_explored.add("movies")
        
        # Trending
        trending = get_trending()
        if trending:
            st.markdown("### 🔥 Trending Now")
            cols = st.columns(5)
            for i, movie in enumerate(trending[:5]):
                with cols[i]:
                    render_movie_card(movie)
        
        # Mood-based
        st.markdown(f"### ✨ Perfect for feeling {st.session_state.desired_feeling}")
        if not st.session_state.movies_feed:
            st.session_state.movies_feed = discover_movies_by_emotion(
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
        
        cols = st.columns(6)
        for i, movie in enumerate(st.session_state.movies_feed[:12]):
            with cols[i % 6]:
                render_movie_card(movie)
        
        if st.button("Load More", use_container_width=True):
            st.session_state.movies_page += 1
            more = discover_movies_by_emotion(
                page=st.session_state.movies_page,
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
            st.session_state.movies_feed.extend(more)
            st.rerun()
    
    with tab2:
        st.session_state.tabs_explored.add("shots")
        vk = FEELING_TO_VIDEOS.get(st.session_state.desired_feeling, "trending")
        st.markdown(f"### ⚡ Quick Dopamine: {vk.title()}")
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(vk)}+shorts"
        st.markdown(f"<a href='{yt_url}' target='_blank' class='btn-primary' style='text-decoration:none;display:inline-block;margin-bottom:1rem'>🎥 Watch {vk.title()} Shorts →</a>", unsafe_allow_html=True)
        components.iframe(f"https://www.youtube.com/embed?listType=search&list={quote_plus(vk)}", height=400)
    
    with tab3:
        st.session_state.tabs_explored.add("music")
        mk = FEELING_TO_MUSIC.get(st.session_state.desired_feeling, "feel good")
        st.markdown(f"### 🎵 Music for: {mk.title()}")
        sp_url = f"https://open.spotify.com/search/{quote_plus(mk)}"
        st.markdown(f"<a href='{sp_url}' target='_blank' class='btn-primary' style='text-decoration:none;display:inline-block;margin-bottom:1rem'>🎧 Open in Spotify →</a>", unsafe_allow_html=True)
        playlists = {"Anxious": "37i9dQZF1DWXe9gFZP0gtP", "Energized": "37i9dQZF1DX76Wlfdnj7AP", "Happy": "37i9dQZF1DX3rxVfibe1L0", "Relaxed": "37i9dQZF1DWTvS1gIcZVp4", "Focused": "37i9dQZF1DWZeKCadgRdKQ"}
        pid = playlists.get(st.session_state.desired_feeling, "37i9dQZF1DX3rxVfibe1L0")
        components.iframe(f"https://open.spotify.com/embed/playlist/{pid}", height=380)
    
    with tab4:
        st.session_state.tabs_explored.add("podcasts")
        topics = {"Anxious": "mental health calm", "Curious": "science explained", "Inspired": "motivational success", "Bored": "true crime mystery", "Focused": "productivity", "Happy": "comedy"}
        topic = topics.get(st.session_state.desired_feeling, "trending podcasts")
        st.markdown(f"### 🎙️ Podcasts: {topic.title()}")
        sp_url = f"https://open.spotify.com/search/{quote_plus(topic)}%20podcast"
        st.markdown(f"<a href='{sp_url}' target='_blank' class='btn-primary' style='text-decoration:none;display:inline-block'>🎙️ Find Podcasts →</a>", unsafe_allow_html=True)
    
    check_badges()
    
    # Badges display
    if st.session_state.badges:
        st.markdown("---")
        st.markdown("### 🏆 Your Badges")
        badge_html = ""
        for badge_id in st.session_state.badges:
            b = BADGES.get(badge_id, {})
            badge_html += f"<span class='badge earned'>{b.get('icon', '🏆')} {b.get('name', badge_id)}</span>"
        st.markdown(f"<div class='badges-row'>{badge_html}</div>", unsafe_allow_html=True)
    
    # Sidebar for mood change
    with st.sidebar:
        st.markdown("### 🎯 Current Mood")
        st.markdown(f"**Feeling:** {st.session_state.current_feeling}")
        st.markdown(f"**Want:** {st.session_state.desired_feeling}")
        
        if st.button("🔄 Change Mood", use_container_width=True):
            st.session_state.view = "onboarding"
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📤 Share & Earn")
        st.markdown("Invite friends to unlock exclusive badges!")
        
        share_url = "https://dopamine.watch"
        st.code(share_url, language=None)
        
        if st.button("📋 Copy Link", use_container_width=True):
            st.toast("Link copied! 🎉")
            if "share_first" not in st.session_state.badges:
                st.session_state.badges.append("share_first")

def render_movie_card(movie):
    provs = get_streaming_providers(movie["id"], movie["type"])
    first_provider = provs["flatrate"][0] if provs["flatrate"] else None
    link = get_deep_link(first_provider.get("provider_name", ""), movie["title"]) if first_provider else f"https://www.google.com/search?q={quote_plus(movie['title'])}"
    
    st.markdown(f"""
    <a href="{link}" target="_blank" style="text-decoration:none;color:inherit">
        <div class="movie-card">
            <img src="{movie['poster']}" class="movie-poster" loading="lazy">
            <div class="movie-info">
                <div class="movie-title">{safe(movie['title'])}</div>
                <div class="movie-meta">
                    {f"<span class='movie-rating'>⭐ {movie['vote_average']:.1f}</span>" if movie.get('vote_average') else ""}
                    <span>{movie.get('release_date', '')[:4]}</span>
                </div>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 11. ROUTER
# --------------------------------------------------
if st.session_state.view == "landing":
    render_landing()
elif st.session_state.view == "onboarding":
    render_onboarding()
else:
    render_home()
