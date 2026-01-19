# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v29.0 - COMPLETE EDITION
# ALL conversation fixes + NLP + NO REFACTORING
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

# --------------------------------------------------
# 1. CONFIG & ASSETS
# --------------------------------------------------
if not hasattr(st, "_page_config_set"):
    st.set_page_config(page_title="Dopamine.watch", page_icon="🧠", layout="wide")
    st._page_config_set = True

APP_NAME = "Dopamine.watch"
LOGO_PATH = "logo.gif" if os.path.exists("logo.gif") else "logo.png"

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"

# Media Assets
VIDEO_URL = "https://youtu.be/-6WCkTeG3Cs"
SPOTIFY_PLAYLIST_ID = "37i9dQZF1DX4sWSpwq3LiO"

# --------------------------------------------------
# 2. MASTER SERVICE MAP (KEEP ORIGINAL - NO REFACTOR)
# --------------------------------------------------
SERVICE_MAP = {
    # --- SUBSCRIPTION ---
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Amazon Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Disney Plus": "https://www.disneyplus.com/search",
    "Max": "https://play.max.com/search",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "Peacock": "https://www.peacocktv.com/search?q={title}",
    "Paramount Plus": "https://www.paramountplus.com/search/",
    "Apple TV Plus": "https://tv.apple.com/search?term={title}",
    "Starz": "https://www.starz.com/us/en/search?q={title}",
    "Showtime": "https://www.showtime.com/search?q={title}",
    "MGM+": "https://www.mgmplus.com/search?q={title}",
    "Criterion Channel": "https://www.criterionchannel.com/search?q={title}",
    "MUBI": "https://mubi.com/en/search/films?query={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",

    # --- FREE / AD-SUPPORTED ---
    "Tubi": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details?query={title}",
    "Freevee": "https://www.amazon.com/s?k={title}&i=instant-video",
    "The Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Plex": "https://app.plex.tv/desktop/#!/search?query={title}",
    "Crackle": "https://www.crackle.com/search/{title}",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Kanopy": "https://www.kanopy.com/en/search?q={title}",
    "Hoopla": "https://www.hoopladigital.com/search?q={title}",

    # --- ANIME ---
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Funimation": "https://www.funimation.com/search/?q={title}",
    "HIDIVE": "https://www.hidive.com/search?q={title}",
    "RetroCrush": "https://www.retrocrush.tv/search?q={title}",

    # --- AUDIO / MUSIC ---
    "Spotify": "https://open.spotify.com/search/{title}",
    "Apple Music": "https://music.apple.com/us/search?term={title}",
    "Audible": "https://www.audible.com/search?keywords={title}",
    "SoundCloud": "https://soundcloud.com/search?q={title}",
}

LOGOS = {
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg"
}

# --------------------------------------------------
# 3. API CLIENTS
# --------------------------------------------------
@st.cache_data
def get_tmdb_key():
    try:
        return st.secrets["tmdb"]["api_key"]
    except:
        st.error("⚠️ TMDB API key not found!")
        return None

try:
    openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])
except Exception:
    openai_client = None

