# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v28.3 - Mr.DP NLP FIX (NO REFACTOR)
# - Mr.DP now understands “vibe prompts” (ex: "I'm bored, need action")
# - Uses TMDB Discover fallback when Search is too literal / returns few results
# - Fixes session_state crashes for existing sessions (nlp_last_prompt missing)
# - Keeps 4x4 provider icon grid inside the movie card
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
import re

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

# --------------------------------------------------
# 2. MASTER SERVICE MAP - DIRECT DEEP LINKS
# NOTE: These templates are kept EXACTLY as your baseline (no refactor).
# --------------------------------------------------
SERVICE_MAP = {
    # SUBSCRIPTION SERVICES
    "Netflix": "https://www.netflix.com/title/{tmdb_id}",
    "Amazon Prime Video": "https://www.amazon.com/gp/video/detail/{tmdb_id}",
    "Disney Plus": "https://www.disneyplus.com/movies/-/{tmdb_id}",
    "Max": "https://play.max.com/video/watch/{tmdb_id}",
    "Hulu": "https://www.hulu.com/watch/{tmdb_id}",
    "Peacock": "https://www.peacocktv.com/watch/asset/{tmdb_id}",
    "Paramount Plus": "https://www.paramountplus.com/movies/video/{tmdb_id}",
    "Apple TV Plus": "https://tv.apple.com/us/movie/{tmdb_id}",
    "Starz": "https://www.starz.com/us/en/movies/{tmdb_id}",
    "Showtime": "https://www.showtime.com/titles/{tmdb_id}",
    "MGM+": "https://www.mgmplus.com/movie/{tmdb_id}",
    "Criterion Channel": "https://www.criterionchannel.com/videos/{tmdb_id}",
    "MUBI": "https://mubi.com/films/{tmdb_id}",
    "Shudder": "https://www.shudder.com/movies/watch/{tmdb_id}",

    # FREE / AD-SUPPORTED
    "Tubi": "https://tubitv.com/movies/{tmdb_id}",
    "Pluto TV": "https://pluto.tv/on-demand/movies/{tmdb_id}",
    "Freevee": "https://www.amazon.com/gp/video/detail/{tmdb_id}",
    "The Roku Channel": "https://therokuchannel.roku.com/details/{tmdb_id}",
    "Plex": "https://watch.plex.tv/movie/{tmdb_id}",
    "Crackle": "https://www.crackle.com/watch/{tmdb_id}",
    "Vudu": "https://www.vudu.com/content/movies/details/{tmdb_id}",

    # ANIME
    "Crunchyroll": "https://www.crunchyroll.com/{tmdb_id}",
    "Funimation": "https://www.funimation.com/shows/{tmdb_id}",
    "HIDIVE": "https://www.hidive.com/movies/{tmdb_id}",
}

LOGOS = {
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    "Trailer": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg"
}

# --------------------------------------------------
# 3. API CLIENTS
# --------------------------------------------------
@st.cache_data
def get_tmdb_key():
    # Minimal safety (no refactor): avoids silent crash when key missing
    try:
        return st.secrets["tmdb"]["api_key"]
    except Exception:
        st.error('KeyError: st.secrets has no key "tmdb". Add it to secrets.toml (tmdb.api_key).')
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
        # FIX: discover endpoint doesn't include media_type - default to "movie"
        media_type = item.get("media_type", "movie")

        # STRICT FILTER: Only actual movies/TV from TMDB
        if media_type not in ["movie", "tv"]:
            continue

        # Must have title and poster
        title = item.get("title") or item.get("name")
        if not title or not item.get("poster_path"):
            continue

        clean.append({
            "id": item.get("id"),
            "type": media_type,
            "title": title,
            "overview": item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "release_date": item.get("release_date") or item.get("first_air_date") or "Unknown"
        })
    return clean

@st.cache_data(ttl=3600)
def discover_movies_by_emotion(page=1, current_feeling=None, desired_feeling=None):
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
            genre_ids.extend([g for g in prefs["prefer"] if g not in genre_ids][:3 - len(genre_ids)])

    try:
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
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
            timeout=8
        )
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except Exception:
        return []

