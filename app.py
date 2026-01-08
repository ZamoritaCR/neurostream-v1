import streamlit as st
import pandas as pd
import time
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

# --- 2. AUTH FUNCTIONS ---
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

# --- 3. DATABASE FUNCTIONS ---
def add_to_db(user_email, title, poster):
    if supabase:
        data = {"user_name": user_email, "movie_title": title, "poster_url": poster}
        supabase.table("watchlist").insert(data).execute()

def remove_from_db(movie_id):
    if supabase:
        supabase.table("watchlist").delete().eq("id", movie_id).execute()

def get_user_watchlist(user_email):
    if supabase:
        response = supabase.table("watchlist").select("*").eq("user_name", user_email).execute()
        return response.data
    return []

@st.cache_data
def load_movie_data():
    try:
        return pd.read_csv("movies.csv", sep="|", keep_default_na=False)
    except:
        return pd.DataFrame()

df = load_movie_data()

# --- 4. SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 5. STYLING ---
st.markdown("""
<style>
    .stApp {background-color: #0e0e0e;}
    .landing-header {font-size: 3rem; font-weight: 800; color: #fff;}
    .landing-sub {font-size: 1.2rem; color: #bbb; line-height: 1.6;}
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

# --- 6. LANDING PAGE (NOT LOGGED IN) ---
if not st.session_state.user:
    col1, col2 = st.columns([3, 2], gap="large")
    
    with col1:
        st.markdown('<p class="landing-header">Stream Smarter.<br>Regulate Better.</p>', unsafe_allow_html=True)
        st.markdown('<p class="landing-sub">The first streaming guide for <b>Neurodivergent Minds</b>. Filter by sensory load, not just genre.</p>', unsafe_allow_html=True)
        st.info("💡 **Demo:** Create any account to test it!")

    with col2:
        with st.container(border=True):
            auth_mode = st.radio("Select Option:", ["Log In", "Sign Up", "Forgot Password?"], horizontal=True)
            st.divider()

            if auth_mode == "Forgot Password?":
                st.subheader("Reset Password")
                st.caption("We will send you a temporary login link.")
                reset_email = st.text_input("Enter your email")
                
                if st.button("Send Magic Link ✨", use_container_width=True):
                    if reset_email:
                        success, err = send_reset_email(reset_email)
                        if success:
                            st.success("Sent! Check your email. The link will log you in temporarily.")
                        else:
                            st.error(f"Error: {err}")
                    else:
                        st.warning("Please enter an email.")

            elif auth_mode == "Sign Up":
                st.subheader("Create Account")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.button("Sign Up", use_container_width=True):
                    res, err = sign_up(email, password)
                    if res and res.user:
                        st.success("Account created! Go to 'Log In' now.")
                    elif err:
                        st.error(f"Error: {err}")
            
            else: # Log In
                st.subheader("Welcome Back")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                if st.button("Log In", use_container_width=True):
                    res, err = sign_in(email, password)
                    if res and res.user:
                        st.session_state.user = res.user
                        st.rerun()
                    elif err:
                        st.error(f"Login failed: {err}")
    st.stop()

# --- 7. MAIN APP (LOGGED IN) ---
user_email = st.session_state.user.email

with st.sidebar:
    st.title("🧠 NeuroStream")
    st.write(f"👤 {user_email}")
    
    # NAVIGATION MENU
    menu = st.radio("Menu", ["🍿 Movies", "📚 Education", "❤️ My Watchlist", "🔐 Change Password"])
    
    st.divider()
    if st.button("Log Out"):
        st.session_state.user = None
        supabase.auth.sign_out()
        st.rerun()

# --- PAGE: CHANGE PASSWORD (The "Redirect" Logic) ---
if menu == "🔐 Change Password":
    st.header("Security Settings")
    st.write("Set your new password below.")
    
    with st.form("password_reset"):
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm New Password", type="password")
        btn = st.form_submit_button("Update & Log Out")
        
        if btn:
            if new_pass == confirm_pass:
                if len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, err = update_password(new_pass)
                    if success:
                        st.success("Password Updated! Redirecting to login...")
                        time.sleep(2) # Show success message for 2 seconds
                        # Log them out and restart app
                        st.session_state.user = None
                        supabase.auth.sign_out()
                        st.rerun()
                    else:
                        st.error(f"Error: {err}")
            else:
                st.error("Passwords do not match.")

# --- PAGE: MOVIES (HOME) ---
elif menu == "🍿 Movies":
    # 🚨 NOTIFICATION BAR for Reset Users
    st.info("💡 **Just used a 'Magic Link'?** If you are here to reset your password, go to **🔐 Change Password** in the sidebar!")

    if not df.empty:
        hero = df.iloc[0]
        st.markdown(f"""
        <div class="hero-container" style="background-image: url('{hero['Backdrop']}');">
            <h1>{hero['Title']}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Trending")
    current_watchlist = get_user_watchlist(user_email)
    saved_titles = [item['movie_title'] for item in current_watchlist] if current_watchlist else []
    
    cols = st.columns(4)
    for index, row in df.iterrows():
        with cols[index % 4]:
            st.image(row['Poster'])
            if row['Title'] in saved_titles:
                st.button("✅ Added", key=f"btn_{index}", disabled=True)
            else:
                if st.button("➕ Add", key=f"btn_{index}"):
                    add_to_db(user_email, row['Title'], row['Poster'])
                    st.rerun()

# --- OTHER PAGES ---
elif menu == "📚 Education":
    st.header("Neuro-Support Hub 🌿")
    st.video("https://www.youtube.com/watch?v=JhzxqLxY5xM")

elif menu == "❤️ My Watchlist":
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