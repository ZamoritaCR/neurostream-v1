# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v34.0 - SUPABASE AUTH 🔐
# Mother Code v33.5 + Real User Database
# --------------------------------------------------
# NEW IN v34:
# ✅ Supabase Authentication (email/password)
# ✅ Persistent user profiles
# ✅ Cloud-saved DP, streaks, achievements
# ✅ Password reset flow
# ✅ Email verification
# ✅ Protected routes
# --------------------------------------------------

import streamlit as st
import os
import requests
import json
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from openai import OpenAI
import html as html_lib
import random
from datetime import datetime, timedelta
import hashlib
import re

# --------------------------------------------------
# 1. CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Dopamine.watch | Feel Better, Watch Better",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "Dopamine.watch"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_URL = "https://image.tmdb.org/t/p/original"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"

# --------------------------------------------------
# 2. SUPABASE CLIENT
# --------------------------------------------------
try:
    from supabase import create_client, Client
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["anon_key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    SUPABASE_ENABLED = True
except Exception as e:
    supabase = None
    SUPABASE_ENABLED = False
    print(f"Supabase not configured: {e}")

# --------------------------------------------------
# 3. SUPABASE AUTH FUNCTIONS
# --------------------------------------------------
def supabase_sign_up(email: str, password: str, name: str = ""):
    """Register a new user with Supabase"""
    if not SUPABASE_ENABLED:
        return {"success": False, "error": "Auth not configured"}
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name,
                    "dopamine_points": 50,  # Welcome bonus
                    "streak_days": 1,
                    "created_at": datetime.now().isoformat()
                }
            }
        })
        if response.user:
            # Create user profile in database
            create_user_profile(response.user.id, email, name)
            return {"success": True, "user": response.user, "session": response.session}
        return {"success": False, "error": "Registration failed"}
    except Exception as e:
        error_msg = str(e)
        if "User already registered" in error_msg:
            return {"success": False, "error": "Email already registered. Try logging in."}
        return {"success": False, "error": error_msg}

def supabase_sign_in(email: str, password: str):
    """Sign in existing user"""
    if not SUPABASE_ENABLED:
        return {"success": False, "error": "Auth not configured"}
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            # Load user profile
            profile = get_user_profile(response.user.id)
            return {"success": True, "user": response.user, "session": response.session, "profile": profile}
        return {"success": False, "error": "Invalid credentials"}
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {"success": False, "error": "Invalid email or password"}
        return {"success": False, "error": error_msg}

def supabase_sign_out():
    """Sign out current user"""
    if not SUPABASE_ENABLED:
        return
    try:
        supabase.auth.sign_out()
    except:
        pass

def supabase_reset_password(email: str):
    """Send password reset email"""
    if not SUPABASE_ENABLED:
        return {"success": False, "error": "Auth not configured"}
    try:
        supabase.auth.reset_password_email(email)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def supabase_get_user():
    """Get current authenticated user"""
    if not SUPABASE_ENABLED:
        return None
    try:
        response = supabase.auth.get_user()
        return response.user if response else None
    except:
        return None

# --------------------------------------------------
# 4. USER PROFILE DATABASE FUNCTIONS
# --------------------------------------------------
def create_user_profile(user_id: str, email: str, name: str):
    """Create user profile in Supabase database"""
    if not SUPABASE_ENABLED:
        return None
    try:
        # Generate referral code
        ref_code = hashlib.md5(f"{user_id}{datetime.now()}".encode()).hexdigest()[:8].upper()
        
        profile = {
            "id": user_id,
            "email": email,
            "name": name or email.split("@")[0],
            "dopamine_points": 50,
            "streak_days": 1,
            "last_visit": datetime.now().date().isoformat(),
            "referral_code": ref_code,
            "referred_by": None,
            "is_premium": False,
            "quick_hit_count": 0,
            "total_watches": 0,
            "favorite_moods": [],
            "watchlist": [],
            "achievements": [],
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("profiles").upsert(profile).execute()
        return profile
    except Exception as e:
        print(f"Error creating profile: {e}")
        return None

def get_user_profile(user_id: str):
    """Get user profile from database"""
    if not SUPABASE_ENABLED:
        return None
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data
    except:
        return None

def update_user_profile(user_id: str, updates: dict):
    """Update user profile in database"""
    if not SUPABASE_ENABLED:
        return None
    try:
        response = supabase.table("profiles").update(updates).eq("id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error updating profile: {e}")
        return None

def add_dopamine_points_db(user_id: str, amount: int, reason: str = ""):
    """Add DP to user's account in database"""
    if not SUPABASE_ENABLED or not user_id:
        return
    try:
        profile = get_user_profile(user_id)
        if profile:
            new_points = profile.get("dopamine_points", 0) + amount
            update_user_profile(user_id, {"dopamine_points": new_points})
    except:
        pass

def update_streak_db(user_id: str):
    """Update user's streak in database"""
    if not SUPABASE_ENABLED or not user_id:
        return
    try:
        profile = get_user_profile(user_id)
        if not profile:
            return
        
        today = datetime.now().date().isoformat()
        last_visit = profile.get("last_visit", "")
        current_streak = profile.get("streak_days", 0)
        
        if last_visit != today:
            yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
            if last_visit == yesterday:
                new_streak = current_streak + 1
                bonus = 10 * new_streak
            else:
                new_streak = 1
                bonus = 10
            
            new_points = profile.get("dopamine_points", 0) + bonus
            update_user_profile(user_id, {
                "streak_days": new_streak,
                "last_visit": today,
                "dopamine_points": new_points
            })
    except Exception as e:
        print(f"Error updating streak: {e}")

def check_referral_code(code: str, new_user_id: str):
    """Check and apply referral code bonus"""
    if not SUPABASE_ENABLED:
        return False
    try:
        # Find user with this referral code
        response = supabase.table("profiles").select("*").eq("referral_code", code.upper()).single().execute()
        if response.data:
            referrer_id = response.data["id"]
            # Give bonus to referrer
            add_dopamine_points_db(referrer_id, 100, "Referral bonus!")
            # Mark new user as referred
            update_user_profile(new_user_id, {"referred_by": referrer_id})
            # Give bonus to new user
            add_dopamine_points_db(new_user_id, 100, "Referral welcome bonus!")
            return True
    except:
        pass
    return False

# --------------------------------------------------
# 5. SERVICE MAPS - COMPREHENSIVE
# --------------------------------------------------
MOVIE_SERVICES = {
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
    "MGM Plus": "https://www.mgmplus.com/search?q={title}",
    "Tubi": "https://tubitv.com/search/{title}",
    "Tubi TV": "https://tubitv.com/search/{title}",
    "Pluto TV": "https://pluto.tv/search/details/{title}",
    "Plex": "https://watch.plex.tv/search?q={title}",
    "Crunchyroll": "https://www.crunchyroll.com/search?q={title}",
    "Shudder": "https://www.shudder.com/search?q={title}",
    "MUBI": "https://mubi.com/search?query={title}",
    "Vudu": "https://www.vudu.com/content/movies/search?searchString={title}",
    "Fandango At Home": "https://www.vudu.com/content/movies/search?searchString={title}",
    "The Roku Channel": "https://therokuchannel.roku.com/search/{title}",
    "Criterion Channel": "https://www.criterionchannel.com/search?q={title}",
}

MUSIC_SERVICES = {
    "Spotify": {"url": "https://open.spotify.com/search/{query}", "color": "#1DB954", "icon": "🟢"},
    "Apple Music": {"url": "https://music.apple.com/search?term={query}", "color": "#FA243C", "icon": "🍎"},
    "YouTube Music": {"url": "https://music.youtube.com/search?q={query}", "color": "#FF0000", "icon": "▶️"},
    "Amazon Music": {"url": "https://music.amazon.com/search/{query}", "color": "#00A8E1", "icon": "🎵"},
    "Tidal": {"url": "https://tidal.com/search?q={query}", "color": "#000000", "icon": "🌊"},
    "SoundCloud": {"url": "https://soundcloud.com/search?q={query}", "color": "#FF5500", "icon": "☁️"},
}

PODCAST_SERVICES = {
    "Spotify": {"url": "https://open.spotify.com/search/{query}/podcasts", "color": "#1DB954", "icon": "🟢"},
    "Apple Podcasts": {"url": "https://podcasts.apple.com/search?term={query}", "color": "#9933CC", "icon": "🎙️"},
    "YouTube": {"url": "https://www.youtube.com/results?search_query={query}+podcast", "color": "#FF0000", "icon": "▶️"},
    "Pocket Casts": {"url": "https://pocketcasts.com/search/{query}", "color": "#F43E37", "icon": "📱"},
    "Overcast": {"url": "https://overcast.fm/search?q={query}", "color": "#FC7E0F", "icon": "🎧"},
}

AUDIOBOOK_SERVICES = {
    "Audible": {"url": "https://www.audible.com/search?keywords={query}", "color": "#F8991D", "icon": "🎧"},
    "Libro.fm": {"url": "https://libro.fm/search?q={query}", "color": "#00A651", "icon": "📗"},
    "Google Play Books": {"url": "https://play.google.com/store/search?q={query}&c=audiobooks", "color": "#4285F4", "icon": "📘"},
    "Kobo": {"url": "https://www.kobo.com/search?query={query}&fcsearchfield=Audiobook", "color": "#BF0000", "icon": "📕"},
    "Chirp": {"url": "https://www.chirpbooks.com/search?query={query}", "color": "#FF6B6B", "icon": "🐦"},
}

# --------------------------------------------------
# 6. API CLIENTS
# --------------------------------------------------
@st.cache_data
def get_tmdb_key():
    try:
        return st.secrets["tmdb"]["api_key"]
    except:
        return None

try:
    openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])
except:
    openai_client = None

# --------------------------------------------------
# 7. EMOTION MAPPINGS - COMPLETE
# --------------------------------------------------
CURRENT_FEELINGS = ["Sad", "Lonely", "Anxious", "Overwhelmed", "Angry", "Stressed", "Bored", "Tired", "Numb", "Confused", "Restless", "Focused", "Calm", "Happy", "Excited", "Curious"]
DESIRED_FEELINGS = ["Comforted", "Calm", "Relaxed", "Focused", "Energized", "Stimulated", "Happy", "Entertained", "Inspired", "Grounded", "Curious", "Sleepy", "Connected"]

MOOD_EMOJIS = {
    "Sad": "🌧️", "Lonely": "🥺", "Anxious": "😰", "Overwhelmed": "😵‍💫",
    "Angry": "😡", "Stressed": "😫", "Bored": "😐", "Tired": "😴",
    "Numb": "🫥", "Confused": "🤔", "Restless": "😬", "Focused": "🎯",
    "Calm": "😌", "Happy": "😊", "Excited": "⚡", "Curious": "🧐",
    "Comforted": "🫶", "Relaxed": "🛋️", "Energized": "🔥", "Stimulated": "🚀",
    "Entertained": "🍿", "Inspired": "✨", "Grounded": "🌱", "Sleepy": "🌙", "Connected": "❤️"
}

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

