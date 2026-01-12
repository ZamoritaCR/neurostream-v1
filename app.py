# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v21.2
# Sprint 1 — AUTH + ONBOARDING + AGGREGATOR (STABLE)
# --------------------------------------------------

import streamlit as st
import os

# --------------------------------------------------
# SAFE PAGE CONFIG (must run once)
# --------------------------------------------------
# This prevents the "StreamlitAPIException" if config is set twice
if "page_config_set" not in st.session_state:
    st.set_page_config(
        page_title="Dopamine.watch",
        page_icon="🧠",
        layout="wide"
    )
    st.session_state.page_config_set = True

# --------------------------------------------------
# 🚨 STARTUP SAFETY CHECK
# --------------------------------------------------
# This catches missing files/libraries and prints the error on screen
try:
    import requests
    # Check if the 'services' folder and files exist
    from services.tmdb import search_global, get_streaming_providers
    from services.llm import get_mood_suggestions
except ImportError as e:
    st.error(f"❌ CRITICAL MISSING DEPENDENCY: {e}")
    st.info("👉 Check your 'requirements.txt' or 'services' folder.")
    st.stop()
except Exception as e:
    st.error(f"❌ STARTUP FAILURE: {e}")
    st.stop()

# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------
APP_NAME = "Dopamine.watch"
LOGO_PATH = "logo.png"

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
def init_state():
    defaults = {
        "user": None,
        "auth_step": None,           # login | signup | onboard
        "username": None,
        "baseline_prefs": {},
        "daily_state": {},
        "onboarding_complete": False,
        "daily_check_done": False,
        "entry_resolved": False,
        "active_search": "",
        "suggestions": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --------------------------------------------------
# STYLES
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b0b0b, #000000);
    color: white;
}
.center { display: flex; justify-content: center; }
.card {
    background: rgba(20,20,20,0.7);
    border-radius: 18px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 20px;
}
button {
    background: linear-gradient(90deg,#00f2ea,#a100f2) !important;
    color: black !important;
    font-weight: 800 !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def render_logo():
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=240)
    else:
        st.markdown(f"## 🧠 {APP_NAME}")

# --------------------------------------------------
# AUTH SCREENS
# --------------------------------------------------
def login_screen():
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Welcome back")

        email = st.text_input("Email")
        st.text_input("Password", type="password")

        if st.button("Log In", use_container_width=True):
            st.session_state.user = email
            st.session_state.auth_step = "done"
            st.rerun()

        st.markdown("---")

        if st.button("Create Account", use_container_width=True):
            st.session_state.auth_step = "signup"
            st.rerun()

        if st.button("👀 Continue as Guest", use_container_width=True):
            st.session_state.user = "guest"
            st.session_state.auth_step = "onboard"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

def signup_screen():
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        render_logo()
        st.markdown("### Create your Dopamine ID")

        username = st.text_input("Username")
        email = st.text_input("Email")
        st.text_input("Password", type="password")

        if st.button("Create Account", use_container_width=True):
            if not username:
                st.error("Username required")
                return
            st.session_state.username = username
            st.session_state.user = email
            st.session_state.auth_step = "onboard"
            st.rerun()

        if st.button("Back", use_container_width=True):
            st.session_state.auth_step = "login"
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# ONBOARDING
# --------------------------------------------------
def onboarding_baseline():
    st.markdown("## 🧠 Let’s calibrate your brain")

    triggers = st.multiselect(
        "What overwhelms you?",
        ["Loud sounds", "Flashing lights", "Fast cuts", "Emotional intensity", "Complex plots"]
    )

    genres = st.multiselect(
        "What do you enjoy?",
        ["Action", "Anime", "Sci-Fi", "Comedy", "Documentary", "Fantasy", "Thriller", "Drama"]
    )

    decision = st.radio(
        "When choosing content:",
        ["Decide for me", "Give me 3 options", "Let me explore freely"]
    )

    if st.button("Save & Continue", use_container_width=True):
        st.session_state.baseline_prefs = {
            "triggers": triggers,
            "genres": genres,
            "decision_style": decision
        }
        st.session_state.onboarding_complete = True
        st.session_state.auth_step = "done"
        st.rerun()

# --------------------------------------------------
# DAILY STATE
# --------------------------------------------------
def daily_state_check():
    st.markdown("## 🧠 How is your brain right now?")

    mood = st.radio(
        "Current state",
        ["Bored", "Anxious", "Stuck", "Hyperfocus"]
    )
    intensity = st.slider("Energy level", 0, 100, 50)

    if st.button("Continue"):
        st.session_state.daily_state = {
            "mood": mood,
            "intensity": intensity
        }
        st.session_state.daily_check_done = True
        st.rerun()

# --------------------------------------------------
# SEARCH
# --------------------------------------------------
def search_screen():
    st.markdown("## 🔎 Find & Locate")

    state = st.session_state.daily_state
    prefs = st.session_state.baseline_prefs

    if state and st.session_state.suggestions is None:
        with st.spinner("🧠 Thinking..."):
            try:
                st.session_state.suggestions = get_mood_suggestions(
                    state.get("mood"),
                    state.get("intensity"),
                    prefs.get("genres") or ["Any"]
                )
            except Exception:
                st.session_state.suggestions = {"reason": "AI unavailable", "queries": []}

    suggestion_data = st.session_state.suggestions
    if suggestion_data and suggestion_data.get("queries"):
        st.info(suggestion_data.get("reason", "Suggested paths"))
        cols = st.columns(3)
        # Ensure we don't crash if fewer than 3 queries returned
        for i, term in enumerate(suggestion_data["queries"][:3]):
            if cols[i].button(term):
                st.session_state.active_search = term
                st.rerun()

    query = st.text_input(
        "Search",
        value=st.session_state.active_search,
        placeholder="e.g. The Bear, Star Wars"
    )

    if query:
        st.session_state.active_search = ""
        try:
            results = search_global(query)
        except Exception:
            st.error("Streaming search unavailable.")
            return

        if not results:
            st.info("No results found.")
            return

        for item in results:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 5])
            with col1:
                if item.get('poster'):
                    st.image(item['poster'], use_container_width=True)
                else:
                    st.markdown("🎬")
            
            with col2:
                st.markdown(f"### {item['title']}")
                st.caption(f"{item['release_date']} • {item['type'].upper()}")
                st.write(item.get("overview", "No description"))

                if st.button("Where can I stream this?", key=item["id"]):
                    try:
                        providers = get_streaming_providers(item["id"], item["type"])
                        st.success(", ".join(providers) if providers else "Not streaming")
                    except Exception:
                        st.warning("Provider lookup failed.")
            
            st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# ENTRY ROUTER
# --------------------------------------------------
# Check query params safely
entry = st.query_params.get("entry")
if entry and not st.session_state.entry_resolved and st.session_state.user is None:
    st.session_state.auth_step = entry
    st.session_state.entry_resolved = True

# --------------------------------------------------
# MAIN ROUTER
# --------------------------------------------------
if st.session_state.user is None:
    if st.session_state.auth_step == "signup":
        signup_screen()
    else:
        login_screen()
    st.stop()

if not st.session_state.onboarding_complete:
    onboarding_baseline()
    st.stop()

if not st.session_state.daily_check_done:
    daily_state_check()
    st.stop()

search_screen()