@st.cache_data(ttl=3600)
def discover_movies(page=1, with_genres=None, without_genres=None, sort_by="popularity.desc", year=None):
    """
    NEW (minimal add): Generic TMDB Discover used by Mr.DP NLP when the prompt is “vibe intent”.
    No refactor: does not replace any existing function; only adds.
    """
    api_key = get_tmdb_key()
    if not api_key:
        return []

    try:
        params = {
            "api_key": api_key,
            "sort_by": sort_by,
            "watch_region": "US",
            "with_watch_monetization_types": "flatrate|rent",
            "page": page,
            "include_adult": "false"
        }

        if with_genres:
            params["with_genres"] = "|".join(map(str, with_genres[:3]))

        if without_genres:
            params["without_genres"] = ",".join(map(str, list(set(without_genres))))

        if year:
            # Discover supports primary_release_year for movies
            params["primary_release_year"] = int(year)

        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=10)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except Exception:
        return []

@st.cache_data(ttl=3600)
def search_movies_only(query, page=1):
    """Search for movies/TV only - NO YOUTUBE OR GOOGLE"""
    api_key = get_tmdb_key()
    if not api_key:
        return []
    if not query:
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
        # Filter to only movies/TV
        results = [item for item in r.json().get("results", [])
                   if item.get("media_type") in ["movie", "tv"]]
        return _clean_results(results)
    except Exception:
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
            "flatrate": data.get("flatrate", [])[:16],  # allow up to 16 to fit 4x4
            "rent": data.get("rent", [])[:16]
        }
    except Exception:
        return {"flatrate": [], "rent": []}

# --------------------------------------------------
# 8. AI ENGINE - EMOTION-DRIVEN SORTING
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def sort_by_emotion(titles, current_feeling, desired_feeling):
    """Use OpenAI to sort content by emotional match"""
    if not titles or not openai_client:
        return titles

    try:
        prompt = f"""Reorder these titles for best match.
Current: {current_feeling}
Desired: {desired_feeling}

Titles: {json.dumps(titles[:20])}

Return ONLY a JSON array of titles. No explanation."""
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "").strip()

        sorted_titles = json.loads(content)
        return sorted_titles
    except Exception:
        return titles

# --------------------------------------------------
# 9. DEEP LINK BUILDER (ACTUALLY WORKS)
# --------------------------------------------------
def get_deep_link(provider_name, title, tmdb_id=None):
    """Build working deep link to streaming service"""

    provider = (provider_name or "").strip()

    # Try direct TMDB ID link first (baseline behavior)
    if tmdb_id and provider in SERVICE_MAP:
        template = SERVICE_MAP[provider]
        if "{tmdb_id}" in template:
            return template.format(tmdb_id=tmdb_id)

    # Try fuzzy match on provider name
    for key, template in SERVICE_MAP.items():
        if key.lower() in provider.lower() or provider.lower() in key.lower():
            if "{tmdb_id}" in template and tmdb_id:
                return template.format(tmdb_id=tmdb_id)
            elif "{title}" in template:
                return template.format(title=quote_plus(title))

    # Fallback: direct provider search
    provider_domains = {
        "Netflix": "https://www.netflix.com/search?q=",
        "Amazon": "https://www.amazon.com/s?k=",
        "Disney": "https://www.disneyplus.com/search",
        "Hulu": "https://www.hulu.com/search?q=",
        "Max": "https://play.max.com/search",
        "Peacock": "https://www.peacocktv.com/search?q=",
    }

    for key, url in provider_domains.items():
        if key.lower() in provider.lower():
            return f"{url}{quote_plus(title)}"

    return f"https://www.google.com/search?q=watch+{quote_plus(title)}+on+{quote_plus(provider)}"

# --------------------------------------------------
# 10. HELPERS
# --------------------------------------------------
def render_logo(sidebar=False):
    if os.path.exists(LOGO_PATH):
        (st.sidebar if sidebar else st).image(LOGO_PATH, width=180 if sidebar else 260)
    else:
        (st.sidebar if sidebar else st).markdown(f"# 🧠 {APP_NAME}")

def safe(s: str) -> str:
    return html_lib.escape(s or "", quote=True)

# --------------------------------------------------
# 10.5 Mr.DP NLP (NEW - minimal add, no refactor)
# - Understands vibe prompts & falls back to Discover automatically
# --------------------------------------------------
TMDB_GENRE_IDS = {
    "action": 28,
    "adventure": 12,
    "animation": 16,
    "comedy": 35,
    "crime": 80,
    "documentary": 99,
    "drama": 18,
    "family": 10751,
    "fantasy": 14,
    "history": 36,
    "horror": 27,
    "music": 10402,
    "mystery": 9648,
    "romance": 10749,
    "sci-fi": 878,
    "scifi": 878,
    "science fiction": 878,
    "thriller": 53,
    "war": 10752,
    "western": 37,
}

