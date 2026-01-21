# FILE: app.py
# DOPAMINE.WATCH v28.4 - SURGICAL FIXES (NO REFACTOR)
# Based on v28.2 - Provider grid 8 max, no Google fallback, working deep links

import streamlit as st
import os
import requests
import json
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from openai import OpenAI
import html as html_lib
import random

if not hasattr(st, "_page_config_set"):
    st.set_page_config(page_title="Dopamine.watch", page_icon="🧠", layout="wide")
    st._page_config_set = True

APP_NAME = "Dopamine.watch"
LOGO_PATH = "logo.gif" if os.path.exists("logo.gif") else "logo.png"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"

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
    "Showtime": "https://www.sho.com/search?q={title}",
    "MGM Plus": "https://www.mgmplus.com/search?q={title}",
    "MGM+": "https://www.mgmplus.com/search?q={title}",
    "Criterion Channel": "https://www.criterionchannel.com/search?q={title}",
    "MUBI": "https://mubi.com/search?query={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",
    "Tubi": "https://tubitv.com/search/{title}",
    "Tubi TV": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details/{title}",
    "Freevee": "https://www.amazon.com/s?k={title}&i=instant-video",
    "Amazon Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "The Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Plex": "https://watch.plex.tv/search?q={title}",
    "Crackle": "https://www.crackle.com/search?q={title}",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Fandango At Home": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Funimation": "https://www.funimation.com/search/?q={title}",
    "HIDIVE": "https://www.hidive.com/search?q={title}",
}

LOGOS = {
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    "Trailer": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
}

@st.cache_data
def get_tmdb_key():
    try:
        return st.secrets["tmdb"]["api_key"]
    except Exception:
        st.error('Missing TMDB API key in secrets.toml')
        return None

try:
    openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])
except Exception:
    openai_client = None

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
            "id": item.get("id"), "type": media_type, "title": title,
            "overview": item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "release_date": item.get("release_date") or item.get("first_air_date") or "Unknown"
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
        if len(genre_ids) < 3:
            genre_ids.extend([g for g in prefs.get("prefer", []) if g not in genre_ids][:3-len(genre_ids)])
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
    except Exception:
        return []

@st.cache_data(ttl=3600)
def search_movies_only(query, page=1):
    api_key = get_tmdb_key()
    if not api_key or not query:
        return []
    try:
        r = requests.get(f"{TMDB_BASE_URL}/search/multi",
                         params={"api_key": api_key, "query": query, "include_adult": "false", "page": page}, timeout=8)
        r.raise_for_status()
        results = [item for item in r.json().get("results", []) if item.get("media_type") in ["movie", "tv"]]
        return _clean_results(results)
    except Exception:
        return []

@st.cache_data(ttl=86400)
def get_streaming_providers(tmdb_id, media_type):
    api_key = get_tmdb_key()
    if not api_key:
        return {"flatrate": [], "rent": []}
    try:
        r = requests.get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
                         params={"api_key": api_key}, timeout=8)
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return {"flatrate": data.get("flatrate", [])[:8], "rent": data.get("rent", [])[:8]}
    except Exception:
        return {"flatrate": [], "rent": []}

@st.cache_data(show_spinner=False)
def sort_by_emotion(titles, current_feeling, desired_feeling):
    if not titles or not openai_client:
        return titles
    try:
        prompt = f"Reorder these titles for best match.\nCurrent: {current_feeling}\nDesired: {desired_feeling}\n\nTitles: {json.dumps(titles[:20])}\n\nReturn ONLY a JSON array of titles."
        response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3)
        content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception:
        return titles

CURRENT_FEELINGS = ["Sad", "Lonely", "Anxious", "Overwhelmed", "Angry", "Stressed", "Bored", "Tired", "Numb", "Confused", "Restless", "Focused", "Calm", "Happy", "Excited", "Curious"]
DESIRED_FEELINGS = ["Comforted", "Calm", "Relaxed", "Focused", "Energized", "Stimulated", "Happy", "Entertained", "Inspired", "Grounded", "Curious", "Sleepy", "Connected"]

