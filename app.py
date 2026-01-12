st.title("SIGN UP SCREEN TEST")

st.text_input("Username")
st.text_input("Email")
st.text_input("Password", type="password")

st.button("Create account")
st.stop()

# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v21.0
# Sprint 1 — AUTH + ONBOARDING ONLY
# --------------------------------------------------

import streamlit as st
import os
import time

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Dopamine.watch",
    page_icon="🧠",
    layout="wide"
)

APP_NAME = "Dopamine.watch"
LOGO_PATH = "logo.png"

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
def init_state():
    defaults = {
        "user": None,
        "auth_step": None,          # login | signup | onboard
        "username": None,
        "baseline_prefs": {},
        "daily_state": {},
        "onboarding_complete": False,
        "entry_resolved": False     # ✅ ADDITION (required)
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# --------------------------------------------------
# STYLES (NEURODIVERGENT FIRST)
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b0b0b, #000000);
    color: white;
}

.center {
    display: flex;
    justify-content: center;
    align-items: center;
}

.glow {
    filter: drop-shadow(0 0 25px #00f2ea);
}

.card {
    background: rgba(20,20,20,0.7);
    border-radius: 18px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.1);
}

button {
    background: linear-gradient(90deg,#00f2ea,#a100f2) !important;
    color: black !important;
    font-weight: 800 !important;
    border: none !important;
}

label {
    font-size: 0.9rem !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def render_logo(centered=True):
    if os.path.exists(LOGO_PATH):
        if centered:
            st.markdown("<div class='center'>", unsafe_allow_html=True)
        st.image(LOGO_PATH, width=240)
        if centered:
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"## 🧠 {APP_NAME}")

# --------------------------------------------------
# AUTH SCREENS
# --------------------------------------------------
def login_screen():
    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        render_logo()
        st.markdown("### Welcome back")

        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

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
    left, center, right = st.columns([1, 1.2, 1])

    with center:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        render_logo()
        st.markdown("### Create your Dopamine ID")

        username = st.text_input("Username (public)")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

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
# ONBOARDING — BASELINE (ONE TIME)
# --------------------------------------------------
def onboarding_baseline():
    st.markdown("## 🧠 Let’s calibrate your brain")
    st.caption("Nothing here is permanent. You can change this anytime.")

    with st.container():
        st.markdown("### 🚨 Sensory Triggers")
        triggers = st.multiselect(
            "What overwhelms you?",
            [
                "Loud sounds", "Flashing lights", "Fast cuts",
                "Emotional intensity", "Complex plots"
            ]
        )

        st.markdown("### 🎬 Genre Affinity")
        genres = st.multiselect(
            "What do you enjoy? (All allowed)",
            [
                "Action", "Anime", "Sci-Fi", "Comedy", "Documentary",
                "Fantasy", "Thriller", "Drama", "Animation", "Mystery"
            ]
        )

        st.markdown("### 🧩 Decision Style")
        decision = st.radio(
            "When choosing content, you prefer:",
            [
                "Decide for me",
                "Give me 3 options",
                "Let me explore freely"
            ]
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
# DAILY STATE (REPEATABLE — NOT SAVED PERMANENTLY)
# --------------------------------------------------
def daily_state_check():
    st.markdown("## 🧠 How is your brain *right now*?")
    st.caption("This resets every day.")

    mood = st.radio(
        "Current state",
        [
            "Bored / Under-stimulated",
            "Anxious / Over-stimulated",
            "Stuck / Can’t decide",
            "Locked-in / Hyperfocus"
        ]
    )

    intensity = st.slider(
        "Energy level",
        0, 100, 50
    )

    st.session_state.daily_state = {
        "mood": mood,
        "intensity": intensity
    }

    if st.button("Continue"):
        st.success("Calibration complete.")
        st.stop()

# --------------------------------------------------
# ENTRY ROUTER (EXPLICIT LOGIN / SIGNUP OVERRIDE)
# --------------------------------------------------
query_params = st.query_params
entry = query_params.get("entry", None)

if entry and not st.session_state.entry_resolved and st.session_state.user is None:
    if entry == "login":
        st.session_state.entry_resolved = True
        login_screen()
        st.stop()

    elif entry == "signup":
        st.session_state.entry_resolved = True
        signup_screen()
        st.stop()

# --------------------------------------------------
# ROUTER (DEFAULT APP FLOW)
# --------------------------------------------------
if st.session_state.user is None:
    if st.session_state.auth_step == "login":
        login_screen()
    elif st.session_state.auth_step == "signup":
        signup_screen()
    st.stop()

if not st.session_state.onboarding_complete:
    onboarding_baseline()
    st.stop()

daily_state_check()