MRDP_KEYWORDS_PREFER = {
    # action / energy
    "action": [28],
    "fight": [28],
    "fights": [28],
    "combat": [28],
    "war": [10752],
    "explosion": [28],
    "explosions": [28],
    "adrenaline": [28, 12],
    "fast": [28, 12],
    "chase": [28, 53],
    "epic": [12, 14, 28],
    "intense": [53, 28],

    # bored -> stimulation
    "bored": [28, 12, 878, 14],
    "boring": [28, 12, 878, 14],

    # comedy / comfort
    "funny": [35],
    "laugh": [35],
    "comedy": [35],
    "light": [35, 16, 10751],
    "comfort": [10751, 16, 35],
    "cozy": [10751, 16, 35],
    "wholesome": [10751, 16, 35],

    # calm / relax
    "calm": [99, 16, 10751],
    "relax": [35, 16, 10751, 99],
    "relaxing": [35, 16, 10751, 99],
    "chill": [35, 16, 10751, 99],
    "sleep": [16, 10751, 10749],

    # genres
    "anime": [16],
    "cartoon": [16],
    "romance": [10749],
    "love": [10749],
    "documentary": [99],
    "history": [36],
    "mystery": [9648],
    "detective": [9648, 80],
    "crime": [80],
    "thriller": [53],
    "scary": [27],
    "horror": [27],
    "fantasy": [14],
    "sci-fi": [878],
    "scifi": [878],
    "space": [878],
    "superhero": [28, 12],
}

MRDP_KEYWORDS_AVOID = {
    "no horror": [27],
    "not horror": [27],
    "no scary": [27],
    "not scary": [27],
    "no thriller": [53],
    "not thriller": [53],
    "no gore": [27],
    "no violence": [28, 80],
}

def _extract_year(text: str):
    m = re.search(r"(19\d{2}|20\d{2})", text or "")
    if not m:
        return None
    y = int(m.group(1))
    if 1900 <= y <= 2099:
        return y
    return None

def mrdp_plan_heuristic(prompt: str):
    text = (prompt or "").strip()
    low = text.lower()

    year = _extract_year(low)

    with_genres = []
    without_genres = []

    # explicit avoid phrases
    for phrase, ids in MRDP_KEYWORDS_AVOID.items():
        if phrase in low:
            without_genres.extend(ids)

    # prefer keywords
    for kw, ids in MRDP_KEYWORDS_PREFER.items():
        if kw in low:
            with_genres.extend(ids)

    # dedupe
    with_genres = list(dict.fromkeys(with_genres))
    without_genres = list(dict.fromkeys(without_genres))

    # Decide intent:
    # - If we detect genre-ish keywords => Discover
    # - Else => Search (title/person query)
    vibe_detected = bool(with_genres or without_genres or any(w in low for w in ["i am", "im ", "feel", "need", "want", "something", "vibe"]))
    intent = "discover" if vibe_detected and (with_genres or without_genres) else "search"

    # If user typed a single-word or short prompt (likely title), keep search
    if len(text.split()) <= 3 and not (with_genres or without_genres):
        intent = "search"

    return {
        "intent": intent,               # "search" or "discover"
        "query": text,                  # used by search, or fallback
        "with_genres": with_genres,     # TMDB genre ids
        "without_genres": without_genres,
        "year": year
    }

def mrdp_plan_openai(prompt: str):
    if not openai_client:
        return None
    try:
        sys = "You are a precise query planner for a movie discovery app."
        user = f"""
User prompt: {prompt}

Return ONLY JSON with these keys:
- intent: "search" or "discover"
- query: string
- with_genres: array of TMDB genre IDs (numbers)
- without_genres: array of TMDB genre IDs (numbers)
- year: number or null

TMDB genre IDs you can use:
Action 28, Adventure 12, Animation 16, Comedy 35, Crime 80, Documentary 99,
Drama 18, Family 10751, Fantasy 14, History 36, Horror 27, Music 10402,
Mystery 9648, Romance 10749, Sci-Fi 878, Thriller 53, War 10752, Western 37

Rules:
- If prompt sounds like mood/vibe ("bored", "need action", "something funny"), choose intent="discover".
- If prompt looks like a title/actor query, choose intent="search".
- Keep with_genres max 3, without_genres max 6.
"""
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": user}
            ],
            temperature=0.2,
            max_tokens=200
        )
        content = resp.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(content)

        # minimal validation
        if plan.get("intent") not in ["search", "discover"]:
            return None
        if "query" not in plan:
            plan["query"] = prompt
        if "with_genres" not in plan:
            plan["with_genres"] = []
        if "without_genres" not in plan:
            plan["without_genres"] = []
        if "year" not in plan:
            plan["year"] = None

        # cap sizes
        plan["with_genres"] = [int(x) for x in plan["with_genres"]][:3]
        plan["without_genres"] = [int(x) for x in plan["without_genres"]][:6]

        return plan
    except Exception:
        return None

