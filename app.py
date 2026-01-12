# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v22.0 (AGGREGATOR RESTORED)
# --------------------------------------------------

import streamlit as st
import os
from urllib.parse import quote_plus

# --------------------------------------------------
# SAFE PAGE CONFIG
# --------------------------------------------------
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title="Dopamine.watch", page_icon="🧠", layout="wide")
    st.session_state.page_config_set = True

# --------------------------------------------------
# SERVICES & IMPORTS
# --------------------------------------------------
try:
    from services.tmdb import search_global, get_streaming_providers, get_popular_movies
    from services.llm import sort_feed_by_mood
except ImportError:
    st.error("❌ Services missing. Please update your 'services' folder.")
    st.stop()

# --------------------------------------------------
# ASSETS & MAPS (EXTRACTED FROM v16.4)
# --------------------------------------------------
APP_NAME = "Dopamine.watch"
LOGO_PATH = "logo.png"

# Maps provider names to direct deep links
SERVICE_MAP = {
    "Netflix": "[https://www.netflix.com/search?q=](https://www.netflix.com/search?q=){title}",
    "Amazon Prime Video": "[https://www.amazon.com/s?k=](https://www.amazon.com/s?k=){title}&i=instant-video",
    "Disney Plus": "[https://www.disneyplus.com/search](https://www.disneyplus.com/search)",
    "Hulu": "[https://www.hulu.com/search?q=](https://www.hulu.com/search?q=){title}",
    "YouTube": "[https://www.youtube.com/results?search_query=watch](https://www.youtube.com/results?search_query=watch)+{title}",
    "Max": "[https://play.max.com/search](https://play.max.com/search)",
    "Apple TV Plus": "[https://tv.apple.com/search?term=](https://tv.apple.com/search?term=){title}",
    "Peacock": "[https://www.peacocktv.com/search?q=](https://www.peacocktv.com/search?q=){title}"
}

LOGOS = {
    "Netflix": "[https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg](https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg)",
    "YouTube": "[https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg](https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg)",
    # Add others if you have specific SVG links, otherwise we use TMDB logos
}

def get_deep_link(provider_name, movie_title):
    """Generates the direct click-to-watch link."""
    clean_name = provider_name.strip()
    template = SERVICE_MAP.get(clean_name)
    if not template:
        # Fallback to Google Search
        return f"[https://www.google.com/search?q=watch](https://www.google.com/search?q=watch)+{quote_plus(movie_title)}+on+{quote_plus(clean_name)}"
    return template.format(title=quote_plus(movie_title))

# --------------------------------------------------
# STATE INIT
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        "user": None,
        "auth_step": "login",
        "onboarding_complete": False,
        "daily_check_done": False,
        "daily_state": {},
        "sorted_feed": None,
        "last_mood": None
    })
    st.session_state.init = True

