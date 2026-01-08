import streamlit as st
import pandas as pd
from supabase import create_client

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

@st.cache_data
def load_movie_data():
    try:
        return pd.read_csv("movies.csv", sep="|", keep_default_na=False)
    except:
        return pd.DataFrame()

df = load_movie_data()

# --- 2. DATABASE FUNCTIONS ---
def add_to_db(user, title, poster):
    if supabase:
        data = {"user_name": user, "movie_title": title, "poster_url": poster}
        supabase.table("watchlist").insert(data).execute()

def remove_from_db(movie_id):
    if supabase:
        supabase.table("watchlist").delete().eq("id", movie_id).execute()

def get_user_watchlist(user):
    if supabase:
        response = supabase.table("watchlist").select("*").eq("user_name", user).execute()
        return response.data
    return []

# --- 3. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Guest"

# --- 4. CUSTOM STYLING (The "Pretty" Part) ---
st.markdown("""
<style>
    .stApp {background-color: #0e0e0e;}
    
    /* Login Page Styling */
    .landing-header {font-size: 3rem; font-weight: 800; color: #fff;}
    .landing-sub {font-size: 1.2rem; color: #bbb; line-height: 1.6;}
    .feature-box {background: #1a1a1a; padding: 20px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #333;}
    
    /* Hero Banner */
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
</style>
""", unsafe_allow_html=True)

# --- 5. THE LANDING PAGE (Pre-Login) ---
if not st.session_state.logged_in:
    
    # Create two columns: Left (Info) | Right (Login)
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        st.markdown('<p class="landing-header">Stream Smarter.<br>Regulate Better.</p>', unsafe_allow_html=True)
        st.markdown('<p class="landing-sub">The world is loud. Your entertainment shouldn\'t be. NeuroStream is the first streaming guide designed for <b>Neurodivergent Minds</b>.</p>', unsafe_allow_html=True)
        
        st.divider()
        
        # Value Props (The "Why")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="feature-box">
                <b>🎯 Sensory Filters</b><br>
                Find movies based on "Spoon Theory" and sensory load, not just genre.
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="feature-box">
                <b>🚫 Trigger Warning</b><br>
                AI-detected audio spikes and visual flash warnings before you watch.
            </div>
            """, unsafe_allow_html=True)
            
    with col2:
        st.write("") 
        st.write("") # Spacers
        with st.container(border=True):
            st.subheader("Member Login")
            username = st.text_input("Username", placeholder="e.g. Johan")
            password = st.text_input("Password", type="password")
            
            if st.button("Enter NeuroStream ▶", use_container_width=True):
                if password == "1234": 
                    st.session_state.logged_in = True
                    st.session_state.user_name = username
                    st.rerun()
                else:
                    st.error("Wrong password. (Hint: 1234)")
            
            st.caption("New here? Use '1234' to demo the Beta.")

    st.stop() # Stop the app here if not logged in

# --- 6. MAIN APP (Logged In) ---

# Sidebar Navigation
with st.sidebar:
    st.title("🧠 NeuroStream")
    st.caption(f"Logged in as: {st.session_state.user_name}")
    
    menu = st.radio("Menu", ["🍿 Movies & Shows", "📚 Education & Tips", "❤️ My Watchlist"])
    
    st.divider()
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# --- TAB: EDUCATION & TIPS (New Feature!) ---
if menu == "📚 Education & Tips":
    st.header("Neuro-Support Hub 🌿")
    st.write("Verified strategies for regulation, focus, and sleep.")
    
    tab1, tab2, tab3 = st.tabs(["🧠 ADHD Hacks", "🧘 Sensory Regulation", "💤 Sleep Aid"])
    
    with tab1:
        st.subheader("How to ADHD")
        c1, c2 = st.columns(2)
        with c1:
            st.video("https://www.youtube.com/watch?v=JhzxqLxY5xM") # ADHD Focus
            st.caption("How to Focus with ADHD")
        with c2:
            st.video("https://www.youtube.com/watch?v=hZnUbq8IkkQ") # Dopamine
            st.caption("The Dopamine Menu")
            
    with tab2:
        st.subheader("Calming the Nervous System")
        st.video("https://www.youtube.com/watch?v=tEmt1Znux58") # Box Breathing
        st.caption("Box Breathing Guide (Visual)")
        
    with tab3:
        st.subheader("Brown Noise & Visuals")
        st.video("https://www.youtube.com/watch?v=RqzGzwTY-6w") # Brown Noise
        st.caption("Deep Brown Noise for Sleep (Black Screen)")

# --- TAB: WATCHLIST ---
elif menu == "❤️ My Watchlist":
    st.header(f"❤️ {st.session_state.user_name}'s Safe List")
    my_list = get_user_watchlist(st.session_state.user_name)
    
    if not my_list:
        st.info("Your list is empty! Go to 'Movies & Shows' to add some.")
    else:
        cols = st.columns(4)
        for index, item in enumerate(my_list):
            with cols[index % 4]:
                st.image(item['poster_url'], use_container_width=True)
                st.write(f"**{item['movie_title']}**")
                if st.button(f"Remove ❌", key=f"del_{item['id']}"):
                    remove_from_db(item['id'])
                    st.rerun()

# --- TAB: MOVIES (Home) ---
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
    
    # Get current watchlist
    current_watchlist = get_user_watchlist(st.session_state.user_name)
    saved_titles = [item['movie_title'] for item in current_watchlist] if current_watchlist else []
    
    cols = st.columns(4)
    for index, row in df.iterrows():
        with cols[index % 4]:
            st.image(row['Poster'], use_container_width=True)
            st.caption(f"{row['Emoji']} {row['Sensory Load']}")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.link_button("▶ Watch", row['Link'])
            with c2:
                if row['Title'] in saved_titles:
                    st.button("✅ Added", key=f"btn_{index}", disabled=True)
                else:
                    if st.button("➕ Add", key=f"btn_{index}"):
                        add_to_db(st.session_state.user_name, row['Title'], row['Poster'])
                        st.toast(f"Saved {row['Title']}!")
                        st.rerun()