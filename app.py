import streamlit as st
import pandas as pd
import requests
import time
from urllib.parse import quote_plus, urlparse, parse_qs
from supabase import create_client, Client

# --- PAGE CONFIG ---
st.set_page_config(page_title="NeuroStream", page_icon="🧠", layout="wide")

# --- 1. SETUP & CONNECTIONS ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        return None

supabase = init_connection()

# --- 2. DEEP LINK LOGIC (The "Walled Garden" Map) ---
# We distinguish between "Direct Search" (Netflix) and "Manual Search" (Disney)
# so the user knows exactly what to expect.

SERVICE_MAP = {
    # ✅ CLASS A: DIRECT SEARCH (Opens results directly)
    "Netflix": {
        "url": "https://www.netflix.com/search?q={title}",
        "action": "Search"
    },
    "Hulu": {
        "url": "https://www.hulu.com/search?q={title}",
        "action": "Search"
    },
    "Peacock": {
        "url": "https://www.peacocktv.com/watch/search?q={title}",
        "action": "Search"
    },
    "Paramount Plus": {
        "url": "https://www.paramountplus.com/search/?q={title}",
        "action": "Search"
    },
    "Apple TV Plus": {
        "url": "https://tv.apple.com/search?term={title}",
        "action": "Search"
    },
    "Amazon Prime Video": {
        "url": "https://www.amazon.com/gp/video/search/ref=atv_nb_sr?phrase={title}&ie=UTF8",
        "action": "Search"
    },
    
    # ⚠️ CLASS B: MANUAL SEARCH (Disney/Max blocked direct links)
    # We link to the Search Bar page to avoid 404s.
    "Disney Plus": {
        "url": "https://www.disneyplus.com/search",
        "action": "Open App" # Specific label so user knows they must type
    },
    "Max": {
        "url": "https://play.max.com/search",
        "action": "Open App"
    }
}

def get_deep_link_info(provider_name, movie_title):
    """
    Returns the URL and the Action Label ('Search' vs 'Open App')
    """
    if provider_name in SERVICE_MAP:
        entry = SERVICE_MAP[provider_name]
        template = entry["url"]
        
        if "{title}" in template:
            clean_title = quote_plus(movie_title)
            final_url = template.format(title=clean_title)
            return final_url, entry["action"]
        else:
            return template, entry["action"]
            
    # Fallback
    return f"https://www.google.com/search?q=watch+{quote_plus(movie_title)}", "Find"

# --- 3. TMDB API FUNCTIONS ---
def fetch_streaming_movies():
    try:
        api_key = st.secrets["tmdb"]["key"]
        # Filter for Subscription Streaming (Flatrate) in US
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_monetization_types=flatrate"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get('results', [])
        return []
    except:
        return []

def fetch_watch_providers(movie_id):
    try:
        api_key = st.secrets["tmdb"]["key"]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and 'US' in data['results']:
                return data['results']['US']
        return None
    except:
        return None

def get_image_url(path):
    if path:
        return f"https://image.tmdb.org/t/p/w500{path}"
    return "https://via.placeholder.com/500x750?text=No+Image"

def get_backdrop_url(path):
    if path:
        return f"https://image.tmdb.org/t/p/original{path}"
    return None