# Music mood mappings
FEELING_TO_MUSIC = {
    "Sad": {"query": "sad songs comfort healing", "playlist": "37i9dQZF1DX7qK8ma5wgG1", "genres": ["acoustic", "piano", "indie folk"]},
    "Lonely": {"query": "comfort songs lonely night", "playlist": "37i9dQZF1DX3YSRoSdA634", "genres": ["indie", "acoustic", "soul"]},
    "Anxious": {"query": "calm relaxing anxiety relief meditation", "playlist": "37i9dQZF1DWXe9gFZP0gtP", "genres": ["ambient", "classical", "new age"]},
    "Overwhelmed": {"query": "peaceful ambient stress relief nature", "playlist": "37i9dQZF1DWZqd5JICZI0u", "genres": ["ambient", "meditation", "nature sounds"]},
    "Angry": {"query": "angry workout metal rock intense", "playlist": "37i9dQZF1DX1tyCD9QhIWF", "genres": ["metal", "hard rock", "punk"]},
    "Stressed": {"query": "meditation spa relaxation peaceful", "playlist": "37i9dQZF1DWU0ScTcjJBdj", "genres": ["spa", "meditation", "ambient"]},
    "Bored": {"query": "upbeat pop hits energy dance", "playlist": "37i9dQZF1DXcBWIGoYBM5M", "genres": ["pop", "dance", "electronic"]},
    "Tired": {"query": "acoustic chill coffee morning", "playlist": "37i9dQZF1DX4WYpdgoIcn6", "genres": ["acoustic", "indie folk", "chill"]},
    "Numb": {"query": "intense electronic bass drop", "playlist": "37i9dQZF1DX4dyzvuaRJ0n", "genres": ["electronic", "dubstep", "bass"]},
    "Confused": {"query": "lo-fi study beats focus", "playlist": "37i9dQZF1DWWQRwui0ExPn", "genres": ["lo-fi", "chillhop", "jazz"]},
    "Restless": {"query": "high energy dance workout edm", "playlist": "37i9dQZF1DX76Wlfdnj7AP", "genres": ["edm", "dance", "house"]},
    "Focused": {"query": "deep focus concentration study", "playlist": "37i9dQZF1DWZeKCadgRdKQ", "genres": ["classical", "ambient", "electronic"]},
    "Calm": {"query": "nature sounds peaceful morning", "playlist": "37i9dQZF1DX4sWSpwq3LiO", "genres": ["nature", "ambient", "classical"]},
    "Happy": {"query": "feel good happy hits mood booster", "playlist": "37i9dQZF1DX3rxVfibe1L0", "genres": ["pop", "dance", "funk"]},
    "Excited": {"query": "party anthems hype energy", "playlist": "37i9dQZF1DXa2PvUpywmrr", "genres": ["edm", "pop", "hip-hop"]},
    "Curious": {"query": "experimental indie discover weekly", "playlist": "37i9dQZF1DX2sUQwD7tbmL", "genres": ["experimental", "indie", "alternative"]},
    "Comforted": {"query": "warm acoustic cozy fireplace", "playlist": "37i9dQZF1DX4E3UdUs7fUx", "genres": ["acoustic", "folk", "singer-songwriter"]},
    "Relaxed": {"query": "sunday morning chill coffee", "playlist": "37i9dQZF1DX6VdMW310YC7", "genres": ["chill", "acoustic", "jazz"]},
    "Energized": {"query": "workout motivation pump beast", "playlist": "37i9dQZF1DX76Wlfdnj7AP", "genres": ["hip-hop", "edm", "rock"]},
    "Stimulated": {"query": "electronic bass intense techno", "playlist": "37i9dQZF1DX0pH2SQMRXnC", "genres": ["electronic", "techno", "trance"]},
    "Entertained": {"query": "viral hits trending tiktok", "playlist": "37i9dQZF1DXcBWIGoYBM5M", "genres": ["pop", "hip-hop", "dance"]},
    "Inspired": {"query": "epic orchestral motivation cinematic", "playlist": "37i9dQZF1DX3rxVfibe1L0", "genres": ["orchestral", "cinematic", "classical"]},
    "Grounded": {"query": "folk roots acoustic americana", "playlist": "37i9dQZF1DX4E3UdUs7fUx", "genres": ["folk", "americana", "acoustic"]},
    "Sleepy": {"query": "sleep sounds rain white noise", "playlist": "37i9dQZF1DWZd79rJ6a7lp", "genres": ["sleep", "ambient", "nature"]},
    "Connected": {"query": "love songs romance ballads", "playlist": "37i9dQZF1DX50QitC6Oqtn", "genres": ["r&b", "soul", "pop"]},
}

# Podcast mood mappings
FEELING_TO_PODCASTS = {
    "Sad": {"query": "mental health comfort healing stories", "shows": [("The Happiness Lab", "Learn the science of happiness"), ("Unlocking Us", "Brené Brown on emotions"), ("On Being", "Deep conversations on life")]},
    "Lonely": {"query": "friendship connection human stories", "shows": [("This American Life", "Human connection stories"), ("Modern Love", "Stories of love & connection"), ("Dear Sugars", "Advice & comfort")]},
    "Anxious": {"query": "anxiety meditation calm mindfulness", "shows": [("The Calm App", "Guided meditations"), ("Ten Percent Happier", "Meditation for skeptics"), ("Anxiety Slayer", "Tips for anxiety")]},
    "Overwhelmed": {"query": "minimalism simple living declutter", "shows": [("The Minimalists", "Less is more"), ("Optimal Living Daily", "Curated self-help"), ("How to Be a Better Human", "Small improvements")]},
    "Angry": {"query": "venting rants comedy", "shows": [("My Favorite Murder", "True crime comedy"), ("Armchair Expert", "Celebrity conversations"), ("The Daily", "News you can trust")]},
    "Stressed": {"query": "relaxation meditation stress relief", "shows": [("Nothing Much Happens", "Bedtime stories"), ("Headspace Guide", "Meditation basics"), ("The Mindful Minute", "Quick calm")]},
    "Bored": {"query": "true crime mystery thriller stories", "shows": [("Serial", "Investigative journalism"), ("My Favorite Murder", "True crime comedy"), ("Casefile", "True crime deep dives")]},
    "Tired": {"query": "easy listening light comedy", "shows": [("Conan O'Brien Needs A Friend", "Comedy interviews"), ("SmartLess", "Jason Bateman & friends"), ("Wait Wait Don't Tell Me", "NPR quiz show")]},
    "Numb": {"query": "intense stories adventure", "shows": [("Radiolab", "Science & wonder"), ("Hardcore History", "Epic history"), ("Revisionist History", "Malcolm Gladwell")]},
    "Confused": {"query": "explained simply learning education", "shows": [("Stuff You Should Know", "Learn anything"), ("Freakonomics", "Hidden economics"), ("TED Radio Hour", "Big ideas")]},
    "Restless": {"query": "adventure travel stories", "shows": [("The Moth", "True stories"), ("Risk!", "True stories"), ("Snap Judgment", "Storytelling")]},
    "Focused": {"query": "productivity business success habits", "shows": [("Deep Work", "Cal Newport on focus"), ("The Tim Ferriss Show", "World-class performers"), ("How I Built This", "Entrepreneur stories")]},
    "Calm": {"query": "nature meditation peaceful", "shows": [("Nothing Much Happens", "Bedtime stories"), ("Sleep With Me", "Boring stories for sleep"), ("The Daily Meditation", "Guided calm")]},
    "Happy": {"query": "comedy funny laugh humor", "shows": [("Conan O'Brien Needs A Friend", "Comedy interviews"), ("SmartLess", "Jason Bateman & friends"), ("My Dad Wrote A Porno", "Hilarious readings")]},
    "Excited": {"query": "new releases pop culture", "shows": [("Pop Culture Happy Hour", "NPR entertainment"), ("The Rewatchables", "Movie deep dives"), ("Switched on Pop", "Music analysis")]},
    "Curious": {"query": "science explained learning discovery", "shows": [("Radiolab", "Science & philosophy"), ("Stuff You Should Know", "Learn anything"), ("Hidden Brain", "Psychology insights")]},
    "Comforted": {"query": "cozy wholesome heartwarming", "shows": [("Everything is Alive", "Objects interviewed"), ("The Moth", "True stories"), ("On Being", "Meaningful conversations")]},
    "Relaxed": {"query": "chill conversations stories", "shows": [("Nothing Much Happens", "Bedtime stories"), ("Sleep With Me", "Boring stories for sleep"), ("The Moth", "True stories")]},
    "Energized": {"query": "motivation success hustle", "shows": [("The School of Greatness", "Lewis Howes"), ("Impact Theory", "Tom Bilyeu"), ("The Tony Robbins Podcast", "Personal development")]},
    "Stimulated": {"query": "intellectual debate ideas", "shows": [("Making Sense", "Sam Harris"), ("Lex Fridman Podcast", "Long conversations"), ("Intelligence Squared", "Debates")]},
    "Entertained": {"query": "entertainment pop culture celebrity", "shows": [("Armchair Expert", "Dax Shepard"), ("Call Her Daddy", "Conversations"), ("The Joe Rogan Experience", "Long form")]},
    "Inspired": {"query": "motivation success stories inspiration", "shows": [("The School of Greatness", "Lewis Howles"), ("Impact Theory", "Tom Bilyeu"), ("The Tony Robbins Podcast", "Personal development")]},
    "Grounded": {"query": "mindfulness nature spirituality", "shows": [("On Being", "Krista Tippett"), ("The Daily Meditation", "Guided meditation"), ("Ten Percent Happier", "Dan Harris")]},
    "Sleepy": {"query": "sleep bedtime stories boring", "shows": [("Nothing Much Happens", "Bedtime stories"), ("Sleep With Me", "Boring stories for sleep"), ("Get Sleepy", "Sleep meditations")]},
    "Connected": {"query": "relationships love connection", "shows": [("Modern Love", "Love stories"), ("Where Should We Begin", "Esther Perel therapy"), ("Dear Sugars", "Advice column")]},
}

