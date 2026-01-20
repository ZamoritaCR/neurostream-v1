# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v31.0 - ULTIMATE VIRAL EDITION 🚀
# Combines: Viral UI + Sidebar Controls + Mr.DP NLP
# --------------------------------------------------
# FEATURES:
# ✅ Glassmorphism UI with animations
# ✅ Sidebar emotion selectors (real-time feed updates)
# ✅ Mr.DP NLP search ("smart sci-fi", "I'm bored")
# ✅ Dopamine Points + Streaks + Levels
# ✅ Shareable mood cards
# ✅ Premium tier ready
# ✅ Referral system
# ✅ Achievement badges
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

# --------------------------------------------------
# 1. CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Dopamine.watch | Feel Better, Watch Better",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "Dopamine.watch"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_URL = "https://image.tmdb.org/t/p/original"
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
    "Starz": "https://www.starz.com/search?q={title}",
    "MGM Plus": "https://www.mgmplus.com/search?q={title}",
    "Tubi": "https://tubitv.com/search/{title}",
    "Tubi TV": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details/{title}",
    "Plex": "https://watch.plex.tv/search?q={title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",
    "MUBI": "https://mubi.com/search?query={title}",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Fandango At Home": "https://www.vudu.com/content/movies/search?searchString={title}",
    "The Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Criterion Channel": "https://www.criterionchannel.com/search?q={title}",
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
            "id": item.get("id"),
            "type": media_type,
            "title": title,
            "overview": item.get("overview", "")[:150] + "..." if len(item.get("overview", "")) > 150 else item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "backdrop": f"{TMDB_BACKDROP_URL}{item.get('backdrop_path', '')}" if item.get('backdrop_path') else None,
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
def get_providers(tmdb_id, media_type):
    api_key = get_tmdb_key()
    if not api_key:
        return []
    try:
        r = requests.get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
                         params={"api_key": api_key}, timeout=8)
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return (data.get("flatrate", []) + data.get("rent", []))[:8]
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

# --------------------------------------------------
# 6. NLP ENGINE (Mr.DP)
# --------------------------------------------------
def nlp_infer_feelings(prompt):
    t = (prompt or "").lower()
    current, desired = None, None
    
    # Current feeling detection
    if any(k in t for k in ["bore", "boring", "nothing to watch", "meh", "blah"]): current = "Bored"
    elif any(k in t for k in ["stress", "burnout", "overwhelm", "too much"]): current = "Stressed"
    elif any(k in t for k in ["anxious", "anxiety", "panic", "nervous", "worried"]): current = "Anxious"
    elif any(k in t for k in ["sad", "down", "depressed", "blue", "crying"]): current = "Sad"
    elif any(k in t for k in ["lonely", "alone", "isolated"]): current = "Lonely"
    elif any(k in t for k in ["angry", "mad", "pissed", "furious", "rage"]): current = "Angry"
    elif any(k in t for k in ["tired", "exhaust", "drained", "sleepy", "fatigue"]): current = "Tired"
    elif any(k in t for k in ["numb", "empty", "void", "nothing"]): current = "Numb"
    elif any(k in t for k in ["confus", "lost", "uncertain"]): current = "Confused"
    elif any(k in t for k in ["restless", "antsy", "fidget", "can't sit"]): current = "Restless"
    
    # Desired feeling detection
    if any(k in t for k in ["comfort", "cozy", "warm", "safe", "wholesome", "soft"]): desired = "Comforted"
    elif any(k in t for k in ["relax", "unwind", "chill", "easy", "low effort", "calm"]): desired = "Relaxed"
    elif any(k in t for k in ["action", "energy", "pump", "hype", "adrenaline", "intense"]): desired = "Energized"
    elif any(k in t for k in ["fun", "funny", "comedy", "laugh", "humor", "entertain"]): desired = "Entertained"
    elif any(k in t for k in ["inspir", "motivat", "uplift", "meaning"]): desired = "Inspired"
    elif any(k in t for k in ["curious", "learn", "discover", "documentary", "interesting"]): desired = "Curious"
    elif any(k in t for k in ["sleep", "bed", "wind down", "night"]): desired = "Sleepy"
    elif any(k in t for k in ["connect", "romance", "love", "relationship", "feel"]): desired = "Connected"
    elif any(k in t for k in ["thrill", "suspense", "edge", "twist", "mind"]): desired = "Stimulated"
    elif any(k in t for k in ["happy", "joy", "cheer", "good mood", "smile"]): desired = "Happy"
    elif any(k in t for k in ["focus", "concentrate", "study", "work", "productive"]): desired = "Focused"
    
    return current, desired

