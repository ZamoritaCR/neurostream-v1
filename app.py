# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v27.6 (STABILITY + SEARCH + CARD UI)
# Fixes:
# - Provider icons contained inside each movie card + wrap into a neat grid
# - Clicking the poster/title opens the best provider link (mobile-friendly)
# - Search supports pagination ("Load more") + a reliable Clear Search button
# - Login/signup card width restored (no more squished layout)
# --------------------------------------------------

import streamlit as st
import os
import requests
import json
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from openai import OpenAI

# --------------------------------------------------
# 1. CONFIG & ASSETS
# --------------------------------------------------
if not hasattr(st, "_page_config_set"):
    st.set_page_config(page_title="Dopamine.watch", page_icon="🧠", layout="wide")
    st._page_config_set = True

APP_NAME = "Dopamine.watch"
LOGO_PATH = "logo.png"

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_PROVIDER_LOGO_BASE = "https://image.tmdb.org/t/p/original"

# Media Assets
VIDEO_URL = "https://youtu.be/-6WCkTeG3Cs"
SPOTIFY_PLAYLIST_ID = "37i9dQZF1DX4sWSpwq3LiO"

# --------------------------------------------------
# 2. MASTER SERVICE MAP
# --------------------------------------------------
# NOTE: We only DISPLAY providers returned by TMDB (for accuracy).
# SERVICE_MAP is used ONLY to build a click-through link for each provider.
SERVICE_MAP = {
    # --- SUBSCRIPTION (VIDEO) ---
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Amazon Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Amazon Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Disney Plus": "https://www.disneyplus.com/search?q={title}",
    "Disney+": "https://www.disneyplus.com/search?q={title}",
    "Max": "https://play.max.com/search?q={title}",
    "HBO Max": "https://play.max.com/search?q={title}",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "Paramount Plus": "https://www.paramountplus.com/search/?q={title}",
    "Paramount+": "https://www.paramountplus.com/search/?q={title}",
    "Apple TV Plus": "https://tv.apple.com/search?term={title}",
    "Apple TV+": "https://tv.apple.com/search?term={title}",
    "Peacock": "https://www.peacocktv.com/search?q={title}",
    "AMC Plus": "https://www.amcplus.com/search?q={title}",
    "AMC+": "https://www.amcplus.com/search?q={title}",
    "Starz": "https://www.starz.com/us/en/search?q={title}",
    "Showtime": "https://www.showtime.com/search?q={title}",
    "MGM+": "https://www.mgmplus.com/search?q={title}",
    "Criterion Channel": "https://www.criterionchannel.com/search?q={title}",
    "MUBI": "https://mubi.com/en/search/films?query={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",
    "Discovery+": "https://www.discoveryplus.com/search?q={title}",

    # --- LIVE TV / AGGREGATORS ---
    "YouTube TV": "https://tv.youtube.com/search?q={title}",
    "fuboTV": "https://www.fubo.tv/search?q={title}",
    "Fubo": "https://www.fubo.tv/search?q={title}",
    "Philo": "https://www.philo.com/search?q={title}",
    "DIRECTV": "https://www.directv.com/search/?query={title}",

    # --- FREE / AD-SUPPORTED (VIDEO) ---
    "Tubi": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details?query={title}",
    "Freevee": "https://www.amazon.com/s?k={title}&i=instant-video",
    "The Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Plex": "https://app.plex.tv/desktop/#!/search?query={title}",
    "Crackle": "https://www.crackle.com/search/{title}",
    "Xumo Play": "https://www.xumo.tv/search?q={title}",
    "Sling Freestream": "https://www.sling.com/freestream",

    # --- RENT / BUY (VIDEO) ---
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Fandango at Home": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Google Play Movies": "https://play.google.com/store/search?q={title}&c=movies",
    "Google Play": "https://play.google.com/store/search?q={title}&c=movies",
    "Apple iTunes": "https://itunes.apple.com/us/search?term={title}&media=movie",

    # --- LIBRARY ---
    "Kanopy": "https://www.kanopy.com/en/search?q={title}",
    "Hoopla": "https://www.hoopladigital.com/search?q={title}",

    # --- ANIME ---
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Funimation": "https://www.funimation.com/search/?q={title}",
    "HIDIVE": "https://www.hidive.com/search?q={title}",
    "RetroCrush": "https://www.retrocrush.tv/search?q={title}",
    "Adult Swim": "https://www.adultswim.com/search?q={title}",

    # --- AUDIO (not used for TMDB providers, but kept for future tabs) ---
    "Spotify": "https://open.spotify.com/search/{title}",
    "Apple Music": "https://music.apple.com/us/search?term={title}",
    "YouTube Music": "https://music.youtube.com/search?q={title}",
    "Amazon Music": "https://music.amazon.com/search/{title}",
    "Tidal": "https://tidal.com/search?q={title}",
    "SoundCloud": "https://soundcloud.com/search?q={title}",
    "Pandora": "https://www.pandora.com/search/{title}",
    "Deezer": "https://www.deezer.com/search/{title}",
    "Audible": "https://www.audible.com/search?keywords={title}",
}