# --------------------------------------------------
# 4. EMOTION → GENRE MAPPING (THE CORE INTELLIGENCE)
# --------------------------------------------------
FEELING_TO_GENRES = {
    # CURRENT FEELINGS (what to avoid/what helps)
    "Sad": {
        "avoid": [18, 10752],  # Drama, War
        "prefer": [35, 10751, 16]  # Comedy, Family, Animation
    },
    "Lonely": {
        "prefer": [10749, 35, 18]  # Romance, Comedy, Drama
    },
    "Anxious": {
        "avoid": [27, 53],  # Horror, Thriller
        "prefer": [35, 16, 10751, 99]  # Comedy, Animation, Family, Documentary
    },
    "Overwhelmed": {
        "avoid": [28, 53, 27],  # Action, Thriller, Horror
        "prefer": [99, 10402, 16]  # Documentary, Music, Animation
    },
    "Angry": {
        "prefer": [28, 53, 80]  # Action, Thriller, Crime (cathartic)
    },
    "Stressed": {
        "avoid": [53, 27],  # Thriller, Horror
        "prefer": [35, 16, 10751]  # Comedy, Animation, Family
    },
    "Bored": {
        "prefer": [12, 878, 14, 28]  # Adventure, Sci-Fi, Fantasy, Action
    },
    "Tired": {
        "prefer": [35, 10749, 16]  # Comedy, Romance, Animation
    },
    "Numb": {
        "prefer": [28, 12, 53]  # Action, Adventure, Thriller (stimulating)
    },
    "Confused": {
        "prefer": [99, 36]  # Documentary, History
    },
    "Restless": {
        "prefer": [28, 12, 878]  # Action, Adventure, Sci-Fi
    },
    "Focused": {
        "prefer": [99, 9648, 36]  # Documentary, Mystery, History
    },
    "Calm": {
        "prefer": [99, 10402, 36]  # Documentary, Music, History
    },
    "Happy": {
        "prefer": [35, 10751, 12]  # Comedy, Family, Adventure
    },
    "Excited": {
        "prefer": [28, 12, 878]  # Action, Adventure, Sci-Fi
    },
    "Curious": {
        "prefer": [99, 878, 9648, 14]  # Documentary, Sci-Fi, Mystery, Fantasy
    },
    
    # DESIRED FEELINGS
    "Comforted": {
        "prefer": [10751, 16, 35, 10749]  # Family, Animation, Comedy, Romance
    },
    "Relaxed": {
        "prefer": [10749, 35, 99]  # Romance, Comedy, Documentary
    },
    "Energized": {
        "prefer": [28, 12, 878]  # Action, Adventure, Sci-Fi
    },
    "Stimulated": {
        "prefer": [878, 14, 53, 9648]  # Sci-Fi, Fantasy, Thriller, Mystery
    },
    "Entertained": {
        "prefer": [12, 28, 35, 14]  # Adventure, Action, Comedy, Fantasy
    },
    "Inspired": {
        "prefer": [18, 36, 99, 10752]  # Drama, History, Documentary, War
    },
    "Grounded": {
        "prefer": [99, 36, 10751]  # Documentary, History, Family
    },
    "Sleepy": {
        "prefer": [16, 10751, 10749]  # Animation, Family, Romance
    },
    "Connected": {
        "prefer": [10749, 18, 10751]  # Romance, Drama, Family
    },
}

# --------------------------------------------------
# 5. EMOTION → MUSIC MOODS (for Spotify)
# --------------------------------------------------
FEELING_TO_MUSIC = {
    "Sad": "sad piano",
    "Lonely": "comfort songs",
    "Anxious": "calm relaxing",
    "Overwhelmed": "peaceful ambient",
    "Angry": "heavy metal workout",
    "Stressed": "meditation spa",
    "Bored": "upbeat pop",
    "Tired": "acoustic chill",
    "Numb": "intense electronic",
    "Confused": "lo-fi study",
    "Restless": "high energy dance",
    "Focused": "deep focus",
    "Calm": "nature sounds",
    "Happy": "feel good hits",
    "Excited": "party anthems",
    "Curious": "experimental indie",
    
    "Comforted": "warm acoustic",
    "Relaxed": "sunday morning",
    "Energized": "workout motivation",
    "Stimulated": "electronic bass",
    "Entertained": "viral hits",
    "Inspired": "epic orchestral",
    "Grounded": "folk roots",
    "Sleepy": "sleep sounds",
    "Connected": "love songs",
}

