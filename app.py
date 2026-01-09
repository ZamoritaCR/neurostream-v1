import streamlit as st
import requests
import time
from urllib.parse import quote_plus, urlparse, parse_qs
from supabase import create_client, Client

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="NeuroStream",
    page_icon="🧠",
    layout="wide"
)

# --------------------------------------------------
# 2. DATABASE CONNECTION (Supabase)
# --------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        return create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
    except Exception:
        return None

supabase = init_connection()

# --------------------------------------------------
# 3. STREAMING SERVICE LINKS (The "Smart Map")
# --------------------------------------------------
SERVICE_MAP = {
    "Netflix": "https://www.netflix.com/search?q={title}",
    "Hulu": "https://www.hulu.com/search?q={title}",
    "Peacock": "https://www.peacocktv.com/watch/search?q={title}",
    "Paramount Plus": "https://www.paramountplus.com/search/?q={title}",
    "Apple TV Plus": "https://tv.apple.com/search?term={title}",
    "Amazon Prime Video": "https://www.amazon.com/gp/video/search/ref=atv_nb_sr?phrase={title}&ie=UTF8",
    "Disney Plus": "https://www.disneyplus.com/search",
    "Max": "https://play.max.com/search",
    "Tubi": "https://tubitv.com/search/{title}",
    "The Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "YouTube": "https://www.youtube.com/results?search_query=watch+{title}",
    "Pluto TV": "https://pluto.tv/en/search/details?query={title}",
    "Freevee": "https://www.amazon.com/gp/video/search/ref=atv_nb_sr?phrase={title}&ie=UTF8",
    "Google Play Movies": "https://play.google.com/store/search?q={title}&c=movies",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "FandangoAtHome": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Apple TV": "https://tv.apple.com/search?term={title}",
}

def get_deep_link(provider_name, title):
    """Generates the direct search link for a provider."""
    provider = provider_name.strip()
    # Get the specific URL template or fallback to a Google Search
    template = SERVICE_MAP.get(
        provider,
        f"https://www.google.com/search?q=watch+{quote_plus(title)}+on+{quote_plus(provider)}"
    )
    if "{title}" in template:
        return template.format(title=quote_plus(title))
    return template

# --------------------------------------------------
# 4. TMDB MOVIE DATA (The "Brain")
# --------------------------------------------------
@st.cache_data(ttl=1800) # Cache results for 30 minutes
def fetch_streaming_movies():
    """Fetches popular movies available on streaming in the US."""
    try:
        url = (
            "https://api.themoviedb.org/3/discover/movie"
            f"?api_key={st.secrets['tmdb']['key']}"
            "&include_adult=false"
            "&include_video=false"
            "&sort_by=popularity.desc"
            "&watch_region=US"
            "&with_watch_monetization_types=flatrate|free|ads|rent"
        )
        return requests.get(url, timeout=6).json().get("results", [])
    except Exception:
        return []

@st.cache_data(ttl=3600) # Cache provider data for 1 hour
def fetch_watch_providers(movie_id):
    """Gets the list of where a movie is streaming."""
    try:
        url = (
            f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
            f"?api_key={st.secrets['tmdb']['key']}"
        )
        data = requests.get(url, timeout=4).json()
        if 'results' in data and 'US' in data['results']:
            return data['results']['US']
        return None
    except Exception:
        return None

# --------------------------------------------------
# 5. IMAGE HELPERS
# --------------------------------------------------
def get_image_url(path):
    return f"https://image.tmdb.org/t/p/w500{path}" if path else "https://via.placeholder.com/500x750?text=No+Image"

def get_logo_url(path):
    return f"https://image.tmdb.org/t/p/original{path}" if path else None

def get_backdrop_url(path):
    return f"https://image.tmdb.org/t/p/original{path}" if path else None

# --------------------------------------------------
# 6. AUTHENTICATION & WATCHLIST
# --------------------------------------------------
def sign_up(email, password):
    try:
        return supabase.auth.sign_up({"email": email, "password": password}), None
    except Exception as e:
        return None, str(e)