def mrdp_build_plan(prompt: str):
    # Try OpenAI planner first (if available), else heuristic (or fallback if OpenAI fails)
    plan_ai = mrdp_plan_openai(prompt)
    if plan_ai:
        return plan_ai
    return mrdp_plan_heuristic(prompt)

def mrdp_run_plan(plan: dict, page: int = 1):
    """
    Executes the plan and applies the key fix:
    - If search returns too few results, fallback to Discover using inferred genres.
    - If discover returns nothing, fallback to Search.
    """
    if not plan:
        return []

    intent = plan.get("intent", "search")
    q = (plan.get("query") or "").strip()
    with_genres = plan.get("with_genres") or []
    without_genres = plan.get("without_genres") or []
    year = plan.get("year")

    if intent == "search":
        results = search_movies_only(q, page=page)
        # FLEX FIX: if too literal, fallback to discover
        if len(results) < 6 and (with_genres or without_genres):
            results = discover_movies(
                page=page,
                with_genres=with_genres,
                without_genres=without_genres,
                year=year
            )
        return results

    # discover intent
    results = discover_movies(
        page=page,
        with_genres=with_genres,
        without_genres=without_genres,
        year=year
    )
    # fallback to search if discover is empty
    if not results and q:
        results = search_movies_only(q, page=page)
    return results

# --------------------------------------------------
# 11. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "user": None,
        "auth_step": "login",
        "onboarding_complete": False,

        "current_feeling": "Bored",
        "desired_feeling": "Entertained",

        "movies_feed": [],
        "movies_page": 1,
        "last_emotion_key": None,

        "quick_hit": None,
        "quick_hit_count": 0,

        "search_query": "",
        "search_results": [],
        "search_page": 1,

        # Mr.DP NLP state (NEW)
        "mrdp_prompt": "",
        "mrdp_plan": None,
        "mrdp_results": [],
        "mrdp_page": 1,
        "mrdp_last_prompt": "",
        "mrdp_history": [],

        # Back-compat keys (to prevent AttributeError on old sessions)
        "nlp_last_prompt": "",
    })
    st.session_state.init = True

# BACK-COMPAT PATCH (CRITICAL):
# If the app redeploys while a user already has session_state.init=True,
# new keys won't be added -> AttributeError. This prevents that.
if "nlp_last_prompt" not in st.session_state:
    st.session_state.nlp_last_prompt = ""
if "mrdp_last_prompt" not in st.session_state:
    st.session_state.mrdp_last_prompt = ""
if "mrdp_results" not in st.session_state:
    st.session_state.mrdp_results = []
if "mrdp_page" not in st.session_state:
    st.session_state.mrdp_page = 1
if "mrdp_plan" not in st.session_state:
    st.session_state.mrdp_plan = None
if "mrdp_history" not in st.session_state:
    st.session_state.mrdp_history = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_page" not in st.session_state:
    st.session_state.search_page = 1
if "movies_feed" not in st.session_state:
    st.session_state.movies_feed = []
if "movies_page" not in st.session_state:
    st.session_state.movies_page = 1
if "current_feeling" not in st.session_state:
    st.session_state.current_feeling = "Bored"
if "desired_feeling" not in st.session_state:
    st.session_state.desired_feeling = "Entertained"