LOGOS = {
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
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
# 4. DATA ENGINE
# --------------------------------------------------
def _clean_results(results):
    clean = []
    for item in results:
        # Skip people
        if item.get("media_type") == "person":
            continue

        # Keep movies + tv
        if item.get("media_type") in ["movie", "tv"] or "title" in item:
            clean.append({
                "id": item.get("id"),
                "type": item.get("media_type", "movie"),
                "title": item.get("title") or item.get("name"),
                "overview": item.get("overview", ""),
                "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}" if item.get("poster_path") else None,
                "release_date": item.get("release_date") or item.get("first_air_date") or "Unknown",
            })
    return clean


@st.cache_data(ttl=3600)
def search_global(query, page=1):
    """Search movies + TV (more complete than /search/multi for our use-case).

    Why:
    - /search/multi mixes in "person" results, which can reduce how many actual titles you see.
    - We want Batman -> many movies + many series, not a page full of people.

    TMDB returns 20 results per page per endpoint.
    """
    if not query:
        return []
    try:
        params = {
            "api_key": get_tmdb_key(),
            "query": query,
            "page": page,
            "include_adult": "false",
        }

        r_movies = requests.get(f"{TMDB_BASE_URL}/search/movie", params=params, timeout=8)
        r_tv = requests.get(f"{TMDB_BASE_URL}/search/tv", params=params, timeout=8)
        r_movies.raise_for_status()
        r_tv.raise_for_status()

        merged = []
        for it in r_movies.json().get("results", []) or []:
            it["media_type"] = "movie"
            merged.append(it)
        for it in r_tv.json().get("results", []) or []:
            it["media_type"] = "tv"
            merged.append(it)

        clean = _clean_results(merged)
        # Dedupe by (type,id)
        out, seen = [], set()
        for item in clean:
            key = (item.get("type"), item.get("id"))
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out
    except Exception:
        return []


@st.cache_data(ttl=600)
def discover_movies(page=1, with_genres=None, sort_by="popularity.desc"):
    params = {
        "api_key": get_tmdb_key(),
        "sort_by": sort_by,
        "watch_region": "US",
        "with_watch_monetization_types": "flatrate|free|ads|rent|buy",
        "page": page,
        "include_adult": "false",
    }
    if with_genres:
        params["with_genres"] = with_genres

    try:
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        return _clean_results(r.json().get("results", []))
    except Exception:
        return []


@st.cache_data(ttl=86400)
def get_streaming_providers(tmdb_id, media_type):
    try:
        m_type = media_type if media_type else "movie"
        r = requests.get(
            f"{TMDB_BASE_URL}/{m_type}/{tmdb_id}/watch/providers",
            params={"api_key": get_tmdb_key()},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return {
            "flatrate": data.get("flatrate", []),
            "free": data.get("free", []),
            "ads": data.get("ads", []),
            "rent": data.get("rent", []),
            "buy": data.get("buy", []),
            "link": data.get("link"),
        }
    except Exception:
        return {"flatrate": [], "free": [], "ads": [], "rent": [], "buy": [], "link": None}


# --------------------------------------------------
# 5. AI ENGINE
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def sort_feed_by_mood(titles, mood):
    # Kept for continuity with your existing flow
    if not titles or not openai_client:
        return titles
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Sort these titles by dopamine preference.\n"
                        f"Mood: {mood}\n"
                        f"Titles: {json.dumps(titles)}\n"
                        "Return ONLY a JSON array."
                    ),
                }
            ],
            temperature=0.1,
        )
        content = response.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "")
        return json.loads(content)
    except Exception:
        return titles


