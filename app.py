import streamlit as st
import pandas as pd
from supabase import create_client

# --- PAGE CONFIG ---
st.set_page_config(page_title="NeuroStream", page_icon="🍿", layout="wide")

# --- 1. CONNECT TO DATABASE ---
# This uses the secrets you just saved
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# --- 2. DATABASE FUNCTIONS ---

def add_to_db(user, title, poster):
    # Saves to the cloud
    data = {"user_name": user, "movie_title": title, "poster_url": poster}
    supabase.table("watchlist").insert(data).execute()

def remove_from_db(movie_id):
    # Deletes from the cloud
    supabase.table("watchlist").delete().eq("id", movie_id).execute()

def get_user_watchlist(user):
    # Downloads the user's list
    response = supabase.table("watchlist").select("*").eq("user_name", user).execute()
    return response.data

# --- 3. LOAD MOVIE DATA ---
@st.cache_data
def load_movie_data():
    try:
        return pd.read_csv("movies.csv", sep="|", keep_default_na=False)
    except:
        return pd.DataFrame()

df = load_movie_data()

# --- 4. SESSION STATE (Login) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Guest"

# --- 5. STYLING ---
st.markdown("""
<style>
    .stApp {background-color: #0e0e0e;}
    .hero-container {
        padding: 3rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        background-size: cover;
        background-position: center;
        box-shadow: inset 0 0 0 2000px rgba(0,0,0,0.7);
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- 6. PAGE: LOGIN ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.write("")
        st.write("")
        with st.container():
            st.title("🧠 NeuroStream")
            username = st.text_input("Username", placeholder="e.g. Johan")
            password = st.text_input("Password", type="password", placeholder="Try '1234'")
            
            if st.button("Log In", use_container_width=True):
                if password == "1234": 
                    st.session_state.logged_in = True
                    st.session_state.user_name = username
                    st.rerun()
                else:
                    st.error("Incorrect password")
    st.stop()

# --- 7. PAGE: DASHBOARD ---
with st.sidebar:
    st.title("🧠 NeuroStream")
    st.write(f"User: **{st.session_state.user_name}**")
    view_mode = st.radio("Navigate:", ["🏠 Home", "❤️ My Watchlist"])
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# --- VIEW: WATCHLIST (CLOUD) ---
if view_mode == "❤️ My Watchlist":
    st.header(f"{st.session_state.user_name}'s Cloud Watchlist ☁️")
    
    # Get real data from cloud
    my_list = get_user_watchlist(st.session_state.user_name)
    
    if not my_list:
        st.info("Your list is empty! Go add some movies.")
    else:
        cols = st.columns(4)
        for index, item in enumerate(my_list):
            with cols[index % 4]:
                st.image(item['poster_url'], use_container_width=True)
                st.write(f"**{item['movie_title']}**")
                if st.button(f"Remove ❌", key=f"del_{item['id']}"):
                    remove_from_db(item['id'])
                    st.rerun()

# --- VIEW: HOME (TRENDING) ---
else:
    # Hero Section
    if not df.empty:
        hero = df.iloc[0]
        st.markdown(f"""
        <div class="hero-container" style="background-image: url('{hero['Backdrop']}');">
            <h1>{hero['Title']}</h1>
            <p><strong>{hero['Emoji']} {hero['Sensory Load']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Trending Now")
    
    # Get current watchlist so we know what is already added
    current_watchlist = get_user_watchlist(st.session_state.user_name)
    saved_titles = [item['movie_title'] for item in current_watchlist]
    
    cols = st.columns(4)
    for index, row in df.iterrows():
        with cols[index % 4]:
            st.image(row['Poster'], use_container_width=True)
            st.caption(f"{row['Emoji']} {row['Sensory Load']}")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.link_button("▶ Watch", row['Link'])
            with c2:
                # Add to Cloud Logic
                if row['Title'] in saved_titles:
                    st.button("✅ Added", key=f"btn_{index}", disabled=True)
                else:
                    if st.button("➕ Add", key=f"btn_{index}"):
                        add_to_db(st.session_state.user_name, row['Title'], row['Poster'])
                        st.toast(f"Saved {row['Title']}!")
                        st.rerun()