@st.cache_data(show_spinner=False, ttl=3600)
def nlp_to_tmdb_plan(prompt):
    p = (prompt or "").strip()
    if not p:
        return {"mode": "search", "query": "", "current_feeling": None, "desired_feeling": None, "raw_prompt": ""}
    
    h_current, h_desired = nlp_infer_feelings(p)
    
    # Determine mode: search (specific title/actor) vs discover (mood-based)
    search_indicators = ["watch", "find", "show me", "looking for", "want to see", "recommend"]
    mood_indicators = ["feel", "mood", "vibe", "something", "anything", "i'm", "i am", "need"]
    
    is_mood = any(k in p.lower() for k in mood_indicators) or h_current or h_desired
    is_search = not is_mood or any(k in p.lower() for k in ["called", "named", "titled", "the movie", "the show", "series"])
    
    heuristic_mode = "search" if is_search and not (h_current or h_desired) else "discover"
    
    if not openai_client:
        return {
            "mode": heuristic_mode,
            "query": p if heuristic_mode == "search" else "",
            "current_feeling": h_current,
            "desired_feeling": h_desired,
            "raw_prompt": p
        }
    
    try:
        sys = f"""Convert user request to JSON for movie/TV recommendations.
Return ONLY valid JSON with these keys:
- mode: "search" (specific title/actor/director) or "discover" (mood/vibe based)
- query: search keywords if mode=search, empty if discover
- current_feeling: one of {CURRENT_FEELINGS} or null
- desired_feeling: one of {DESIRED_FEELINGS} or null

Examples:
"I'm bored, need action" → {{"mode":"discover","query":"","current_feeling":"Bored","desired_feeling":"Energized"}}
"Batman movie" → {{"mode":"search","query":"Batman","current_feeling":null,"desired_feeling":null}}
"something funny for a sad day" → {{"mode":"discover","query":"","current_feeling":"Sad","desired_feeling":"Entertained"}}
"Christopher Nolan films" → {{"mode":"search","query":"Christopher Nolan","current_feeling":null,"desired_feeling":null}}"""

        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": p}],
            temperature=0.2
        )
        content = (resp.choices[0].message.content or "").strip()
        content = content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(content)
        
        plan.setdefault("mode", heuristic_mode)
        plan.setdefault("query", "")
        plan.setdefault("current_feeling", h_current)
        plan.setdefault("desired_feeling", h_desired)
        plan["raw_prompt"] = p
        
        # Validate feelings
        if plan.get("current_feeling") not in CURRENT_FEELINGS:
            plan["current_feeling"] = h_current
        if plan.get("desired_feeling") not in DESIRED_FEELINGS:
            plan["desired_feeling"] = h_desired
            
        return plan
    except:
        return {
            "mode": heuristic_mode,
            "query": p if heuristic_mode == "search" else "",
            "current_feeling": h_current,
            "desired_feeling": h_desired,
            "raw_prompt": p
        }

@st.cache_data(ttl=3600)
def nlp_search_tmdb(plan, page=1):
    if not plan:
        return []
    
    mode = (plan.get("mode") or "search").lower()
    query = (plan.get("query") or "").strip()
    current_feeling = plan.get("current_feeling")
    desired_feeling = plan.get("desired_feeling")
    
    # Mood-based discovery
    if mode == "discover" and (current_feeling or desired_feeling):
        return discover_movies_by_emotion(page=page, current_feeling=current_feeling, desired_feeling=desired_feeling)
    
    # Search mode
    if query:
        results = search_movies(query, page=page)
        if results:
            return results
        # Fallback to mood if search fails
        h_current, h_desired = nlp_infer_feelings(plan.get("raw_prompt", ""))
        if h_current or h_desired:
            return discover_movies_by_emotion(page=page, current_feeling=h_current, desired_feeling=h_desired)
    
    return []

# --------------------------------------------------
# 7. GAMIFICATION ENGINE
# --------------------------------------------------
def get_dopamine_points():
    return st.session_state.get("dopamine_points", 0)