# Audiobook mood mappings
FEELING_TO_AUDIOBOOKS = {
    "Sad": {"query": "comfort healing memoir uplifting", "genres": ["Self-Help", "Memoir", "Fiction"], "picks": [("It's OK That You're Not OK", "Megan Devine"), ("Maybe You Should Talk to Someone", "Lori Gottlieb"), ("A Man Called Ove", "Fredrik Backman")]},
    "Lonely": {"query": "connection friendship heartwarming", "genres": ["Fiction", "Memoir", "Self-Help"], "picks": [("Eleanor Oliphant Is Completely Fine", "Gail Honeyman"), ("The House in the Cerulean Sea", "TJ Klune"), ("Tuesdays with Morrie", "Mitch Albom")]},
    "Anxious": {"query": "anxiety calm mindfulness peace", "genres": ["Self-Help", "Mindfulness", "Psychology"], "picks": [("Dare", "Barry McDonagh"), ("The Anxiety Toolkit", "Alice Boyes"), ("Breath", "James Nestor")]},
    "Overwhelmed": {"query": "simplify organize minimalism", "genres": ["Self-Help", "Productivity", "Lifestyle"], "picks": [("Essentialism", "Greg McKeown"), ("The Life-Changing Magic of Tidying Up", "Marie Kondo"), ("Digital Minimalism", "Cal Newport")]},
    "Angry": {"query": "justice revenge thriller", "genres": ["Thriller", "True Crime", "Fiction"], "picks": [("The Girl with the Dragon Tattoo", "Stieg Larsson"), ("The Count of Monte Cristo", "Alexandre Dumas"), ("Gone Girl", "Gillian Flynn")]},
    "Stressed": {"query": "relaxation mindfulness calm", "genres": ["Self-Help", "Mindfulness", "Health"], "picks": [("The Untethered Soul", "Michael A. Singer"), ("10% Happier", "Dan Harris"), ("Why We Sleep", "Matthew Walker")]},
    "Bored": {"query": "thriller mystery page turner exciting", "genres": ["Thriller", "Mystery", "Suspense"], "picks": [("The Silent Patient", "Alex Michaelides"), ("Gone Girl", "Gillian Flynn"), ("The Girl on the Train", "Paula Hawkins")]},
    "Tired": {"query": "light easy read feel good", "genres": ["Romance", "Comedy", "Fiction"], "picks": [("Beach Read", "Emily Henry"), ("The Rosie Project", "Graeme Simsion"), ("Where'd You Go, Bernadette", "Maria Semple")]},
    "Numb": {"query": "intense gripping emotional", "genres": ["Literary Fiction", "Drama", "Memoir"], "picks": [("A Little Life", "Hanya Yanagihara"), ("Educated", "Tara Westover"), ("The Kite Runner", "Khaled Hosseini")]},
    "Confused": {"query": "clarity wisdom philosophy", "genres": ["Philosophy", "Self-Help", "Psychology"], "picks": [("Man's Search for Meaning", "Viktor Frankl"), ("The Alchemist", "Paulo Coelho"), ("Siddhartha", "Hermann Hesse")]},
    "Restless": {"query": "adventure travel exploration", "genres": ["Adventure", "Travel", "Memoir"], "picks": [("Wild", "Cheryl Strayed"), ("Into the Wild", "Jon Krakauer"), ("The Alchemist", "Paulo Coelho")]},
    "Focused": {"query": "productivity business focus success", "genres": ["Business", "Self-Help", "Psychology"], "picks": [("Deep Work", "Cal Newport"), ("The 4-Hour Workweek", "Tim Ferriss"), ("Thinking, Fast and Slow", "Daniel Kahneman")]},
    "Calm": {"query": "peaceful gentle soothing", "genres": ["Fiction", "Nature", "Spirituality"], "picks": [("The Little Prince", "Antoine de Saint-Exupéry"), ("Pilgrim at Tinker Creek", "Annie Dillard"), ("When Breath Becomes Air", "Paul Kalanithi")]},
    "Happy": {"query": "feel good comedy romance joy", "genres": ["Romance", "Comedy", "Fiction"], "picks": [("Beach Read", "Emily Henry"), ("The House in the Cerulean Sea", "TJ Klune"), ("Anxious People", "Fredrik Backman")]},
    "Excited": {"query": "adventure action thriller", "genres": ["Thriller", "Adventure", "Sci-Fi"], "picks": [("Ready Player One", "Ernest Cline"), ("The Martian", "Andy Weir"), ("Dark Matter", "Blake Crouch")]},
    "Curious": {"query": "science history fascinating nonfiction", "genres": ["Science", "History", "Biography"], "picks": [("Sapiens", "Yuval Noah Harari"), ("The Code Breaker", "Walter Isaacson"), ("Outliers", "Malcolm Gladwell")]},
    "Comforted": {"query": "cozy heartwarming wholesome", "genres": ["Fiction", "Romance", "Family"], "picks": [("A Man Called Ove", "Fredrik Backman"), ("The House in the Cerulean Sea", "TJ Klune"), ("Anxious People", "Fredrik Backman")]},
    "Relaxed": {"query": "easy listening gentle stories", "genres": ["Fiction", "Memoir", "Essays"], "picks": [("A Year in Provence", "Peter Mayle"), ("Under the Tuscan Sun", "Frances Mayes"), ("Eat Pray Love", "Elizabeth Gilbert")]},
    "Energized": {"query": "motivation biography success inspiring", "genres": ["Biography", "Business", "Self-Help"], "picks": [("Atomic Habits", "James Clear"), ("Can't Hurt Me", "David Goggins"), ("Shoe Dog", "Phil Knight")]},
    "Stimulated": {"query": "mind bending science fiction ideas", "genres": ["Sci-Fi", "Philosophy", "Psychology"], "picks": [("Dune", "Frank Herbert"), ("Brave New World", "Aldous Huxley"), ("1984", "George Orwell")]},
    "Entertained": {"query": "fun engaging popular bestseller", "genres": ["Fiction", "Thriller", "Fantasy"], "picks": [("The Thursday Murder Club", "Richard Osman"), ("Project Hail Mary", "Andy Weir"), ("The Midnight Library", "Matt Haig")]},
    "Inspired": {"query": "motivation biography success stories", "genres": ["Biography", "Business", "Self-Help"], "picks": [("Atomic Habits", "James Clear"), ("Can't Hurt Me", "David Goggins"), ("Shoe Dog", "Phil Knight")]},
    "Grounded": {"query": "nature spirituality mindfulness", "genres": ["Nature", "Spirituality", "Memoir"], "picks": [("Braiding Sweetgrass", "Robin Wall Kimmerer"), ("The Overstory", "Richard Powers"), ("A Walk in the Woods", "Bill Bryson")]},
    "Sleepy": {"query": "fantasy fiction gentle bedtime", "genres": ["Fantasy", "Fiction", "Classic"], "picks": [("The Hobbit", "J.R.R. Tolkien"), ("Harry Potter", "J.K. Rowling"), ("The Night Circus", "Erin Morgenstern")]},
    "Connected": {"query": "romance love relationships", "genres": ["Romance", "Contemporary", "Fiction"], "picks": [("The Notebook", "Nicholas Sparks"), ("Me Before You", "Jojo Moyes"), ("Outlander", "Diana Gabaldon")]},
}

# Shorts/Videos mood mappings
FEELING_TO_VIDEOS = {
    "Sad": "wholesome animals cute puppies kittens",
    "Lonely": "heartwarming friendship stories",
    "Anxious": "satisfying oddly calming asmr",
    "Overwhelmed": "calming nature scenery peaceful",
    "Angry": "epic fails funny karma instant",
    "Stressed": "meditation guided relaxing calm",
    "Bored": "mind blowing facts amazing",
    "Tired": "asmr relaxing sleep sounds",
    "Numb": "extreme sports adrenaline rush",
    "Confused": "explained simply 5 minute crafts",
    "Restless": "action parkour extreme sports",
    "Focused": "productivity hacks study tips",
    "Calm": "ocean waves nature sounds rain",
    "Happy": "funny moments comedy fails",
    "Excited": "epic moments incredible amazing",
    "Curious": "science experiments cool facts",
    "Comforted": "cozy vibes aesthetic room",
    "Relaxed": "coffee shop ambience rain sounds",
    "Energized": "hype motivation workout beast",
    "Stimulated": "wtf moments mind blown",
    "Entertained": "viral comedy trending funny",
    "Inspired": "success stories motivation transformation",
    "Grounded": "minimalist living simple life",
    "Sleepy": "rain sounds sleep asmr",
    "Connected": "friendship goals wholesome couples",
}

# --------------------------------------------------
# 8. DATA ENGINE - MOVIES
# --------------------------------------------------
def _clean_movie_results(results):
    clean = []
    for item in results:
        media_type = item.get("media_type", "movie")
        if media_type not in ["movie", "tv"]:
            continue
        title = item.get("title") or item.get("name")
        if not title or not item.get("poster_path"):
            continue
        clean.append({
            "id": item.get("id"),
            "type": media_type,
            "title": title,
            "overview": item.get("overview", "")[:150] + "..." if len(item.get("overview", "")) > 150 else item.get("overview", ""),
            "poster": f"{TMDB_IMAGE_URL}{item['poster_path']}",
            "backdrop": f"{TMDB_BACKDROP_URL}{item.get('backdrop_path', '')}" if item.get('backdrop_path') else None,
            "release_date": item.get("release_date") or item.get("first_air_date") or "",
            "vote_average": item.get("vote_average", 0),
        })
    return clean

@st.cache_data(ttl=3600)
def discover_movies(page=1, current_feeling=None, desired_feeling=None):
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
    try:
        params = {
            "api_key": api_key,
            "sort_by": "popularity.desc",
            "watch_region": "US",
            "with_watch_monetization_types": "flatrate|rent",
            "page": page,
            "include_adult": "false"
        }
        if genre_ids:
            params["with_genres"] = "|".join(map(str, list(set(genre_ids))[:3]))
        if avoid_genres:
            params["without_genres"] = ",".join(map(str, list(set(avoid_genres))))
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        return _clean_movie_results(r.json().get("results", []))
    except:
        return []

@st.cache_data(ttl=3600)
def search_movies(query, page=1):
    api_key = get_tmdb_key()
    if not api_key or not query:
        return []
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/search/multi",
            params={"api_key": api_key, "query": query, "include_adult": "false", "page": page},
            timeout=8
        )
        r.raise_for_status()
        results = [item for item in r.json().get("results", []) if item.get("media_type") in ["movie", "tv"]]
        return _clean_movie_results(results)
    except:
        return []

@st.cache_data(ttl=86400)
def get_movie_providers(tmdb_id, media_type):
    api_key = get_tmdb_key()
    if not api_key:
        return []
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
            params={"api_key": api_key},
            timeout=8
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        return (data.get("flatrate", []) + data.get("rent", []))[:8]
    except:
        return []

def get_movie_deep_link(provider_name, title):
    provider = (provider_name or "").strip()
    safe_title = quote_plus(title)
    if provider in MOVIE_SERVICES:
        return MOVIE_SERVICES[provider].format(title=safe_title)
    for key, template in MOVIE_SERVICES.items():
        if key.lower() in provider.lower() or provider.lower() in key.lower():
            return template.format(title=safe_title)
    return None

