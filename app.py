# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v21.0
# MOVIES TAB = MAGNET (STABLE BASE)
# --------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components
import requests
import random
import os
from urllib.parse import quote_plus
from supabase import create_client

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Dopamine.watch",
    page_icon="🧠",
    layout="wide"
)

APP_NAME = "Dopamine.watch"
TAGLINE = "Regulate Your Vibe."
TMDB_REGION = "US"
LOGO_PATH = "logo.png"

# --------------------------------------------------
# SUPABASE
# --------------------------------------------------
@st.cache_resource
def init_supabase():
    try:
        return create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
    except:
        return None

supabase = init_supabase()

# --------------------------------------------------
# SESSION
# --------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "hit_me_movie" not in st.session_state:
    st.session_state.hit_me_movie = None

# --------------------------------------------------
# STYLES (ADHD SAFE)
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background:#0e0e0e; color:white; }

.section-title {
    font-size:1.6rem;
    font-weight:800;
    margin:30px 0 10px 0;
}

.movie-card {
    background:#161616;
    border-radius:14px;
    padding:8px;
    border:1px solid #333;
}

.provider {
    display:flex;
    align-items:center;
    gap:8px;
    margin-top:6px;
    background:#222;
    padding:5px 8px;
    border-radius:8px;
    text-decoration:none !important;
    color:white !important;
    font-size:0.85rem;
}

