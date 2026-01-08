import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="NeuroStream", page_icon="🍿", layout="wide")

# --- SESSION STATE (The Brain of the App) ---
# This remembers who you are and what you saved, even if you click buttons.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Guest"
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# --- CUSTOM CSS (The "Netflix" Look) ---
st.markdown("""
<style>
    /* Dark Mode Polish */
    .stApp {background-color: #0e0e0e;}
    
    /* Hero Banner */
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
    
    /* Login Box */
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 50px;
        background-color: #1a1a1a;
        border-radius: 15px;
        border: 1px solid #333;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("movies.csv", sep="|", keep_default_na=False)
    except:
        return pd.DataFrame()

df = load_data()

# --- PAGE 1: LOGIN SCREEN ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.write("")
        st.write("") # Spacers to push content down
        st.write("")
        
        # A nice "Card" for login
        with st.container():
            st.title("🧠 NeuroStream")
            st.write("Stream smarter. Regulate better.")
            
            username = st.text_input("Username", placeholder="e.g. Johan")
            password = st.text_input("Password", type="password", placeholder="Try '1234'")
            
            if st.button("Log In", use_container_width=True):
                if password == "1234":  # Simple "fake" password for the demo
                    st.session_state.logged_in = True
                    st.session_state.user_name = username
                    st.rerun()
                else:
                    st.error("Incorrect password (Hint: 1234)")
    
    st.stop() # Stop here if not logged in

# --- PAGE 2: THE DASHBOARD (Logged In) ---

# Sidebar Navigation
with st.sidebar:
    st.title("🧠 NeuroStream")
    st.write(f"Welcome back, **{st.session_state.user_name}**!")
    
    view_mode = st.radio("Navigate:", ["🏠 Home", "❤️ My Watchlist"])
    
    st.divider()
    st.caption(f"Watchlist: {len(st.session_state.watchlist)} items")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# --- VIEW: WATCHLIST ---
if view_mode == "❤️ My Watchlist":
    st.header(f"{st.session_state.user_name}'s Safe List")
    
    if not st.session_state.watchlist:
        st.info("Your list is empty! Go to Home and click 'Add' on a movie.")
    else:
        # Show saved movies
        saved_df = df[df['Title'].isin(st.session_state.watchlist)]
        cols = st.columns(4)
        for index, row in saved_df.iterrows():
            with cols[index % 4]:
                st.image(row['Poster'], use_container_width=True)
                st.write(f"**{row['Title']}**")
                if st.button(f"Remove ❌", key=f"remove_{index}"):
                    st.session_state.watchlist.remove(row['Title'])
                    st.rerun()

# --- VIEW: HOME (Trending) ---
else:
    # Hero Section (Top Movie)
    if not df.empty:
        hero = df.iloc[0]
        st.markdown(f"""
        <div class="hero-container" style="background-image: url('{hero['Backdrop']}');">
            <h1>{hero['Title']}</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">{hero['Overview'][:150]}...</p>
            <p><strong>{hero['Emoji']} {hero['Sensory Load']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Trending Now")
    
    # Grid Logic
    cols = st.columns(4)
    for index, row in df.iterrows():
        col = cols[index % 4]
        with col:
            st.image(row['Poster'], use_container_width=True)
            st.caption(f"{row['Emoji']} {row['Sensory Load']}")
            
            # Action Buttons
            c1, c2 = st.columns([1, 1])
            with c1:
                st.link_button("▶ Watch", row['Link'])
            with c2:
                # The "Add to List" Logic
                if row['Title'] in st.session_state.watchlist:
                    st.button("✅ Added", key=f"btn_{index}", disabled=True)
                else:
                    if st.button("➕ Add", key=f"btn_{index}"):
                        st.session_state.watchlist.append(row['Title'])
                        st.rerun()
            st.write("") # Spacer