def sign_in(email, password):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password}), None
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
            if params.get("access_token") and params.get("refresh_token"):
                return supabase.auth.set_session(params.get("access_token"), params.get("refresh_token")), None
        
        parsed_url = urlparse(url_string)
        query_params = parse_qs(parsed_url.query)
        if 'token_hash' in query_params and 'type' in query_params:
            return supabase.auth.verify_otp({"token_hash": query_params['token_hash'][0], "type": query_params['type'][0]}), None
        return None, "Invalid link."
    except Exception as e:
        return None, str(e)

def add_to_db(user_email, title, poster, tmdb_id):
    if supabase:
        supabase.table("watchlist").insert({
            "user_name": user_email,
            "movie_title": title,
            "poster_url": poster,
            "tmdb_id": tmdb_id
        }).execute()

def remove_from_db(item_id):
    if supabase:
        supabase.table("watchlist").delete().eq("id", item_id).execute()

def get_user_watchlist(user_email):
    if supabase:
        return supabase.table("watchlist").select("*").eq("user_name", user_email).execute().data
    return []

# --------------------------------------------------
# 7. CSS STYLING (The Look & Feel)
# --------------------------------------------------
if 'user' not in st.session_state:
    st.session_state.user = None

st.markdown("""
<style>
    /* Dark Background */
    .stApp {background-color: #0e0e0e;}
    
    /* Hero Section */
    .hero-container {
        padding: 4rem; border-radius: 20px; color: white; margin-bottom: 2rem;
        background-size: cover; background-position: center;
        box-shadow: inset 0 0 0 2000px rgba(0,0,0,0.7); border: 1px solid #333;
    }
    
    /* Movie Poster Styling */
    .movie-poster {
        border-radius: 12px; width: 100%; border: 1px solid #333;
        transition: transform 0.2s;
    }
    .movie-poster:hover { transform: scale(1.03); border: 2px solid #7D4CDB; }
    
    /* THE AGGREGATOR ROW (Logos + Labels + Buttons) */
    .provider-row {
        display: flex; align-items: center; justify-content: space-between;
        background-color: #1a1a1a; padding: 10px; margin-bottom: 8px;
        border-radius: 10px; border: 1px solid #333;
        text-decoration: none !important; color: white !important;
        transition: background 0.2s;
    }
    .provider-row:hover { background-color: #252525; border-color: #7D4CDB; }
    
    .provider-left { display: flex; align-items: center; gap: 12px; }
    .provider-icon { width: 35px; height: 35px; border-radius: 8px; }
    
    .provider-info { display: flex; flex-direction: column; line-height: 1.2; }
    .provider-name { font-size: 0.95rem; font-weight: 600; }
    .provider-meta { font-size: 0.75rem; color: #aaa; }
    
    /* The "Watch" Button Pill */
    .provider-btn {
        background-color: transparent; color: white; padding: 6px 14px;
        border-radius: 20px; font-size: 0.8rem; border: 1px solid #777;
        display: flex; align-items: center; gap: 5px;
    }
    .provider-btn:hover { background-color: #fff; color: #000; border-color: #fff; }

    /* Clean Expander Header */
    .streamlit-expanderHeader { background-color: transparent; color: #ccc; font-size: 0.85rem; }
    
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 8. LANDING PAGE (Login / Sign Up)
# --------------------------------------------------
if not st.session_state.user:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.title("Stream Smarter.")
        st.info("💡 **Demo:** Create an account to see the live feed!")
    with col2:
        with st.container(border=True):
            auth_mode = st.radio("Option", ["Log In", "Sign Up", "Forgot Password?"], horizontal=True)
            
            if auth_mode == "Forgot Password?":
                st.subheader("Reset")
                tab1, tab2 = st.tabs(["📧 Email", "🔗 Paste Link"])
                with tab1:
                    with st.form("reset"):
                        email = st.text_input("Email")
                        if st.form_submit_button("Send"):
                            send_reset_email(email)
                            st.success("Check email!")
                with tab2:
                    with st.form("verify"):
                        url = st.text_input("Paste URL")
                        if st.form_submit_button("Login"):
                            res, err = login_with_url(url)
                            if res and res.user:
                                st.session_state.user = res.user
                                st.rerun()

            elif auth_mode == "Sign Up":
                with st.form("signup"):
                    email = st.text_input("Email")
                    pwd = st.text_input("Password", type="password")
                    if st.form_submit_button("Sign Up"):
                        res, err = sign_up(email, pwd)
                        if res: st.success("Created!")
            else:
                with st.form("login"):
                    email = st.text_input("Email")
                    pwd = st.text_input("Password", type="password")
                    if st.form_submit_button("Log In"):
                        res, err = sign_in(email, pwd)
                        if res and res.user:
                            st.session_state.user = res.user
                            st.rerun()
    st.stop()

# --------------------------------------------------
# 9. MAIN APP DASHBOARD
# --------------------------------------------------
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
    with st.form("pwd"):
        p1 = st.text_input("New", type="password")
        p2 = st.text_input("Confirm", type="password")
        if st.form_submit_button("Update"):
            if p1 == p2:
                update_password(p1)
                st.success("Updated! Logging out...")
                time.sleep(1)
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
    cols = st.columns(4)
    if my_list:
        for i, item in enumerate(my_list):
            with cols[i % 4]:
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
        # Hero Section
        st.markdown(f"""
        <div class='hero-container' style='background-image: url({get_backdrop_url(hero.get('backdrop_path'))});'>
            <h1>{hero['title']}</h1>
            <p>{hero['overview'][:150]}...</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Streaming Now")
    
    current_watchlist = get_user_watchlist(user_email)
    saved_titles = [item['movie_title'] for item in current_watchlist] if current_watchlist else []

    cols = st.columns(4)
    for index, movie in enumerate(movies):
        with cols[index % 4]:
            poster = get_image_url(movie.get('poster_path'))
            
            # --- 1. FETCH PROVIDERS & SORT THEM ---
            all_provs = fetch_watch_providers(movie['id'])
            
            # Create a list of tuples: (ProviderData, "Label")
            display_list = []
            if all_provs:
                if 'flatrate' in all_provs:
                    for p in all_provs['flatrate']: display_list.append((p, "Subscription"))
                if 'free' in all_provs:
                    for p in all_provs['free']: display_list.append((p, "Free"))
                if 'ads' in all_provs:
                    for p in all_provs['ads']: display_list.append((p, "Free (Ads)"))
                if 'rent' in all_provs:
                    for p in all_provs['rent']: display_list.append((p, "Rent"))

            # --- 2. RENDER POSTER & BUTTONS ---
            st.image(poster, use_container_width=True, className="movie-poster")

            if movie['title'] in saved_titles:
                st.button("✅ Saved", key=f"btn_{index}", disabled=True)
            else:
                if st.button("➕ Add", key=f"btn_{index}"):
                    add_to_db(user_email, movie['title'], poster, movie['id'])
                    st.rerun()
            
            # --- 3. RENDER THE "WHERE TO WATCH" DROPDOWN ---
            if display_list:
                # Remove duplicates (e.g. Netflix appearing in both Subs and Ads)
                seen = set()
                unique_list = []
                for p, p_type in display_list:
                    p_name = p['provider_name']
                    if p_name not in seen:
                        unique_list.append((p, p_type))
                        seen.add(p_name)

                # The Expander Menu
                with st.expander(f"📺 Watch ({len(unique_list)} options)"):
                    # Limit to top 6 to prevent scrolling fatigue
                    for prov, p_type in unique_list[:6]:
                        p_name = prov['provider_name']
                        p_logo = get_logo_url(prov['logo_path'])
                        p_link = get_deep_link(p_name, movie['title'])
                        
                        # The HTML for the Provider Row
                        st.markdown(f"""
                        <a href="{p_link}" target="_blank" class="provider-row">
                            <div class="provider-left">
                                <img src="{p_logo}" class="provider-icon">
                                <div class="provider-info">
                                    <span class="provider-name">{p_name}</span>
                                    <span class="provider-meta">{p_type}</span>
                                </div>
                            </div>
                            <div class="provider-btn">▶ Watch</div>
                        </a>
                        """, unsafe_allow_html=True)
            else:
                st.caption("No streaming info.")