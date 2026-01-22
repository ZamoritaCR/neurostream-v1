# FILE: app.py
# --------------------------------------------------
# 🧠 DOPAMINE.WATCH v40.0 - ADHD-OPTIMIZED EDITION
# --------------------------------------------------
# Built on extensive ADHD/neurodivergent research:
# ✅ Lexend font (dyslexia-friendly, scientifically proven)
# ✅ Softened color palette (reduces sensory overload)
# ✅ Reduced cognitive load (minimalist, clean UI)
# ✅ Variable reward dopamine triggers
# ✅ Focus Mode toggle for sensory sensitivity
# ✅ ADHD-aware Mr.DP AI assistant
# ✅ Quick Dope Hit (decision paralysis killer)
# ✅ Gamification with streak-freeze protection
# --------------------------------------------------

import streamlit as st
import os
import requests
import json
import base64
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from openai import OpenAI
import html as html_lib
import random
from datetime import datetime, timedelta
import hashlib
import re

# --------------------------------------------------
# 1. CONFIG - ADHD-OPTIMIZED
# --------------------------------------------------
st.set_page_config(
    page_title="dopamine.watch | Your Brain, Your Vibe",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "dopamine.watch"
APP_VERSION = "40.0"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_URL = "https://image.tmdb.org/t/p/original"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"
LOGO_PATH = "logo.png"

# --------------------------------------------------
# 2. ENVIRONMENT - API KEYS
# --------------------------------------------------
def get_tmdb_key():
    return os.environ.get("TMDB_API_KEY", st.secrets.get("TMDB_API_KEY", ""))

def get_openai_key():
    return os.environ.get("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))

openai_client = None
if get_openai_key():
    openai_client = OpenAI(api_key=get_openai_key())

# --------------------------------------------------
# 3. ADHD-OPTIMIZED CSS
# --------------------------------------------------
# Based on extensive research:
# - Lexend font (scientifically designed for reading ease)
# - Softened colors (no pure white/black - reduces visual stress)
# - Muted purple & teal (calming for ADHD brains)
# - Increased letter-spacing (dyslexia-friendly)
# - 1.6 line-height (easier tracking)
# - Reduced animations (sensory-safe)
# --------------------------------------------------

st.markdown("""
<style>
/* ============================================
   ADHD-OPTIMIZED DESIGN SYSTEM
   Based on neuroscience research for ADHD/dyslexia
   ============================================ */

/* Import Lexend - scientifically designed for reading ease */
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&display=swap');

:root {
    /* ADHD-SAFE COLOR PALETTE (Research-backed)
       - No pure white (#fff) - causes eye strain
       - No pure black (#000) - too harsh contrast
       - Muted, calming tones that don't overstimulate */
    
    /* Primary - Soft Purple (calming, creative) */
    --primary: #9B8EC2;
    --primary-light: #B8ADDA;
    --primary-dark: #7A6BA3;
    --primary-muted: rgba(155, 142, 194, 0.15);
    
    /* Secondary - Soft Teal (grounding, not harsh blue) */
    --secondary: #6BA3A3;
    --secondary-light: #8FBFBF;
    --secondary-dark: #4D8585;
    --secondary-muted: rgba(107, 163, 163, 0.15);
    
    /* Accent - Warm Sage (success, positive) */
    --accent: #7BC47F;
    --accent-light: #9DD69F;
    --accent-dark: #5DA361;
    
    /* Backgrounds - Warm, not sterile */
    --bg-primary: #0D0D14;          /* Soft dark with slight warmth */
    --bg-secondary: #12121C;        /* Slightly lighter */
    --bg-card: rgba(155, 142, 194, 0.04);  /* Purple-tinted glass */
    --bg-card-hover: rgba(155, 142, 194, 0.08);
    
    /* Text - Reduced contrast (easier on eyes) */
    --text-primary: #E8E4F0;        /* Soft white with purple tint */
    --text-secondary: rgba(232, 228, 240, 0.65);
    --text-muted: rgba(232, 228, 240, 0.45);
    
    /* Glass Effects */
    --glass: rgba(155, 142, 194, 0.05);
    --glass-border: rgba(155, 142, 194, 0.12);
    --glass-hover: rgba(155, 142, 194, 0.10);
    
    /* Semantic */
    --success: #68B984;
    --warning: #E8A87C;
    --error: #D98B8B;
}

/* Global Typography - ADHD-Optimized */
* {
    font-family: 'Lexend', -apple-system, BlinkMacSystemFont, sans-serif !important;
    letter-spacing: 0.01em;  /* Dyslexia-friendly spacing */
}

/* Main App Container */
.main {
    background: var(--bg-primary);
    color: var(--text-primary);
}

/* Streamlit Overrides */
.stApp {
    background: var(--bg-primary);
}

/* Headers - Reduced visual weight */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 500 !important;  /* Not too bold */
    line-height: 1.4 !important;
}

h1 { font-size: 2rem !important; }
h2 { font-size: 1.5rem !important; }
h3 { font-size: 1.25rem !important; }

/* Body Text - Dyslexia-Friendly */
p, div, span, label {
    color: var(--text-secondary);
    line-height: 1.6 !important;  /* Easier tracking */
    font-size: 1rem;
}

/* Buttons - ADHD-Safe Interactions */
.stButton button {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;  /* Fast, not jarring */
    backdrop-filter: blur(10px) !important;
}

.stButton button:hover {
    background: var(--glass-hover) !important;
    border-color: var(--primary) !important;
    transform: translateY(-2px);  /* Subtle lift */
    box-shadow: 0 4px 12px rgba(155, 142, 194, 0.15);
}

.stButton button:active {
    transform: translateY(0);  /* Quick feedback */
}

/* Primary Action Buttons */
.stButton button[kind="primary"] {
    background: var(--primary) !important;
    border: none !important;
    color: #fff !important;
}

.stButton button[kind="primary"]:hover {
    background: var(--primary-light) !important;
}

/* Input Fields - Calm, Clear */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 0.75rem !important;
    font-size: 1rem !important;
}

.stTextInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--primary-muted) !important;
    outline: none !important;
}

/* Sidebar - Clean, Organized */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
}

[data-testid="stSidebar"] .stButton button {
    width: 100%;
    margin-bottom: 0.5rem;
}

/* Movie Cards - Glass Morphism */
.movie-card {
    background: var(--bg-card);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.movie-card:hover {
    background: var(--bg-card-hover);
    border-color: var(--primary);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(155, 142, 194, 0.15);
}

/* Tabs - Clear Hierarchy */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    color: var(--text-secondary);
    padding: 0.5rem 1rem;
    font-weight: 500;
}

.stTabs [aria-selected="true"] {
    background: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #fff !important;
}

/* Expanders - Reduce Visual Clutter */
.streamlit-expanderHeader {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

/* Toast Notifications - Dopamine Hits! */
.stToast {
    background: var(--primary) !important;
    color: #fff !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    font-weight: 500 !important;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Scrollbar - Soft Styling */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--glass-border);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary);
}

/* Reduced Motion for Accessibility */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* Focus Mode - Optional Ultra-Minimal */
.focus-mode {
    filter: contrast(0.95) brightness(0.98);
}

.focus-mode .movie-card {
    border-color: transparent;
}

.focus-mode .movie-card:hover {
    border-color: var(--primary);
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. FEELING → GENRE MAPPINGS (Enhanced)
# --------------------------------------------------
FEELING_TO_GENRES = {
    "Bored": {"prefer": [28, 12, 878], "avoid": []},  # Action, Adventure, Sci-Fi
    "Anxious": {"prefer": [35, 10751, 16], "avoid": [27, 53]},  # Comedy, Family, Animation (avoid Horror, Thriller)
    "Sad": {"prefer": [35, 10402, 16], "avoid": [18]},  # Comedy, Music, Animation (avoid Drama)
    "Stressed": {"prefer": [16, 10751, 35], "avoid": [27, 53, 28]},  # Animation, Family, Comedy
    "Angry": {"prefer": [28, 80, 53], "avoid": [10749]},  # Action, Crime, Thriller
    "Lonely": {"prefer": [10749, 35, 18], "avoid": []},  # Romance, Comedy, Drama
    "Tired": {"prefer": [16, 35, 10751], "avoid": [28, 27]},  # Animation, Comedy, Family
    "Restless": {"prefer": [28, 12, 53], "avoid": [36, 99]},  # Action, Adventure, Thriller
    "Unmotivated": {"prefer": [99, 18, 36], "avoid": []},  # Documentary, Drama, History
    "Overwhelmed": {"prefer": [10751, 16, 14], "avoid": [878, 27]},  # Family, Animation, Fantasy
    "Nostalgic": {"prefer": [36, 10749, 18], "avoid": [27, 53]},  # History, Romance, Drama
    "Creative": {"prefer": [878, 14, 10402], "avoid": []},  # Sci-Fi, Fantasy, Music
    "Curious": {"prefer": [99, 9648, 878], "avoid": []},  # Documentary, Mystery, Sci-Fi
    "Energetic": {"prefer": [28, 12, 10402], "avoid": []},  # Action, Adventure, Music
    "Entertained": {"prefer": [35, 12, 16], "avoid": []},  # Comedy, Adventure, Animation
    "Inspired": {"prefer": [18, 99, 36], "avoid": [27]},  # Drama, Documentary, History
    "Happy": {"prefer": [35, 10751, 10402], "avoid": [27, 53]},  # Comedy, Family, Music
    "Relaxed": {"prefer": [10749, 16, 14], "avoid": [28, 27]},  # Romance, Animation, Fantasy
    "Thoughtful": {"prefer": [18, 9648, 878], "avoid": [28]},  # Drama, Mystery, Sci-Fi
    "Excited": {"prefer": [28, 12, 878], "avoid": []},  # Action, Adventure, Sci-Fi
}

COMMON_FEELINGS = list(FEELING_TO_GENRES.keys())

# --------------------------------------------------
# 5. TMDB API FUNCTIONS
# --------------------------------------------------
@st.cache_data(ttl=3600)
def discover_movies(current_feeling=None, desired_feeling=None, page=1):
    api_key = get_tmdb_key()
    if not api_key:
        return []
    
    genre_ids = []
    avoid_genres = []
    
    if desired_feeling and desired_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[desired_feeling]
        genre_ids.extend(prefs.get("prefer", []))
        avoid_genres.extend(prefs.get("avoid", []))
    
    if current_feeling and current_feeling in FEELING_TO_GENRES:
        avoid_genres.extend(FEELING_TO_GENRES[current_feeling].get("avoid", []))
    
    try:
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
            "page": page,
            "include_adult": "false"
        }
        
        if genre_ids:
            params["with_genres"] = "|".join(map(str, list(set(genre_ids))[:3]))
        
        if avoid_genres:
            params["without_genres"] = ",".join(map(str, list(set(avoid_genres))))
        
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        results = r.json().get("results", [])
        
        # CRITICAL FIX: Add media_type to each result
        for item in results:
            if "media_type" not in item:
                item["media_type"] = "movie"
        
        return results
    except Exception as e:
        st.error(f"Error discovering movies: {e}")
        return []

@st.cache_data(ttl=3600)
def search_movies(query, page=1):
    api_key = get_tmdb_key()
    if not api_key or not query:
        return []
    
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/search/multi",
            params={
                "api_key": api_key,
                "query": query,
                "include_adult": "false",
                "page": page
            },
            timeout=8
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        
        # Filter to movies/TV only
        filtered = [item for item in results if item.get("media_type") in ["movie", "tv"]]
        return filtered
    except Exception as e:
        st.error(f"Error searching: {e}")
        return []

@st.cache_data(ttl=86400)
def get_movie_providers(tmdb_id, media_type):
    api_key = get_tmdb_key()
    if not api_key:
        return [], None
    
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
            params={"api_key": api_key},
            timeout=8
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        providers = data.get("flatrate", [])[:6]
        tmdb_link = f"https://www.themoviedb.org/{media_type}/{tmdb_id}/watch?locale=US"
        return providers, tmdb_link
    except:
        return [], None

def discover_movies_fresh(current_feeling=None, desired_feeling=None):
    """Non-cached version for Quick Dope Hit"""
    api_key = get_tmdb_key()
    if not api_key:
        return []
    
    genre_ids = []
    if desired_feeling and desired_feeling in FEELING_TO_GENRES:
        genre_ids = FEELING_TO_GENRES[desired_feeling].get("prefer", [])[:3]
    
    try:
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
            "page": random.randint(1, 5),
            "include_adult": "false"
        }
        
        if genre_ids:
            params["with_genres"] = "|".join(map(str, genre_ids))
        
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        results = r.json().get("results", [])
        random.shuffle(results)
        
        # Add media_type
        for item in results:
            if "media_type" not in item:
                item["media_type"] = "movie"
        
        return results
    except:
        return []

# --------------------------------------------------
# 6. MR.DP AI ENGINE (ADHD-Aware)
# --------------------------------------------------
def mrdp_plan_query(user_prompt):
    """ADHD-optimized query planning with Mr.DP"""
    if not openai_client:
        return None
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": """You are Mr.DP, an ADHD-aware AI assistant for dopamine.watch.

**Your Understanding:**
- Users often struggle with decision paralysis
- They may use vague, stream-of-consciousness language
- They want quick, exciting recommendations without overthinking

**Your Response Style:**
- Be encouraging, never overwhelming
- Keep responses SHORT (2-3 sentences max)
- Use emojis sparingly for dopamine hits
- Acknowledge their mood/energy level

**Query Analysis:**
Extract these from the user's message:
1. Search terms (keywords for TMDB)
2. Mood context (current/desired feeling)
3. Preferences (genre, decade, etc.)

Respond in JSON:
{
    "search_query": "concise TMDB search terms",
    "mood_context": "brief mood summary",
    "response_text": "friendly 2-3 sentence response"
}"""
            },
            {
                "role": "user",
                "content": user_prompt
            }],
            temperature=0.7,
            max_tokens=200
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        plan = json.loads(content)
        return plan
    except Exception as e:
        st.error(f"Mr.DP error: {e}")
        return None

# --------------------------------------------------
# 7. GAMIFICATION FUNCTIONS
# --------------------------------------------------
def get_dp():
    return st.session_state.get("dopamine_points", 0)

def add_dp(amount, reason=""):
    st.session_state.dopamine_points = st.session_state.get("dopamine_points", 0) + amount
    if reason:
        st.toast(f"⚡ +{amount} DP: {reason}", icon="🎉")

def get_streak():
    return st.session_state.get("streak_days", 0)

def update_streak():
    today = datetime.now().strftime("%Y-%m-%d")
    last = st.session_state.get("last_visit_date", "")
    
    if last != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        if last == yesterday:
            st.session_state.streak_days = st.session_state.get("streak_days", 0) + 1
            streak = st.session_state.streak_days
            add_dp(10 * streak, f"{streak} day streak! 🔥")
        else:
            # ADHD-friendly: Allow 1-day grace period (time-blindness support)
            day_before_yesterday = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            if last == day_before_yesterday:
                # Streak freeze! No penalty
                st.toast("🛡️ Streak Freeze Applied - You're Safe!", icon="💎")
            else:
                st.session_state.streak_days = 1
        
        st.session_state.last_visit_date = today

def get_level():
    p = get_dp()
    if p < 100:
        return ("Newbie", 1, 100)
    elif p < 500:
        return ("Explorer", 2, 500)
    elif p < 1500:
        return ("Curator", 3, 1500)
    elif p < 5000:
        return ("Connoisseur", 4, 5000)
    return ("Dopamine Master", 5, 999999)

def get_achievements():
    ach = []
    if get_streak() >= 3:
        ach.append(("🔥", "Hot Streak"))
    if get_streak() >= 7:
        ach.append(("💎", "Week Warrior"))
    if st.session_state.get("quick_hit_count", 0) >= 10:
        ach.append(("⚡", "Quick Draw"))
    if get_dp() >= 100:
        ach.append(("🌟", "Rising Star"))
    if get_dp() >= 1000:
        ach.append(("👑", "Royalty"))
    return ach

# --------------------------------------------------
# 8. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        # Auth
        "user": {"name": "Friend"},  # Auto-login for simplicity
        "auth_step": "lobby",
        "is_premium": False,
        
        # Mood
        "current_feeling": "Bored",
        "desired_feeling": "Entertained",
        "last_emotion_key": None,
        
        # Movies
        "movies_feed": [],
        "movies_page": 1,
        
        # Search
        "search_query": "",
        "search_results": [],
        "search_page": 1,
        
        # Mr.DP
        "mrdp_prompt": "",
        "mrdp_plan": None,
        "mrdp_results": [],
        "mrdp_page": 1,
        "mrdp_last_prompt": "",
        "mrdp_history": [],
        
        # Quick Hit
        "quick_hit": None,
        "quick_hit_count": 0,
        
        # Gamification
        "dopamine_points": 0,
        "streak_days": 0,
        "last_visit_date": "",
        
        # Social
        "referral_code": hashlib.md5(str(random.random()).encode()).hexdigest()[:8].upper(),
        
        # UI
        "active_tab": "movies",
        "show_trailers": True,
        "focus_mode": False,  # ADHD accessibility toggle
    })
    st.session_state.init = True

# Back-compat patch
_DEFAULTS = {
    "mrdp_prompt": "",
    "mrdp_plan": None,
    "mrdp_results": [],
    "mrdp_page": 1,
    "mrdp_last_prompt": "",
    "mrdp_history": [],
    "show_trailers": True,
    "focus_mode": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --------------------------------------------------
# 9. HELPER FUNCTIONS
# --------------------------------------------------
def render_logo(sidebar=False):
    if os.path.exists(LOGO_PATH):
        (st.sidebar if sidebar else st).image(LOGO_PATH, width=180 if sidebar else 260)
    else:
        (st.sidebar if sidebar else st).markdown(f"### 🧠 {APP_NAME}")

def safe(s: str) -> str:
    return html_lib.escape(s or "")

# --------------------------------------------------
# 10. MOVIE CARD RENDERER
# --------------------------------------------------
def render_movie_card(movie):
    """ADHD-optimized movie card with visual clarity"""
    media_type = movie.get("media_type", "movie")
    title = safe(movie.get("title") or movie.get("name", "Unknown"))
    year = (movie.get("release_date") or movie.get("first_air_date", ""))[:4]
    rating = movie.get("vote_average", 0)
    poster = movie.get("poster_path")
    tmdb_id = movie.get("id")
    overview = safe(movie.get("overview", "No description available."))
    
    # Poster
    poster_url = f"{TMDB_IMAGE_URL}{poster}" if poster else "https://via.placeholder.com/300x450?text=No+Image"
    
    # Providers
    providers, tmdb_link = get_movie_providers(tmdb_id, media_type)
    
    # Card HTML
    card_html = f"""
    <div class="movie-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; gap: 1rem;">
            <img src="{poster_url}" 
                 style="width: 120px; height: 180px; object-fit: cover; border-radius: 10px; flex-shrink: 0;">
            <div style="flex: 1;">
                <h3 style="margin: 0 0 0.5rem 0; color: var(--text-primary); font-size: 1.2rem;">
                    {title} {f"({year})" if year else ""}
                </h3>
                <div style="margin-bottom: 0.5rem;">
                    <span style="background: var(--primary); color: #fff; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">
                        ⭐ {rating:.1f}/10
                    </span>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.5; margin: 0.5rem 0;">
                    {overview[:200]}{"..." if len(overview) > 200 else ""}
                </p>
    """
    
    # Providers
    if providers:
        card_html += '<div style="margin-top: 0.75rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">'
        for p in providers:
            logo = p.get("logo_path")
            name = p.get("provider_name", "")
            if logo:
                card_html += f'<img src="{TMDB_LOGO_URL}{logo}" alt="{name}" title="{name}" style="width: 40px; height: 40px; border-radius: 6px; object-fit: contain; background: #fff; padding: 4px;">'
        card_html += '</div>'
    
    if tmdb_link:
        card_html += f'<div style="margin-top: 0.75rem;"><a href="{tmdb_link}" target="_blank" style="color: var(--primary); text-decoration: none; font-weight: 500;">🔗 View Streaming Options</a></div>'
    
    card_html += """
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

# --------------------------------------------------
# 11. MAIN LOBBY SCREEN
# --------------------------------------------------
def lobby_screen():
    # Update streak
    update_streak()
    
    # Apply focus mode CSS if enabled
    if st.session_state.get("focus_mode", False):
        st.markdown('<div class="focus-mode">', unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        render_logo(sidebar=True)
        st.markdown("---")
        
        # Gamification Stats
        level_name, level_num, next_threshold = get_level()
        dp = get_dp()
        streak = get_streak()
        
        st.markdown(f"""
        <div style="background: var(--glass); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--primary);">{dp} DP</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary);">Level {level_num}: {level_name}</div>
                </div>
                <div style="font-size: 2rem;">🔥{streak}</div>
            </div>
            <div style="margin-top: 0.75rem; background: var(--bg-secondary); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, var(--primary), var(--primary-light)); height: 100%; width: {min(100, (dp / next_threshold) * 100)}%; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Achievements
        achievements = get_achievements()
        if achievements:
            st.markdown("**🏆 Achievements**")
            for emoji, name in achievements:
                st.markdown(f"{emoji} {name}")
            st.markdown("---")
        
        # Mood Controls
        st.markdown("### 🎭 How are you feeling?")
        current = st.selectbox(
            "Right now I feel...",
            COMMON_FEELINGS,
            index=COMMON_FEELINGS.index(st.session_state.current_feeling)
        )
        
        desired = st.selectbox(
            "I want to feel...",
            COMMON_FEELINGS,
            index=COMMON_FEELINGS.index(st.session_state.desired_feeling)
        )
        
        if st.button("🎯 Update Mood", use_container_width=True):
            st.session_state.current_feeling = current
            st.session_state.desired_feeling = desired
            st.session_state.movies_feed = []
            st.session_state.movies_page = 1
            st.session_state.last_emotion_key = None
            add_dp(5, "Mood updated!")
            st.rerun()
        
        st.markdown("---")
        
        # Quick Dope Hit
        st.markdown("### ⚡ Quick Dope Hit")
        st.markdown("<p style='font-size: 0.85rem; color: var(--text-secondary);'>Can't decide? We got you.</p>", unsafe_allow_html=True)
        
        if st.button("🎲 Surprise Me!", use_container_width=True):
            results = discover_movies_fresh(
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
            if results:
                st.session_state.quick_hit = random.choice(results)
                st.session_state.quick_hit_count = st.session_state.get("quick_hit_count", 0) + 1
                add_dp(15, "Quick Hit! 🎯")
                st.rerun()
        
        st.markdown("---")
        
        # Accessibility
        st.markdown("### ♿ Accessibility")
        focus = st.checkbox("Focus Mode", value=st.session_state.get("focus_mode", False))
        if focus != st.session_state.get("focus_mode", False):
            st.session_state.focus_mode = focus
            st.rerun()
        
        trailers = st.checkbox("Show Trailers", value=st.session_state.get("show_trailers", True))
        if trailers != st.session_state.get("show_trailers", True):
            st.session_state.show_trailers = trailers
            st.rerun()
    
    # MAIN AREA
    st.markdown(f"## Hey {st.session_state.user.get('name', 'Friend')}! 👋")
    st.markdown(f"<p style='font-size: 1.1rem; color: var(--text-secondary);'>Feeling <strong style='color: var(--primary);'>{st.session_state.current_feeling}</strong> → Want to feel <strong style='color: var(--secondary);'>{st.session_state.desired_feeling}</strong></p>", unsafe_allow_html=True)
    
    # Quick Hit Display
    if st.session_state.get("quick_hit"):
        st.markdown("### ⚡ Your Quick Dope Hit")
        render_movie_card(st.session_state.quick_hit)
        if st.button("✨ Another One!", key="another_quick_hit"):
            results = discover_movies_fresh(
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
            if results:
                st.session_state.quick_hit = random.choice(results)
                add_dp(15, "Quick Hit! 🎯")
                st.rerun()
        st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎬 Movies", "🔍 Search", "💬 Mr.DP Chat"])
    
    with tab1:
        # Load movies if needed
        emotion_key = f"{st.session_state.current_feeling}_{st.session_state.desired_feeling}"
        if not st.session_state.movies_feed or st.session_state.last_emotion_key != emotion_key:
            with st.spinner("Finding your vibe..."):
                st.session_state.movies_feed = discover_movies(
                    current_feeling=st.session_state.current_feeling,
                    desired_feeling=st.session_state.desired_feeling,
                    page=1
                )
                st.session_state.movies_page = 1
                st.session_state.last_emotion_key = emotion_key
        
        # Display
        if st.session_state.movies_feed:
            for movie in st.session_state.movies_feed:
                render_movie_card(movie)
            
            # Load More
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Load More", use_container_width=True):
                    st.session_state.movies_page += 1
                    more = discover_movies(
                        current_feeling=st.session_state.current_feeling,
                        desired_feeling=st.session_state.desired_feeling,
                        page=st.session_state.movies_page
                    )
                    st.session_state.movies_feed.extend(more)
                    add_dp(3, "Exploring more!")
                    st.rerun()
        else:
            st.info("🤔 No movies found for this mood combo. Try adjusting your feelings!")
    
    with tab2:
        st.markdown("### 🔍 Search Movies & Shows")
        query = st.text_input("Search for...", value=st.session_state.search_query, placeholder="e.g., Inception, Breaking Bad, Marvel")
        
        if st.button("Search", type="primary", use_container_width=True) and query:
            st.session_state.search_query = query
            st.session_state.search_results = search_movies(query, page=1)
            st.session_state.search_page = 1
            add_dp(5, "Searching!")
            st.rerun()
        
        if st.session_state.search_results:
            for movie in st.session_state.search_results:
                render_movie_card(movie)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Load More Results", use_container_width=True, key="search_more"):
                    st.session_state.search_page += 1
                    more = search_movies(st.session_state.search_query, page=st.session_state.search_page)
                    st.session_state.search_results.extend(more)
                    st.rerun()
    
    with tab3:
        st.markdown("### 💬 Chat with Mr.DP")
        st.markdown("<p style='font-size: 0.95rem; color: var(--text-secondary);'>Your ADHD-friendly AI assistant. Just type what you're in the mood for!</p>", unsafe_allow_html=True)
        
        # Chat history
        for msg in st.session_state.mrdp_history:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.markdown(f"**You:** {content}")
            else:
                st.markdown(f"**Mr.DP:** {content}")
        
        # Input
        user_input = st.text_area(
            "Ask Mr.DP anything...",
            placeholder="e.g., I'm feeling overwhelmed, need something light and funny",
            height=100,
            key="mrdp_input"
        )
        
        if st.button("Send to Mr.DP", type="primary", use_container_width=True) and user_input:
            if user_input != st.session_state.mrdp_last_prompt:
                st.session_state.mrdp_last_prompt = user_input
                st.session_state.mrdp_history.append({"role": "user", "content": user_input})
                
                with st.spinner("Mr.DP is thinking..."):
                    plan = mrdp_plan_query(user_input)
                    
                    if plan:
                        response_text = plan.get("response_text", "Got it! Let me find something for you.")
                        search_query = plan.get("search_query", "")
                        
                        st.session_state.mrdp_history.append({"role": "assistant", "content": response_text})
                        
                        if search_query:
                            results = search_movies(search_query, page=1)
                            st.session_state.mrdp_results = results
                            st.session_state.mrdp_page = 1
                        
                        add_dp(10, "Chatted with Mr.DP!")
                        st.rerun()
        
        # Results
        if st.session_state.mrdp_results:
            st.markdown("---")
            st.markdown("### 🎬 Mr.DP's Recommendations")
            for movie in st.session_state.mrdp_results:
                render_movie_card(movie)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("More from Mr.DP", use_container_width=True, key="mrdp_more"):
                    st.session_state.mrdp_page += 1
                    more = search_movies(st.session_state.mrdp_last_prompt, page=st.session_state.mrdp_page)
                    st.session_state.mrdp_results.extend(more)
                    st.rerun()
    
    if st.session_state.get("focus_mode", False):
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 12. MAIN APP FLOW
# --------------------------------------------------
def main():
    lobby_screen()

if __name__ == "__main__":
    main()