def add_dopamine_points(amount, reason=""):
    current = st.session_state.get("dopamine_points", 0)
    st.session_state.dopamine_points = current + amount
    if reason:
        st.toast(f"+{amount} DP: {reason}", icon="⚡")

def get_streak():
    return st.session_state.get("streak_days", 0)

def update_streak():
    today = datetime.now().strftime("%Y-%m-%d")
    last_visit = st.session_state.get("last_visit_date", "")
    if last_visit != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if last_visit == yesterday:
            st.session_state.streak_days = st.session_state.get("streak_days", 0) + 1
            add_dopamine_points(10 * st.session_state.streak_days, f"{st.session_state.streak_days} day streak!")
        else:
            st.session_state.streak_days = 1
        st.session_state.last_visit_date = today

def get_level():
    points = get_dopamine_points()
    if points < 100: return ("Newbie", 1, 100)
    elif points < 500: return ("Explorer", 2, 500)
    elif points < 1500: return ("Curator", 3, 1500)
    elif points < 5000: return ("Connoisseur", 4, 5000)
    else: return ("Dopamine Master", 5, 999999)

def get_achievements():
    achievements = []
    points = get_dopamine_points()
    streak = get_streak()
    hits = st.session_state.get("quick_hit_count", 0)
    if streak >= 3: achievements.append(("🔥", "Hot Streak", "3+ days"))
    if streak >= 7: achievements.append(("💎", "Week Warrior", "7+ days"))
    if hits >= 10: achievements.append(("⚡", "Quick Draw", "10+ hits"))
    if hits >= 50: achievements.append(("🎯", "Sharpshooter", "50+ hits"))
    if points >= 100: achievements.append(("🌟", "Rising Star", "100+ DP"))
    if points >= 1000: achievements.append(("👑", "Royalty", "1000+ DP"))
    return achievements

# --------------------------------------------------
# 8. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "user": None,
        "is_premium": False,
        "current_feeling": "Bored",
        "desired_feeling": "Entertained",
        "last_emotion_key": None,
        "movies_feed": [],
        "feed_page": 1,
        "quick_hit": None,
        "quick_hit_count": 0,
        "dopamine_points": 0,
        "streak_days": 0,
        "last_visit_date": "",
        "nlp_prompt": "",
        "nlp_plan": None,
        "nlp_results": [],
        "nlp_page": 1,
        "nlp_last_prompt": "",
        "search_query": "",
        "search_results": [],
        "referral_code": None,
        "show_premium_modal": False,
        "show_trailers": True,
    })
    st.session_state.init = True

# Generate referral code
if not st.session_state.get("referral_code"):
    st.session_state.referral_code = hashlib.md5(str(random.random()).encode()).hexdigest()[:8].upper()

# Update streak
update_streak()

# --------------------------------------------------
# 9. VIRAL CSS - GLASSMORPHISM + ANIMATIONS
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #050508;
    --bg-secondary: #0a0a10;
    --bg-card: rgba(255, 255, 255, 0.02);
    --accent-primary: #8b5cf6;
    --accent-secondary: #06b6d4;
    --accent-tertiary: #10b981;
    --accent-gradient: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
    --accent-gradient-2: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.6);
    --glass: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-hover: rgba(255, 255, 255, 0.06);
}

* { font-family: 'Outfit', sans-serif; }
h1, h2, h3, .stat-value, .hero-title { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: var(--bg-primary);
    background-image: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 100% 100%, rgba(6, 182, 212, 0.1) 0%, transparent 50%),
        radial-gradient(ellipse 40% 30% at 0% 100%, rgba(16, 185, 129, 0.08) 0%, transparent 50%);
}

/* Hide Streamlit UI */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
div[data-testid="stToolbar"] {display: none;}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
}

section[data-testid="stSidebar"] .stTextArea textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* Stats Bar */
.stats-bar {
    display: flex;
    gap: 16px;
    padding: 16px 20px;
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    justify-content: center;
}

.stat-item {
    text-align: center;
    min-width: 80px;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 0.65rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}