# --------------------------------------------------
# 9. NLP ENGINE (Mr.DP) - ENHANCED
# --------------------------------------------------
def nlp_infer_feelings(prompt):
    """Enhanced feeling detection with more keywords and smart inference"""
    t = (prompt or "").lower()
    current, desired = None, None
    
    # CURRENT FEELING DETECTION (expanded keywords)
    current_map = {
        "Bored": ["bored", "boring", "nothing to watch", "meh", "blah", "dull", "uninterested", "nothing good", "same old", "monoton"],
        "Stressed": ["stress", "burnout", "overwhelm", "too much", "pressure", "tense", "wound up", "frazzled", "overwork"],
        "Anxious": ["anxious", "anxiety", "panic", "nervous", "worried", "uneasy", "on edge", "jittery", "freaking out", "scared"],
        "Sad": ["sad", "down", "depressed", "blue", "crying", "upset", "unhappy", "miserable", "low", "bummed", "heartbr", "grief"],
        "Lonely": ["lonely", "alone", "isolated", "nobody", "no one", "by myself", "disconnected", "miss people"],
        "Angry": ["angry", "mad", "pissed", "furious", "rage", "annoyed", "irritated", "frustrated", "aggravat"],
        "Tired": ["tired", "exhaust", "drained", "sleepy", "fatigue", "worn out", "wiped", "no energy", "beat", "weary"],
        "Numb": ["numb", "empty", "void", "nothing", "hollow", "dead inside", "flat", "detached"],
        "Confused": ["confus", "lost", "uncertain", "don't know", "unsure", "unclear", "what to watch"],
        "Restless": ["restless", "antsy", "fidget", "can't sit still", "agitated", "edgy"],
        "Happy": ["happy", "good mood", "great day", "wonderful", "cheerful", "joyful", "feeling good"],
        "Excited": ["excited", "pumped", "hyped", "thrilled", "stoked", "can't wait", "amped"],
        "Calm": ["calm", "peaceful", "serene", "tranquil", "at ease", "relaxed already"],
        "Focused": ["focused", "productive", "in the zone", "concentrating", "working"],
    }
    
    # DESIRED FEELING DETECTION (expanded keywords)
    desired_map = {
        "Comforted": ["comfort", "cozy", "warm", "safe", "wholesome", "soft", "soothing", "hug", "feel better", "healing"],
        "Relaxed": ["relax", "unwind", "chill", "easy", "calm down", "de-stress", "mellow", "peaceful", "zen"],
        "Energized": ["action", "energy", "pump", "hype", "adrenaline", "intense", "exciting", "thrilling", "wild", "rush"],
        "Entertained": ["fun", "funny", "comedy", "laugh", "humor", "entertain", "amusing", "hilarious", "silly", "light", "enjoyable"],
        "Inspired": ["inspir", "motivat", "uplift", "meaning", "powerful", "moving", "profound", "thought-provok"],
        "Curious": ["curious", "learn", "discover", "documentary", "interesting", "fascinating", "intriguing", "mind-blowing", "educational"],
        "Sleepy": ["sleep", "bed", "wind down", "night", "drowsy", "ready for bed", "knock out"],
        "Connected": ["connect", "romance", "love", "relationship", "feel something", "emotional", "touching", "heartfelt", "romantic"],
        "Stimulated": ["thrill", "suspense", "edge", "twist", "mind", "think", "smart", "clever", "cerebral", "mystery", "puzzle"],
        "Happy": ["happy", "joy", "cheer", "good mood", "smile", "upbeat", "positive", "feel-good", "uplifting", "bright"],
        "Focused": ["focus", "concentrate", "study", "work", "productive", "get stuff done", "background"],
        "Grounded": ["grounded", "centered", "balanced", "stable", "rooted", "real"],
        "Calm": ["calm", "peace", "tranquil", "serene", "quiet", "still", "seren"],
    }
    
    # Find current feeling
    for feeling, keywords in current_map.items():
        if any(k in t for k in keywords):
            current = feeling
            break
    
    # Find desired feeling
    for feeling, keywords in desired_map.items():
        if any(k in t for k in keywords):
            desired = feeling
            break
    
    # SMART INFERENCE: If only current detected, infer desired
    if current and not desired:
        inference_map = {
            "Bored": "Entertained",
            "Stressed": "Relaxed",
            "Anxious": "Calm",
            "Sad": "Comforted",
            "Lonely": "Connected",
            "Angry": "Calm",
            "Tired": "Energized",
            "Numb": "Stimulated",
            "Confused": "Curious",
            "Restless": "Calm",
            "Happy": "Entertained",
            "Excited": "Energized",
            "Calm": "Relaxed",
            "Focused": "Focused",
        }
        desired = inference_map.get(current, "Entertained")
    
    # If no current but desired, infer current
    if desired and not current:
        reverse_inference = {
            "Comforted": "Sad",
            "Relaxed": "Stressed",
            "Calm": "Anxious",
            "Energized": "Tired",
            "Entertained": "Bored",
            "Stimulated": "Numb",
            "Connected": "Lonely",
            "Curious": "Bored",
            "Inspired": "Numb",
            "Happy": "Sad",
            "Focused": "Confused",
            "Grounded": "Anxious",
            "Sleepy": "Tired",
        }
        current = reverse_inference.get(desired, "Bored")
    
    return current, desired

def discover_movies_fresh(current_feeling=None, desired_feeling=None):
    """
    Non-cached movie discovery with randomization.
    Returns DIFFERENT results each time for variety.
    """
    api_key = get_tmdb_key()
    if not api_key:
        return []
    
    # Randomize for variety
    page = random.randint(1, 5)
    sort_options = ["popularity.desc", "vote_average.desc", "vote_count.desc"]
    sort_by = random.choice(sort_options)
    
    genre_ids, avoid_genres = [], []
    
    if desired_feeling and desired_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[desired_feeling]
        genre_ids.extend(prefs.get("prefer", [])[:3])
        avoid_genres.extend(prefs.get("avoid", []))
    
    if current_feeling and current_feeling in FEELING_TO_GENRES:
        prefs = FEELING_TO_GENRES[current_feeling]
        avoid_genres.extend(prefs.get("avoid", []))
    
    # Shuffle genres for variety
    if genre_ids:
        random.shuffle(genre_ids)
    
    try:
        params = {
            "api_key": api_key,
            "sort_by": sort_by,
            "watch_region": "US",
            "with_watch_monetization_types": "flatrate|rent",
            "page": page,
            "include_adult": "false",
            "vote_count.gte": 50,
        }
        
        if genre_ids:
            params["with_genres"] = "|".join(map(str, list(set(genre_ids))[:3]))
        
        if avoid_genres:
            params["without_genres"] = ",".join(map(str, list(set(avoid_genres))))
        
        r = requests.get(f"{TMDB_BASE_URL}/discover/movie", params=params, timeout=8)
        r.raise_for_status()
        results = r.json().get("results", [])
        
        # Shuffle results for variety
        random.shuffle(results)
        
        return _clean_movie_results(results)
    except Exception as e:
        print(f"Fresh discover error: {e}")
        return []


@st.cache_data(show_spinner=False, ttl=3600)
def nlp_to_tmdb_plan(prompt):
    p = (prompt or "").strip()
    if not p:
        return {"mode": "search", "query": "", "current_feeling": None, "desired_feeling": None, "raw_prompt": ""}
    
    h_current, h_desired = nlp_infer_feelings(p)
    mood_indicators = ["feel", "mood", "vibe", "something", "anything", "i'm", "i am", "need"]
    is_mood = any(k in p.lower() for k in mood_indicators) or h_current or h_desired
    heuristic_mode = "discover" if is_mood and (h_current or h_desired) else "search"
    
    if not openai_client:
        return {
            "mode": heuristic_mode,
            "query": p if heuristic_mode == "search" else "",
            "current_feeling": h_current,
            "desired_feeling": h_desired,
            "raw_prompt": p
        }
    
    try:
        sys = f"""Convert user request to JSON for movie/TV recommendations.
Return ONLY valid JSON with these keys:
- mode: "search" (specific title/actor/director) or "discover" (mood/vibe based)
- query: search keywords if mode=search, empty if discover
- current_feeling: one of {CURRENT_FEELINGS} or null
- desired_feeling: one of {DESIRED_FEELINGS} or null"""

        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": p}],
            temperature=0.2
        )
        content = (resp.choices[0].message.content or "").strip()
        content = content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(content)
        
        plan.setdefault("mode", heuristic_mode)
        plan.setdefault("query", "")
        plan.setdefault("current_feeling", h_current)
        plan.setdefault("desired_feeling", h_desired)
        plan["raw_prompt"] = p
        
        if plan.get("current_feeling") not in CURRENT_FEELINGS:
            plan["current_feeling"] = h_current
        if plan.get("desired_feeling") not in DESIRED_FEELINGS:
            plan["desired_feeling"] = h_desired
            
        return plan
    except:
        return {
            "mode": heuristic_mode,
            "query": p if heuristic_mode == "search" else "",
            "current_feeling": h_current,
            "desired_feeling": h_desired,
            "raw_prompt": p
        }

def nlp_search_tmdb(plan, page=1):
    """
    Execute NLP search plan - uses FRESH results (not cached) for variety.
    """
    if not plan:
        return []
    
    mode = (plan.get("mode") or "search").lower()
    query = (plan.get("query") or "").strip()
    current_feeling = plan.get("current_feeling")
    desired_feeling = plan.get("desired_feeling")
    
    # DISCOVER MODE: Use fresh (non-cached) results for variety
    if mode == "discover" and (current_feeling or desired_feeling):
        return discover_movies_fresh(current_feeling=current_feeling, desired_feeling=desired_feeling)
    
    # SEARCH MODE: Search by title/actor/director
    if query:
        results = search_movies(query, page=page)
        if results:
            return results
        # Fallback to discover if search fails
        h_current, h_desired = nlp_infer_feelings(plan.get("raw_prompt", ""))
        if h_current or h_desired:
            return discover_movies_fresh(current_feeling=h_current, desired_feeling=h_desired)
    
    # FALLBACK: If nothing else works, use feelings from plan
    if current_feeling or desired_feeling:
        return discover_movies_fresh(current_feeling=current_feeling, desired_feeling=desired_feeling)
    
    return []

# --------------------------------------------------
# 10. GAMIFICATION ENGINE
# --------------------------------------------------
def get_dopamine_points():
    if st.session_state.get("db_user_id") and SUPABASE_ENABLED:
        profile = get_user_profile(st.session_state.db_user_id)
        if profile:
            return profile.get("dopamine_points", 0)
    return st.session_state.get("dopamine_points", 0)

def add_dopamine_points(amount, reason=""):
    # Update local state
    current = st.session_state.get("dopamine_points", 0)
    st.session_state.dopamine_points = current + amount
    
    # Update database if logged in
    if st.session_state.get("db_user_id") and SUPABASE_ENABLED:
        add_dopamine_points_db(st.session_state.db_user_id, amount, reason)
    
    if reason:
        st.toast(f"+{amount} DP: {reason}", icon="⚡")

def get_streak():
    if st.session_state.get("db_user_id") and SUPABASE_ENABLED:
        profile = get_user_profile(st.session_state.db_user_id)
        if profile:
            return profile.get("streak_days", 0)
    return st.session_state.get("streak_days", 0)

def update_streak():
    if st.session_state.get("db_user_id") and SUPABASE_ENABLED:
        update_streak_db(st.session_state.db_user_id)
    else:
        # Local fallback
        today = datetime.now().strftime("%Y-%m-%d")
        last_visit = st.session_state.get("last_visit_date", "")
        if last_visit != today:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            if last_visit == yesterday:
                st.session_state.streak_days = st.session_state.get("streak_days", 0) + 1
                add_dopamine_points(10 * st.session_state.streak_days, f"{st.session_state.streak_days} day streak!")
            else:
                st.session_state.streak_days = 1
            st.session_state.last_visit_date = today

def get_level():
    points = get_dopamine_points()
    if points < 100:
        return ("Newbie", 1, 100)
    elif points < 500:
        return ("Explorer", 2, 500)
    elif points < 1500:
        return ("Curator", 3, 1500)
    elif points < 5000:
        return ("Connoisseur", 4, 5000)
    else:
        return ("Dopamine Master", 5, 999999)

def get_achievements():
    achievements = []
    points = get_dopamine_points()
    streak = get_streak()
    hits = st.session_state.get("quick_hit_count", 0)
    
    if streak >= 3:
        achievements.append(("🔥", "Hot Streak", "3+ days in a row"))
    if streak >= 7:
        achievements.append(("💎", "Week Warrior", "7+ day streak"))
    if streak >= 30:
        achievements.append(("🏆", "Monthly Master", "30+ day streak"))
    if hits >= 10:
        achievements.append(("⚡", "Quick Draw", "10+ Dope Hits"))
    if hits >= 50:
        achievements.append(("🎯", "Sharpshooter", "50+ Dope Hits"))
    if hits >= 100:
        achievements.append(("🎪", "Hit Machine", "100+ Dope Hits"))
    if points >= 100:
        achievements.append(("🌟", "Rising Star", "100+ DP"))
    if points >= 500:
        achievements.append(("⭐", "Bright Star", "500+ DP"))
    if points >= 1000:
        achievements.append(("👑", "Royalty", "1000+ DP"))
    if points >= 5000:
        achievements.append(("🦄", "Legendary", "5000+ DP"))
    
    return achievements

# --------------------------------------------------
# 11. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        # Auth
        "user": None,
        "db_user_id": None,
        "auth_step": "landing",
        "is_premium": False,
        "auth_error": None,
        "auth_success": None,
        
        # Mood
        "current_feeling": "Bored",
        "desired_feeling": "Entertained",
        "last_emotion_key": None,
        
        # Navigation
        "active_page": "🎬 Movies",
        
        # Movies
        "movies_feed": [],
        "movies_page": 1,
        
        # Search
        "search_query": "",
        "search_results": [],
        "search_page": 1,
        
        # NLP
        "nlp_prompt": "",
        "nlp_plan": None,
        "nlp_results": [],
        "nlp_page": 1,
        "nlp_last_prompt": "",
        
        # Quick Hit
        "quick_hit": None,
        "quick_hit_count": 0,
        
        # Gamification
        "dopamine_points": 0,
        "streak_days": 0,
        "last_visit_date": "",
        
        # Social
        "referral_code": None,
        "watchlist": [],
        "mood_history": [],
        
        # UI
        "show_premium_modal": False,
        "show_trailers": True,
    })
    st.session_state.init = True