# --------------------------------------------------
# 6. EMOTION → VIDEO KEYWORDS (for Shot tab)
# --------------------------------------------------
FEELING_TO_VIDEOS = {
    "Sad": "wholesome animals",
    "Lonely": "heartwarming stories",
    "Anxious": "satisfying oddly",
    "Overwhelmed": "calming nature",
    "Angry": "epic fails funny",
    "Stressed": "meditation guided",
    "Bored": "mind blowing facts",
    "Tired": "asmr relaxing",
    "Numb": "extreme sports",
    "Confused": "explained simply",
    "Restless": "action parkour",
    "Focused": "productivity hacks",
    "Calm": "ocean waves",
    "Happy": "funny moments",
    "Excited": "epic moments",
    "Curious": "science experiments",
    
    "Comforted": "cozy vibes",
    "Relaxed": "coffee shop",
    "Energized": "hype motivation",
    "Stimulated": "wtf moments",
    "Entertained": "viral comedy",
    "Inspired": "success stories",
    "Grounded": "minimalist living",
    "Sleepy": "rain sounds",
    "Connected": "friendship goals",
}

# --------------------------------------------------
# 7. DATA ENGINE - MOVIES ONLY (NO YOUTUBE/GOOGLE)
# --------------------------------------------------
def _clean_results(results):
    """Clean and validate movie/TV results only"""
    clean = []
    for item in results:
        # STRICT FILTER: Only actual movies/TV from TMDB
        if item.get("media_type") not in ["movie", "tv"]:
            continue
        
        # Must have title and poster
        title = item.get("title") or item.get("name")
        if not title or not item.get("poster_path"):
            continue
            
        clean.append({
            "id": item.get("id"),
            "type": item.get("media_type", "movie"),
            "title": title,
            "overview": item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "release_date": item.get("release_date") or item.get("first_air_date") or "Unknown"
        })
    return clean

@st.cache_data(ttl=3600)
def search_global(query, page=1):
    """Search for movies/TV only - NO YOUTUBE OR GOOGLE"""
    api_key = get_tmdb_key()
    if not query or not api_key:
        return []
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/search/multi",
            params={"api_key": api_key, "query": query, "include_adult": "false", "page": page},
            timeout=8
        )
        r.raise_for_status()
        # Filter to only movies/TV
        results = [item for item in r.json().get("results", []) 
                   if item.get("media_type") in ["movie", "tv"]]
        return _clean_results(results)
    except Exception:
        return []

@st.cache_data(ttl=3600)
def discover_movies(page=1, sort_by="popularity.desc", current_feeling=None, desired_feeling=None):
    """Discover movies filtered by emotional state"""
    api_key = get_tmdb_key()
    if not api_key:
        return []
    
    # Build genre preferences
    genre_ids = []
    avoid_genres = []
    
    # Add desired feeling preferences first (highest priority)
    if desired_feeling and desired_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[desired_feeling]
        if "prefer" in prefs:
            genre_ids.extend(prefs["prefer"][:3])
        if "avoid" in prefs:
            avoid_genres.extend(prefs["avoid"])
    
    # Add current feeling considerations
    if current_feeling and current_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[current_feeling]
        if "avoid" in prefs:
            avoid_genres.extend(prefs["avoid"])
        if "prefer" in prefs and len(genre_ids) < 3:
            genre_ids.extend([g for g in prefs["prefer"] if g not in genre_ids][:3-len(genre_ids)])
    
    try:
        params = {
            "api_key": api_key,
            "sort_by": sort_by,
            "watch_region": "US",
            "with_watch_monetization_types": "flatrate|rent",
            "page": page,
            "include_adult": "false"
        }
        
        # Add genre filtering
        if genre_ids:
            params["with_genres"] = "|".join(map(str, list(set(genre_ids))[:3]))
        
        if avoid_genres:
            params["without_genres"] = ",".join(map(str, list(set(avoid_genres))))
        
        r = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            params=params,
            timeout=10
        )
        r.raise_for_status()
        results = _clean_results(r.json().get("results", []))
        
        # FALLBACK: If no results, try without genre filtering
        if not results:
            params.pop("with_genres", None)
            params.pop("without_genres", None)
            r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=10)
            r.raise_for_status()
            results = _clean_results(r.json().get("results", []))
        
        return results
    except Exception as e:
        st.error(f"TMDB Error: {e}")
        return []

