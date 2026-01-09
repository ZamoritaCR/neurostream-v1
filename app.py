# FILE: app.py
# --------------------------------------------------
# Dopamine.watch v18.1 — SAFE AI REORDER
# --------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import json
from urllib.parse import quote_plus
from supabase import create_client
from openai import OpenAI

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Dopamine.watch", page_icon="🧠", layout="wide")

APP_NAME = "Dopamine.watch"
TAGLINE = "Regulate Your Vibe"
TMDB_REGION = "US"

VIDEO_URL = "https://youtu.be/-6WCkTeG3Cs"
AUTH_IMG = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2564&auto=format&fit=crop"

# --------------------------------------------------
# CONNECTIONS
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

try:
    openai_client = OpenAI(api_key=st.secrets["openai"]["key"])
    AI_ENABLED = True
except:
    AI_ENABLED = False

# --------------------------------------------------
# ASSETS
# --------------------------------------------------
LOGOS = {
    "Netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Amazon Prime Video": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Prime_Video.png",
    "Disney Plus": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
    "Hulu": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Hulu_Logo.svg",
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    "Spotify": "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
    "Audible": "https://upload.wikimedia.org/wikipedia/commons/0/05/Audible_logo.svg",
    "Max": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Max_logo.svg",
}

SERVICE_MAP = {
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Amazon Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Disney Plus": "https://www.disneyplus.com/search",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "YouTube": "https://www.youtube.com/results?search_query=watch+{title}",
    "Audible": "https://www.audible.com/search?keywords={title}",
    "Max": "https://play.max.com/search",
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def render_logo():
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180)
    else:
        st.markdown(f"<h1 style='color:#00E5FF;'>🧠 {APP_NAME}</h1>", unsafe_allow_html=True)

def get_image_url(path):
    if not path:
        return "https://via.placeholder.com/500x750?text=No+Image"
    if path.startswith("http"):
        return path
    return f"https://image.tmdb.org/t/p/w500{path}"

def get_deep_link(provider, title):
    template = SERVICE_MAP.get(provider)
    if not template:
        return f"https://www.google.com/search?q=watch+{quote_plus(title)}"
    return template.format(title=quote_plus(title))

# --------------------------------------------------
# AI — SAFE REORDER (NEVER REMOVES ITEMS)
# --------------------------------------------------
def ai_reorder_movies(movies, mood):
    if not AI_ENABLED or not movies:
        return movies

    try:
        titles = [m["title"] for m in movies]

        prompt = f"""
You are curating media for a neurodivergent user.

Mood rules:
- Focus = calm, slow, documentary, animation
- Regulate = familiar, comforting, mainstream
- Stimulate = action, fast-paced, anime, superhero

Reorder these titles for mood: {mood}

Return ONLY a JSON array of titles.
Do not add or remove titles.

Titles:
{json.dumps(titles)}
"""

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "")
        ordered_titles = json.loads(raw)

        ordered = []
        for t in ordered_titles:
            for m in movies:
                if m["title"] == t:
                    ordered.append(m)
                    break

        return ordered if ordered else movies

    except:
        return movies

# --------------------------------------------------
# DATA
# --------------------------------------------------
@st.cache_data(ttl=1800)
def fetch_movies():
    try:
        url = (
            "https://api.themoviedb.org/3/discover/movie"
            f"?api_key={st.secrets['tmdb']['key']}"
            "&include_adult=false"
            "&sort_by=popularity.desc"
            f"&watch_region={TMDB_REGION}"
            "&with_watch_monetization_types=flatrate|rent"
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
    col1, col2 = st.columns([2,1])
    with col1:
        render_logo()
        st.markdown(f"<h2>{TAGLINE}</h2>", unsafe_allow_html=True)
        st.image(AUTH_IMG, use_container_width=True)
    with col2:
        with st.form("login"):
            email = st.text_input("Email")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Log In"):
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
# MAIN
# --------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    auth_page()
    st.stop()

with st.sidebar:
    render_logo()
    mood = st.radio("How do you want to feel?", ["Focus", "Regulate", "Stimulate"])
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()

tab_movies, tab_shot, tab_music = st.tabs(["🎬 Movies", "⚡ Dopamine Shot", "🎵 Music"])

# --------------------------------------------------
# MOVIES
# --------------------------------------------------
with tab_movies:
    movies = ai_reorder_movies(fetch_movies(), mood)
    cols = st.columns(6)

    for i, movie in enumerate(movies[:18]):
        with cols[i % 6]:
            st.image(get_image_url(movie.get("poster_path")), use_container_width=True)

            provs = fetch_providers(movie["id"])
            for p in provs.get("flatrate", [])[:1]:
                link = get_deep_link(p["provider_name"], movie["title"])
                st.markdown(
                    f"<a href='{link}' target='_blank'>▶ {p['provider_name']}</a>",
                    unsafe_allow_html=True
                )

            st.markdown(
                f"<a href='{get_deep_link('YouTube', movie['title'])}' target='_blank'>🎬 Trailer</a>",
                unsafe_allow_html=True
            )

# --------------------------------------------------
# DOPAMINE SHOT
# --------------------------------------------------
with tab_shot:
    st.subheader("Today’s Dopamine Shot")
    st.video(VIDEO_URL)

# --------------------------------------------------
# MUSIC
# --------------------------------------------------
with tab_music:
    playlist_map = {
        "Focus": "37i9dQZF1DX4sWSpwq3LiO",
        "Regulate": "37i9dQZF1DWZd79rJ6a7lp",
        "Stimulate": "37i9dQZF1DX7HOk71GPfSw"
    }
    components.iframe(
        f"https://open.spotify.com/embed/playlist/{playlist_map[mood]}",
        height=380
    )