# Generate referral code (fallback)
if not st.session_state.get("referral_code"):
    st.session_state.referral_code = hashlib.md5(str(random.random()).encode()).hexdigest()[:8].upper()

# --------------------------------------------------
# 12. CSS - COMPLETE STYLING
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #050508;
    --bg-secondary: #0a0a10;
    --bg-card: rgba(255, 255, 255, 0.02);
    --accent-primary: #8b5cf6;
    --accent-secondary: #06b6d4;
    --accent-tertiary: #10b981;
    --accent-gradient: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
    --accent-gradient-2: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
    --text-primary: #ffffff;
    --text-secondary: rgba(255, 255, 255, 0.6);
    --glass: rgba(255, 255, 255, 0.03);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-hover: rgba(255, 255, 255, 0.06);
    --error: #ef4444;
    --success: #10b981;
}

* { font-family: 'Outfit', sans-serif; }
h1, h2, h3, .stat-value, .hero-title { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: var(--bg-primary);
    background-image: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse 60% 40% at 100% 100%, rgba(6, 182, 212, 0.1) 0%, transparent 50%),
        radial-gradient(ellipse 40% 30% at 0% 100%, rgba(16, 185, 129, 0.08) 0%, transparent 50%);
}

#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
div[data-testid="stToolbar"] {display: none;}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
}

section[data-testid="stSidebar"] .stTextArea textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

.landing-hero {
    text-align: center;
    padding: 60px 20px;
    max-width: 900px;
    margin: 0 auto;
}

.landing-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
    line-height: 1.1;
}

.landing-subtitle {
    font-size: 1.5rem;
    color: var(--text-secondary);
    margin-bottom: 40px;
    line-height: 1.5;
}

.landing-tagline {
    font-size: 1.1rem;
    color: var(--text-secondary);
    margin-bottom: 32px;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin: 48px 0;
}

.feature-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    transition: all 0.3s;
}

.feature-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-4px);
}

.feature-icon { font-size: 2.5rem; margin-bottom: 16px; }
.feature-title { font-weight: 600; font-size: 1.1rem; margin-bottom: 8px; color: var(--text-primary); }
.feature-desc { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5; }

.auth-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 40px;
    max-width: 420px;
    margin: 0 auto;
}

.auth-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 8px;
}

.auth-subtitle {
    text-align: center;
    color: var(--text-secondary);
    margin-bottom: 24px;
}

.auth-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--error);
    color: var(--error);
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 16px;
    font-size: 0.9rem;
}

.auth-success {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--success);
    color: var(--success);
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 16px;
    font-size: 0.9rem;
}

.auth-divider {
    display: flex;
    align-items: center;
    margin: 20px 0;
    color: var(--text-secondary);
    font-size: 0.8rem;
}

.auth-divider::before, .auth-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--glass-border);
}

.auth-divider span { padding: 0 16px; }

.stats-bar {
    display: flex;
    gap: 16px;
    padding: 16px 20px;
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    justify-content: center;
}

.stat-item {
    text-align: center;
    min-width: 80px;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    font-size: 0.65rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}

@keyframes fireGlow {
    0%, 100% { filter: drop-shadow(0 0 4px #ff6b35) drop-shadow(0 0 8px #ff6b35); transform: scale(1); }
    50% { filter: drop-shadow(0 0 8px #ff9f1c) drop-shadow(0 0 16px #ff9f1c); transform: scale(1.1); }
}
.streak-fire { animation: fireGlow 1.5s ease-in-out infinite; font-size: 1.5rem; }

.level-bar {
    height: 6px;
    background: var(--glass);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 6px;
}
.level-progress {
    height: 100%;
    background: var(--accent-gradient);
    border-radius: 3px;
    transition: width 0.5s ease;
}

.movie-card {
    background: var(--glass);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 16px;
}
.movie-card:hover {
    transform: scale(1.04) translateY(-8px);
    border-color: var(--accent-primary);
    box-shadow: 0 20px 40px rgba(139, 92, 246, 0.25);
}
.movie-poster {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
}
.movie-info {
    padding: 14px;
}
.movie-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-primary);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.movie-year {
    font-size: 0.75rem;
    color: var(--text-secondary);
}
.movie-rating {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 215, 0, 0.15);
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    color: #ffd700;
    margin-top: 6px;
}

.provider-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 10px 14px;
    border-top: 1px solid var(--glass-border);
    max-height: 80px;
    overflow: hidden;
}
.provider-btn {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: var(--bg-secondary);
    border: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    text-decoration: none;
}
.provider-btn:hover {
    transform: scale(1.15);
    border-color: var(--accent-primary);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}
.provider-icon {
    width: 22px;
    height: 22px;
    border-radius: 5px;
}

.service-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 18px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    text-decoration: none;
    color: var(--text-primary);
    transition: all 0.2s;
    margin-bottom: 10px;
}
.service-btn:hover {
    border-color: var(--accent-primary);
    transform: translateX(4px);
    background: var(--glass-hover);
}
.service-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}
.service-name { font-weight: 600; font-size: 0.95rem; }
.service-desc { font-size: 0.8rem; color: var(--text-secondary); }

.stButton > button {
    background: var(--accent-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
}

.glass-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 16px;
}
.glass-card:hover {
    border-color: rgba(139, 92, 246, 0.3);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 24px 0 16px 0;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0;
}
.section-icon { font-size: 1.4rem; }

.nlp-header {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid var(--accent-primary);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 20px;
}
.nlp-prompt {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}
.nlp-meta {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

.achievement {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 10px;
    margin: 3px;
    font-size: 0.75rem;
}
.achievement-icon { font-size: 1rem; }
.achievement-text { color: var(--text-secondary); }

.share-card {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid var(--accent-primary);
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.share-card::before {
    content: '';
    position: absolute;
    top: -100%;
    left: -100%;
    width: 300%;
    height: 300%;
    background: radial-gradient(circle, rgba(139, 92, 246, 0.05) 0%, transparent 40%);
    animation: rotate 15s linear infinite;
}
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.share-title { font-size: 1.2rem; font-weight: 700; position: relative; }
.share-mood { font-size: 2.5rem; margin: 12px 0; position: relative; }

.referral-code {
    font-family: 'Space Grotesk', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 3px;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.premium-badge {
    background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
    color: black;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.pricing-card {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 32px;
    text-align: center;
    transition: all 0.3s;
}
.pricing-card.featured {
    border-color: var(--accent-primary);
    transform: scale(1.05);
    box-shadow: 0 20px 60px rgba(139, 92, 246, 0.3);
}
.pricing-name { font-weight: 700; font-size: 1.3rem; margin-bottom: 8px; }
.pricing-price { font-size: 2.5rem; font-weight: 700; }
.pricing-period { color: var(--text-secondary); }

.testimonial {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.testimonial-text { font-style: italic; color: var(--text-secondary); margin-bottom: 12px; line-height: 1.6; }
.testimonial-author { font-weight: 600; color: var(--text-primary); }

.about-section {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 40px;
    margin: 40px 0;
}

.menu-btn {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    margin: 4px 0;
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    cursor: pointer;
    color: var(--text-secondary);
    font-weight: 500;
    transition: all 0.2s;
    text-decoration: none;
}
.menu-btn:hover {
    background: rgba(139, 92, 246, 0.1);
    border-color: var(--accent-primary);
    color: var(--text-primary);
    transform: translateX(4px);
}
.menu-btn.active {
    background: var(--accent-gradient);
    border-color: transparent;
    color: white;
}
.menu-icon { font-size: 1.3rem; }
.menu-label { font-size: 0.95rem; }

.stTextInput input, .stTextArea textarea {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-secondary); }
::-webkit-scrollbar-thumb { background: var(--accent-primary); border-radius: 3px; }

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.5); }
    50% { box-shadow: 0 0 0 12px rgba(245, 158, 11, 0); }
}
.pulse { animation: pulse 2s infinite; }

.hero-container {
    position: relative;
    border-radius: 28px;
    overflow: hidden;
    margin-bottom: 28px;
    background: var(--glass);
    border: 1px solid var(--glass-border);
}
.hero-backdrop {
    width: 100%;
    height: 380px;
    object-fit: cover;
    opacity: 0.7;
    mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
    -webkit-mask-image: linear-gradient(to bottom, black 40%, transparent 100%);
}
.hero-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 32px;
    background: linear-gradient(to top, var(--bg-primary) 20%, transparent 100%);
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: white;
    margin: 0 0 8px 0;
    text-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.hero-meta {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 12px;
}
.hero-overview {
    color: var(--text-secondary);
    max-width: 550px;
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.5;
}

.supabase-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: rgba(62, 207, 142, 0.1);
    border: 1px solid #3ecf8e;
    border-radius: 8px;
    font-size: 0.7rem;
    color: #3ecf8e;
}

.verified-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    color: var(--success);
    font-size: 0.8rem;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 13. HELPER FUNCTIONS
# --------------------------------------------------
def safe(s):
    return html_lib.escape(s or "")

def render_stats_bar():
    level_name, level_num, next_level = get_level()
    points = get_dopamine_points()
    streak = get_streak()
    progress = min(100, (points / next_level) * 100)
    
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{points}</div>
            <div class="stat-label">Dopamine Points</div>
        </div>
        <div class="stat-item">
            <span class="streak-fire">🔥</span>
            <div class="stat-value">{streak}</div>
            <div class="stat-label">Day Streak</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">Lv.{level_num}</div>
            <div class="stat-label">{level_name}</div>
            <div class="level-bar"><div class="level-progress" style="width: {progress}%"></div></div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{st.session_state.get('quick_hit_count', 0)}</div>
            <div class="stat-label">Dope Hits</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_movie_card(item, show_providers=True):
    title = item.get("title", "")
    year = item.get("release_date", "")[:4]
    rating = item.get("vote_average", 0)
    poster = item.get("poster")
    tmdb_id = item.get("id")
    media_type = item.get("type", "movie")
    
    providers_html = ""
    if show_providers:
        providers = get_movie_providers(tmdb_id, media_type)
        if providers:
            icons = ""
            for p in providers[:6]:
                name = p.get("provider_name", "")
                logo = p.get("logo_path")
                if not logo:
                    continue
                link = get_movie_deep_link(name, title)
                if not link:
                    continue
                icons += f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='{safe(name)}'><img src='{TMDB_LOGO_URL}{logo}' class='provider-icon'></a>"
            if icons:
                providers_html = f"<div class='provider-grid'>{icons}</div>"
    
    rating_html = f"<div class='movie-rating'>⭐ {rating:.1f}</div>" if rating > 0 else ""
    
    st.markdown(f"""
    <div class="movie-card">
        <img src="{safe(poster)}" class="movie-poster" loading="lazy" onerror="this.style.background='#1a1a2e'">
        <div class="movie-info">
            <div class="movie-title">{safe(title)}</div>
            <div class="movie-year">{year}</div>
            {rating_html}
        </div>
        {providers_html}
    </div>
    """, unsafe_allow_html=True)