# --------------------------------------------------
# STYLES (RESTORED PROVIDER BUTTONS)
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top, #0b0b0b, #000000); color: white; }
.card {
    background: #141414; border-radius: 12px; padding: 0px; 
    overflow: hidden; margin-bottom: 20px; border: 1px solid #333;
}
.card-content { padding: 15px; }
.provider-btn {
    display: flex; align-items: center; gap: 10px;
    background: #222; padding: 8px 12px; border-radius: 6px;
    margin-top: 6px; text-decoration: none !important;
    color: white !important; font-size: 0.85rem; border: 1px solid #333;
    transition: all 0.2s;
}
.provider-btn:hover { background: #333; border-color: #00f2ea; }
.provider-icon { width: 20px; height: 20px; object-fit: contain; border-radius: 4px; }
h3 { margin-bottom: 5px; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# COMPONENTS
# --------------------------------------------------
def render_movie_card(item):
    """Renders a single movie card with poster and deep links."""
    with st.container():
        # Poster
        if item.get("poster"):
            st.image(item["poster"], use_container_width=True)
        else:
            st.markdown("🎬 **No Poster**")

        # Title & Logic
        # We fetch providers ON DEMAND here for the feed, or you can fetch all at once.
        # Note: Fetching providers for 18 movies might be slow. 
        # v16.4 did it inside the loop.
        provs = get_streaming_providers(item['id'], item['type'])
        
        # 1. Flatrate (Netflix, etc.)
        shown_count = 0
        for p in provs.get("flatrate", [])[:1]: # Show top 1
            shown_count += 1
            link = get_deep_link(p["provider_name"], item["title"])
            img = f"[https://image.tmdb.org/t/p/original](https://image.tmdb.org/t/p/original){p['logo_path']}"
            st.markdown(
                f"""
                <a href="{link}" target="_blank" class="provider-btn">
                    <img src="{img}" class="provider-icon">
                    <span>Watch on {p['provider_name']}</span>
                </a>
                """, unsafe_allow_html=True
            )

        # 2. Rent (if no flatrate shown)
        if shown_count == 0:
            for p in provs.get("rent", [])[:1]:
                link = get_deep_link(p["provider_name"], item["title"])
                img = f"[https://image.tmdb.org/t/p/original](https://image.tmdb.org/t/p/original){p['logo_path']}"
                st.markdown(
                    f"""
                    <a href="{link}" target="_blank" class="provider-btn">
                        <img src="{img}" class="provider-icon">
                        <span>Rent on {p['provider_name']}</span>
                    </a>
                    """, unsafe_allow_html=True
                )

        # 3. Always show Trailer
        yt_link = get_deep_link("YouTube", item["title"])
        st.markdown(
            f"""
            <a href="{yt_link}" target="_blank" class="provider-btn">
                <img src="{LOGOS['YouTube']}" class="provider-icon">
                <span>Trailer</span>
            </a>
            """, unsafe_allow_html=True
        )
        st.caption(f"{item['title']}")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# --------------------------------------------------
# SCREENS
# --------------------------------------------------
def lobby_screen():
    st.markdown(f"## 🧠 The Lobby")
    
    # 1. Search Bar (Top)
    query = st.text_input("Search for specific content...", placeholder="Type a movie or show...")
    
    if query:
        st.markdown("### 🔎 Search Results")
        results = search_global(query)
        if not results:
            st.warning("No results found.")
        else:
            cols = st.columns(6)
            for i, item in enumerate(results):
                with cols[i % 6]:
                    render_movie_card(item)
        return

    # 2. Aggregator Feed (If no search)
    mood = st.session_state.daily_state.get("mood", "Neutral")
    st.markdown(f"### 🔥 Trending for *{mood}*")
    
    # Fetch Feed
    feed = get_popular_movies()
    
    # Sort Feed (AI) - Only run if mood changed or feed not sorted
    if st.session_state.sorted_feed is None or st.session_state.last_mood != mood:
        titles = [m["title"] for m in feed[:18]] # limit to 18 for speed
        with st.spinner(f"🧠 Re-ordering feed for {mood} state..."):
            sorted_titles = sort_feed_by_mood(titles, mood)
        
        # Re-construct list in new order
        ordered_feed = []
        for t in sorted_titles:
            for m in feed:
                if m["title"] == t:
                    ordered_feed.append(m)
                    break
        # Add leftovers
        for m in feed:
            if m not in ordered_feed:
                ordered_feed.append(m)
                
        st.session_state.sorted_feed = ordered_feed
        st.session_state.last_mood = mood
    
    # Render Grid
    cols = st.columns(6) # 6 columns like v16.4
    for i, item in enumerate(st.session_state.sorted_feed[:18]):
        with cols[i % 6]:
            render_movie_card(item)

# --------------------------------------------------
# ROUTING
# --------------------------------------------------
# (Simplified auth for brevity - assuming you have the auth/onboarding from previous step)
def daily_state_check():
    st.markdown("## 🧠 Status Check")
    mood = st.radio("Current Vibe", ["Focus", "Regulate", "Stimulate"])
    if st.button("Enter Lobby"):
        st.session_state.daily_state = {"mood": mood}
        st.session_state.daily_check_done = True
        st.rerun()

# --- MAIN EXECUTION ---
if not st.session_state.user:
    # Quick Guest/Auth Toggle for testing
    if st.button("Login as Guest"):
        st.session_state.user = "guest"
        st.rerun()
    st.stop()

if not st.session_state.daily_check_done:
    daily_state_check()
else:
    lobby_screen()