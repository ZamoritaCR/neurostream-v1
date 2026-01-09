import streamlit as st
import pandas as pd
import requests
import time
from urllib.parse import urlparse, parse_qs
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

# --- 2. TMDB API FUNCTIONS (Strictly Streaming) ---
def fetch_streaming_movies():
    """
    Fetches popular movies that are SPECIFICALLY streaming on Flatrate services (Netflix, etc)
    Filters out theatrical-only movies like Zootopia 2.
    """
    try:
        api_key = st.secrets["tmdb"]["key"]
        # discover endpoint allows strict filtering
        # with_watch_monetization_types=flatrate -> Only subscription services (no rent/buy)
        # watch_region=US -> US Availability (Change to GB/CA etc if needed)
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc&watch_region=US&with_watch_monetization_types=flatrate"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json().get('results', [])
        return []
    except:
        return []

def fetch_watch_providers(movie_id):
    """Checks exact providers for the cards."""
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

# --- 3. AUTH FUNCTIONS ---
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

# --- 4. DATABASE FUNCTIONS ---
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

# --- 6. STYLING ---
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
    .movie-poster {
        border-radius: 10px;
        transition: transform 0.2s; 
        width: 100%;
        margin-bottom: 10px;
    }
    .movie-poster:hover {
        transform: scale(1.05);
        cursor: pointer;
        border: 2px solid #ff4b4b;
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
    # NOW CALLING THE NEW FUNCTION
    movies = fetch_streaming_movies()
    
    # HERO SECTION
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
    st.caption("These movies are available on subscription services (US).")
    
    current_watchlist = get_user_watchlist(user_email)
    saved_titles = [item['movie_title'] for item in current_watchlist] if current_watchlist else []

    cols = st.columns(4)
    for index, movie in enumerate(movies):
        with cols[index % 4]:
            # 1. Get Data
            poster_url = get_image_url(movie.get('poster_path'))
            providers = fetch_watch_providers(movie['id'])
            
            # 2. Determine Link
            # Note: TMDB API Terms require us to link to their landing page for deep-linking.
            # We can't bypass this on the free tier, but we can make it clear.
            if providers and 'link' in providers:
                click_link = providers['link']
            else:
                click_link = f"https://www.themoviedb.org/movie/{movie['id']}"

            # 3. Render Clickable Image
            st.markdown(f"""
                <a href="{click_link}" target="_blank">
                    <img src="{poster_url}" class="movie-poster">
                </a>
            """, unsafe_allow_html=True)
            
            # 4. Show Providers Text
            if providers and 'flatrate' in providers:
                streamers = [p['provider_name'] for p in providers['flatrate'][:2]]
                st.caption(f"📺 {', '.join(streamers)}")
            else:
                st.caption("Checking availability...")

            # 5. Watchlist Button
            if movie['title'] in saved_titles:
                st.button("✅ Saved", key=f"btn_{index}", disabled=True)
            else:
                if st.button("➕ Add", key=f"btn_{index}"):
                    add_to_db(user_email, movie['title'], poster_url, movie['id'])
                    st.rerun()