# --- 4. AUTH & DB FUNCTIONS ---
def sign_up(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response, None
    except Exception as e:
        return None, str(e)

def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response, None
    except Exception as e:
        return None, str(e)

def send_reset_email(email):
    try:
        supabase.auth.reset_password_email(email)
        return True, None
    except Exception as e:
        return False, str(e)

def update_password(new_password):
    try:
        supabase.auth.update_user({"password": new_password})
        return True, None
    except Exception as e:
        return False, str(e)

def login_with_url(url_string):
    try:
        if "#" in url_string:
            fragment = url_string.split("#")[1]
            params = dict(item.split("=") for item in fragment.split("&") if "=" in item)
            access_token = params.get("access_token")
            refresh_token = params.get("refresh_token")
            if access_token and refresh_token:
                response = supabase.auth.set_session(access_token, refresh_token)
                return response, None
        
        parsed_url = urlparse(url_string)
        query_params = parse_qs(parsed_url.query)
        if 'token_hash' in query_params and 'type' in query_params:
            token_hash = query_params['token_hash'][0]
            email_type = query_params['type'][0]
            response = supabase.auth.verify_otp({"token_hash": token_hash, "type": email_type})
            return response, None
        return None, "Invalid link."
    except Exception as e:
        return None, str(e)

def add_to_db(user_email, title, poster, tmdb_id):
    if supabase:
        data = {"user_name": user_email, "movie_title": title, "poster_url": poster, "tmdb_id": tmdb_id}
        supabase.table("watchlist").insert(data).execute()

def remove_from_db(item_id):
    if supabase:
        supabase.table("watchlist").delete().eq("id", item_id).execute()

def get_user_watchlist(user_email):
    if supabase:
        response = supabase.table("watchlist").select("*").eq("user_name", user_email).execute()
        return response.data
    return []

# --- 5. SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 6. STYLING (Neuro-Friendly) ---
st.markdown("""
<style>
    .stApp {background-color: #0e0e0e;}
    .hero-container {
        padding: 4rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        background-size: cover;
        background-position: center;
        box-shadow: inset 0 0 0 2000px rgba(0,0,0,0.7);
        border: 1px solid #333;
    }
    
    .movie-card {
        position: relative;
        margin-bottom: 10px;
    }

    .movie-poster {
        border-radius: 12px;
        transition: transform 0.2s ease-in-out; 
        width: 100%;
        display: block;
        border: 1px solid #333;
    }
    .movie-poster:hover {
        transform: scale(1.03);
        cursor: pointer;
        border: 2px solid #7D4CDB;
        box-shadow: 0 0 15px rgba(125, 76, 219, 0.4);
    }

    .service-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: rgba(0, 0, 0, 0.85);
        color: white;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
        backdrop-filter: blur(4px);
        border: 1px solid #444;
        pointer-events: none;
    }
    
    /* New: Action Hint on Hover */
    .action-hint {
        font-size: 0.8rem;
        color: #bbb;
        text-align: center;
        margin-top: 5px;
    }

    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 7. LANDING PAGE ---
if not st.session_state.user:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.title("Stream Smarter.")
        st.write("The streaming guide for Neurodivergent Minds.")
        st.info("💡 **Demo:** Create an account to see the live feed!")
    with col2:
        with st.container(border=True):
            auth_mode = st.radio("Option", ["Log In", "Sign Up", "Forgot Password?"], horizontal=True)
            
            if auth_mode == "Forgot Password?":
                st.subheader("Reset")
                tab1, tab2 = st.tabs(["📧 Email", "🔗 Paste Link"])
                with tab1:
                    with st.form("reset_form"):
                        reset_email = st.text_input("Email")
                        if st.form_submit_button("Send Link"):
                            send_reset_email(reset_email)
                            st.success("Check email!")
                with tab2:
                    with st.form("verify_form"):
                        url = st.text_input("Paste Link")
                        if st.form_submit_button("Verify"):
                            res, err = login_with_url(url)
                            if res and res.user:
                                st.session_state.user = res.user
                                st.rerun()

            elif auth_mode == "Sign Up":
                with st.form("signup_form"):
                    email = st.text_input("Email")
                    passw = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign Up"):
                        res, err = sign_up(email, passw)
                        if res: st.success("Created! Log in now.")
                        elif err: st.error(err)

            else: # Log In
                with st.form("login_form"):
                    email = st.text_input("Email")
                    passw = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Log In")
                    
                    if submitted:
                        res, err = sign_in(email, passw)
                        if res and res.user:
                            st.session_state.user = res.user
                            st.rerun()
                        elif err:
                            st.error(f"Login failed: {err}")
    st.stop()

# --- 8. MAIN APP ---
user_email = st.session_state.user.email

with st.sidebar:
    st.title("🧠 NeuroStream")
    st.write(f"👤 {user_email}")
    menu = st.radio("Menu", ["🍿 Live Feed", "📚 Education", "❤️ Watchlist", "🔐 Change Password"])
    st.divider()
    if st.button("Log Out"):
        st.session_state.user = None
        supabase.auth.sign_out()
        st.rerun()

if menu == "🔐 Change Password":
    st.header("Change Password")
    with st.form("pwd"):
        p1 = st.text_input("New", type="password")
        p2 = st.text_input("Confirm", type="password")
        if st.form_submit_button("Update"):
            if p1 == p2:
                update_password(p1)
                st.success("Updated! Logging out...")
                time.sleep(2)
                st.session_state.user = None
                supabase.auth.sign_out()
                st.rerun()
            else:
                st.error("Mismatch.")

elif menu == "📚 Education":
    st.header("Neuro-Support Hub 🌿")
    st.video("https://www.youtube.com/watch?v=JhzxqLxY5xM")

elif menu == "❤️ Watchlist":
    st.header("Your Safe List")
    my_list = get_user_watchlist(user_email)
    if my_list:
        cols = st.columns(4)
        for index, item in enumerate(my_list):
            with cols[index % 4]:
                st.image(item['poster_url'])
                if st.button("Remove", key=f"del_{item['id']}"):
                    remove_from_db(item['id'])
                    st.rerun()
    else:
        st.info("List is empty.")

elif menu == "🍿 Live Feed":
    movies = fetch_streaming_movies()
    
    if movies:
        hero = movies[0]
        backdrop = get_backdrop_url(hero.get('backdrop_path'))
        st.markdown(f"""
        <div class="hero-container" style="background-image: url('{backdrop}');">
            <h1>{hero['title']}</h1>
            <p>{hero['overview'][:150]}...</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Streaming Now")
    st.caption("Click a poster to watch.")
    
    current_watchlist = get_user_watchlist(user_email)
    saved_titles = [item['movie_title'] for item in current_watchlist] if current_watchlist else []

    cols = st.columns(4)
    for index, movie in enumerate(movies):
        with cols[index % 4]:
            poster_url = get_image_url(movie.get('poster_path'))
            providers = fetch_watch_providers(movie['id'])
            
            # --- INTELLIGENT DEEP LINKING ---
            deep_link = "#"
            service_name = "Watch"
            action_label = "Open"
            
            if providers and 'flatrate' in providers:
                primary_provider = providers['flatrate'][0]['provider_name']
                service_name = primary_provider
                
                # GET LINK AND ACTION TYPE (Search vs Open App)
                deep_link, action_label = get_deep_link_info(primary_provider, movie['title'])
            else:
                service_name = "Details"
                deep_link = f"https://www.themoviedb.org/movie/{movie['id']}"

            # --- RENDER CARD ---
            # Badge text now adapts: "On Netflix" vs "Open Disney+"
            st.markdown(f"""
                <div class="movie-card">
                    <a href="{deep_link}" target="_blank" title="Click to {action_label}">
                        <div class="service-badge">{service_name}</div>
                        <img src="{poster_url}" class="movie-poster">
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            # Helper text for Disney/Max users
            if action_label == "Open App":
                st.caption(f"⚠️ Type '{movie['title']}'")
            else:
                st.caption(f"✅ {action_label} Results")

            # Watchlist Button
            if movie['title'] in saved_titles:
                st.button("✅ Saved", key=f"btn_{index}", disabled=True)
            else:
                if st.button("➕ Add", key=f"btn_{index}"):
                    add_to_db(user_email, movie['title'], poster_url, movie['id'])
                    st.rerun()