# --------------------------------------------------
# 6. HELPERS (NO MARKDOWN IN URLS)
# --------------------------------------------------
def get_deep_link(provider, title):
    key = (provider or "").strip()
    template = SERVICE_MAP.get(key)

    if not template and key:
        # Fuzzy match
        for k, v in SERVICE_MAP.items():
            if k.lower() in key.lower() or key.lower() in k.lower():
                template = v
                break

    if not template:
        return f"https://www.google.com/search?q=watch+{quote_plus(title)}+on+{quote_plus(provider)}"

    return template.format(title=quote_plus(title))


def tmdb_title_link(tmdb_id, media_type):
    m_type = media_type if media_type in ["movie", "tv"] else "movie"
    return f"https://www.themoviedb.org/{m_type}/{tmdb_id}"


def render_logo(sidebar=False):
    if os.path.exists(LOGO_PATH):
        (st.sidebar if sidebar else st).image(LOGO_PATH, width=200 if sidebar else 240)
    else:
        (st.sidebar if sidebar else st).markdown(f"## 🧠 {APP_NAME}")


# --------------------------------------------------
# 7. STATE & UI
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update(
        {
            # existing state (unchanged behavior)
            "user": None,
            "auth_step": "login",
            "onboarding_complete": False,
            "sorted_feed": None,
            "last_mood": None,

            # feelings/profile
            "current_feeling": None,
            "desired_feeling": None,

            # quick hit
            "show_dope_hit": False,
            "last_hit_id": None,

            # feed paging
            "feed_cache": None,
            "feed_page": 1,

            # search paging
            "search_input": "",
            "search_results": [],
            "search_page": 1,
            "last_search_query": "",
        }
    )
    st.session_state.init = True


st.markdown(
    """
<style>
.stApp { background: radial-gradient(circle at top, #0b0b0b, #000000); color: white; }

.card {
    background: rgba(20,20,20,0.86);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 18px;
}

/* Movie cards */
.movie-card {
    background: rgba(20,20,20,0.78);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    overflow: hidden;
}
.movie-poster {
    width: 100%;
    aspect-ratio: 2 / 3;
    object-fit: cover;
    display: block;
    background: #0f0f10;
}
.movie-meta {
    padding: 12px 12px 14px 12px;
}
.movie-title {
    margin-top: 10px;
    font-size: 0.95rem;
    opacity: 0.92;
}
.movie-title a { color: rgba(255,255,255,0.92); text-decoration: none; }
.movie-title a:hover { text-decoration: underline; }

/* Provider icons (contained + wrapped) */
.provider-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
}
.provider-chip {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    justify-content: center;
}
.provider-chip img {
    width: 22px;
    height: 22px;
    object-fit: contain;
}
.provider-chip:hover {
    border-color: rgba(0,242,234,0.9);
}

/* Force style on Streamlit buttons */
div.stButton > button {
    background: linear-gradient(90deg,#00f2ea,#a100f2) !important;
    color: black !important; font-weight: 800 !important; border: none !important;
    border-radius: 10px !important;
}

/* Floating Quick Hit */
.quick-hit {
    position: fixed;
    right: 22px;
    bottom: 22px;
    z-index: 9999;
}
.quick-hit button {
    padding: 14px 18px !important;
    border-radius: 999px !important;
    box-shadow: 0 14px 40px rgba(0,0,0,0.45);
}

/* Small helper text */
.muted { opacity: 0.72; font-size: 0.9rem; }
</style>
""",
    unsafe_allow_html=True,
)


def _dedupe_providers(provs_dict):
    """Merge providers across categories so we don't show duplicates.

    Returns list of dicts: {name, logo_path, categories:set[str]}
    """
    merged = {}
    cat_map = {
        "flatrate": "Included",
        "free": "Free",
        "ads": "Ads",
        "rent": "Rent",
        "buy": "Buy",
    }

    for key, label in cat_map.items():
        for p in provs_dict.get(key, []) or []:
            name = p.get("provider_name")
            if not name:
                continue
            if name not in merged:
                merged[name] = {
                    "name": name,
                    "logo_path": p.get("logo_path"),
                    "categories": set(),
                }
            merged[name]["categories"].add(label)
            # Prefer a logo if we don't already have one
            if not merged[name].get("logo_path") and p.get("logo_path"):
                merged[name]["logo_path"] = p.get("logo_path")

    # Stable ordering: Included first, then Free, Ads, Rent, Buy
    priority = {"Included": 0, "Free": 1, "Ads": 2, "Rent": 3, "Buy": 4}

    def sort_key(item):
        cats = item["categories"]
        best = min((priority.get(c, 9) for c in cats), default=9)
        return (best, item["name"].lower())

    return sorted(merged.values(), key=sort_key)