.provider:hover { background:#333; }

.provider img {
    width:20px;
    height:20px;
    object-fit:contain;
}

.badge {
    font-size:0.7rem;
    color:#00E5FF;
    margin-top:4px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOGOS & PROVIDERS
# --------------------------------------------------
LOGOS = {
    "Netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Disney Plus": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
    "Amazon Prime Video": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png",
    "Hulu": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Hulu_Logo.svg",
    "Max": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Max_logo.svg",
    "Apple TV Plus": "https://upload.wikimedia.org/wikipedia/commons/2/28/Apple_TV_Plus_Logo.svg",
    "Paramount Plus": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Paramount_Plus.svg",
    "Peacock": "https://upload.wikimedia.org/wikipedia/commons/d/d3/NBCUniversal_Peacock_Logo.svg",
    "Crunchyroll": "https://upload.wikimedia.org/wikipedia/commons/0/08/Crunchyroll_Logo.svg",
    "Tubi TV": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Tubi_logo.svg",
    "Pluto TV": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Pluto_TV_logo.svg",
    "Freevee": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Amazon_Freevee_logo.svg",
    "Plex": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Plex_logo.svg",
}

SERVICE_MAP = {
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Disney Plus": "https://www.disneyplus.com/search",
    "Amazon Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "Max": "https://play.max.com/search",
    "Apple TV Plus": "https://tv.apple.com/search?term={title}",
    "Paramount Plus": "https://www.paramountplus.com/search",
    "Peacock": "https://www.peacocktv.com/search?q={title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Tubi TV": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details?query={title}",
    "Freevee": "https://www.amazon.com/freevee/search?q={title}",
    "Plex": "https://watch.plex.tv/search?q={title}"
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def render_logo():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
    else:
        st.markdown(f"## 🧠 {APP_NAME}")

def poster(path):
    if not path:
        return "https://via.placeholder.com/500x750?text=No+Image"
    return f"https://image.tmdb.org/t/p/w500{path}"

def provider_link(name, title):
    tpl = SERVICE_MAP.get(name)
    if tpl:
        return tpl.format(title=quote_plus(title))
    return None  # hard stop – no Google by default

def provider_icon(name):
    src = LOGOS.get(name)
    if src:
        return f"<img src='{src}'>"
    return "📺"

# --------------------------------------------------
# TMDB FETCHING
# --------------------------------------------------
@st.cache_data(ttl=1800)
def discover_movies(extra_params=""):
    try:
        url = (
            "https://api.themoviedb.org/3/discover/movie"
            f"?api_key={st.secrets['tmdb']['key']}"
            "&include_adult=false"
            "&sort_by=popularity.desc"
            f"&watch_region={TMDB_REGION}"
            "&with_watch_monetization_types=flatrate|free|ads|rent"
            f"{extra_params}"
        )
        return requests.get(url, timeout=6).json().get("results", [])
    except:
        return []

def fetch_providers(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={st.secrets['tmdb']['key']}"
        data = requests.get(url, timeout=4).json()
        return data.get("results", {}).get(TMDB_REGION, {})
    except:
        return {}

# --------------------------------------------------
# AUTH
# --------------------------------------------------
def auth_page():
    col1, col2 = st.columns([1.5,1])
    with col1:
        render_logo()
        st.markdown(f"### {TAGLINE}")
    with col2:
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Log In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                st.session_state.user = res.user
                st.rerun()
            except:
                st.error("Login failed")
        if st.button("Guest Mode"):
            st.session_state.user = "guest"
            st.rerun()

# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------
if not st.session_state.user:
    auth_page()
    st.stop()

with st.sidebar:
    render_logo()
    if st.button("🎲 Hit Me"):
        all_movies = (
            discover_movies("&with_genres=16") +
            discover_movies("&with_genres=16&with_original_language=ja") +
            discover_movies("")
        )
        if all_movies:
            st.session_state.hit_me_movie = random.choice(all_movies)
            st.toast("Dopamine injected 🎬")
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()

# --------------------------------------------------
# TABS
# --------------------------------------------------
tab_movies, tab_stub = st.tabs(["🎬 Movies", "⚙️ Coming Next"])

# --------------------------------------------------
# MOVIES TAB (MAGNET)
# --------------------------------------------------
with tab_movies:

    # HIT ME FEATURE
    if st.session_state.hit_me_movie:
        m = st.session_state.hit_me_movie
        st.markdown("## 🎲 Hit Me")
        st.image(poster(m["poster_path"]), width=220)
        st.markdown(f"**{m['title']}**")
        provs = fetch_providers(m["id"])
        for p in provs.get("flatrate", [])[:3]:
            link = provider_link(p["provider_name"], m["title"])
            if link:
                st.markdown(
                    f"<a href='{link}' target='_blank' class='provider'>"
                    f"{provider_icon(p['provider_name'])} {p['provider_name']}</a>",
                    unsafe_allow_html=True
                )
        st.divider()

    # CARTOONS & ANIMATION
    st.markdown("<div class='section-title'>🎨 Cartoons & Animation</div>", unsafe_allow_html=True)
    cartoons = discover_movies("&with_genres=16")
    cols = st.columns(4)
    for i, m in enumerate(cartoons[:12]):
        with cols[i % 4]:
            st.image(poster(m["poster_path"]), use_container_width=True)
            provs = fetch_providers(m["id"])
            for p in provs.get("flatrate", [])[:2]:
                link = provider_link(p["provider_name"], m["title"])
                if link:
                    st.markdown(
                        f"<a href='{link}' target='_blank' class='provider'>"
                        f"{provider_icon(p['provider_name'])}</a>",
                        unsafe_allow_html=True
                    )

    # ANIME
    st.markdown("<div class='section-title'>🍣 Anime</div>", unsafe_allow_html=True)
    anime = discover_movies("&with_genres=16&with_original_language=ja")
    cols = st.columns(4)
    for i, m in enumerate(anime[:12]):
        with cols[i % 4]:
            st.image(poster(m["poster_path"]), use_container_width=True)
            provs = fetch_providers(m["id"])
            for p in provs.get("flatrate", [])[:2]:
                link = provider_link(p["provider_name"], m["title"])
                if link:
                    st.markdown(
                        f"<a href='{link}' target='_blank' class='provider'>"
                        f"{provider_icon(p['provider_name'])}</a>",
                        unsafe_allow_html=True
                    )

    # TRENDING LIVE ACTION
    st.markdown("<div class='section-title'>🎬 Trending Now</div>", unsafe_allow_html=True)
    trending = discover_movies("")
    cols = st.columns(4)
    for i, m in enumerate(trending[:12]):
        with cols[i % 4]:
            st.image(poster(m["poster_path"]), use_container_width=True)
            provs = fetch_providers(m["id"])
            for p in provs.get("flatrate", [])[:2]:
                link = provider_link(p["provider_name"], m["title"])
                if link:
                    st.markdown(
                        f"<a href='{link}' target='_blank' class='provider'>"
                        f"{provider_icon(p['provider_name'])}</a>",
                        unsafe_allow_html=True
                    )

# --------------------------------------------------
# STUB TAB (INTENTIONAL)
# --------------------------------------------------
with tab_stub:
    st.info("Spotify, Education, AI curation, and Watchlists come next — now that Movies are stable.")