/* Streak Animation */
@keyframes fireGlow {
    0%, 100% { filter: drop-shadow(0 0 4px #ff6b35) drop-shadow(0 0 8px #ff6b35); transform: scale(1); }
    50% { filter: drop-shadow(0 0 8px #ff9f1c) drop-shadow(0 0 16px #ff9f1c); transform: scale(1.1); }
}
.streak-fire { animation: fireGlow 1.5s ease-in-out infinite; font-size: 1.5rem; }

/* Level Bar */
.level-bar {
    height: 6px;
    background: var(--glass);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 6px;
}
.level-progress {
    height: 100%;
    background: var(--accent-gradient);
    border-radius: 3px;
    transition: width 0.5s ease;
}

/* Hero Section */
.hero-container {
    position: relative;
    border-radius: 28px;
    overflow: hidden;
    margin-bottom: 28px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
}
.hero-backdrop {
    width: 100%;
    height: 380px;
    object-fit: cover;
    opacity: 0.7;
    mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
}
.hero-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 32px;
    background: linear-gradient(to top, var(--bg-primary) 20%, transparent 100%);
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: white;
    margin: 0 0 8px 0;
    text-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.hero-meta {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 12px;
}
.hero-overview {
    color: var(--text-secondary);
    max-width: 550px;
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* Movie Card */
.movie-card {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 16px;
}
.movie-card:hover {
    transform: scale(1.04) translateY(-8px);
    border-color: var(--accent-primary);
    box-shadow: 0 20px 40px rgba(139, 92, 246, 0.25);
}
.movie-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
}
.movie-info {
    padding: 14px;
}
.movie-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-primary);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.movie-year {
    font-size: 0.75rem;
    color: var(--text-secondary);
}
.movie-rating {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 215, 0, 0.15);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    color: #ffd700;
    margin-top: 6px;
}

/* Provider Grid */
.provider-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 10px 14px;
    border-top: 1px solid var(--glass-border);
}
.provider-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    text-decoration: none;
}
.provider-btn:hover {
    transform: scale(1.15);
    border-color: var(--accent-primary);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}
.provider-icon {
    width: 22px;
    height: 22px;
    border-radius: 5px;
}

/* Buttons */
.stButton > button {
    background: var(--accent-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
}

/* Quick Hit Button */
.quick-hit-btn {
    background: var(--accent-gradient-2) !important;
    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4) !important;
}

/* Achievement Badge */
.achievement {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    margin: 3px;
    font-size: 0.75rem;
}
.achievement-icon { font-size: 1rem; }
.achievement-text { color: var(--text-secondary); }

/* Share Card */
.share-card {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid var(--accent-primary);
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.share-card::before {
    content: '';
    position: absolute;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
    animation: rotate 15s linear infinite;
}
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.share-title { font-size: 1.2rem; font-weight: 700; position: relative; }
.share-mood { font-size: 2.5rem; margin: 12px 0; position: relative; }

/* Referral Code */
.referral-code {
    font-family: 'Space Grotesk', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 3px;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Glass Card */
.glass-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 16px;
}
.glass-card:hover {
    border-color: rgba(139, 92, 246, 0.3);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 10px 20px;
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    background: var(--accent-gradient);
    border-color: transparent;
    color: white;
}

/* Section Headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 24px 0 16px 0;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}
.section-icon { font-size: 1.4rem; }

/* NLP Result Header */
.nlp-header {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid var(--accent-primary);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 20px;
}
.nlp-prompt {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}
.nlp-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent-primary); border-radius: 3px; }

/* Pulse Animation */
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.5); }
    50% { box-shadow: 0 0 0 12px rgba(245, 158, 11, 0); }
}
.pulse { animation: pulse 2s infinite; }