def render_movie_card(item, provs):
    """Single-card render in one HTML block so icons NEVER escape the card."""
    title = item.get("title") or "Untitled"
    poster = item.get("poster")
    tmdb_link = tmdb_title_link(item.get("id"), item.get("type"))

    # Choose a "primary" link for the poster/title click:
    # flatrate > free > ads > rent > buy > TMDB
    primary_provider = None
    for k in ["flatrate", "free", "ads", "rent", "buy"]:
        arr = provs.get(k, []) or []
        if arr:
            primary_provider = arr[0].get("provider_name")
            break

    primary_link = get_deep_link(primary_provider, title) if primary_provider else tmdb_link

    providers = _dedupe_providers(provs)
    chips = []
    for p in providers:
        if not p.get("logo_path"):
            continue
        logo_url = f"{TMDB_PROVIDER_LOGO_BASE}{p['logo_path']}"
        link = get_deep_link(p["name"], title)
        cats = ", ".join(sorted(p["categories"]))
        chips.append(
            f"""<a class="provider-chip" href="{link}" target="_blank" rel="noopener noreferrer" title="{p['name']} — {cats}">
                <img src="{logo_url}" alt="{p['name']}"/>
            </a>"""
        )

    # Always include trailer icon (kept from your previous flow)
    yt = get_deep_link("YouTube", title)
    chips.append(
        f"""<a class="provider-chip" href="{yt}" target="_blank" rel="noopener noreferrer" title="Trailer">
                <img src="{LOGOS['YouTube']}" alt="Trailer"/>
            </a>"""
    )

    chips_html = "".join(chips)

    poster_html = (
        f"""<a href="{primary_link}" target="_blank" rel="noopener noreferrer" title="Open in {primary_provider or 'TMDB'}">
                <img class="movie-poster" src="{poster}" alt="{title}"/>
            </a>"""
        if poster
        else f"""<a href="{primary_link}" target="_blank" rel="noopener noreferrer" title="Open in {primary_provider or 'TMDB'}">
                <div class="movie-poster" style="display:flex;align-items:center;justify-content:center;opacity:0.7;">🎬</div>
            </a>"""
    )

    card_html = f"""
    <div class="movie-card">
        {poster_html}
        <div class="movie-meta">
            <div class="provider-grid">{chips_html}</div>
            <div class="movie-title"><a href="{primary_link}" target="_blank" rel="noopener noreferrer">{title}</a></div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# --------------------------------------------------
# 8. SCREEN LOGIC
# --------------------------------------------------
def login_screen():
    # Restored width: bigger middle column + max-width on card
    _, c, _ = st.columns([1, 1.6, 1])
    with c:
        st.markdown("<div class='card' style='max-width:520px;margin:0 auto;'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Welcome back")
        st.caption("Prototype mode: authentication is demo-only right now.")
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
    _, c, _ = st.columns([1, 1.6, 1])
    with c:
        st.markdown("<div class='card' style='max-width:520px;margin:0 auto;'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Create ID")
        st.caption("Prototype mode: authentication is demo-only right now.")
        st.caption("Demo signup (no real authentication yet).")
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
    st.markdown("## 🧠 Let’s calibrate your brain")
    st.caption("This helps us filter content for you.")
    triggers = st.multiselect(
        "What overwhelms you?",
        ["Loud sounds", "Flashing lights", "Fast cuts", "Emotional intensity"],
    )
    genres = st.multiselect(
        "What do you enjoy?",
        ["Action", "Anime", "Sci-Fi", "Comedy", "Documentary", "Fantasy", "Drama"],
    )
    decision = st.radio(
        "When choosing content:",
        ["Decide for me", "Give me 3 options", "Let me explore freely"],
    )

    if st.button("Save & Continue", use_container_width=True):
        st.session_state.baseline_prefs = {
            "triggers": triggers,
            "genres": genres,
            "decision_style": decision,
        }
        st.session_state.onboarding_complete = True
        st.rerun()


def lobby_screen():
    # SIDEBAR
    with st.sidebar:
        render_logo(sidebar=True)
        st.markdown("### 🎛️ Control")
        mood = st.radio("Vibe Check", ["Focus", "Regulate", "Stimulate"])
        st.markdown("---")

        # FEELINGS (selectors instead of all-on-page buttons)
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
        DESIRED = [
            ("🌧️", "Stay Sad"),
            ("🫶", "Comforted"),
            ("🌊", "Calm"),
            ("🛋️", "Relaxed"),
            ("🎯", "Focused"),
            ("🔥", "Energized"),
            ("🚀", "Stimulated"),
            ("🌞", "Happy"),
            ("🎮", "Distracted"),
            ("✨", "Inspired"),
            ("🌱", "Grounded"),
            ("🍿", "Entertained"),
            ("🔍", "Curious"),
            ("🌙", "Sleepy"),
            ("❤️", "Connected"),
        ]

        feeling_opts = ["(no selection)"] + [f"{e} {l}" for e, l in FEELINGS]
        desired_opts = ["(no selection)"] + [f"{e} {l}" for e, l in DESIRED]

        cur = st.selectbox("How do you feel right now?", feeling_opts, index=0)
        want = st.selectbox("What do you want to feel instead?", desired_opts, index=0)

        st.session_state.current_feeling = None if cur == "(no selection)" else cur.split(" ", 1)[1]
        st.session_state.desired_feeling = None if want == "(no selection)" else want.split(" ", 1)[1]

        if st.session_state.current_feeling:
            st.caption(f"Current: **{st.session_state.current_feeling}**")
        if st.session_state.desired_feeling:
            st.caption(f"Target: **{st.session_state.desired_feeling}**")

        c1, c2 = st.columns(2)

        def _clear_profile():
            st.session_state.current_feeling = None
            st.session_state.desired_feeling = None
            st.session_state.show_dope_hit = False
            st.session_state.last_hit_id = None
            st.session_state.feed_cache = None
            st.session_state.feed_page = 1
            st.session_state.search_input = ""
            st.session_state.search_results = []
            st.session_state.search_page = 1
            st.session_state.last_search_query = ""

        with c1:
            st.button("Clear", use_container_width=True, on_click=_clear_profile)
        with c2:
            if st.button("Log out", use_container_width=True):
                st.session_state.user = None
                st.rerun()

    # MAIN
    st.markdown("## 🔎 The Lobby")

    # --------------------------------------------------
    # SEARCH (with pagination + real Clear Search)
    # --------------------------------------------------
    def _clear_search_only():
        st.session_state.search_input = ""
        st.session_state.search_results = []
        st.session_state.search_page = 1
        st.session_state.last_search_query = ""

    s1, s2 = st.columns([6, 1])
    with s1:
        st.text_input(
            "Search for content...",
            placeholder="Movies, TV, Anime...",
            key="search_input",
        )
    with s2:
        st.write("\n")
        st.button("Clear", use_container_width=True, on_click=_clear_search_only)

    query = (st.session_state.search_input or "").strip()

    # Reset pagination when query changes
    if query != st.session_state.last_search_query:
        st.session_state.search_results = []
        st.session_state.search_page = 1
        st.session_state.last_search_query = query

    if query:
        st.markdown("### Results")

        # Fetch first page on-demand
        if not st.session_state.search_results:
            st.session_state.search_results.extend(search_global(query, page=1))

        results = st.session_state.search_results

        if not results:
            st.warning("No results found.")
        else:
            cols = st.columns(6)
            for i, item in enumerate(results):
                with cols[i % 6]:
                    provs = get_streaming_providers(item["id"], item["type"])
                    render_movie_card(item, provs)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("Load more results ⬇️", use_container_width=True):
                st.session_state.search_page += 1
                more = search_global(query, page=st.session_state.search_page)
                if more:
                    st.session_state.search_results.extend(more)
                st.rerun()

        return

    # --------------------------------------------------
    # TRENDING (dynamic based on feelings + paging)
    # --------------------------------------------------
    st.markdown(f"### 🔥 Trending for *{mood}*")
    t1, t2, t3, t4, t5 = st.tabs(["🎬 Movies", "⚡ Shot", "🎵 Music", "🎙️ Podcasts", "📚 Audiobooks"])

    # Genre mapping (simple + safe)
    mood_to_genres = {
        "Sad": "18,10749",  # drama, romance
        "Lonely": "10749,18",  # romance, drama
        "Anxious": "35,10751",  # comedy, family
        "Overwhelmed": "16,35,10751",  # animation, comedy, family
        "Angry": "28,53",  # action, thriller
        "Stressed": "99,36",  # documentary, history
        "Bored": "28,12,878",  # action, adventure, sci-fi
        "Tired": "16,10751",  # animation, family
        "Numb": "9648,18",  # mystery, drama
        "Confused": "9648,878",  # mystery, sci-fi
        "Restless": "28,53,12",  # action, thriller, adventure
        "Focused": "99,36",  # doc, history
        "Calm": "10751,16,35",  # family, animation, comedy
        "Happy": "35,12,16",  # comedy, adventure, animation
        "Excited": "28,12,53",  # action, adventure, thriller
        "Curious": "99,9648,878",  # doc, mystery, sci-fi
    }
    target_to_genres = {
        "Stay Sad": "18,10749",
        "Comforted": "10751,16,35",
        "Calm": "10751,16,35",
        "Relaxed": "35,10751",
        "Focused": "99,36",
        "Energized": "28,12",
        "Stimulated": "28,53,878",
        "Happy": "35,12,16",
        "Distracted": "28,12,35",
        "Inspired": "18,36",
        "Grounded": "99,18",
        "Entertained": "35,12",
        "Curious": "99,9648,878",
        "Sleepy": "16,10751",
        "Connected": "10749,18",
    }

    with t1:
        current = st.session_state.get("current_feeling")
        target = st.session_state.get("desired_feeling")

        with_genres = None
        if target and target in target_to_genres:
            with_genres = target_to_genres[target]
        elif current and current in mood_to_genres:
            with_genres = mood_to_genres[current]

        signature = f"{mood}|{current}|{target}|{with_genres}"

        if st.session_state.feed_cache is None or st.session_state.last_mood != signature:
            st.session_state.feed_page = 1
            feed = discover_movies(page=1, with_genres=with_genres)

            # Keep your AI sort behavior (top 18)
            titles = [m["title"] for m in feed[:18]]
            
            if openai_client:
                with st.spinner("AI is curating your vibe..."):
                    sorted_titles = sort_feed_by_mood(titles, mood)
            else:
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

            st.session_state.feed_cache = ordered
            st.session_state.last_mood = signature

        movies = st.session_state.feed_cache or []
        cols = st.columns(6)
        for i, item in enumerate(movies):
            with cols[i % 6]:
                provs = get_streaming_providers(item["id"], item["type"])
                render_movie_card(item, provs)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Load More Movies ⬇️", use_container_width=True):
            st.session_state.feed_page += 1
            more = discover_movies(page=st.session_state.feed_page, with_genres=with_genres)
            if more:
                st.session_state.feed_cache.extend(more)
            st.rerun()

    with t2:
        st.video(VIDEO_URL)

    with t3:
        components.iframe(
            f"https://open.spotify.com/embed/playlist/{SPOTIFY_PLAYLIST_ID}?utm_source=generator",
            height=380,
        )

    # --------------------------------------------------
    # PODCASTS (TAB)
    # --------------------------------------------------
    with t4:
        st.markdown("### 🎙️ Podcasts")
        st.caption("Coming next: vibe-based podcast picks + deep links.")
        q = st.text_input("Search podcasts...", key="podcast_search", placeholder="Try: ADHD, dopamine, anxiety, focus")
        if q:
            st.link_button("Open in Spotify", f"https://open.spotify.com/search/{quote_plus(q)}")

    # --------------------------------------------------
    # AUDIOBOOKS (TAB)
    # --------------------------------------------------
    with t5:
        st.markdown("### 📚 Audiobooks")
        st.caption("Coming next: audiobook picks + links (Audible, Libby, etc.).")
        q = st.text_input("Search audiobooks...", key="audiobook_search", placeholder="Try: Atomic Habits, Deep Work")
        if q:
            st.link_button("Open in Audible", f"https://www.audible.com/search?keywords={quote_plus(q)}")

    # --------------------------------------------------
    # QUICK DOPE HIT (FLOATING)
    # --------------------------------------------------
    if st.session_state.desired_feeling:
        components.html(
            """
            <div class="quick-hit">
                <form action="#" method="get">
                    <button type="submit">Quick Dope Hit ⚡</button>
                </form>
            </div>
            """,
            height=0,
        )
        if st.session_state.show_dope_hit:
            st.info("Hit delivered ✅ (next step: wire this to a curated one-click pick)")


# --------------------------------------------------
# 9. MAIN ROUTER
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