# --------------------------------------------------
# 12. CUSTOM CSS - CLEAN, DOPAMINE-OPTIMIZED
# --------------------------------------------------
st.markdown("""
<style>
/* Dark gradient background */
.stApp {
    background: radial-gradient(circle at top, #0f0f23, #000000);
    color: white;
}

/* Movie card */
.card {
    background: #1a1a2e;
    border: 1px solid #2a2a3e;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 16px;
    transition: transform 0.2s, border-color 0.2s;
}

.card:hover {
    transform: translateY(-4px);
    border-color: #00f2ea;
}

/* Poster inside card */
.poster-img {
    width: 100%;
    height: auto;
    display: block;
}

/* Provider grid - 4 columns (fits 4x4 without spilling) */
.provider-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    padding: 12px;
    max-width: 100%;
}

.provider-grid.rent {
    opacity: 0.6;
    border-top: 1px solid #2a2a3e;
}

/* Provider button */
.provider-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: #0f0f23;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #2a2a3e;
    transition: all 0.2s;
    text-decoration: none !important;
    min-height: 40px;
}

.provider-btn:hover {
    border-color: #00f2ea;
    background: #16213e;
    transform: scale(1.05);
}

.provider-icon {
    width: 24px;
    height: 24px;
    object-fit: contain;
}

/* Movie title */
.movie-title {
    padding: 8px 12px;
    font-weight: 700;
    font-size: 0.95rem;
    color: white;
}

.movie-sub {
    padding: 0 12px 8px 12px;
    opacity: 0.7;
    font-size: 0.8rem;
}

/* Buttons - gradient */
button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    transition: all 0.3s !important;
}

button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4) !important;
}

/* Small note */
.small-note {
    opacity: 0.75;
    font-size: 0.9rem;
    margin: 12px 0;
}

/* Trailer button wrapper */
.trailer-wrap {
    padding: 0 12px 12px 12px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 13. MOVIE CARD COMPONENT (4x4 PROVIDER GRID)
# --------------------------------------------------
def render_movie_card(item):
    """Render movie card with clean provider grid (4 cols)"""
    title = item.get("title", "")
    media_type = item.get("type", "movie")
    tmdb_id = item.get("id")

    provs = get_streaming_providers(tmdb_id, media_type)
    flatrate = (provs.get("flatrate") or [])[:16]
    rent = (provs.get("rent") or [])[:16]

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Poster INSIDE the card (not st.image, to keep everything contained)
    poster = item.get("poster")
    if poster:
        st.markdown(f"<img src='{safe(poster)}' class='poster-img' loading='lazy' />", unsafe_allow_html=True)

    # INCLUDED providers
    if flatrate:
        icons_html = ""
        for p in flatrate:
            provider = p.get("provider_name", "")
            logo_path = p.get("logo_path")
            if not logo_path:
                continue
            link = get_deep_link(provider, title, tmdb_id)
            logo = f"{TMDB_LOGO_URL}{logo_path}"
            icons_html += (
                f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='Watch on {safe(provider)}'>"
                f"<img src='{safe(logo)}' class='provider-icon' alt='{safe(provider)}' />"
                f"</a>"
            )
        if icons_html:
            st.markdown(f"<div class='provider-grid'>{icons_html}</div>", unsafe_allow_html=True)

    # RENT providers (dimmed)
    if rent:
        icons_html = ""
        for p in rent:
            provider = p.get("provider_name", "")
            logo_path = p.get("logo_path")
            if not logo_path:
                continue
            link = get_deep_link(provider, title, tmdb_id)
            logo = f"{TMDB_LOGO_URL}{logo_path}"
            icons_html += (
                f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='Rent/Buy on {safe(provider)}'>"
                f"<img src='{safe(logo)}' class='provider-icon' alt='{safe(provider)}' />"
                f"</a>"
            )
        if icons_html:
            st.markdown(f"<div class='provider-grid rent'>{icons_html}</div>", unsafe_allow_html=True)

    # Trailer (YouTube search)
    yt_search = f"https://www.youtube.com/results?search_query={quote_plus(title)}+trailer"
    st.markdown(
        "<div class='trailer-wrap'>"
        f"<a href='{safe(yt_search)}' target='_blank' class='provider-btn' title='Watch Trailer'>"
        f"<img src='{safe(LOGOS['Trailer'])}' class='provider-icon' alt='Trailer' />"
        "</a>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(f"<div class='movie-title'>{safe(title)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='movie-sub'>{safe(item.get('release_date', ''))}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 14. QUICK DOPE HIT ENGINE
# --------------------------------------------------
def get_quick_dope_hit():
    """Get ONE match based on emotions"""
    current = st.session_state.current_feeling
    desired = st.session_state.desired_feeling

    candidates = discover_movies_by_emotion(
        page=random.randint(1, 3),
        current_feeling=current,
        desired_feeling=desired
    )

    if not candidates:
        return None

    if openai_client and len(candidates) > 5:
        titles = [m["title"] for m in candidates[:10]]
        sorted_titles = sort_by_emotion(titles, current, desired)
        for t in sorted_titles[:1]:
            match = next((m for m in candidates if m["title"] == t), None)
            if match:
                return match

    return candidates[0]

# --------------------------------------------------
# 15. AUTH SCREENS
# --------------------------------------------------
def login_screen():
    _, c, _ = st.columns([1, 1.2, 1])
    with c:
        st.markdown("<div class='card' style='padding:30px'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Welcome to your dopamine engine")
        e = st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            st.session_state.user = e or "demo"
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
        st.markdown("<div class='card' style='padding:30px'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Create your dopamine profile")
        st.text_input("Username")
        e = st.text_input("Email")
        st.text_input("Password", type="password")
        if st.button("Sign Up", use_container_width=True):
            st.session_state.user = e or "demo"
            st.rerun()
        if st.button("Back to Login", use_container_width=True):
            st.session_state.auth_step = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def onboarding_baseline():
    st.markdown("## 🧠 Let's calibrate your brain")
    st.caption("This helps us personalize content for your neurodivergent needs")

    triggers = st.multiselect(
        "What overwhelms you?",
        ["Loud sounds", "Flashing lights", "Fast cuts", "Emotional intensity", "Violence", "Jump scares"]
    )

    genres = st.multiselect(
        "What do you enjoy?",
        ["Action", "Anime", "Sci-Fi", "Comedy", "Documentary", "Fantasy", "Drama", "Horror", "Romance"]
    )

    decision = st.radio(
        "When choosing content:",
        ["Decide for me (Quick Dope Hit)", "Give me 3 options", "Let me explore freely"]
    )

    if st.button("Save & Start Watching", use_container_width=True):
        st.session_state.baseline_prefs = {
            "triggers": triggers,
            "genres": genres,
            "decision_style": decision
        }
        st.session_state.onboarding_complete = True
        st.rerun()

# --------------------------------------------------
# 16. MAIN LOBBY - EMOTION-DRIVEN + Mr.DP NLP (SIDEBAR)
# --------------------------------------------------
def lobby_screen():
    # SIDEBAR - CONTROLS
    with st.sidebar:
        render_logo(sidebar=True)

        st.markdown("### 🎯 How do you feel?")

        FEELINGS = [
            ("🌧️", "Sad"), ("🥺", "Lonely"), ("😰", "Anxious"), ("😵‍💫", "Overwhelmed"),
            ("😡", "Angry"), ("😫", "Stressed"), ("😐", "Bored"), ("😴", "Tired"),
            ("🫥", "Numb"), ("🤔", "Confused"), ("😬", "Restless"), ("🎯", "Focused"),
            ("😌", "Calm"), ("😊", "Happy"), ("⚡", "Excited"), ("🧐", "Curious"),
        ]

        DESIRED_FEELINGS = [
            ("🫶", "Comforted"), ("🌊", "Calm"), ("🛋️", "Relaxed"), ("🎯", "Focused"),
            ("🔥", "Energized"), ("🚀", "Stimulated"), ("🌞", "Happy"), ("🍿", "Entertained"),
            ("✨", "Inspired"), ("🌱", "Grounded"), ("🔍", "Curious"), ("🌙", "Sleepy"),
            ("❤️", "Connected"),
        ]

        current_idx = next((i for i, (_, t) in enumerate(FEELINGS) if t == st.session_state.current_feeling), 0)
        current_choice = st.selectbox(
            "Right now I feel...",
            options=[f"{e} {t}" for e, t in FEELINGS],
            index=current_idx
        )
        st.session_state.current_feeling = current_choice.split(" ", 1)[1]

        desired_idx = next((i for i, (_, t) in enumerate(DESIRED_FEELINGS) if t == st.session_state.desired_feeling), 0)
        desired_choice = st.selectbox(
            "I want to feel...",
            options=[f"{e} {t}" for e, t in DESIRED_FEELINGS],
            index=desired_idx
        )
        st.session_state.desired_feeling = desired_choice.split(" ", 1)[1]

        st.markdown("---")

        # QUICK DOPE HIT
        if st.button("⚡ QUICK DOPE HIT", use_container_width=True):
            with st.spinner("Finding your perfect match..."):
                st.session_state.quick_hit = get_quick_dope_hit()
                st.session_state.quick_hit_count += 1
                st.rerun()

        st.metric("Dope Hits", st.session_state.quick_hit_count)

        st.markdown("---")

        # --------------------------------------------------
        # Mr.DP (NLP) — sidebar chat box
        # --------------------------------------------------
        st.markdown("### 📚 Mr.DP")
        st.caption("Head Librarian & Curator — tell me what you want. I’ll pull the best shelf first. 😈📖")

        mrdp_input = st.text_input(
            "Ask Mr.DP",
            key="mrdp_prompt_input",
            placeholder="Example: I'm bored — I need action. Or: something funny & light."
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Search", use_container_width=True, key="mrdp_search_btn"):
                if mrdp_input.strip():
                    with st.spinner("Mr.DP is indexing the shelves..."):
                        plan = mrdp_build_plan(mrdp_input.strip())
                        results = mrdp_run_plan(plan, page=1)

                        # store
                        st.session_state.mrdp_prompt = mrdp_input.strip()
                        st.session_state.mrdp_plan = plan
                        st.session_state.mrdp_results = results
                        st.session_state.mrdp_page = 1
                        st.session_state.mrdp_last_prompt = mrdp_input.strip()

                        # back-compat alias
                        st.session_state.nlp_last_prompt = mrdp_input.strip()

                        # history (minimal)
                        st.session_state.mrdp_history.append(mrdp_input.strip())
                        st.rerun()

        with col_b:
            if st.button("Clear", use_container_width=True, key="mrdp_clear_btn"):
                st.session_state.mrdp_prompt = ""
                st.session_state.mrdp_plan = None
                st.session_state.mrdp_results = []
                st.session_state.mrdp_page = 1
                st.session_state.mrdp_last_prompt = ""
                st.session_state.nlp_last_prompt = ""
                st.rerun()

        if st.session_state.mrdp_last_prompt:
            st.caption(f"Last ask: {st.session_state.mrdp_last_prompt}")

        st.markdown("---")
        if st.button("🚪 Log out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # MAIN CONTENT AREA
    st.markdown("## 🔎 The Lobby")

    # --------------------------------------------------
    # Mr.DP results (show first, override the page until cleared)
    # --------------------------------------------------
    if st.session_state.mrdp_last_prompt:
        st.markdown(f"### 📚 Mr.DP pulled these for: “{safe(st.session_state.mrdp_last_prompt)}”")

        if not st.session_state.mrdp_results:
            st.warning("No matches yet — try adding a genre (action/comedy), a title, or a year.")
        else:
            cols = st.columns(6)
            for i, item in enumerate(st.session_state.mrdp_results[:24]):
                with cols[i % 6]:
                    render_movie_card(item)

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Load more Mr.DP results", use_container_width=True, key="mrdp_more_btn"):
                    with st.spinner("Fetching more shelf results..."):
                        st.session_state.mrdp_page += 1
                        more = mrdp_run_plan(st.session_state.mrdp_plan, page=st.session_state.mrdp_page)

                        # append (dedupe by tmdb id)
                        existing_ids = set([m.get("id") for m in st.session_state.mrdp_results])
                        for m in more:
                            if m.get("id") not in existing_ids:
                                st.session_state.mrdp_results.append(m)
                                existing_ids.add(m.get("id"))
                        st.rerun()

            with col2:
                st.caption(f"Page {st.session_state.mrdp_page}")

        # Don’t mix Mr.DP results with the rest of the lobby
        return

    # --------------------------------------------------
    # QUICK DOPE HIT (main)
    # --------------------------------------------------
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
            if st.button("✕ Close", use_container_width=True):
                st.session_state.quick_hit = None
                st.rerun()

    st.markdown("---")

    # --------------------------------------------------
    # SEARCH BAR (unchanged baseline behavior, but clear button always works)
    # --------------------------------------------------
    query = st.text_input("🔍 Search for something specific...", key="search_input")

    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        if query and query != st.session_state.search_query:
            st.session_state.search_query = query
            st.session_state.search_page = 1
            st.session_state.search_results = search_movies_only(query, page=1)

    with col_s2:
        if st.button("Clear Search", use_container_width=True, key="clear_search_btn"):
            st.session_state.search_query = ""
            st.session_state.search_results = []
            st.session_state.search_page = 1
            st.rerun()

    if st.session_state.search_results:
        st.markdown(f"### 🔎 Results for '{safe(st.session_state.search_query)}'")
        cols = st.columns(6)
        for i, item in enumerate(st.session_state.search_results[:24]):
            with cols[i % 6]:
                render_movie_card(item)

        if st.button("Load more results", use_container_width=True):
            st.session_state.search_page += 1
            more = search_movies_only(st.session_state.search_query, st.session_state.search_page)
            st.session_state.search_results.extend(more)
            st.rerun()

        return

    # --------------------------------------------------
    # TABS - ALL EMOTION-DRIVEN
    # --------------------------------------------------
    st.markdown("## 🎬 Explore by type")

    t1, t2, t3, t4, t5 = st.tabs(["🎬 Movies", "⚡ Shot", "🎵 Music", "🎙️ Podcasts", "📚 Audiobooks"])

    # TAB 1: MOVIES (emotion-filtered)
    with t1:
        emotion_key = f"{st.session_state.current_feeling}_{st.session_state.desired_feeling}"

        # Reload feed if emotions changed
        if st.session_state.last_emotion_key != emotion_key:
            st.session_state.movies_page = 1
            st.session_state.movies_feed = discover_movies_by_emotion(
                page=1,
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
            st.session_state.last_emotion_key = emotion_key
        elif not st.session_state.movies_feed:
            st.session_state.movies_feed = discover_movies_by_emotion(page=1)

        if st.session_state.movies_feed:
            titles = [m["title"] for m in st.session_state.movies_feed[:20]]
            sorted_titles = sort_by_emotion(
                titles,
                st.session_state.current_feeling,
                st.session_state.desired_feeling
            )

            feed_map = {m["title"]: m for m in st.session_state.movies_feed}
            sorted_feed = []
            for title in sorted_titles:
                if title in feed_map:
                    sorted_feed.append(feed_map[title])

            for m in st.session_state.movies_feed:
                if m not in sorted_feed:
                    sorted_feed.append(m)

            cols = st.columns(6)
            for i, item in enumerate(sorted_feed[:18]):
                with cols[i % 6]:
                    render_movie_card(item)

            if st.button("Load More Movies", use_container_width=True):
                st.session_state.movies_page += 1
                more = discover_movies_by_emotion(
                    page=st.session_state.movies_page,
                    current_feeling=st.session_state.current_feeling,
                    desired_feeling=st.session_state.desired_feeling
                )
                st.session_state.movies_feed.extend(more)
                st.rerun()
        else:
            st.warning("No movies found. Try adjusting your feelings.")

    # TAB 2: SHOT
    with t2:
        st.markdown("### ⚡ Quick dopamine shots")
        video_keyword = FEELING_TO_VIDEOS.get(st.session_state.desired_feeling, "trending viral videos")
        st.markdown(f"**Curated for:** {st.session_state.desired_feeling}")
        yt_search_url = f"https://www.youtube.com/results?search_query={quote_plus(video_keyword)}+shorts"
        st.markdown(
            f"<a href='{yt_search_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"🎥 Watch {safe(video_keyword.title())} Videos →"
            f"</button></a>",
            unsafe_allow_html=True
        )

    # TAB 3: MUSIC
    with t3:
        st.markdown("### 🎵 Music for your mood")
        music_keyword = FEELING_TO_MUSIC.get(st.session_state.desired_feeling, "feel good music")
        st.markdown(f"**Curated for:** {st.session_state.desired_feeling}")
        spotify_search_url = f"https://open.spotify.com/search/{quote_plus(music_keyword)}"
        st.markdown(
            f"<a href='{spotify_search_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"🎧 Listen to {safe(music_keyword.title())} →"
            f"</button></a>",
            unsafe_allow_html=True
        )

    # TAB 4: PODCASTS
    with t4:
        st.markdown("### 🎙️ Podcasts (coming next)")
        st.caption("This tab is scaffolded. Next step: wire a podcast search/provider map.")

    # TAB 5: AUDIOBOOKS
    with t5:
        st.markdown("### 📚 Audiobooks (coming next)")
        st.caption("This tab is scaffolded. Next step: wire Audible/Libby/Hoopla deep links + icons.")

# --------------------------------------------------
# 17. MAIN ROUTER
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