def render_hero(movie):
    if not movie:
        return
    backdrop = movie.get("backdrop") or movie.get("poster")
    title = movie.get("title", "")
    overview = movie.get("overview", "")
    year = movie.get("release_date", "")[:4]
    rating = movie.get("vote_average", 0)
    
    st.markdown(f"""
    <div class="hero-container">
        <img src="{safe(backdrop)}" class="hero-backdrop" onerror="this.style.opacity='0.3'">
        <div class="hero-content">
            <div class="hero-title">{safe(title)}</div>
            <div class="hero-meta">{year} {'• ⭐ ' + f'{rating:.1f}' if rating else ''}</div>
            <p class="hero-overview">{safe(overview)}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_service_buttons(services, query):
    for name, data in services.items():
        url = data["url"].format(query=quote_plus(query))
        color = data.get("color", "#8b5cf6")
        icon = data.get("icon", "🔗")
        st.markdown(f"""
        <a href="{url}" target="_blank" class="service-btn">
            <div class="service-icon" style="background:{color};">{icon}</div>
            <div>
                <div class="service-name">{name}</div>
                <div class="service-desc">Search "{query[:25]}..."</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

def render_share_card():
    current = st.session_state.current_feeling
    desired = st.session_state.desired_feeling
    points = get_dopamine_points()
    streak = get_streak()
    
    st.markdown(f"""
    <div class="share-card">
        <div class="share-title">My Dopamine Profile</div>
        <div class="share-mood">{MOOD_EMOJIS.get(current, '😊')} → {MOOD_EMOJIS.get(desired, '✨')}</div>
        <p style="color: var(--text-secondary); position: relative; margin: 0;">
            Feeling <strong>{current}</strong>, seeking <strong>{desired}</strong>
        </p>
        <div style="margin-top: 12px; position: relative;">
            <span style="margin: 0 8px;">🔥 {streak} day streak</span>
            <span style="margin: 0 8px;">⚡ {points} DP</span>
        </div>
        <p style="margin-top: 12px; font-size: 0.75rem; color: var(--text-secondary); position: relative;">
            dopamine.watch
        </p>
    </div>
    """, unsafe_allow_html=True)

def get_quick_hit():
    movies = discover_movies(
        page=random.randint(1, 3),
        current_feeling=st.session_state.current_feeling,
        desired_feeling=st.session_state.desired_feeling
    )
    if movies:
        add_dopamine_points(15, "Quick Hit!")
        st.session_state.quick_hit_count = st.session_state.get("quick_hit_count", 0) + 1
        return random.choice(movies[:5])
    return None

# --------------------------------------------------
# 14. LANDING PAGE
# --------------------------------------------------
def render_landing():
    st.markdown("""
    <div class="landing-hero">
        <h1 class="landing-title">🧠 Dopamine.watch</h1>
        <p class="landing-subtitle">The first streaming guide designed for <strong>ADHD & neurodivergent brains</strong>.</p>
        <p class="landing-tagline">Tell us how you feel. We'll find the perfect content to match your mood.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth status badge
    if SUPABASE_ENABLED:
        st.markdown("<div style='text-align:center;margin-bottom:20px;'><span class='supabase-badge'>🔐 Secure Auth Enabled</span></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Get Started Free", use_container_width=True, key="cta_signup"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button("🔑 Log In", use_container_width=True, key="cta_login"):
                st.session_state.auth_step = "login"
                st.rerun()
    
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Mood-Driven Discovery</div>
            <div class="feature-desc">Select how you feel now and how you want to feel. We'll curate content that takes you there.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧾</div>
            <div class="feature-title">Mr.DP - AI Curator</div>
            <div class="feature-desc">Just type what you want in plain English. "Something funny for a stressed day" — done.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Quick Dope Hit</div>
            <div class="feature-desc">Can't decide? One button gives you the perfect match. No scrolling required.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎬</div>
            <div class="feature-title">Movies & TV</div>
            <div class="feature-desc">Emotion-filtered recommendations from Netflix, Disney+, Max, and 20+ streaming services.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎵</div>
            <div class="feature-title">Music & Playlists</div>
            <div class="feature-desc">Mood-matched music from Spotify, Apple Music, and more. Perfect vibes, every time.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎙️</div>
            <div class="feature-title">Podcasts & Books</div>
            <div class="feature-desc">Curated podcasts and audiobooks based on your current headspace.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>💬</span><h2 class='section-title'>What People Are Saying</h2></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"Finally an app that understands my ADHD brain. No more endless scrolling through Netflix!"</div>
            <div class="testimonial-author">— Sarah K., Designer</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"The Quick Dope Hit button is a game changer. Decision fatigue? Gone. I love this app."</div>
            <div class="testimonial-author">— Marcus T., Developer</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="testimonial">
            <div class="testimonial-text">"I love that it asks how I WANT to feel, not just what genre I want. So thoughtful."</div>
            <div class="testimonial-author">— Jamie L., Teacher</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>💎</span><h2 class='section-title'>Simple Pricing</h2></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-name">Free</div>
            <div class="pricing-price">$0</div>
            <div class="pricing-period">forever</div>
            <hr style="border-color: var(--glass-border); margin: 20px 0;">
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.8;">
                ✓ Mood-based discovery<br>
                ✓ Quick Dope Hit<br>
                ✓ All content types<br>
                ✓ Basic Mr.DP
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="pricing-card featured">
            <div style="background: var(--accent-gradient); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; display: inline-block; margin-bottom: 12px;">MOST POPULAR</div>
            <div class="pricing-name">Plus</div>
            <div class="pricing-price">$4.99</div>
            <div class="pricing-period">/month</div>
            <hr style="border-color: var(--glass-border); margin: 20px 0;">
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.8;">
                ✓ Everything in Free<br>
                ✓ Advanced AI curation<br>
                ✓ No ads<br>
                ✓ 2x Dopamine Points<br>
                ✓ Mood analytics
            </p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-name">Pro</div>
            <div class="pricing-price">$9.99</div>
            <div class="pricing-period">/month</div>
            <hr style="border-color: var(--glass-border); margin: 20px 0;">
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.8;">
                ✓ Everything in Plus<br>
                ✓ Priority support<br>
                ✓ Early features<br>
                ✓ Custom triggers<br>
                ✓ API access
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="about-section">
        <h2 style="text-align: center; margin-bottom: 24px;">About Dopamine.watch</h2>
        <p style="color: var(--text-secondary); text-align: center; max-width: 700px; margin: 0 auto; line-height: 1.8;">
            We built Dopamine.watch because we know the struggle. Spending 45 minutes scrolling through Netflix, 
            only to give up and rewatch The Office again. Decision fatigue is real, especially for neurodivergent brains.
            <br><br>
            Our mission is simple: <strong>help you feel better, faster</strong>. By understanding your current emotional 
            state and where you want to be, we cut through the noise and deliver exactly what you need.
            <br><br>
            Built with ❤️ for ADHD brains, by ADHD brains.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align: center;'>Ready to feel better?</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Start Free", use_container_width=True, key="footer_cta"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button("👤 Continue as Guest", use_container_width=True, key="guest_landing"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()

# --------------------------------------------------
# 15. AUTH SCREENS - WITH SUPABASE
# --------------------------------------------------
def render_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🧠</h1>
            <div class="auth-title">Welcome Back</div>
            <div class="auth-subtitle">Log in to your dopamine engine</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show errors/success
        if st.session_state.get("auth_error"):
            st.markdown(f"<div class='auth-error'>❌ {st.session_state.auth_error}</div>", unsafe_allow_html=True)
            st.session_state.auth_error = None
        if st.session_state.get("auth_success"):
            st.markdown(f"<div class='auth-success'>✅ {st.session_state.auth_success}</div>", unsafe_allow_html=True)
            st.session_state.auth_success = None
        
        email = st.text_input("Email", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
        
        if st.button("🔑 Log In", use_container_width=True, key="login_btn"):
            if email and password:
                if SUPABASE_ENABLED:
                    with st.spinner("Logging in..."):
                        result = supabase_sign_in(email, password)
                    if result["success"]:
                        st.session_state.user = {
                            "email": email,
                            "name": result.get("profile", {}).get("name", email.split("@")[0]),
                            "id": result["user"].id
                        }
                        st.session_state.db_user_id = result["user"].id
                        
                        # Load profile data
                        profile = result.get("profile") or {}
                        st.session_state.dopamine_points = profile.get("dopamine_points", 0)
                        st.session_state.streak_days = profile.get("streak_days", 0)
                        st.session_state.referral_code = profile.get("referral_code", st.session_state.referral_code)
                        st.session_state.is_premium = profile.get("is_premium", False)
                        
                        update_streak()
                        st.balloons()
                        st.rerun()
                    else:
                        st.session_state.auth_error = result.get("error", "Login failed")
                        st.rerun()
                else:
                    # Fallback to local auth
                    st.session_state.user = {"email": email, "name": email.split("@")[0]}
                    update_streak()
                    add_dopamine_points(25, "Welcome back!")
                    st.rerun()
            else:
                st.session_state.auth_error = "Please enter email and password"
                st.rerun()
        
        # Forgot password
        if SUPABASE_ENABLED:
            st.markdown("<div class='auth-divider'><span>or</span></div>", unsafe_allow_html=True)
            if st.button("Forgot Password?", use_container_width=True, key="forgot_pass"):
                st.session_state.auth_step = "reset"
                st.rerun()
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Create Account", use_container_width=True, key="to_signup"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button("👤 Guest Mode", use_container_width=True, key="guest_login"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()
        
        if st.button("← Back to Home", key="back_login"):
            st.session_state.auth_step = "landing"
            st.rerun()

def render_signup():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🧠</h1>
            <div class="auth-title">Create Account</div>
            <div class="auth-subtitle">Start your dopamine journey</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show errors
        if st.session_state.get("auth_error"):
            st.markdown(f"<div class='auth-error'>❌ {st.session_state.auth_error}</div>", unsafe_allow_html=True)
            st.session_state.auth_error = None
        
        name = st.text_input("Name", key="signup_name", placeholder="Your name")
        email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="signup_pass", placeholder="••••••••  (min 6 chars)")
        referral = st.text_input("Referral Code (optional)", key="signup_referral", placeholder="ABCD1234")
        
        if st.button("🚀 Create Account", use_container_width=True, key="signup_btn"):
            if email and name and password:
                if len(password) < 6:
                    st.session_state.auth_error = "Password must be at least 6 characters"
                    st.rerun()
                elif SUPABASE_ENABLED:
                    with st.spinner("Creating account..."):
                        result = supabase_sign_up(email, password, name)
                    if result["success"]:
                        st.session_state.user = {
                            "email": email,
                            "name": name,
                            "id": result["user"].id
                        }
                        st.session_state.db_user_id = result["user"].id
                        st.session_state.dopamine_points = 50
                        st.session_state.streak_days = 1
                        
                        # Apply referral code bonus
                        if referral:
                            check_referral_code(referral, result["user"].id)
                        
                        st.balloons()
                        st.toast("🎉 Welcome to Dopamine.watch! +50 DP", icon="⚡")
                        st.rerun()
                    else:
                        st.session_state.auth_error = result.get("error", "Registration failed")
                        st.rerun()
                else:
                    # Fallback to local
                    st.session_state.user = {"email": email, "name": name}
                    update_streak()
                    add_dopamine_points(50, "Welcome to Dopamine.watch!")
                    st.balloons()
                    st.rerun()
            else:
                st.session_state.auth_error = "Please fill in all fields"
                st.rerun()
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Have Account? Log In", use_container_width=True, key="to_login"):
                st.session_state.auth_step = "login"
                st.rerun()
        with c2:
            if st.button("👤 Guest Mode", use_container_width=True, key="guest_signup"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()
        
        if st.button("← Back to Home", key="back_signup"):
            st.session_state.auth_step = "landing"
            st.rerun()

def render_reset_password():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🔐</h1>
            <div class="auth-title">Reset Password</div>
            <div class="auth-subtitle">We'll send you a reset link</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("auth_error"):
            st.markdown(f"<div class='auth-error'>❌ {st.session_state.auth_error}</div>", unsafe_allow_html=True)
            st.session_state.auth_error = None
        if st.session_state.get("auth_success"):
            st.markdown(f"<div class='auth-success'>✅ {st.session_state.auth_success}</div>", unsafe_allow_html=True)
            st.session_state.auth_success = None
        
        email = st.text_input("Email", key="reset_email", placeholder="your@email.com")
        
        if st.button("📧 Send Reset Link", use_container_width=True, key="reset_btn"):
            if email:
                result = supabase_reset_password(email)
                if result["success"]:
                    st.session_state.auth_success = "Check your email for the reset link!"
                else:
                    st.session_state.auth_error = result.get("error", "Failed to send reset email")
                st.rerun()
            else:
                st.session_state.auth_error = "Please enter your email"
                st.rerun()
        
        st.markdown("---")
        
        if st.button("← Back to Login", use_container_width=True, key="back_reset"):
            st.session_state.auth_step = "login"
            st.rerun()

# --------------------------------------------------
# 16. SIDEBAR
# --------------------------------------------------
def render_sidebar():
    with st.sidebar:
        user_name = st.session_state.user.get('name', 'Friend')
        user_email = st.session_state.user.get('email', '')
        
        st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; margin: 0;">
                🧠 Dopamine<span style="background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">.watch</span>
            </h1>
            <p style="color: var(--text-secondary); font-size: 0.75rem; margin: 4px 0 0 0;">
                Hey, {user_name}! 👋
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show verified badge if logged in via Supabase
        if st.session_state.get("db_user_id") and SUPABASE_ENABLED:
            st.markdown(f"<span class='verified-badge'>✓ {user_email[:20]}...</span>", unsafe_allow_html=True)
        
        if st.session_state.get("is_premium"):
            st.markdown("<span class='premium-badge'>⭐ Premium</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # NAVIGATION MENU
        st.markdown("#### 📍 Navigate")
        
        menu_items = [
            ("🎬", "Movies"),
            ("🎵", "Music"),
            ("🎙️", "Podcasts"),
            ("📚", "Audiobooks"),
            ("⚡", "Shorts"),
        ]
        
        for icon, label in menu_items:
            full_label = f"{icon} {label}"
            is_active = st.session_state.active_page == full_label
            btn_type = "primary" if is_active else "secondary"
            if st.button(full_label, use_container_width=True, key=f"nav_{label}", type=btn_type):
                st.session_state.active_page = full_label
                st.session_state.search_results = []
                st.session_state.search_query = ""
                st.session_state.nlp_results = []
                st.session_state.quick_hit = None
                st.rerun()
        
        st.markdown("---")
        
        # MOOD SELECTORS
        st.markdown("#### 🎯 Your Mood")
        
        current_options = [f"{MOOD_EMOJIS.get(f, '😊')} {f}" for f in CURRENT_FEELINGS]
        current_idx = CURRENT_FEELINGS.index(st.session_state.current_feeling) if st.session_state.current_feeling in CURRENT_FEELINGS else 6
        current_choice = st.selectbox(
            "I feel...",
            options=current_options,
            index=current_idx,
            key="current_select"
        )
        new_current = current_choice.split(" ", 1)[1] if " " in current_choice else current_choice
        if new_current != st.session_state.current_feeling:
            st.session_state.current_feeling = new_current
            st.session_state.movies_feed = []
            add_dopamine_points(5, "Mood check!")
        
        desired_options = [f"{MOOD_EMOJIS.get(f, '✨')} {f}" for f in DESIRED_FEELINGS]
        desired_idx = DESIRED_FEELINGS.index(st.session_state.desired_feeling) if st.session_state.desired_feeling in DESIRED_FEELINGS else 7
        desired_choice = st.selectbox(
            "I want...",
            options=desired_options,
            index=desired_idx,
            key="desired_select"
        )
        new_desired = desired_choice.split(" ", 1)[1] if " " in desired_choice else desired_choice
        if new_desired != st.session_state.desired_feeling:
            st.session_state.desired_feeling = new_desired
            st.session_state.movies_feed = []
            add_dopamine_points(5, "Mood updated!")
        
        st.markdown("---")
        
        # QUICK HIT
        if st.button("⚡ QUICK DOPE HIT", use_container_width=True, key="quick_hit_sidebar", type="primary"):
            st.session_state.quick_hit = get_quick_hit()
            st.session_state.nlp_results = []
            st.session_state.nlp_last_prompt = ""
            st.session_state.search_results = []
            st.rerun()
        
        st.markdown("---")
        
        # MR.DP NLP
        st.markdown("#### 🧾 Mr.DP")
        st.caption("Your AI curator — describe what you want!")
        
        nlp_prompt = st.text_area(
            "Ask Mr.DP",
            placeholder="Examples:\n• 'smart sci-fi from the 90s'\n• 'I'm sad, need comfort'\n• 'Christopher Nolan films'",
            height=100,
            key="nlp_input",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔮 Ask", use_container_width=True, key="nlp_ask"):
                if nlp_prompt.strip():
                    with st.spinner("Mr.DP is thinking..."):
                        st.session_state.nlp_last_prompt = nlp_prompt
                        st.session_state.nlp_plan = nlp_to_tmdb_plan(nlp_prompt)
                        
                        # Update sidebar moods based on NLP detection
                        plan = st.session_state.nlp_plan
                        if plan.get("current_feeling"):
                            st.session_state.current_feeling = plan["current_feeling"]
                        if plan.get("desired_feeling"):
                            st.session_state.desired_feeling = plan["desired_feeling"]
                        
                        # Clear old movies feed so it updates
                        st.session_state.movies_feed = []
                        
                        # Get fresh results (not cached!)
                        st.session_state.nlp_results = nlp_search_tmdb(st.session_state.nlp_plan, page=1)
                        st.session_state.nlp_page = 1
                        st.session_state.quick_hit = None
                        st.session_state.search_results = []
                        add_dopamine_points(10, "Asked Mr.DP!")
                    st.rerun()
        with col2:
            if st.button("✕ Clear", use_container_width=True, key="nlp_clear"):
                st.session_state.nlp_results = []
                st.session_state.nlp_last_prompt = ""
                st.session_state.nlp_plan = None
                st.rerun()
        
        st.markdown("---")
        
        # SHARE
        st.markdown("#### 📤 Share & Invite")
        ref_code = st.session_state.referral_code
        st.markdown(f"<div style='text-align: center;'><span class='referral-code'>{ref_code}</span></div>", unsafe_allow_html=True)
        st.caption("Share your code — both get 100 DP!")
        
        st.markdown("---")
        
        # PREMIUM
        if not st.session_state.get("is_premium"):
            if st.button("⭐ Go Premium", use_container_width=True, key="premium_sidebar"):
                st.session_state.show_premium_modal = True
                st.rerun()
        
        st.markdown("---")
        
        # LOGOUT
        if st.button("🚪 Log Out", use_container_width=True, key="logout_btn"):
            if SUPABASE_ENABLED:
                supabase_sign_out()
            st.session_state.user = None
            st.session_state.db_user_id = None
            st.session_state.auth_step = "landing"
            st.rerun()
        
        st.caption("v34.0 • Supabase Auth 🔐")

# --------------------------------------------------
# 17. MAIN CONTENT
# --------------------------------------------------
def render_main():
    render_stats_bar()
    
    achievements = get_achievements()
    if achievements:
        ach_html = "".join([f"<span class='achievement'><span class='achievement-icon'>{a[0]}</span><span class='achievement-text'>{a[1]}</span></span>" for a in achievements[:5]])
        st.markdown(f"<div style='margin-bottom: 20px;'>{ach_html}</div>", unsafe_allow_html=True)
    
    # GLOBAL SEARCH
    st.markdown("#### 🔍 Search Everything")
    search_col1, search_col2 = st.columns([5, 1])
    with search_col1:
        search_query = st.text_input(
            "Search",
            placeholder="Search movies, shows, actors, directors...",
            key="global_search",
            label_visibility="collapsed"
        )
    with search_col2:
        search_clicked = st.button("Search", use_container_width=True, key="search_btn")
    
    if search_clicked and search_query:
        st.session_state.search_query = search_query
        st.session_state.search_results = search_movies(search_query)
        st.session_state.quick_hit = None
        st.session_state.nlp_results = []
        add_dopamine_points(5, "Searching!")
    
    if st.session_state.search_results:
        if st.button("✕ Clear Search Results", key="clear_search"):
            st.session_state.search_results = []
            st.session_state.search_query = ""
            st.rerun()
    
    st.markdown("---")
    
    # QUICK HIT
    if st.session_state.quick_hit:
        st.markdown("<div class='section-header'><span class='section-icon'>⚡</span><h2 class='section-title'>Your Perfect Match</h2></div>", unsafe_allow_html=True)
        render_hero(st.session_state.quick_hit)
        
        providers = get_movie_providers(st.session_state.quick_hit.get("id"), st.session_state.quick_hit.get("type", "movie"))
        if providers:
            provider_cols = st.columns(min(len(providers), 6))
            for i, p in enumerate(providers[:6]):
                with provider_cols[i]:
                    link = get_movie_deep_link(p.get("provider_name", ""), st.session_state.quick_hit.get("title", ""))
                    if link:
                        st.markdown(f"<a href='{link}' target='_blank' style='display:block; text-align:center; padding:12px; background:var(--glass); border:1px solid var(--glass-border); border-radius:12px; color:white; text-decoration:none; font-size:0.8rem;'>{p.get('provider_name', '')[:12]}</a>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🔄 Another Hit", use_container_width=True, key="another_hit"):
                st.session_state.quick_hit = get_quick_hit()
                st.rerun()
        with col2:
            if st.button("📤 Share", use_container_width=True, key="share_hit"):
                st.toast("Share card copied!", icon="📤")
        with col3:
            if st.button("✕ Close", use_container_width=True, key="close_hit"):
                st.session_state.quick_hit = None
                st.rerun()
        
        st.markdown("---")
    
    # SEARCH RESULTS
    if st.session_state.search_results:
        st.markdown(f"<div class='section-header'><span class='section-icon'>🔍</span><h2 class='section-title'>Results for \"{safe(st.session_state.search_query)}\"</h2></div>", unsafe_allow_html=True)
        cols = st.columns(6)
        for i, movie in enumerate(st.session_state.search_results[:24]):
            with cols[i % 6]:
                render_movie_card(movie)
        st.markdown("---")
    
    # NLP RESULTS
    if st.session_state.nlp_last_prompt and st.session_state.nlp_results:
        plan = st.session_state.nlp_plan or {}
        mode = plan.get("mode", "search")
        query = plan.get("query", "")
        current_f = plan.get("current_feeling", "")
        desired_f = plan.get("desired_feeling", "")
        
        # Build metadata string
        meta_parts = [f"Mode: {mode.title()}"]
        if query:
            meta_parts.append(f"Query: {query}")
        if current_f:
            meta_parts.append(f"Feeling: {MOOD_EMOJIS.get(current_f, '')} {current_f}")
        if desired_f:
            meta_parts.append(f"Want: {MOOD_EMOJIS.get(desired_f, '')} {desired_f}")
        
        st.markdown(f"""
        <div class="nlp-header">
            <div class="nlp-prompt">🧾 Mr.DP: "{safe(st.session_state.nlp_last_prompt)}"</div>
            <div class="nlp-meta">{' • '.join(meta_parts)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(6)
        for i, movie in enumerate(st.session_state.nlp_results[:24]):
            with cols[i % 6]:
                render_movie_card(movie)
        
        # Action buttons for NLP results
        btn_cols = st.columns([1, 1, 1])
        with btn_cols[0]:
            if st.button("🔄 Shuffle Results", key="nlp_shuffle", use_container_width=True):
                # Get fresh results with same feelings
                st.session_state.nlp_results = nlp_search_tmdb(st.session_state.nlp_plan, page=1)
                add_dopamine_points(5, "Shuffled!")
                st.rerun()
        with btn_cols[1]:
            if len(st.session_state.nlp_results) >= 20:
                if st.button("📥 Load More", key="nlp_more", use_container_width=True):
                    st.session_state.nlp_page += 1
                    more = discover_movies_fresh(
                        current_feeling=st.session_state.nlp_plan.get("current_feeling"),
                        desired_feeling=st.session_state.nlp_plan.get("desired_feeling")
                    )
                    st.session_state.nlp_results.extend(more)
                    add_dopamine_points(5, "Exploring!")
                    st.rerun()
        with btn_cols[2]:
            if st.button("✕ Clear", key="nlp_clear_main", use_container_width=True):
                st.session_state.nlp_results = []
                st.session_state.nlp_last_prompt = ""
                st.rerun()
        
        st.markdown("---")
    
    # PAGE CONTENT
    page = st.session_state.active_page
    
    if page == "🎬 Movies":
        st.markdown(f"<div class='section-header'><span class='section-icon'>🎬</span><h2 class='section-title'>Movies for {MOOD_EMOJIS.get(st.session_state.current_feeling, '')} → {MOOD_EMOJIS.get(st.session_state.desired_feeling, '')}</h2></div>", unsafe_allow_html=True)
        st.caption(f"Feeling {st.session_state.current_feeling}, seeking {st.session_state.desired_feeling}")
        
        emotion_key = f"{st.session_state.current_feeling}_{st.session_state.desired_feeling}"
        if st.session_state.get("last_emotion_key") != emotion_key:
            st.session_state.movies_feed = []
            st.session_state.movies_page = 1
            st.session_state.last_emotion_key = emotion_key
        
        if not st.session_state.movies_feed:
            st.session_state.movies_feed = discover_movies(
                page=1,
                current_feeling=st.session_state.current_feeling,
                desired_feeling=st.session_state.desired_feeling
            )
        
        movies = st.session_state.movies_feed
        if movies:
            cols = st.columns(6)
            for i, movie in enumerate(movies[:24]):
                with cols[i % 6]:
                    render_movie_card(movie)
            
            if st.button("Load More Movies", use_container_width=True, key="load_more_movies"):
                st.session_state.movies_page += 1
                more = discover_movies(
                    page=st.session_state.movies_page,
                    current_feeling=st.session_state.current_feeling,
                    desired_feeling=st.session_state.desired_feeling
                )
                st.session_state.movies_feed.extend(more)
                add_dopamine_points(5, "Exploring!")
                st.rerun()
        else:
            st.warning("No movies found. Try different moods!")
    
    elif page == "🎵 Music":
        mood_music = FEELING_TO_MUSIC.get(st.session_state.desired_feeling, FEELING_TO_MUSIC["Happy"])
        st.markdown(f"<div class='section-header'><span class='section-icon'>🎵</span><h2 class='section-title'>Music for {st.session_state.desired_feeling}</h2></div>", unsafe_allow_html=True)
        st.caption(f"Genres: {', '.join(mood_music['genres'])}")
        
        st.markdown("##### 🎧 Curated Playlist")
        components.iframe(f"https://open.spotify.com/embed/playlist/{mood_music['playlist']}?theme=0", height=380)
        
        st.markdown("##### 🔍 Open in Your Music App")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(MUSIC_SERVICES.items())[:3]), mood_music["query"])
        with c2:
            render_service_buttons(dict(list(MUSIC_SERVICES.items())[3:]), mood_music["query"])
        
        st.markdown("##### 🎹 Custom Search")
        music_query = st.text_input("Search for music...", placeholder="Artist, song, genre, or mood", key="music_search")
        if music_query:
            render_service_buttons(MUSIC_SERVICES, music_query)
    
    elif page == "🎙️ Podcasts":
        mood_pods = FEELING_TO_PODCASTS.get(st.session_state.desired_feeling, FEELING_TO_PODCASTS.get("Curious"))
        st.markdown(f"<div class='section-header'><span class='section-icon'>🎙️</span><h2 class='section-title'>Podcasts for {st.session_state.desired_feeling}</h2></div>", unsafe_allow_html=True)
        
        st.markdown("##### ⭐ Recommended Shows")
        for show, desc in mood_pods["shows"]:
            st.markdown(f"""
            <div class="glass-card" style="display:flex;align-items:center;gap:16px;">
                <div style="font-size:2rem;">🎙️</div>
                <div>
                    <div style="font-weight:600;">{show}</div>
                    <div style="color:var(--text-secondary);font-size:0.85rem;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("##### 🔍 Search Podcasts")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(PODCAST_SERVICES.items())[:3]), mood_pods["query"])
        with c2:
            render_service_buttons(dict(list(PODCAST_SERVICES.items())[3:]), mood_pods["query"])
        
        st.markdown("##### 🎤 Custom Search")
        pod_query = st.text_input("Search for podcasts...", placeholder="Topic, show name, or host", key="pod_search")
        if pod_query:
            render_service_buttons(PODCAST_SERVICES, pod_query)
    
    elif page == "📚 Audiobooks":
        mood_books = FEELING_TO_AUDIOBOOKS.get(st.session_state.desired_feeling, FEELING_TO_AUDIOBOOKS.get("Curious"))
        st.markdown(f"<div class='section-header'><span class='section-icon'>📚</span><h2 class='section-title'>Audiobooks for {st.session_state.desired_feeling}</h2></div>", unsafe_allow_html=True)
        st.caption(f"Genres: {', '.join(mood_books['genres'])}")
        
        st.markdown("##### ⭐ Top Picks")
        cols = st.columns(len(mood_books["picks"]))
        for i, (title, author) in enumerate(mood_books["picks"]):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center;padding:24px;">
                    <div style="font-size:3rem;margin-bottom:12px;">📖</div>
                    <div style="font-weight:600;font-size:0.95rem;">{title}</div>
                    <div style="color:var(--text-secondary);font-size:0.8rem;margin-top:4px;">{author}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("##### 🔍 Search Audiobooks")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[:3]), mood_books["query"])
        with c2:
            render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[3:]), mood_books["query"])
        
        st.markdown("##### 📕 Custom Search")
        book_query = st.text_input("Search for audiobooks...", placeholder="Title, author, or genre", key="book_search")
        if book_query:
            render_service_buttons(AUDIOBOOK_SERVICES, book_query)
        
        st.info("💡 **Tip:** Check if your local library offers free audiobooks through **Libby** or **Hoopla**!")
    
    elif page == "⚡ Shorts":
        vq = FEELING_TO_VIDEOS.get(st.session_state.desired_feeling, "trending viral shorts")
        st.markdown(f"<div class='section-header'><span class='section-icon'>⚡</span><h2 class='section-title'>Quick Dopamine for {st.session_state.desired_feeling}</h2></div>", unsafe_allow_html=True)
        st.caption(f"Perfect content: {vq}")
        
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(vq)}+shorts"
        tt_url = f"https://www.tiktok.com/search?q={quote_plus(vq)}"
        ig_url = f"https://www.instagram.com/explore/tags/{quote_plus(vq.replace(' ', ''))}/"
        
        st.markdown(f"""
        <a href="{yt_url}" target="_blank" style="display:block;text-align:center;padding:28px;background:linear-gradient(135deg, #FF0000, #CC0000);border-radius:20px;color:white;text-decoration:none;font-weight:700;font-size:1.2rem;margin-bottom:16px;">
            ▶️ Watch {vq.split()[0].title()} Shorts on YouTube →
        </a>
        <a href="{tt_url}" target="_blank" style="display:block;text-align:center;padding:28px;background:linear-gradient(135deg,#ff0050,#00f2ea);border-radius:20px;color:white;text-decoration:none;font-weight:700;font-size:1.2rem;margin-bottom:16px;">
            📱 Browse {vq.split()[0].title()} on TikTok →
        </a>
        <a href="{ig_url}" target="_blank" style="display:block;text-align:center;padding:28px;background:linear-gradient(135deg,#833AB4,#FD1D1D,#F77737);border-radius:20px;color:white;text-decoration:none;font-weight:700;font-size:1.2rem;">
            📸 Explore on Instagram Reels →
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("##### 🔍 Custom Search")
        shorts_query = st.text_input("Search for shorts...", placeholder="Any topic or vibe", key="shorts_search")
        if shorts_query:
            yt2 = f"https://www.youtube.com/results?search_query={quote_plus(shorts_query)}+shorts"
            tt2 = f"https://www.tiktok.com/search?q={quote_plus(shorts_query)}"
            st.markdown(f"""
            <a href="{yt2}" target="_blank" class="service-btn"><div class="service-icon" style="background:#FF0000;">▶️</div><div><div class="service-name">YouTube Shorts</div><div class="service-desc">Search "{shorts_query}"</div></div></a>
            <a href="{tt2}" target="_blank" class="service-btn"><div class="service-icon" style="background:linear-gradient(135deg,#ff0050,#00f2ea);">📱</div><div><div class="service-name">TikTok</div><div class="service-desc">Search "{shorts_query}"</div></div></a>
            """, unsafe_allow_html=True)
    
    # SHARE
    st.markdown("---")
    st.markdown("<div class='section-header'><span class='section-icon'>📤</span><h2 class='section-title'>Share Your Vibe</h2></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        render_share_card()
    with col2:
        ref_code = st.session_state.referral_code
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="margin-top: 0;">🎁 Invite Friends</h4>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">Share your code — both get <strong>100 bonus DP</strong>!</p>
            <div style="margin: 16px 0; text-align: center;">
                <span class="referral-code" style="font-size: 1.8rem;">{ref_code}</span>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.75rem; text-align: center;">
                dopamine.watch/r/{ref_code}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # PREMIUM MODAL
    if st.session_state.get("show_premium_modal"):
        st.markdown("---")
        st.markdown("<div class='section-header'><span class='section-icon'>⭐</span><h2 class='section-title'>Unlock Premium</h2></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card" style="border-color: #ffd700;">
            <h3 style="margin-top: 0; text-align: center;">Dopamine<span style="color: #ffd700;">+</span> Premium</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0;">
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🚫 No ads</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🤖 Advanced AI</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">📊 Mood analytics</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🔥 2x DP earnings</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">🏆 Exclusive badges</div>
                <div style="padding: 12px; background: var(--glass); border-radius: 12px;">💬 Priority support</div>
            </div>
            <div style="text-align: center; margin: 24px 0;">
                <span style="font-size: 2.5rem; font-weight: 700;">$4.99</span>
                <span style="color: var(--text-secondary);">/month</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Maybe Later", use_container_width=True, key="premium_later"):
                st.session_state.show_premium_modal = False
                st.rerun()
        with col2:
            if st.button("🚀 Subscribe", use_container_width=True, key="premium_subscribe"):
                st.toast("Premium coming soon with Stripe! Join waitlist.", icon="⭐")
                st.session_state.show_premium_modal = False

# --------------------------------------------------
# 18. MAIN ROUTER
# --------------------------------------------------
if not st.session_state.get("user"):
    if st.session_state.get("auth_step") == "login":
        render_login()
    elif st.session_state.get("auth_step") == "signup":
        render_signup()
    elif st.session_state.get("auth_step") == "reset":
        render_reset_password()
    else:
        render_landing()
else:
    render_sidebar()
    render_main()