# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v28.2 - NLP (Mr.DP) + HARD 4x4 PROVIDER GRID
# Baseline v28.0 (NO REFACTOR) + additions requested
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

# --------------------------------------------------
# 2. MASTER SERVICE MAP - DIRECT DEEP LINKS
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
    "Trailer": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
}

# --------------------------------------------------
# 3. API CLIENTS
# --------------------------------------------------
@st.cache_data
def get_tmdb_key():
    return st.secrets["tmdb"]["api_key"]

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
            "api_key": get_tmdb_key(),
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
def search_movies_only(query, page=1):
    """Search for movies/TV only - NO YOUTUBE OR GOOGLE"""
    if not query:
        return []
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/search/multi",
            params={
                "api_key": get_tmdb_key(),
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
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
            params={"api_key": get_tmdb_key()},
            timeout=8
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return {
            "flatrate": data.get("flatrate", [])[:8],  # Max 8 providers
            "rent": data.get("rent", [])[:8]
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
        prompt = f"""You are a dopamine-optimization engine for neurodivergent users.

Current feeling: {current_feeling}
Desired feeling: {desired_feeling}

Reorder these titles to maximize emotional transition and dopamine response.
Prioritize titles that help shift from current to desired feeling.

Titles: {json.dumps(titles[:20])}

Return ONLY a JSON array of titles in optimal order. No explanation."""

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
# 8.5 NLP (Mr.DP) - FREE TEXT -> TMDB PLAN
# --------------------------------------------------
@st.cache_data(show_spinner=False, ttl=3600)
def nlp_to_tmdb_plan(prompt: str):
    """Convert user free text into a TMDB search plan.

    NOTE: This is intentionally utilitarian (no rapport / no emotion commentary).
    """
    p = (prompt or "").strip()
    if not p:
        return {
            "query": "",
            "media_type": "multi",
            "year": None,
            "with_genres": [],
            "sort_by": "popularity.desc",
        }

    # Fallback: if OpenAI not available, use the prompt as the query
    if not openai_client:
        return {
            "query": p,
            "media_type": "multi",
            "year": None,
            "with_genres": [],
            "sort_by": "popularity.desc",
        }

    try:
        sys = (
            "You convert user requests into a JSON plan for searching TMDB. "
            "Return ONLY valid JSON. No markdown.\n"
            "Keys: query (string), media_type (movie|tv|multi), year (int|null), "
            "with_genres (array of ints), sort_by (string).\n"
            "Rules: keep query short (<= 6 words). If user asks for new/latest -> sort_by=release_date.desc. "
            "If user names a title -> query=that title." 
        )

        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys},
                {"role": "user", "content": p},
            ],
            temperature=0.2,
        )

        content = (resp.choices[0].message.content or "").strip()
        plan = json.loads(content)

        # Normalize + defaults
        plan.setdefault("query", "")
        plan.setdefault("media_type", "multi")
        plan.setdefault("year", None)
        plan.setdefault("with_genres", [])
        plan.setdefault("sort_by", "popularity.desc")

        if plan.get("media_type") not in ["movie", "tv", "multi"]:
            plan["media_type"] = "multi"

        if not isinstance(plan.get("with_genres"), list):
            plan["with_genres"] = []

        return plan

    except Exception:
        return {
            "query": p,
            "media_type": "multi",
            "year": None,
            "with_genres": [],
            "sort_by": "popularity.desc",
        }


@st.cache_data(ttl=3600)
def nlp_search_tmdb(plan: dict, page: int = 1):
    """Search TMDB based on the NLP plan."""
    if not plan:
        return []

    query = (plan.get("query") or "").strip()
    year = plan.get("year", None)
    with_genres = plan.get("with_genres", []) or []
    sort_by = plan.get("sort_by", "popularity.desc") or "popularity.desc"

    # If query exists, use search (best recall)
    if query:
        return search_movies_only(query, page=page)

    # Otherwise discover (no query)
    try:
        params = {
            "api_key": get_tmdb_key(),
            "sort_by": sort_by,
            "watch_region": "US",
            "with_watch_monetization_types": "flatrate|rent",
            "page": page,
            "include_adult": "false"
        }

        if with_genres:
            params["with_genres"] = "|".join(map(str, with_genres[:3]))

        if year and isinstance(year, int):
            params["primary_release_year"] = year

        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except Exception:
        return []


