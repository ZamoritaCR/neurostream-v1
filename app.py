# FILE: app.py
# --------------------------------------------------
# "CLOUD READY" VERSION - No separate bouncer needed!
# Run with: python3 -m streamlit run app.py
# --------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components
import requests
from urllib.parse import quote_plus, urlparse

# --------------------------------------------------
# 1. CONFIGURATION & SAFETY
# --------------------------------------------------
st.set_page_config(page_title="NeuroStream", page_icon="🧠", layout="wide")

# Allowed Domains (The Internal Bouncer)
ALLOWED_DOMAINS = {
    "netflix.com", "disneyplus.com", "hulu.com", "max.com", "amazon.com",
    "youtube.com", "crunchyroll.com", "spotify.com", "audible.com",
    "khanacademy.org", "ted.com", "kanopy.com", "hoopladigital.com",
    "apple.com", "google.com", "vudu.com", "tubitv.com"
}

def is_safe_url(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        # Check if the domain (or root domain) is in our allowed list
        for allowed in ALLOWED_DOMAINS:
            if allowed in domain:
                return True
        return False
    except:
        return False

# --- ASSETS (LOGOS) ---
LOGOS = {
    "Spotify": "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
    "Netflix": "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
    "Disney Plus": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Disney%2B_logo.svg",
    "Hulu": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Hulu_Logo.svg",
    "Max": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Max_logo.svg",
    "YouTube": "https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg",
    "Audible": "https://upload.wikimedia.org/wikipedia/commons/0/05/Audible_logo.svg",
    "Khan Academy": "https://upload.wikimedia.org/wikipedia/commons/1/15/Khan_Academy_Logo_2018.svg",
    "Crunchyroll": "https://upload.wikimedia.org/wikipedia/commons/0/08/Crunchyroll_Logo.png",
    "TED-Ed": "https://upload.wikimedia.org/wikipedia/commons/a/aa/TED_three_letter_logo.svg"
}

# --- SERVICE MAP ---
SERVICE_MAP = {
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Disney Plus": "https://www.disneyplus.com/search",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "Max": "https://play.max.com/search",
    "Amazon Prime Video": "https://www.amazon.com/s?k={title}&i=instant-video",
    "YouTube": "https://www.youtube.com/results?search_query=watch+{title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Spotify": "http://open.spotify.com/search/{title}",
    "Audible": "https://www.audible.com/search?keywords={title}",
    "Khan Academy": "https://www.khanacademy.org/search?page_search_query={title}",
    "TED-Ed": "https://www.ted.com/search?q={title}"
}

def get_deep_link(provider_name, title):
    p_name = provider_name.strip()
    template = SERVICE_MAP.get(p_name)
    if not template:
        template = "https://www.youtube.com/results?search_query=watch+{title}+on+" + quote_plus(p_name)
    
    if "{title}" in template:
        raw_link = template.format(title=quote_plus(title))
    else:
        raw_link = template

    # Safety Check inside the app
    if is_safe_url(raw_link):
        return raw_link
    else:
        # Fallback to a safe search if the link looks weird
        return "https://www.google.com/search?q=" + quote_plus(title)

# --- CSS STYLING (THE "LINES & ROUND" UPDATE) ---
st.markdown("""
<style>
    .stApp {background-color: #0e0e0e;}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #1a1a1a;
        border-radius: 10px; color: #fff; font-weight: 600;
        border: 1px solid #333; /* Tab Lines */
    }
    .stTabs [aria-selected="true"] { 
        background-color: #7D4CDB; color: white; border-color: #9D6CEB;
    }

    /* Cards */
    .movie-card {
        background-color: #1a1a1a; border-radius: 12px; padding: 10px; 
        border: 1px solid #333; margin-bottom: 20px;
        transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .movie-card:hover { 
        transform: scale(1.03); 
        border-color: #7D4CDB; 
        box-shadow: 0 0 15px rgba(125, 76, 219, 0.3); /* Glow Effect */
    }
    
    /* Badges */
    .badge {padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; margin-right: 5px; display: inline-block;}
    .badge-low { background-color: #2e7d32; color: #fff; }
    .badge-med { background-color: #f57f17; color: #000; }
    .badge-high { background-color: #c62828; color: #fff; }
    
    /* THE ENHANCED BUTTONS (Round with Lines) */
    .provider-card {
        display: flex; align-items: center; justify-content: space-between;
        background-color: #1E1E1E; 
        border: 1px solid #444; /* The Line */
        border-radius: 50px; /* Fully Round */
        padding: 8px 15px; margin-bottom: 8px;
        text-decoration: none !important; 
        transition: all 0.2s ease-in-out;
    }
    .provider-card:hover { 
        background-color: #333; 
        border-color: #7D4CDB; /* Purple Line on Hover */
        box-shadow: 0 0 10px rgba(125, 76, 219, 0.4); /* Glow */
        transform: translateY(-2px);
    }
    .provider-logo { width: 25px; height: 25px; object-fit: contain; margin-right: 10px; }
    .provider-info { display: flex; flex-direction: column; line-height: 1.2; }
    .provider-name { color: #fff; font-weight: 600; font-size: 0.85rem; }
    .provider-type { color: #aaa; font-size: 0.7rem; }
    .provider-btn-arrow { color: #fff; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATA ---
def get_educational_content():
    return [
        {"title": "The Body Keeps the Score", "type": "Audiobook", "sensory": "Medium", "poster": "https://m.media-amazon.com/images/I/81fljC+KkUL._SL1500_.jpg", "embed": None},
        {"title": "Cosmos: Possible Worlds", "type": "Docu-Series", "sensory": "Low (Calming)", "poster": "https://image.tmdb.org/t/p/w500/u3N2i8c62prX2j4Wq15X4uQ8cM6.jpg", "embed": "https://www.youtube.com/embed/m95iY23Fec0"},
        {"title": "Bluey", "type": "Animation", "sensory": "Medium", "poster": "https://image.tmdb.org/t/p/w500/aPL2hK02iG1iHlA4N8.jpg", "embed": None},
        {"title": "Neuroplasticity", "type": "Lesson", "sensory": "Low", "poster": "https://cdn.kastatic.org/ka-perseus-images/179247497274092b6045d315694b0754860b001a.png", "embed": "https://www.youtube.com/embed/ELpfYCZa87g"},
        {"title": "Mind of a Procrastinator", "type": "Talk", "sensory": "Medium", "poster": "https://pi.tedcdn.com/r/talkstar-photos.s3.amazonaws.com/uploads/703c80e1-482a-4340-9a25-925769742512/TimUrban_2016-embed.jpg", "embed": "https://www.youtube.com/embed/arj7oStGLkU"}
    ]

def get_music_vibes(mood_filter):
    # Real Spotify Embed IDs
    all_playlists = [
        {"title": "Brown Noise", "vibe": "Focus", "sensory": "Low", "embed_id": "37i9dQZF1DX4sWSpwq3LiO", "img": "https://i.scdn.co/image/ab67616d0000b2734121faee8df82c5269fc2856"},
        {"title": "Lo-Fi Beats", "vibe": "Focus", "sensory": "Low", "embed_id": "37i9dQZF1DWWQRwui0ExPn", "img": "https://i.scdn.co/image/ab67616d0000b27352b2a64db801b6973c9f2b8e"},
        {"title": "Hyperpop Energy", "vibe": "Stimulation", "sensory": "High", "embed_id": "37i9dQZF1DX7HOk71GPfSw", "img": "https://i.scdn.co/image/ab67616d0000b273a048d0a0f0259e8674d8e755"},
        {"title": "Deep Sleep", "vibe": "Regulation", "sensory": "Low", "embed_id": "37i9dQZF1DWZd79rJ6a7lp", "img": "https://i.scdn.co/image/ab67616d0000b273614995964082269a919293a5"},
    ]
    if mood_filter == "All": return all_playlists
    return [p for p in all_playlists if p['vibe'] == mood_filter]

# --- API FETCH ---
@st.cache_data(ttl=1800)
def fetch_streaming_movies():
    try:
        url = (f"https://api.themoviedb.org/3/discover/movie?api_key={st.secrets['tmdb']['key']}"
               "&include_adult=false&sort_by=popularity.desc&watch_region=US"
               "&with_watch_monetization_types=flatrate|free|ads|rent")
        results = requests.get(url, timeout=6).json().get("results", [])
        return results
    except: return []

@st.cache_data(ttl=3600)
def fetch_watch_providers(movie_id):
    try:
        url = (f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={st.secrets['tmdb']['key']}")
        data = requests.get(url, timeout=4).json()
        if 'results' in data and 'US' in data['results']: return data['results']['US']
        return None
    except: return None

# --- UI COMPONENTS ---
def get_image_url(path):
    if not path: return "https://via.placeholder.com/500x750?text=No+Image"
    if "http" in path: return path
    return f"https://image.tmdb.org/t/p/w500{path}"

def get_logo_url(path):
    return f"https://image.tmdb.org/t/p/original{path}" if path else None

def render_pro_card(title, poster, sensory_label, content_func):
    # 1. Map Sensory Label to Color
    b_cls = "badge-low"
    if "Medium" in sensory_label: b_cls = "badge-med"
    if "High" in sensory_label: b_cls = "badge-high"
    
    # 2. Render The Card
    st.markdown(f"""
    <div class="movie-card">
        <img src="{poster}" style="width:100%; border-radius:8px;">
        <div style="margin-top:10px;">
            <span class="badge {b_cls}">{sensory_label}</span>
            <div style="font-size:0.9rem; font-weight:bold; color:#eee; margin-top:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{title}</div>
        </div>
    </div>""", unsafe_allow_html=True)
    
    # 3. The Options (Expandable)
    with st.expander("▶ Play / Options"):
        content_func()

def render_provider_link(name, p_type, link, logo_path=None):
    real_logo = LOGOS.get(name)
    if real_logo:
        logo_html = f'<img src="{real_logo}" class="provider-logo">'
    elif logo_path:
        logo_url = get_logo_url(logo_path)
        logo_html = f'<img src="{logo_url}" class="provider-logo">'
    else:
        logo_html = '<div class="provider-logo" style="display:flex; align-items:center; justify-content:center;">🔗</div>'
    
    st.markdown(f"""
    <a href="{link}" target="_blank" class="provider-card">
        <div style="display:flex; align-items:center;">
            {logo_html}
            <div class="provider-info">
                <span class="provider-name">{name}</span>
                <span class="provider-type">{p_type}</span>
            </div>
        </div>
        <div class="provider-btn-arrow">→</div>
    </a>
    """, unsafe_allow_html=True)

# --- MAIN APP LOGIC ---
if 'user' not in st.session_state: st.session_state.user = None
if not st.session_state.user:
    st.title("🧠 NeuroStream")
    st.caption("Sensory-Safe Entertainment & Education")
    if st.button("Log In (Demo Mode)"):
        st.session_state.user = "DemoUser"
        st.rerun()
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    selected_mood = st.radio("Mood:", ["Any Mood", "Happy", "Comforting", "Excited", "Educational"], index=0)
    max_sensory = st.select_slider("Intensity:", options=["Low (Calming)", "Medium (Balanced)", "High (Stimulating)"], value="High (Stimulating)")
    if st.button("Log Out"): st.session_state.user = None; st.rerun()

# --- MAIN PAGE ---
st.title("NeuroStream")
tab_watch, tab_learn, tab_music = st.tabs(["🎬 Movies & TV", "🧠 Learn & Listen", "🎵 Music & Vibe"])

# TAB 1: MOVIES
with tab_watch:
    movies = fetch_streaming_movies()
    # Simple Mock Sensory Data for the Demo since TMDB doesn't have it
    import random
    filtered_movies = []
    for m in movies:
        m['sensory'] = random.choice(["Low (Calming)", "Medium (Balanced)", "High (Stimulating)"])
        m['mood'] = random.choice(["Happy", "Excited", "Comforting", "Melancholy", "Educational"])
        
        # Filter
        if selected_mood != "Any Mood" and m['mood'] != selected_mood: continue
        if max_sensory == "Low (Calming)" and m['sensory'] != "Low (Calming)": continue
        if max_sensory == "Medium (Balanced)" and m['sensory'] == "High (Stimulating)": continue
        filtered_movies.append(m)

    if not filtered_movies: st.warning("No matches found.")
    else:
        st.subheader("🔥 Trending")
        cols = st.columns(4)
        for i, movie in enumerate(filtered_movies[:8]): # Show top 8
            with cols[i % 4]:
                def show_movie_ops():
                    provs = fetch_watch_providers(movie['id'])
                    if provs:
                        for p in provs.get('flatrate', [])[:2]: # Show top 2 streams
                            render_provider_link(p['provider_name'], "Stream", get_deep_link(p['provider_name'], movie['title']), p.get('logo_path'))
                    render_provider_link("YouTube", "Search", get_deep_link("YouTube", movie['title']))
                
                render_pro_card(movie['title'], get_image_url(movie.get('poster_path')), movie['sensory'], show_movie_ops)

# TAB 2: EDUCATION (Updated Layout)
with tab_learn:
    st.caption("Curated Educational Content")
    edu_items = get_educational_content()
    e_cols = st.columns(4) # Matching the Movie Grid
    for i, item in enumerate(edu_items):
        with e_cols[i % 4]:
            def show_edu_ops():
                if item.get('embed'):
                    st.video(item['embed'])
                render_provider_link("Khan Academy", "Learn", get_deep_link("Khan Academy", item['title']))
                render_provider_link("Audible", "Audiobook", get_deep_link("Audible", item['title']))

            render_pro_card(item['title'], get_image_url(item['poster']), item['sensory'], show_edu_ops)

# TAB 3: MUSIC
with tab_music:
    st.subheader("🎧 Brain State Tuner")
    vibe_mode = st.radio("I need to:", ["Focus (Work/Study)", "Stimulate (Energy)", "Regulate (Calm/Sleep)"], horizontal=True)
    
    filter_key = "Focus"
    if "Stimulate" in vibe_mode: filter_key = "Stimulation"
    if "Regulate" in vibe_mode: filter_key = "Regulation"
    
    st.divider()
    playlists = get_music_vibes(filter_key)
    p_cols = st.columns(3)
    for i, p in enumerate(playlists):
        with p_cols[i % 3]:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{p['img']}" style="width:100%; border-radius:8px;">
                <div style="margin-top:10px; font-weight:bold; color:white;">{p['title']}</div>
            </div>""", unsafe_allow_html=True)
            
            with st.expander("▶ Play Here"):
                embed_url = f"https://open.spotify.com/embed/playlist/{p['embed_id']}?utm_source=generator&theme=0"
                components.iframe(embed_url, height=380)
            
            safe_link = f"http://open.spotify.com/search/{quote_plus(p['title'])}"
            render_provider_link("Spotify", "Open App", safe_link)