def nlp_infer_feelings(prompt):
    t = (prompt or "").lower()
    current, desired = None, None
    if any(k in t for k in ["bore", "boring", "nothing", "meh"]): current = "Bored"
    elif any(k in t for k in ["stress", "burnout"]): current = "Stressed"
    elif any(k in t for k in ["overwhelm", "too much"]): current = "Overwhelmed"
    elif any(k in t for k in ["anxious", "anxiety", "panic"]): current = "Anxious"
    elif any(k in t for k in ["sad", "down", "depressed"]): current = "Sad"
    elif any(k in t for k in ["lonely", "alone"]): current = "Lonely"
    elif any(k in t for k in ["angry", "mad", "pissed"]): current = "Angry"
    elif any(k in t for k in ["tired", "exhaust", "drained"]): current = "Tired"
    if any(k in t for k in ["comfort", "cozy", "wholesome"]): desired = "Comforted"
    elif any(k in t for k in ["relax", "unwind", "easy"]): desired = "Relaxed"
    elif any(k in t for k in ["action", "energy", "hype", "adrenaline"]): desired = "Energized"
    elif any(k in t for k in ["fun", "funny", "comedy", "entertain"]): desired = "Entertained"
    elif any(k in t for k in ["inspir", "motivational"]): desired = "Inspired"
    elif any(k in t for k in ["curious", "learn", "documentary"]): desired = "Curious"
    elif any(k in t for k in ["sleep", "sleepy"]): desired = "Sleepy"
    elif any(k in t for k in ["connect", "romance", "love"]): desired = "Connected"
    return current, desired

@st.cache_data(show_spinner=False, ttl=3600)
def nlp_to_tmdb_plan(prompt):
    p = (prompt or "").strip()
    if not p:
        return {"mode": "search", "query": "", "current_feeling": None, "desired_feeling": None, "raw_prompt": ""}
    h_current, h_desired = nlp_infer_feelings(p)
    heuristic_mode = "discover" if (h_current or h_desired) else "search"
    if not openai_client:
        return {"mode": heuristic_mode, "query": p if heuristic_mode == "search" else "",
                "current_feeling": h_current, "desired_feeling": h_desired, "raw_prompt": p}
    try:
        sys = f"Convert user request to JSON plan. Keys: mode (search|discover), query (string), current_feeling, desired_feeling. If mood -> discover. If title/actor -> search."
        resp = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": sys}, {"role": "user", "content": p}], temperature=0.2)
        content = (resp.choices[0].message.content or "").strip().replace("```json", "").replace("```", "").strip()
        plan = json.loads(content)
        plan.setdefault("mode", heuristic_mode)
        plan.setdefault("query", "")
        plan.setdefault("current_feeling", h_current)
        plan.setdefault("desired_feeling", h_desired)
        plan["raw_prompt"] = p
        if plan.get("current_feeling") not in CURRENT_FEELINGS: plan["current_feeling"] = h_current
        if plan.get("desired_feeling") not in DESIRED_FEELINGS: plan["desired_feeling"] = h_desired
        return plan
    except Exception:
        return {"mode": heuristic_mode, "query": p if heuristic_mode == "search" else "",
                "current_feeling": h_current, "desired_feeling": h_desired, "raw_prompt": p}

@st.cache_data(ttl=3600)
def nlp_search_tmdb(plan, page=1):
    if not plan:
        return []
    mode = (plan.get("mode") or "search").lower()
    query = (plan.get("query") or "").strip()
    current_feeling = plan.get("current_feeling")
    desired_feeling = plan.get("desired_feeling")
    if mode == "discover" and (current_feeling or desired_feeling):
        return discover_movies_by_emotion(page=page, current_feeling=current_feeling, desired_feeling=desired_feeling)
    if query:
        results = search_movies_only(query, page=page)
        if results:
            return results
        h_current, h_desired = nlp_infer_feelings(plan.get("raw_prompt", ""))
        if h_current or h_desired:
            return discover_movies_by_emotion(page=page, current_feeling=h_current, desired_feeling=h_desired)
    return []

def get_deep_link(provider_name, title, tmdb_id=None):
    provider = (provider_name or "").strip()
    safe_title = quote_plus(title)
    if provider in SERVICE_MAP:
        return SERVICE_MAP[provider].format(title=safe_title)
    for key, template in SERVICE_MAP.items():
        if key.lower() in provider.lower() or provider.lower() in key.lower():
            return template.format(title=safe_title)
    return None

def render_logo(sidebar=False):
    if os.path.exists(LOGO_PATH):
        (st.sidebar if sidebar else st).image(LOGO_PATH, width=180 if sidebar else 260)
    else:
        (st.sidebar if sidebar else st).markdown(f"# 🧠 {APP_NAME}")