/* Premium Badge */
.premium-badge {
    background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
    color: black;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Input overrides */
.stTextInput input, .stTextArea textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 10. HELPER FUNCTIONS
# --------------------------------------------------
def safe(s):
    return html_lib.escape(s or "")

def render_stats_bar():
    level_name, level_num, next_level = get_level()
    points = get_dopamine_points()
    streak = get_streak()
    progress = min(100, (points / next_level) * 100)
    
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{points}</div>
            <div class="stat-label">Dopamine Points</div>
        </div>
        <div class="stat-item">
            <span class="streak-fire">🔥</span>
            <div class="stat-value">{streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">Lv.{level_num}</div>
            <div class="stat-label">{level_name}</div>
            <div class="level-bar"><div class="level-progress" style="width: {progress}%"></div></div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state.get('quick_hit_count', 0)}</div>
            <div class="stat-label">Dope Hits</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_movie_card(item, show_providers=True):
    title = item.get("title", "")
    year = item.get("release_date", "")[:4]
    rating = item.get("vote_average", 0)
    poster = item.get("poster")
    tmdb_id = item.get("id")
    media_type = item.get("type", "movie")
    
    providers_html = ""
    if show_providers:
        providers = get_providers(tmdb_id, media_type)
        if providers:
            icons = ""
            for p in providers[:6]:
                name = p.get("provider_name", "")
                logo = p.get("logo_path")
                if not logo: continue
                link = get_deep_link(name, title)
                if not link: continue
                icons += f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='{safe(name)}'><img src='{TMDB_LOGO_URL}{logo}' class='provider-icon'></a>"
            if icons:
                providers_html = f"<div class='provider-grid'>{icons}</div>"
    
    rating_html = f"<div class='movie-rating'>⭐ {rating:.1f}</div>" if rating > 0 else ""
    
    st.markdown(f"""
    <div class="movie-card">
        <img src="{safe(poster)}" class="movie-poster" loading="lazy" onerror="this.style.background='#1a1a2e'">
        <div class="movie-info">
            <div class="movie-title">{safe(title)}</div>
            <div class="movie-year">{year}</div>
            {rating_html}
        </div>
        {providers_html}
    </div>
    """, unsafe_allow_html=True)

def render_hero(movie):
    if not movie: return
    backdrop = movie.get("backdrop") or movie.get("poster")
    title = movie.get("title", "")
    overview = movie.get("overview", "")
    year = movie.get("release_date", "")[:4]
    rating = movie.get("vote_average", 0)
    
    st.markdown(f"""
    <div class="hero-container">
        <img src="{safe(backdrop)}" class="hero-backdrop" onerror="this.style.opacity='0.3'">
        <div class="hero-content">
            <div class="hero-title">{safe(title)}</div>
            <div class="hero-meta">{year} {'• ⭐ ' + f'{rating:.1f}' if rating else ''}</div>
            <p class="hero-overview">{safe(overview)}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_share_card():
    current = st.session_state.current_feeling
    desired = st.session_state.desired_feeling
    points = get_dopamine_points()
    streak = get_streak()
    
    st.markdown(f"""
    <div class="share-card">
        <div class="share-title">My Dopamine Profile</div>
        <div class="share-mood">{MOOD_EMOJIS.get(current, '😊')} → {MOOD_EMOJIS.get(desired, '✨')}</div>
        <p style="color: var(--text-secondary); position: relative; margin: 0;">
            Feeling <strong>{current}</strong>, seeking <strong>{desired}</strong>
        </p>
        <div style="margin-top: 12px; position: relative;">
            <span style="margin: 0 8px;">🔥 {streak} day streak</span>
            <span style="margin: 0 8px;">⚡ {points} DP</span>
        </div>
        <p style="margin-top: 12px; font-size: 0.75rem; color: var(--text-secondary); position: relative;">
            dopamine.watch
        </p>
    </div>
    """, unsafe_allow_html=True)

def get_quick_hit():
    movies = discover_movies_by_emotion(
        page=random.randint(1, 3),
        current_feeling=st.session_state.current_feeling,
        desired_feeling=st.session_state.desired_feeling
    )
    if movies:
        add_dopamine_points(15, "Quick Hit!")
        st.session_state.quick_hit_count = st.session_state.get("quick_hit_count", 0) + 1
        return random.choice(movies[:5])
    return None

# --------------------------------------------------
# 11. SIDEBAR
# --------------------------------------------------
def render_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; margin-bottom: 8px;">
            🧠 Dopamine<span style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">.watch</span>
        </h1>
        """, unsafe_allow_html=True)
        
        # Premium badge
        if st.session_state.get("is_premium"):
            st.markdown("<span class='premium-badge'>⭐ Premium</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Emotion Selectors
        st.markdown("### 🎯 How do you feel?")
        
        current_options = [f"{MOOD_EMOJIS.get(f, '😊')} {f}" for f in CURRENT_FEELINGS]
        current_idx = CURRENT_FEELINGS.index(st.session_state.current_feeling) if st.session_state.current_feeling in CURRENT_FEELINGS else 6
        current_choice = st.selectbox(
            "Right now I feel...",
            options=current_options,
            index=current_idx,
            key="current_select"
        )
        new_current = current_choice.split(" ", 1)[1] if " " in current_choice else current_choice
        if new_current != st.session_state.current_feeling:
            st.session_state.current_feeling = new_current
            st.session_state.movies_feed = []  # Reset feed
            add_dopamine_points(5, "Mood check!")
        
        desired_options = [f"{MOOD_EMOJIS.get(f, '✨')} {f}" for f in DESIRED_FEELINGS]
        desired_idx = DESIRED_FEELINGS.index(st.session_state.desired_feeling) if st.session_state.desired_feeling in DESIRED_FEELINGS else 7
        desired_choice = st.selectbox(
            "I want to feel...",
            options=desired_options,
            index=desired_idx,
            key="desired_select"
        )
        new_desired = desired_choice.split(" ", 1)[1] if " " in desired_choice else desired_choice
        if new_desired != st.session_state.desired_feeling:
            st.session_state.desired_feeling = new_desired
            st.session_state.movies_feed = []  # Reset feed
            add_dopamine_points(5, "Mood updated!")
        
        st.markdown("---")
        
        # Quick Hit Button
        if st.button("⚡ QUICK DOPE HIT", use_container_width=True, key="quick_hit_sidebar"):
            st.session_state.quick_hit = get_quick_hit()
            st.session_state.nlp_results = []
            st.session_state.nlp_last_prompt = ""
            st.rerun()
        
        st.markdown("---")
        
        # Mr.DP NLP
        st.markdown("### 🧾 Mr.DP")
        st.caption("Your AI curator — describe what you want!")
        
        nlp_prompt = st.text_area(
            "Ask Mr.DP",
            placeholder="Examples:\n• 'smart sci-fi from the 90s'\n• 'I'm sad, need comfort'\n• 'Christopher Nolan films'\n• 'something funny and light'",
            height=100,
            key="nlp_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔮 Ask", use_container_width=True, key="nlp_ask"):
                if nlp_prompt.strip():
                    with st.spinner("Mr.DP is searching..."):
                        st.session_state.nlp_last_prompt = nlp_prompt
                        st.session_state.nlp_plan = nlp_to_tmdb_plan(nlp_prompt)
                        st.session_state.nlp_results = nlp_search_tmdb(st.session_state.nlp_plan, page=1)
                        st.session_state.nlp_page = 1
                        st.session_state.quick_hit = None
                        add_dopamine_points(10, "Asked Mr.DP!")
                    st.rerun()
        with col2:
            if st.button("✕ Clear", use_container_width=True, key="nlp_clear"):
                st.session_state.nlp_results = []
                st.session_state.nlp_last_prompt = ""
                st.session_state.nlp_plan = None
                st.rerun()
        
        st.markdown("---")
        
        # Share Section
        st.markdown("### 📤 Share & Invite")
        st.markdown(f"<div style='text-align: center;'><span class='referral-code'>{st.session_state.referral_code}</span></div>", unsafe_allow_html=True)
        st.caption("Share your code for bonus DP!")
        
        st.markdown("---")
        
        # Premium CTA
        if not st.session_state.get("is_premium"):
            if st.button("⭐ Go Premium", use_container_width=True, key="premium_sidebar"):
                st.session_state.show_premium_modal = True
                st.rerun()
        
        st.markdown("---")
        st.caption("v31.0 • Built for ADHD brains 🧠")

# --------------------------------------------------
# 12. MAIN CONTENT
# --------------------------------------------------
def render_main():
    # Stats Bar
    render_stats_bar()
    
    # Achievements
    achievements = get_achievements()
    if achievements:
        ach_html = "".join([f"<span class='achievement'><span class='achievement-icon'>{a[0]}</span><span class='achievement-text'>{a[1]}</span></span>" for a in achievements])
        st.markdown(f"<div style='margin-bottom: 20px;'>{ach_html}</div>", unsafe_allow_html=True)
    
    # Show Mr.DP Results
    if st.session_state.nlp_last_prompt and st.session_state.nlp_results:
        plan = st.session_state.nlp_plan or {}
        mode = plan.get("mode", "search")
        query = plan.get("query", "")
        
        st.markdown(f"""
        <div class="nlp-header">
            <div class="nlp-prompt">🧾 Mr.DP: "{safe(st.session_state.nlp_last_prompt)}"</div>
            <div class="nlp-meta">Mode: {mode.title()} {'• Query: ' + query if query else ''}</div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(6)
        for i, movie in enumerate(st.session_state.nlp_results[:24]):
            with cols[i % 6]:
                render_movie_card(movie)
        
        if len(st.session_state.nlp_results) >= 20:
            if st.button("Load More Results", key="nlp_more", use_container_width=True):
                st.session_state.nlp_page += 1
                more = nlp_search_tmdb(st.session_state.nlp_plan, page=st.session_state.nlp_page)
                st.session_state.nlp_results.extend(more)
                add_dopamine_points(5, "Exploring!")
                st.rerun()
        return
    
    # Show Quick Hit Result
    if st.session_state.quick_hit:
        st.markdown("<div class='section-header'><span class='section-icon'>🎬</span><h2 class='section-title'>Your Perfect Match</h2></div>", unsafe_allow_html=True)
        render_hero(st.session_state.quick_hit)
        
        # Provider buttons
        providers = get_providers(st.session_state.quick_hit.get("id"), st.session_state.quick_hit.get("type", "movie"))
        if providers:
            provider_cols = st.columns(min(len(providers), 6))
            for i, p in enumerate(providers[:6]):
                with provider_cols[i]:
                    link = get_deep_link(p.get("provider_name", ""), st.session_state.quick_hit.get("title", ""))
                    if link:
                        st.markdown(f"<a href='{link}' target='_blank' style='display:block; text-align:center; padding:12px; background:var(--glass); border:1px solid var(--glass-border); border-radius:12px; color:white; text-decoration:none; font-size:0.8rem;'>{p.get('provider_name', '')[:12]}</a>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 Another Hit", use_container_width=True, key="another_hit"):
                st.session_state.quick_hit = get_quick_hit()
                st.rerun()
        with col2:
            if st.button("📤 Share", use_container_width=True, key="share_hit"):
                st.toast("Share card copied!", icon="📤")
        with col3:
            if st.button("✕ Close", use_container_width=True, key="close_hit"):
                st.session_state.quick_hit = None
                st.rerun()
        
        st.markdown("---")
    
    # Main Feed
    st.markdown("<div class='section-header'><span class='section-icon'>🍿</span><h2 class='section-title'>Curated For You</h2></div>", unsafe_allow_html=True)
    st.caption(f"Based on: {MOOD_EMOJIS.get(st.session_state.current_feeling, '')} {st.session_state.current_feeling} → {MOOD_EMOJIS.get(st.session_state.desired_feeling, '')} {st.session_state.desired_feeling}")
    
    # Check if emotions changed
    emotion_key = f"{st.session_state.current_feeling}_{st.session_state.desired_feeling}"
    if st.session_state.get("last_emotion_key") != emotion_key:
        st.session_state.movies_feed = []
        st.session_state.feed_page = 1
        st.session_state.last_emotion_key = emotion_key
    
    # Load movies
    if not st.session_state.movies_feed:
        st.session_state.movies_feed = discover_movies_by_emotion(
            page=1,
            current_feeling=st.session_state.current_feeling,
            desired_feeling=st.session_state.desired_feeling
        )
    
    # Display grid
    movies = st.session_state.movies_feed
    if movies:
        cols = st.columns(6)
        for i, movie in enumerate(movies[:24]):
            with cols[i % 6]:
                render_movie_card(movie)
        
        if st.button("Load More", use_container_width=True, key="load_more_main"):
            st.session_state.feed_page += 1
            more = discover_movies_by_emotion(
                page=st.session_state.feed_page,
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
            st.session_state.movies_feed.extend(more)
            add_dopamine_points(5, "Exploring!")
            st.rerun()
    else:
        st.warning("No movies found. Try different moods!")
    
    # Tabs for other content
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>🎭</span><h2 class='section-title'>More Content</h2></div>", unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["⚡ Shorts", "🎵 Music", "🎙️ Podcasts", "📚 Books"])
    
    with t1:
        vk = FEELING_TO_VIDEOS.get(st.session_state.desired_feeling, "trending")
        st.markdown(f"**Perfect for:** {st.session_state.desired_feeling}")
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(vk)}+shorts"
        st.markdown(f"<a href='{yt_url}' target='_blank' style='display:block; text-align:center; padding:20px; background:var(--accent-gradient); border-radius:16px; color:white; text-decoration:none; font-weight:600;'>🎥 Watch {vk.title()} Shorts →</a>", unsafe_allow_html=True)
    
    with t2:
        mk = FEELING_TO_MUSIC.get(st.session_state.desired_feeling, "feel good")
        st.markdown(f"**Perfect for:** {st.session_state.desired_feeling}")
        sp_url = f"https://open.spotify.com/search/{quote_plus(mk)}"
        st.markdown(f"<a href='{sp_url}' target='_blank' style='display:block; text-align:center; padding:20px; background:var(--accent-gradient); border-radius:16px; color:white; text-decoration:none; font-weight:600;'>🎧 Listen to {mk.title()} →</a>", unsafe_allow_html=True)
        playlists = {"Anxious": "37i9dQZF1DWXe9gFZP0gtP", "Energized": "37i9dQZF1DX76Wlfdnj7AP", "Happy": "37i9dQZF1DX3rxVfibe1L0", "Focused": "37i9dQZF1DWZeKCadgRdKQ", "Relaxed": "37i9dQZF1DX4WYpdgoIcn6"}
        pid = playlists.get(st.session_state.desired_feeling, "37i9dQZF1DX3rxVfibe1L0")
        components.iframe(f"https://open.spotify.com/embed/playlist/{pid}?theme=0", height=352)
    
    with t3:
        topics = {"Anxious": "anxiety mental health", "Curious": "science explained", "Bored": "true crime mystery", "Inspired": "motivational success", "Focused": "productivity"}
        topic = topics.get(st.session_state.desired_feeling, "trending podcasts")
        st.markdown(f"**Perfect for:** {st.session_state.desired_feeling}")
        pod_url = f"https://open.spotify.com/search/{quote_plus(topic)}%20podcast"
        st.markdown(f"<a href='{pod_url}' target='_blank' style='display:block; text-align:center; padding:20px; background:var(--accent-gradient); border-radius:16px; color:white; text-decoration:none; font-weight:600;'>🎙️ Find {topic.title()} Podcasts →</a>", unsafe_allow_html=True)
    
    with t4:
        genres = {"Anxious": "self-help mindfulness", "Curious": "science history", "Bored": "thriller mystery", "Inspired": "biography motivation", "Sleepy": "fantasy fiction"}
        genre = genres.get(st.session_state.desired_feeling, "bestsellers")
        st.markdown(f"**Perfect for:** {st.session_state.desired_feeling}")
        aud_url = f"https://www.audible.com/search?keywords={quote_plus(genre)}"
        st.markdown(f"<a href='{aud_url}' target='_blank' style='display:block; text-align:center; padding:20px; background:var(--accent-gradient); border-radius:16px; color:white; text-decoration:none; font-weight:600;'>📖 Browse {genre.title()} Audiobooks →</a>", unsafe_allow_html=True)
    
    # Share Section
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>📤</span><h2 class='section-title'>Share Your Vibe</h2></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        render_share_card()
    with col2:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="margin-top: 0;">🎁 Invite Friends</h4>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">Share your code — both get <strong>100 bonus DP</strong>!</p>
            <div style="margin: 16px 0; text-align: center;">
                <span class="referral-code" style="font-size: 1.8rem;">{st.session_state.referral_code}</span>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.75rem; text-align: center;">
                0 friends invited • dopamine.watch/r/{st.session_state.referral_code}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Premium Modal
    if st.session_state.get("show_premium_modal"):
        st.markdown("---")
        st.markdown("<div class='section-header'><span class='section-icon'>⭐</span><h2 class='section-title'>Unlock Premium</h2></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="border-color: #ffd700;">
            <h3 style="margin-top: 0; text-align: center;">Dopamine<span style="color: #ffd700;">+</span> Premium</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0;">
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🚫 No ads</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🤖 Advanced AI</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">📊 Mood analytics</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🔥 2x DP earnings</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🏆 Exclusive badges</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">💬 Priority support</div>
            </div>
            <div style="text-align: center; margin: 24px 0;">
                <span style="font-size: 2.5rem; font-weight: 700;">$4.99</span>
                <span style="color: var(--text-secondary);">/month</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Maybe Later", use_container_width=True, key="premium_later"):
                st.session_state.show_premium_modal = False
                st.rerun()
        with col2:
            if st.button("🚀 Subscribe", use_container_width=True, key="premium_subscribe"):
                st.toast("Premium coming soon! Join waitlist.", icon="⭐")
                st.session_state.show_premium_modal = False

# --------------------------------------------------
# 13. RUN APP
# --------------------------------------------------
render_sidebar()
render_main()