# --------------------------------------------------
# 9. DEEP LINK BUILDER (ACTUALLY WORKS)
# --------------------------------------------------
def get_deep_link(provider_name, title, tmdb_id=None):
    """Build working deep link to streaming service"""

    # Normalize provider name
    provider = provider_name.strip()

    # Try direct TMDB ID link first (most reliable)
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

    # Fallback: Direct provider search
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

    # Last resort: Google search for specific provider
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
    return html_lib.escape(s or "")


# --------------------------------------------------
# 11. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "nlp_last_prompt": "",

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

        # NLP (Mr.DP) state (NEW)
        "mrdp_prompt": "",
        "mrdp_plan": None,
        "mrdp_results": [],
        "mrdp_page": 1,
        "mrdp_last_prompt": "",
        "mrdp_history": [],
    })
    st.session_state.init = True

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

/* Provider grid - HARD 4x4 LAYOUT */
.provider-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    padding: 12px;
    max-width: 100%;
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

/* Buttons - GRADIENT DOPAMINE */
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

/* Feeling selectors */
.stSelectbox {
    background: #1a1a2e !important;
    border-radius: 8px !important;
}

/* Small text */
.small-note {
    opacity: 0.75;
    font-size: 0.9rem;
    margin: 12px 0;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #1a1a2e;
    border-radius: 8px;
    padding: 12px 24px;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Mr.DP sidebar styling (lightweight) */
.mrdp-card {
    background: #141426;
    border: 1px solid #2a2a3e;
    border-radius: 12px;
    padding: 12px;
}

.mrdp-title {
    font-weight: 800;
    font-size: 1.0rem;
}

.mrdp-sub {
    opacity: 0.78;
    font-size: 0.85rem;
    margin-top: 4px;
}

.mrdp-chip {
    display: inline-block;
    margin-top: 8px;
    padding: 4px 8px;
    border-radius: 999px;
    border: 1px solid #2a2a3e;
    opacity: 0.9;
    font-size: 0.78rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 13. MOVIE CARD COMPONENT (HARD 4x4 GRID)
# --------------------------------------------------
def render_movie_card(item):
    """Render movie card with HARD 4x4 provider icon grid (max 16)."""
    title = item.get("title", "")
    media_type = item.get("type", "movie")
    tmdb_id = item.get("id")

    # Get providers
    provs = get_streaming_providers(tmdb_id, media_type)
    flatrate = provs.get("flatrate", [])[:8]
    rent = provs.get("rent", [])[:8]

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # Poster
    if item.get("poster"):
        st.image(item["poster"], use_container_width=True)

    # --------------------------------------------------
    # PROVIDER ICONS: HARD 4x4 GRID (MAX 16 TOTAL)
    # Order: flatrate first, then rent, then trailer (if space)
    # --------------------------------------------------
    icons = []
    for p in flatrate:
        icons.append(("watch", p))
    for p in rent:
        icons.append(("rent", p))

    # Cap providers so we never exceed 16 slots
    # Reserve one slot for a Trailer icon when possible
    icons = icons[:15]

    # Trailer icon (always present)
    yt_search = f"https://www.youtube.com/results?search_query={quote_plus(title)}+trailer"
    icons.append(("trailer", {"provider_name": "Trailer", "logo_path": None, "link": yt_search}))

    st.markdown("<div class='provider-grid'>", unsafe_allow_html=True)

    for kind, p in icons[:16]:
        if kind == "trailer":
            link = p["link"]
            logo = LOGOS["Trailer"]
            opacity = "1.0"
            tooltip = "Trailer"
        else:
            provider = p.get("provider_name", "")
            logo_path = p.get("logo_path")
            if not logo_path:
                continue

            link = get_deep_link(provider, title, tmdb_id)
            logo = f"{TMDB_LOGO_URL}{logo_path}"
            opacity = "0.6" if kind == "rent" else "1.0"
            tooltip = f"{provider} ({'Rent/Buy' if kind == 'rent' else 'Included'})"

        st.markdown(
            f"<a href='{safe(link)}' target='_blank' class='provider-btn' style='opacity:{opacity};' title='{safe(tooltip)}'>"
            f"<img src='{safe(logo)}' class='provider-icon' alt='{safe(tooltip)}'>"
            f"</a>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Title and date
    st.markdown(f"<div class='movie-title'>{safe(title)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='movie-sub'>{safe(item.get('release_date', ''))}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# 14. QUICK DOPE HIT ENGINE
# --------------------------------------------------
def get_quick_dope_hit():
    """Get ONE perfect match based on emotions"""
    current = st.session_state.current_feeling
    desired = st.session_state.desired_feeling

    # Get emotion-filtered movies
    candidates = discover_movies_by_emotion(
        page=random.randint(1, 3),
        current_feeling=current,
        desired_feeling=desired
    )

    if not candidates:
        return None

    # Use AI to pick the BEST match
    if openai_client and len(candidates) > 5:
        titles = [m["title"] for m in candidates[:10]]
        sorted_titles = sort_by_emotion(titles, current, desired)

        # Return the top match
        for title in sorted_titles[:1]:
            match = next((m for m in candidates if m["title"] == title), None)
            if match:
                return match

    # Fallback: return top result
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
# 16. MAIN LOBBY - EMOTION-DRIVEN EVERYTHING + NLP (Mr.DP)
# --------------------------------------------------
def lobby_screen():
    # SIDEBAR - ALL CONTROLS
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

        # QUICK DOPE HIT BUTTON IN SIDEBAR
        if st.button("⚡ QUICK DOPE HIT", use_container_width=True):
            with st.spinner("Finding your perfect match..."):
                st.session_state.quick_hit = get_quick_dope_hit()
                st.session_state.quick_hit_count += 1
                st.rerun()

        st.metric("Dope Hits", st.session_state.quick_hit_count)

        # --------------------------------------------------
        # Mr.DP — NLP CHAT BOX (SIDEBAR)
        # --------------------------------------------------
        st.markdown("---")
        st.markdown("### 🧾 Mr.DP")
        st.caption("Your **librarian & curator** — dressed in velvet gloves, armed with chaos-friendly taste.\n\n"
                   "Tell Mr.DP what you want. He’ll quietly pull the best matches from the library.")

        dp_prompt = st.text_area(
            "Ask Mr.DP",
            placeholder="Examples: \n• ‘smart sci-fi from the 90s’\n• ‘something funny, low effort’\n• ‘Batman animated series’\n• ‘new thriller, not too scary’",
            height=110,
            key="mrdp_prompt_input"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Ask", use_container_width=True, key="mrdp_ask_btn"):
                if dp_prompt.strip():
                    with st.spinner("Mr.DP is pulling the catalog..."):
                        st.session_state.nlp_prompt = dp_prompt
                        st.session_state.nlp_last_prompt = dp_prompt
                        st.session_state.nlp_page = 1
                        st.session_state.nlp_plan = nlp_to_tmdb_plan(dp_prompt)
                        st.session_state.nlp_results = nlp_search_tmdb(st.session_state.nlp_plan, page=1)
                        # keep normal search clean
                        st.session_state.search_query = ""
                        st.session_state.search_results = []
                        st.session_state.search_page = 1
                    st.rerun()
        with col_b:
            if st.button("Clear", use_container_width=True, key="mrdp_clear_btn"):
                st.session_state.nlp_prompt = ""
                st.session_state.nlp_plan = None
                st.session_state.nlp_results = []
                st.session_state.nlp_page = 1
                st.session_state.nlp_last_prompt = ""
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Log out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # MAIN CONTENT AREA - ONLY MEDIA
    st.markdown("## 🔎 The Lobby")

    # --------------------------------------------------
    # Mr.DP RESULTS (MAIN AREA)
    # --------------------------------------------------
    if st.session_state.nlp_last_prompt:
        st.markdown(f"### 📚 Mr.DP pulled these for: ‘{safe(st.session_state.nlp_last_prompt)}’")

        if st.session_state.nlp_plan and st.session_state.nlp_plan.get("query"):
            st.caption(f"Search query: {st.session_state.nlp_plan.get('query')}")

        # Clear / Load More controls
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("Load more", use_container_width=True, key="mrdp_load_more"):
                st.session_state.nlp_page += 1
                more = nlp_search_tmdb(st.session_state.nlp_plan, page=st.session_state.nlp_page)
                st.session_state.nlp_results.extend(more)
                st.rerun()
        with c2:
            if st.button("Clear results", use_container_width=True, key="mrdp_clear_main"):
                st.session_state.nlp_prompt = ""
                st.session_state.nlp_plan = None
                st.session_state.nlp_results = []
                st.session_state.nlp_page = 1
                st.session_state.nlp_last_prompt = ""
                st.rerun()
        with c3:
            st.caption(f"Page {st.session_state.nlp_page}")

        if not st.session_state.nlp_results:
            st.warning("No matches yet. Try being more specific (title, genre, actor, year).")
        else:
            cols = st.columns(6)
            for i, item in enumerate(st.session_state.nlp_results):
                with cols[i % 6]:
                    render_movie_card(item)

        return  # Keep Mr.DP results as the primary view

    # --------------------------------------------------
    # Show quick hit result if exists
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

    # SEARCH BAR
    query = st.text_input("🔍 Search for something specific...", key="search_input")

    if query and query != st.session_state.search_query:
        st.session_state.search_query = query
        st.session_state.search_page = 1
        st.session_state.search_results = search_movies_only(query, page=1)

    if st.session_state.search_query and st.button("Clear Search", use_container_width=True):
        st.session_state.search_query = ""
        st.session_state.search_results = []
        st.session_state.search_page = 1
        st.rerun()

    # Show search results
    if st.session_state.search_results:
        st.markdown(f"### 🔎 Results for '{safe(st.session_state.search_query)}'")
        cols = st.columns(6)
        for i, item in enumerate(st.session_state.search_results[:18]):
            with cols[i % 6]:
                render_movie_card(item)

        if len(st.session_state.search_results) >= 18:
            if st.button("Load more results", use_container_width=True):
                st.session_state.search_page += 1
                more = search_movies_only(st.session_state.search_query, st.session_state.search_page)
                st.session_state.search_results.extend(more)
                st.rerun()

        return  # Don't show tabs when searching

    # TABS - ALL EMOTION-DRIVEN
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
            # Show AI-sorted feed
            titles = [m["title"] for m in st.session_state.movies_feed[:20]]
            sorted_titles = sort_by_emotion(
                titles,
                st.session_state.current_feeling,
                st.session_state.desired_feeling
            )

            # Reorder feed
            feed_map = {m["title"]: m for m in st.session_state.movies_feed}
            sorted_feed = []
            for title in sorted_titles:
                if title in feed_map:
                    sorted_feed.append(feed_map[title])

            # Add remaining unsorted
            for m in st.session_state.movies_feed:
                if m not in sorted_feed:
                    sorted_feed.append(m)

            # Display grid
            cols = st.columns(6)
            for i, item in enumerate(sorted_feed[:18]):
                with cols[i % 6]:
                    render_movie_card(item)

            # Load more
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

    # TAB 2: SHOT (TikTok-style videos)
    with t2:
        st.markdown("### ⚡ Quick dopamine shots")

        # Get video keyword based on desired feeling
        video_keyword = FEELING_TO_VIDEOS.get(
            st.session_state.desired_feeling,
            "trending viral videos"
        )

        st.markdown(f"**Curated for:** {safe(st.session_state.desired_feeling)}")

        # Embed YouTube search results (no API needed)
        yt_search_url = f"https://www.youtube.com/results?search_query={quote_plus(video_keyword)}+shorts"

        st.markdown(
            f"<a href='{yt_search_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"🎥 Watch {safe(video_keyword.title())} Videos →"
            f"</button></a>",
            unsafe_allow_html=True
        )

        # Show sample embed
        sample_videos = {
            "Anxious": "https://www.youtube.com/embed/1ZYbU82GVz4",  # Oddly satisfying
            "Sad": "https://www.youtube.com/embed/AK3PWHxoT_E",  # Wholesome animals
            "Bored": "https://www.youtube.com/embed/tlTKTTt47WE",  # Mind blown
            "Tired": "https://www.youtube.com/embed/UfcAVejslrU",  # ASMR
        }

        embed = sample_videos.get(st.session_state.desired_feeling, sample_videos["Bored"])
        components.iframe(embed, height=400)

    # TAB 3: MUSIC (emotion-driven Spotify)
    with t3:
        st.markdown("### 🎵 Music for your mood")

        # Get music keyword based on feelings
        music_keyword = FEELING_TO_MUSIC.get(
            st.session_state.desired_feeling,
            "feel good music"
        )

        st.markdown(f"**Curated for:** {safe(st.session_state.desired_feeling)}")

        # Spotify search embed (works without API)
        spotify_search_url = f"https://open.spotify.com/search/{quote_plus(music_keyword)}"

        st.markdown(
            f"<a href='{spotify_search_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"🎧 Listen to {safe(music_keyword.title())} →"
            f"</button></a>",
            unsafe_allow_html=True
        )

        # Popular playlists by mood
        mood_playlists = {
            "Anxious": "37i9dQZF1DWXe9gFZP0gtP",  # Peaceful Piano
            "Energized": "37i9dQZF1DX76Wlfdnj7AP",  # Beast Mode
            "Happy": "37i9dQZF1DX3rxVfibe1L0",  # Mood Booster
            "Sad": "37i9dQZF1DX7qK8ma5wgG1",  # Life Sucks
            "Focused": "37i9dQZF1DWZeKCadgRdKQ",  # Deep Focus
        }

        playlist_id = mood_playlists.get(st.session_state.desired_feeling, "37i9dQZF1DX3rxVfibe1L0")
        components.iframe(
            f"https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator",
            height=380
        )

    # TAB 4: PODCASTS (emotion-driven)
    with t4:
        st.markdown("### 🎙️ Podcasts for your headspace")

        podcast_topics = {
            "Anxious": "anxiety mental health",
            "Curious": "science explained",
            "Inspired": "motivational success",
            "Bored": "true crime mystery",
            "Focused": "productivity business",
            "Happy": "comedy funny",
        }

        topic = podcast_topics.get(st.session_state.desired_feeling, "trending podcasts")

        st.markdown(f"**Recommended:** {safe(topic.title())}")

        # Spotify podcast search
        spotify_url = f"https://open.spotify.com/search/{quote_plus(topic)}%20podcast"

        st.markdown(
            f"<a href='{spotify_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"🎙️ Find {safe(topic.title())} Podcasts →"
            f"</button></a>",
            unsafe_allow_html=True
        )

        # Featured podcasts
        st.markdown("#### 🔥 Popular picks:")
        featured = [
            ("Huberman Lab", "Science-based mental health", "https://open.spotify.com/show/79CkJF3UJTHFV8Dse3Oy0P"),
            ("The Daily", "News explained", "https://open.spotify.com/show/3IM0lmZxpFAY7CwMuv9H4g"),
            ("SmartLess", "Comedy interviews", "https://open.spotify.com/show/5fYAKY5CtCCpVqfcP1OXzl"),
        ]

        for title, desc, url in featured:
            st.markdown(
                f"**{safe(title)}** - {safe(desc)} | [Listen →]({url})",
                unsafe_allow_html=True
            )

    # TAB 5: AUDIOBOOKS (emotion-driven)
    with t5:
        st.markdown("### 📚 Audiobooks for your vibe")

        audiobook_genres = {
            "Anxious": "self-help mindfulness",
            "Curious": "science history",
            "Inspired": "biography motivation",
            "Bored": "thriller mystery",
            "Sleepy": "fantasy fiction",
            "Happy": "romance comedy",
        }

        genre = audiobook_genres.get(st.session_state.desired_feeling, "bestsellers")

        st.markdown(f"**Genre match:** {safe(genre.title())}")

        # Audible search
        audible_url = f"https://www.audible.com/search?keywords={quote_plus(genre)}"

        st.markdown(
            f"<a href='{audible_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"📖 Browse {safe(genre.title())} Audiobooks →"
            f"</button></a>",
            unsafe_allow_html=True
        )

        # Libro.fm (supports indie bookstores)
        libro_url = f"https://libro.fm/search?search={quote_plus(genre)}"

        st.markdown(
            f"<a href='{libro_url}' target='_blank'>"
            f"<button style='width:100%; padding:20px; font-size:1.1rem;'>"
            f"📚 Support Indie Bookstores (Libro.fm) →"
            f"</button></a>",
            unsafe_allow_html=True
        )

        st.caption("💡 Tip: Check if your library offers free audiobooks via Libby or Hoopla!")


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