@st.cache_data(ttl=86400)
def get_streaming_providers(tmdb_id, media_type):
    """Get streaming providers for a title"""
    api_key = get_tmdb_key()
    if not api_key:
        return {"flatrate": [], "rent": []}
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
            params={"api_key": api_key},
            timeout=8
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return {
            "flatrate": data.get("flatrate", [])[:8],  # Max 8 providers for clean grid
            "rent": data.get("rent", [])[:8]
        }
    except Exception:
        return {"flatrate": [], "rent": []}

# --------------------------------------------------
# 8. AI ENGINE - EMOTION-DRIVEN SORTING
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def sort_feed_by_mood(titles, mood):
    """Use OpenAI to sort content by emotional match"""
    if not titles or not openai_client:
        return titles
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Sort these titles by dopamine preference.\nMood: {mood}\nTitles: {json.dumps(titles)}\nReturn ONLY a JSON array."
            }],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception:
        return titles

# --------------------------------------------------
# 9. NEW: NLP CONVERSATIONAL AI ENGINE
# --------------------------------------------------
def process_natural_language_feeling(user_text):
    """Extract feelings from natural language using OpenAI"""
    if not openai_client:
        return None, None
    
    try:
        prompt = f"""User says: "{user_text}"

Extract EXACTLY TWO feelings:
1. Current feeling (how they feel NOW)
2. Desired feeling (how they WANT to feel)

Available feelings:
Current: Sad, Lonely, Anxious, Overwhelmed, Angry, Stressed, Bored, Tired, Numb, Confused, Restless, Focused, Calm, Happy, Excited, Curious
Desired: Comforted, Calm, Relaxed, Focused, Energized, Stimulated, Happy, Entertained, Inspired, Grounded, Curious, Sleepy, Connected

Return ONLY this format:
CURRENT: [feeling]
DESIRED: [feeling]"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        lines = content.split("\n")
        
        current = None
        desired = None
        
        for line in lines:
            if "CURRENT:" in line:
                current = line.split("CURRENT:")[1].strip()
            elif "DESIRED:" in line:
                desired = line.split("DESIRED:")[1].strip()
        
        return current, desired
    except Exception as e:
        st.error(f"NLP Error: {e}")
        return None, None

def ai_conversation_response(user_message, current_feeling, desired_feeling):
    """Generate conversational AI response about feelings and recommendations"""
    if not openai_client:
        return "I'm here to help! Try describing how you feel and what you want to watch."
    
    try:
        prompt = f"""You are a dopamine-optimization coach for neurodivergent users.

User feels: {current_feeling}
User wants to feel: {desired_feeling}
User said: "{user_message}"

Respond warmly and helpfully in 2-3 sentences. Suggest content types that match their emotional transition. Be encouraging and understanding."""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
    except Exception:
        return "I hear you. Let me find something perfect for that vibe."

# --------------------------------------------------
# 10. DEEP LINK BUILDER (ACTUALLY WORKS)
# --------------------------------------------------
def get_deep_link(provider, title):
    """Build working deep link to streaming service"""
    key = (provider or "").strip()
    template = SERVICE_MAP.get(key)

    if not template:
        for k, v in SERVICE_MAP.items():
            if k in key or key in k:
                template = v
                break

    if not template:
        return f"https://www.google.com/search?q=watch+{quote_plus(title)}+on+{quote_plus(provider)}"

    return template.format(title=quote_plus(title))

# --------------------------------------------------
# 11. HELPERS
# --------------------------------------------------
def render_logo(sidebar=False):
    if os.path.exists(LOGO_PATH):
        (st.sidebar if sidebar else st).image(LOGO_PATH, width=180 if sidebar else 260)
    else:
        (st.sidebar if sidebar else st).markdown(f"# 🧠 {APP_NAME}")

def safe(s: str) -> str:
    return html_lib.escape(s or "")

# --------------------------------------------------
# 12. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "user": None,
        "auth_step": "login",
        "onboarding_complete": False,
        "sorted_feed": None,
        "last_mood": None,

        "current_feeling": None,
        "desired_feeling": None,

        "search_page": 1,
        "last_search": "",
        "search_results": [],

        "discover_page": 1,
        "feed": [],
        
        "quick_hit": None,
        "quick_hit_count": 0,
        
        # NEW: NLP chat mode
        "nlp_mode": False,
        "chat_history": [],
    })
    st.session_state.init = True

# --------------------------------------------------
# 13. CUSTOM CSS - CLEAN, DOPAMINE-OPTIMIZED
# --------------------------------------------------
st.markdown("""
<style>
/* Dark gradient background */
.stApp {
    background: radial-gradient(circle at top, #0b0b0b, #000000);
    color: white;
}

/* Movie card */
.card {
    background: #141414;
    border: 1px solid #333;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 20px;
    padding-bottom: 10px;
}

/* Provider grid - CLEAN 2x4 LAYOUT */
.provider-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 6px;
    padding: 8px 10px 0 10px;
}