def safe(s):
    return html_lib.escape(s or "")

if "init" not in st.session_state:
    st.session_state.update({
        "user": None, "auth_step": "login", "onboarding_complete": False,
        "current_feeling": "Bored", "desired_feeling": "Entertained",
        "movies_feed": [], "movies_page": 1, "last_emotion_key": None,
        "quick_hit": None, "quick_hit_count": 0,
        "search_query": "", "search_results": [], "search_page": 1,
        "nlp_prompt": "", "nlp_plan": None, "nlp_results": [], "nlp_page": 1, "nlp_last_prompt": "",
        "show_trailers": True,
    })
    st.session_state.init = True

for _k in ["nlp_prompt", "nlp_plan", "nlp_results", "nlp_page", "nlp_last_prompt", "show_trailers"]:
    if _k not in st.session_state:
        st.session_state[_k] = "" if "prompt" in _k else ([] if "results" in _k else (1 if "page" in _k else (None if "plan" in _k else True)))

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top, #0f0f23, #000000); color: white; }
.card { background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 12px; overflow: hidden; margin-bottom: 16px; }
.card:hover { transform: translateY(-4px); border-color: #00f2ea; }
.provider-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; padding: 10px; max-height: 96px; overflow: hidden; }
.provider-btn { display: flex; align-items: center; justify-content: center; background: #0f0f23; padding: 6px; border-radius: 8px; border: 1px solid #2a2a3e; text-decoration: none !important; min-height: 36px; }
.provider-btn:hover { border-color: #00f2ea; background: #16213e; }
.provider-icon { width: 22px; height: 22px; object-fit: contain; }
.movie-title { padding: 8px 12px; font-weight: 700; color: white; }
.movie-sub { padding: 0 12px 8px; opacity: 0.7; font-size: 0.8rem; }
button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; font-weight: 700 !important; border: none !important; }
.trailer-wrap { padding: 0 10px 10px; }
</style>
""", unsafe_allow_html=True)

def render_movie_card(item):
    title = item.get("title", "")
    media_type = item.get("type", "movie")
    tmdb_id = item.get("id")
    provs = get_streaming_providers(tmdb_id, media_type)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    if item.get("poster"):
        st.image(item["poster"], use_container_width=True)
    for ptype in ["flatrate", "rent"]:
        providers = provs.get(ptype, [])[:8]
        if providers:
            icons_html = ""
            for p in providers:
                provider = p.get("provider_name", "")
                logo_path = p.get("logo_path")
                if not logo_path:
                    continue
                link = get_deep_link(provider, title, tmdb_id)
                if not link:
                    continue
                logo = f"{TMDB_LOGO_URL}{logo_path}"
                opacity = "0.6" if ptype == "rent" else "1"
                icons_html += f"<a href='{safe(link)}' target='_blank' class='provider-btn' style='opacity:{opacity}' title='{safe(provider)}'><img src='{safe(logo)}' class='provider-icon'></a>"
            if icons_html:
                st.markdown(f"<div class='provider-grid'>{icons_html}</div>", unsafe_allow_html=True)
    if st.session_state.get("show_trailers", True):
        yt = f"https://www.youtube.com/results?search_query={quote_plus(title)}+trailer"
        st.markdown(f"<div class='trailer-wrap'><a href='{safe(yt)}' target='_blank' class='provider-btn' title='Trailer'><img src='{safe(LOGOS['Trailer'])}' class='provider-icon'></a></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='movie-title'>{safe(title)}</div><div class='movie-sub'>{safe(item.get('release_date', ''))}</div></div>", unsafe_allow_html=True)

def get_quick_dope_hit():
    candidates = discover_movies_by_emotion(page=random.randint(1, 3), current_feeling=st.session_state.current_feeling, desired_feeling=st.session_state.desired_feeling)
    if not candidates:
        return None
    if openai_client and len(candidates) > 5:
        titles = [m["title"] for m in candidates[:10]]
        sorted_titles = sort_by_emotion(titles, st.session_state.current_feeling, st.session_state.desired_feeling)
        for t in sorted_titles[:1]:
            match = next((m for m in candidates if m["title"] == t), None)
            if match:
                return match
    return candidates[0]

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
    triggers = st.multiselect("What overwhelms you?", ["Loud sounds", "Flashing lights", "Fast cuts", "Emotional intensity", "Violence", "Jump scares"])
    genres = st.multiselect("What do you enjoy?", ["Action", "Anime", "Sci-Fi", "Comedy", "Documentary", "Fantasy", "Drama", "Horror", "Romance"])
    if st.button("Save & Start Watching", use_container_width=True):
        st.session_state.baseline_prefs = {"triggers": triggers, "genres": genres}
        st.session_state.onboarding_complete = True
        st.rerun()

def lobby_screen():
    with st.sidebar:
        render_logo(sidebar=True)
        st.markdown("### 🎯 How do you feel?")
        FEELINGS = [("🌧️", "Sad"), ("🥺", "Lonely"), ("😰", "Anxious"), ("😵‍💫", "Overwhelmed"), ("😡", "Angry"), ("😫", "Stressed"), ("😐", "Bored"), ("😴", "Tired"), ("🫥", "Numb"), ("🤔", "Confused"), ("😬", "Restless"), ("🎯", "Focused"), ("😌", "Calm"), ("😊", "Happy"), ("⚡", "Excited"), ("🧐", "Curious")]
        DESIRED = [("🫶", "Comforted"), ("🌊", "Calm"), ("🛋️", "Relaxed"), ("🎯", "Focused"), ("🔥", "Energized"), ("🚀", "Stimulated"), ("🌞", "Happy"), ("🍿", "Entertained"), ("✨", "Inspired"), ("🌱", "Grounded"), ("🔍", "Curious"), ("🌙", "Sleepy"), ("❤️", "Connected")]
        current_idx = next((i for i, (_, t) in enumerate(FEELINGS) if t == st.session_state.current_feeling), 0)
        current_choice = st.selectbox("Right now I feel...", [f"{e} {t}" for e, t in FEELINGS], index=current_idx)
        st.session_state.current_feeling = current_choice.split(" ", 1)[1]
        desired_idx = next((i for i, (_, t) in enumerate(DESIRED) if t == st.session_state.desired_feeling), 0)
        desired_choice = st.selectbox("I want to feel...", [f"{e} {t}" for e, t in DESIRED], index=desired_idx)
        st.session_state.desired_feeling = desired_choice.split(" ", 1)[1]
        st.markdown("---")
        if st.button("⚡ QUICK DOPE HIT", use_container_width=True):
            st.session_state.quick_hit = get_quick_dope_hit()
            st.session_state.quick_hit_count += 1
            st.rerun()
        st.metric("Dope Hits", st.session_state.quick_hit_count)
        st.markdown("---")
        st.markdown("### 🧾 Mr.DP")
        dp_prompt = st.text_area("Ask Mr.DP", placeholder="'smart sci-fi' or 'something funny'", height=80, key="mrdp_input")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Ask", use_container_width=True):
                if dp_prompt.strip():
                    st.session_state.nlp_last_prompt = dp_prompt
                    st.session_state.nlp_plan = nlp_to_tmdb_plan(dp_prompt)
                    st.session_state.nlp_results = nlp_search_tmdb(st.session_state.nlp_plan, page=1)
                    st.session_state.nlp_page = 1
                    st.rerun()
        with c2:
            if st.button("Clear", use_container_width=True):
                st.session_state.nlp_last_prompt = ""
                st.session_state.nlp_results = []
                st.rerun()
        st.markdown("---")
        st.session_state.show_trailers = st.checkbox("Show trailers", value=st.session_state.get("show_trailers", True))
        st.markdown("---")
        if st.button("🚪 Log out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.markdown("## 🔎 The Lobby")
    if st.session_state.nlp_last_prompt:
        st.markdown(f"### 📚 Mr.DP: '{safe(st.session_state.nlp_last_prompt)}'")
        if not st.session_state.nlp_results:
            st.warning("No matches. Try being more specific.")
        else:
            cols = st.columns(6)
            for i, item in enumerate(st.session_state.nlp_results[:24]):
                with cols[i % 6]:
                    render_movie_card(item)
            if st.button("Load more", key="nlp_more"):
                st.session_state.nlp_page += 1
                more = nlp_search_tmdb(st.session_state.nlp_plan, page=st.session_state.nlp_page)
                st.session_state.nlp_results.extend(more)
                st.rerun()
        return

    if st.session_state.quick_hit:
        st.markdown("### 🎬 Your Perfect Match:")
        cols = st.columns([1, 2, 1])
        with cols[1]:
            render_movie_card(st.session_state.quick_hit)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Another hit"):
                st.session_state.quick_hit = get_quick_dope_hit()
                st.session_state.quick_hit_count += 1
                st.rerun()
        with c2:
            if st.button("✕ Close"):
                st.session_state.quick_hit = None
                st.rerun()

    st.markdown("---")
    query = st.text_input("🔍 Search...", key="search_input")
    if query and query != st.session_state.search_query:
        st.session_state.search_query = query
        st.session_state.search_results = search_movies_only(query, page=1)
    if st.session_state.search_results:
        cols = st.columns(6)
        for i, item in enumerate(st.session_state.search_results[:18]):
            with cols[i % 6]:
                render_movie_card(item)
        return

    st.markdown("## 🎬 Explore")
    t1, t2, t3, t4, t5 = st.tabs(["🎬 Movies", "⚡ Shot", "🎵 Music", "🎙️ Podcasts", "📚 Audiobooks"])
    with t1:
        ek = f"{st.session_state.current_feeling}_{st.session_state.desired_feeling}"
        if st.session_state.last_emotion_key != ek:
            st.session_state.movies_feed = discover_movies_by_emotion(page=1, current_feeling=st.session_state.current_feeling, desired_feeling=st.session_state.desired_feeling)
            st.session_state.last_emotion_key = ek
        if st.session_state.movies_feed:
            titles = [m["title"] for m in st.session_state.movies_feed[:20]]
            sorted_titles = sort_by_emotion(titles, st.session_state.current_feeling, st.session_state.desired_feeling)
            feed_map = {m["title"]: m for m in st.session_state.movies_feed}
            sorted_feed = [feed_map[t] for t in sorted_titles if t in feed_map] + [m for m in st.session_state.movies_feed if m["title"] not in sorted_titles]
            cols = st.columns(6)
            for i, item in enumerate(sorted_feed[:18]):
                with cols[i % 6]:
                    render_movie_card(item)
            if st.button("Load More Movies"):
                st.session_state.movies_page += 1
                more = discover_movies_by_emotion(page=st.session_state.movies_page, current_feeling=st.session_state.current_feeling, desired_feeling=st.session_state.desired_feeling)
                st.session_state.movies_feed.extend(more)
                st.rerun()
    with t2:
        vk = FEELING_TO_VIDEOS.get(st.session_state.desired_feeling, "trending")
        st.markdown(f"### ⚡ {vk.title()}")
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(vk)}+shorts"
        st.markdown(f"<a href='{yt_url}' target='_blank'><button style='width:100%;padding:20px'>🎥 Watch →</button></a>", unsafe_allow_html=True)
    with t3:
        mk = FEELING_TO_MUSIC.get(st.session_state.desired_feeling, "feel good")
        st.markdown(f"### 🎵 {mk.title()}")
        sp_url = f"https://open.spotify.com/search/{quote_plus(mk)}"
        st.markdown(f"<a href='{sp_url}' target='_blank'><button style='width:100%;padding:20px'>🎧 Listen →</button></a>", unsafe_allow_html=True)
        playlists = {"Anxious": "37i9dQZF1DWXe9gFZP0gtP", "Energized": "37i9dQZF1DX76Wlfdnj7AP", "Happy": "37i9dQZF1DX3rxVfibe1L0"}
        pid = playlists.get(st.session_state.desired_feeling, "37i9dQZF1DX3rxVfibe1L0")
        components.iframe(f"https://open.spotify.com/embed/playlist/{pid}", height=380)
    with t4:
        topics = {"Anxious": "anxiety mental health", "Curious": "science explained", "Bored": "true crime mystery"}
        topic = topics.get(st.session_state.desired_feeling, "trending podcasts")
        st.markdown(f"### 🎙️ {topic.title()}")
        sp_url = f"https://open.spotify.com/search/{quote_plus(topic)}%20podcast"
        st.markdown(f"<a href='{sp_url}' target='_blank'><button style='width:100%;padding:20px'>🎙️ Find →</button></a>", unsafe_allow_html=True)
    with t5:
        genres = {"Anxious": "self-help", "Curious": "science history", "Bored": "thriller mystery"}
        genre = genres.get(st.session_state.desired_feeling, "bestsellers")
        st.markdown(f"### 📚 {genre.title()}")
        aud_url = f"https://www.audible.com/search?keywords={quote_plus(genre)}"
        st.markdown(f"<a href='{aud_url}' target='_blank'><button style='width:100%;padding:20px'>📖 Browse →</button></a>", unsafe_allow_html=True)

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