.provider-grid.rent {
    opacity: 0.65;
}

/* Provider button */
.provider-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #1e1e1e;
    padding: 6px;
    border-radius: 8px;
    text-decoration: none !important;
    border: 1px solid #333;
}

.provider-btn:hover {
    border-color: #00f2ea;
}

.provider-icon {
    width: 22px;
    height: 22px;
    object-fit: contain;
}

/* Movie title */
.movie-title {
    padding: 0 10px;
    margin-top: 6px;
    font-weight: 700;
    font-size: 0.95rem;
}

.movie-sub {
    padding: 0 10px;
    opacity: 0.75;
    font-size: 0.8rem;
}

/* Buttons - GRADIENT DOPAMINE */
button {
    background: linear-gradient(90deg,#00f2ea,#a100f2) !important;
    color: black !important;
    font-weight: 800 !important;
    border: none !important;
}

/* Small text */
.small-note {
    opacity: 0.75;
    font-size: 0.85rem;
}

/* NEW: Chat bubbles for NLP mode */
.chat-bubble {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 3px solid #00f2ea;
}

.ai-response {
    background: #2a1a3e;
    border-left-color: #a100f2;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 14. MOVIE CARD COMPONENT (CLEAN 2x4 GRID)
# --------------------------------------------------
def render_movie_card(item):
    """Render movie card with clean provider grid"""
    title = item.get("title", "")
    media_type = item.get("type", "movie")
    tmdb_id = item.get("id")

    provs = get_streaming_providers(tmdb_id, media_type)
    flatrate = provs.get("flatrate", [])[:12]
    rent = provs.get("rent", [])[:12]

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if item.get("poster"):
        st.image(item["poster"], use_container_width=True)
    else:
        st.markdown("🎬 **No Poster**")

    # INCLUDED providers (2x4 grid)
    if flatrate:
        st.markdown("<div class='provider-grid'>", unsafe_allow_html=True)
        for p in flatrate:
            provider = p.get("provider_name", "")
            logo_path = p.get("logo_path", "")
            if not logo_path:
                continue
            link = get_deep_link(provider, title)
            logo = f"{TMDB_LOGO_URL}{logo_path}"
            st.markdown(
                f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='{safe(provider)} (Included)'>"
                f"<img src='{safe(logo)}' class='provider-icon'></a>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # RENT providers (dimmed, 2x4 grid)
    if rent:
        st.markdown("<div class='provider-grid rent'>", unsafe_allow_html=True)
        for p in rent:
            provider = p.get("provider_name", "")
            logo_path = p.get("logo_path", "")
            if not logo_path:
                continue
            link = get_deep_link(provider, title)
            logo = f"{TMDB_LOGO_URL}{logo_path}"
            st.markdown(
                f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='{safe(provider)} (Rent/Buy)'>"
                f"<img src='{safe(logo)}' class='provider-icon'></a>",
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Trailer button
    yt = get_deep_link("YouTube", title)
    st.markdown(
        f"<div style='padding:8px 10px 0 10px'>"
        f"<a href='{safe(yt)}' target='_blank' class='provider-btn' title='Trailer'>"
        f"<img src='{safe(LOGOS['YouTube'])}' class='provider-icon'></a>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown(f"<div class='movie-title'>{safe(title)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='movie-sub'>{safe(item.get('release_date',''))}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 15. QUICK DOPE HIT ENGINE
# --------------------------------------------------
def get_quick_dope_hit():
    """Get ONE perfect match based on emotions"""
    current = st.session_state.current_feeling
    desired = st.session_state.desired_feeling
    
    # Get emotion-filtered movies
    candidates = discover_movies(
        page=random.randint(1, 3),
        current_feeling=current,
        desired_feeling=desired
    )
    
    if not candidates:
        return None
    
    # Use AI to pick the BEST match if available
    if openai_client and len(candidates) > 5:
        titles = [m["title"] for m in candidates[:10]]
        sorted_titles = sort_feed_by_mood(titles, f"{current} → {desired}")
        
        # Return the top match
        for title in sorted_titles[:1]:
            match = next((m for m in candidates if m["title"] == title), None)
            if match:
                return match
    
    # Fallback: return top result
    return candidates[0]

# --------------------------------------------------
# 16. AUTH SCREENS
# --------------------------------------------------
def login_screen():
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        st.markdown("<div class='card' style='padding:20px'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Welcome back")
        e = st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            st.session_state.user = e
            st.rerun()
        st.markdown("---")
        if st.button("Create Account", use_container_width=True):
            st.session_state.auth_step = "signup"
            st.rerun()
        if st.button("Guest Mode", use_container_width=True):
            st.session_state.user = "guest"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def signup_screen():
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        st.markdown("<div class='card' style='padding:20px'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Create ID")
        st.text_input("Username")
        e = st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Sign Up", use_container_width=True):
            st.session_state.user = e
            st.rerun()
        if st.button("Back", use_container_width=True):
            st.session_state.auth_step = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def onboarding_baseline():
    st.markdown("## 🧠 Let's calibrate your brain")
    st.caption("This helps us filter content for you.")
    triggers = st.multiselect("What overwhelms you?", ["Loud sounds", "Flashing lights", "Fast cuts", "Emotional intensity"])
    genres = st.multiselect("What do you enjoy?", ["Action", "Anime", "Sci-Fi", "Comedy", "Documentary", "Fantasy", "Drama"])
    decision = st.radio("When choosing content:", ["Decide for me", "Give me 3 options", "Let me explore freely"])

    if st.button("Save & Continue", use_container_width=True):
        st.session_state.baseline_prefs = {
            "triggers": triggers,
            "genres": genres,
            "decision_style": decision
        }
        st.session_state.onboarding_complete = True
        st.rerun()

# --------------------------------------------------
# 17. MAIN LOBBY - EMOTION-DRIVEN EVERYTHING + NLP
# --------------------------------------------------
def lobby_screen():
    # SIDEBAR
    with st.sidebar:
        render_logo(sidebar=True)
        st.markdown("### 🎛️ Control")
        mood = st.radio("Vibe Check", ["Focus", "Regulate", "Stimulate"])
        st.markdown("---")
        st.markdown("### ⚡ Stats")
        st.metric("Dope Hits", st.session_state.quick_hit_count)
        st.markdown("---")
        if st.button("Log out"):
            st.session_state.user = None
            st.rerun()

    st.markdown("## 🔎 The Lobby")

    # NEW: NLP MODE TOGGLE
    col_toggle = st.columns([1, 1])
    with col_toggle[0]:
        if st.button("💬 Talk to AI" if not st.session_state.nlp_mode else "🎯 Use Selectors", use_container_width=True):
            st.session_state.nlp_mode = not st.session_state.nlp_mode
            st.rerun()

    st.markdown("---")

    # FEELINGS SELECTOR OR NLP CHAT
    if st.session_state.nlp_mode:
        # NLP CONVERSATION MODE
        st.markdown("### 💬 Tell me how you feel")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-bubble'>👤 {safe(msg['content'])}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble ai-response'>🤖 {safe(msg['content'])}</div>", unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Type how you feel and what you want...", 
                                   placeholder="I'm feeling stressed and want something relaxing",
                                   key="nlp_input")
        
        if user_input:
            # Add to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Extract feelings
            current, desired = process_natural_language_feeling(user_input)
            
            if current and desired:
                st.session_state.current_feeling = current
                st.session_state.desired_feeling = desired
                
                # Generate AI response
                ai_response = ai_conversation_response(user_input, current, desired)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
                st.rerun()
            else:
                response = "I understand! Let me help you find something. Could you tell me a bit more about your mood?"
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    else:
        # ORIGINAL FEELINGS SELECTORS (COMPACT)
        FEELINGS = [
            ("🌧️", "Sad"),
            ("🥺", "Lonely"),
            ("😰", "Anxious"),
            ("😵‍💫", "Overwhelmed"),
            ("😡", "Angry"),
            ("😫", "Stressed"),
            ("😐", "Bored"),
            ("😴", "Tired"),
            ("🫥", "Numb"),
            ("🤔", "Confused"),
            ("😬", "Restless"),
            ("🎯", "Focused"),
            ("😌", "Calm"),
            ("😊", "Happy"),
            ("⚡", "Excited"),
            ("🧐", "Curious"),
        ]

        DESIRED_FEELINGS = [
            ("🫶", "Comforted"),
            ("🌊", "Calm"),
            ("🛋️", "Relaxed"),
            ("🎯", "Focused"),
            ("🔥", "Energized"),
            ("🚀", "Stimulated"),
            ("🌞", "Happy"),
            ("🍿", "Entertained"),
            ("✨", "Inspired"),
            ("🌱", "Grounded"),
            ("🔍", "Curious"),
            ("🌙", "Sleepy"),
            ("❤️", "Connected"),
        ]

        left, right = st.columns(2)
        with left:
            st.markdown("### How do you feel right now?")
            current_choice = st.selectbox(
                "Current feeling",
                options=[f"{e} {t}" for e, t in FEELINGS],
                index=0 if not st.session_state.current_feeling else
                      next((i for i, (_, t) in enumerate(FEELINGS) if t == st.session_state.current_feeling), 0),
                label_visibility="collapsed"
            )
            st.session_state.current_feeling = current_choice.split(" ", 1)[1]

        with right:
            st.markdown("### What do you want to feel instead?")
            desired_choice = st.selectbox(
                "Desired feeling",
                options=[f"{e} {t}" for e, t in DESIRED_FEELINGS],
                index=0 if not st.session_state.desired_feeling else
                      next((i for i, (_, t) in enumerate(DESIRED_FEELINGS) if t == st.session_state.desired_feeling), 0),
                label_visibility="collapsed"
            )
            st.session_state.desired_feeling = desired_choice.split(" ", 1)[1]

        st.markdown(
            f"<div class='small-note'>Current: <b>{safe(st.session_state.current_feeling)}</b> &nbsp;&nbsp;→&nbsp;&nbsp; "
            f"Desired: <b>{safe(st.session_state.desired_feeling)}</b></div>",
            unsafe_allow_html=True
        )
        
        # CLEAR FEELINGS BUTTON
        if st.button("🔄 Reset Feelings", use_container_width=True):
            st.session_state.current_feeling = None
            st.session_state.desired_feeling = None
            st.rerun()

    st.markdown("---")

    # QUICK DOPE HIT - THE VIRAL BUTTON
    st.markdown("## ⚡ Need instant dopamine?")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 GIVE ME A QUICK DOPE HIT", use_container_width=True, key="dope_btn"):
            with st.spinner("Finding your perfect match..."):
                st.session_state.quick_hit = get_quick_dope_hit()
                st.session_state.quick_hit_count += 1
                st.rerun()
    
    # Show quick hit result
    if st.session_state.quick_hit:
        st.markdown("### 🎬 Your Perfect Match:")
        cols = st.columns([1, 2, 1])
        with cols[1]:
            render_movie_card(st.session_state.quick_hit)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Give me another hit", use_container_width=True):
                st.session_state.quick_hit = get_quick_dope_hit()
                st.session_state.quick_hit_count += 1
                st.rerun()
        with col_b:
            if st.button("👀 Show me more options", use_container_width=True):
                st.session_state.quick_hit = None
                st.rerun()
    
    st.markdown("---")

    # SEARCH BAR (PAGINATED)
    query = st.text_input("Search for content...", placeholder="Movies, TV, Anime...")

    if st.button("Clear Search", use_container_width=True):
        st.session_state.search_page = 1
        st.session_state.last_search = ""
        st.session_state.search_results = []
        st.rerun()

    if query:
        if query != st.session_state.last_search:
            st.session_state.search_page = 1
            st.session_state.search_results = []
            st.session_state.last_search = query

        results = search_global(query, page=st.session_state.search_page)
        if results:
            st.session_state.search_results.extend(results)

        st.markdown("### Results")
        if not st.session_state.search_results:
            st.warning("No results found.")
        else:
            cols = st.columns(6)
            for i, item in enumerate(st.session_state.search_results):
                with cols[i % 6]:
                    render_movie_card(item)

            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("Load more results", use_container_width=True):
                    st.session_state.search_page += 1
                    st.rerun()
            with col_b:
                st.caption(f"Page {st.session_state.search_page}")

        return

    # TABS (MOVIES + SHORT + MUSIC + PODCASTS + AUDIOBOOKS)
    st.markdown(f"### 🔥 Trending for *{mood}*")

    t1, t2, t3, t4, t5 = st.tabs(["🎬 Movies", "⚡ Shot", "🎵 Music", "🎙️ Podcasts", "📚 Audiobooks"])

    with t1:
        if not st.session_state.feed:
            st.session_state.discover_page = 1
            st.session_state.feed = discover_movies(
                page=1,
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )

        # apply AI vibe ordering only to the first batch (prototype behavior)
        if st.session_state.sorted_feed is None or st.session_state.last_mood != mood:
            feed = st.session_state.feed
            titles = [m["title"] for m in feed[:18]]
            sorted_titles = sort_feed_by_mood(titles, mood)
            feed_map = {m["title"]: m for m in feed}
            ordered = []
            seen = set()

            for t in sorted_titles:
                if t in feed_map and t not in seen:
                    ordered.append(feed_map[t])
                    seen.add(t)

            for m in feed:
                if m["title"] not in seen:
                    ordered.append(m)
                    seen.add(m["title"])

            st.session_state.sorted_feed = ordered
            st.session_state.last_mood = mood

        cols = st.columns(6)
        for i, item in enumerate(st.session_state.sorted_feed[:18]):
            with cols[i % 6]:
                render_movie_card(item)

        if st.button("Load More Movies", use_container_width=True):
            st.session_state.discover_page += 1
            more = discover_movies(
                page=st.session_state.discover_page,
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
            st.session_state.feed.extend(more)
            # keep stable: just append without re-sorting
            st.session_state.sorted_feed.extend([m for m in more if m not in st.session_state.sorted_feed])
            st.rerun()

    with t2:
        st.video(VIDEO_URL)

    with t3:
        components.iframe(
            f"https://open.spotify.com/embed/playlist/{SPOTIFY_PLAYLIST_ID}?utm_source=generator",
            height=380
        )

    with t4:
        st.markdown("### 🎙️ Podcasts (coming next)")
        st.caption("This tab is scaffolded. Next step: wire a podcast search/provider map.")

    with t5:
        st.markdown("### 📚 Audiobooks (coming next)")
        st.caption("This tab is scaffolded. Next step: wire Audible/Libby/Hoopla deep links + icons.")

# --------------------------------------------------
# 18. MAIN ROUTER
# --------------------------------------------------
if not st.session_state.user:
    if st.session_state.auth_step == "signup":
        signup_screen()
    else:
        login_screen()
    st.stop()

if not st.session_state.onboarding_complete:
    onboarding_baseline()
    st.stop()

lobby_screen()
