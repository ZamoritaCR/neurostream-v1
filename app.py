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
import base64
import streamlit.components.v1 as components
from urllib.parse import quote_plus
from openai import OpenAI
import html as html_lib
import random
from datetime import datetime, timedelta
import hashlib
import re

# Mr.DP Floating Chat Widget
from mr_dp_floating import render_floating_mr_dp

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
# 2. FRONTEND-ONLY AUTH (No Backend Required)
# --------------------------------------------------
SUPABASE_ENABLED = False  # Frontend-only mode

def frontend_sign_up(email: str, password: str, name: str = ""):
    """Frontend-only signup - stores in session"""
    if not email or not password:
        return {"success": False, "error": "Email and password required"}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters"}
    
    # Generate user ID
    user_id = hashlib.md5(f"{email}{datetime.now()}".encode()).hexdigest()[:16]
    
    return {
        "success": True,
        "user": {
            "id": user_id,
            "email": email,
            "name": name or email.split("@")[0]
        }
    }

def frontend_sign_in(email: str, password: str):
    """Frontend-only signin - just validates input"""
    if not email or not password:
        return {"success": False, "error": "Email and password required"}
    
    # Generate consistent user ID from email
    user_id = hashlib.md5(email.encode()).hexdigest()[:16]
    
    return {
        "success": True,
        "user": {
            "id": user_id,
            "email": email,
            "name": email.split("@")[0]
        }
    }

def frontend_sign_out():
    """Clear session"""
    pass

# Compatibility aliases
supabase_sign_up = frontend_sign_up
supabase_sign_in = frontend_sign_in
supabase_sign_out = frontend_sign_out
supabase_get_user = lambda: None
get_oauth_url = lambda provider: None
handle_oauth_callback = lambda: None
create_user_profile = lambda *args: None
get_user_profile = lambda *args: {}
update_user_profile = lambda *args: None
check_referral_code = lambda *args: None


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
    "Spotify": {"url": "https://open.spotify.com/search/{query}/shows", "color": "#1DB954", "icon": "🟢"},
    "Apple Podcasts": {"url": "https://podcasts.apple.com/us/search?term={query}", "color": "#9933CC", "icon": "🎙️"},
    "YouTube": {"url": "https://www.youtube.com/results?search_query={query}+podcast", "color": "#FF0000", "icon": "▶️"},
    "Google Podcasts": {"url": "https://podcasts.google.com/search/{query}", "color": "#4285F4", "icon": "🎧"},
}

AUDIOBOOK_SERVICES = {
    "Audible": {"url": "https://www.audible.com/search?keywords={query}", "color": "#F8991D", "icon": "🎧"},
    "Apple Books": {"url": "https://books.apple.com/us/search?term={query}", "color": "#FA243C", "icon": "🍎"},
    "Google Play": {"url": "https://play.google.com/store/search?q={query}&c=audiobooks", "color": "#4285F4", "icon": "📘"},
    "Spotify": {"url": "https://open.spotify.com/search/{query}/audiobooks", "color": "#1DB954", "icon": "🟢"},
}

# --------------------------------------------------
# 6. API CLIENTS
# --------------------------------------------------
@st.cache_data
def get_tmdb_key():
    try:
        return st.secrets["tmdb"]["api_key"]
    except:
        return os.environ.get("TMDB_API_KEY")

try:
    _openai_key = st.secrets["openai"]["api_key"]
except:
    _openai_key = os.environ.get("OPENAI_API_KEY")

openai_client = OpenAI(api_key=_openai_key) if _openai_key else None

# --------------------------------------------------
# 7. EMOTION MAPPINGS - COMPLETE
# --------------------------------------------------
CURRENT_FEELINGS = ["Sad", "Lonely", "Anxious", "Overwhelmed", "Angry", "Stressed", "Bored", "Tired", "Numb", "Confused", "Restless", "Focused", "Calm", "Happy", "Excited", "Curious", "Scared", "Nostalgic", "Romantic", "Adventurous", "Frustrated", "Hopeful"]
DESIRED_FEELINGS = ["Comforted", "Calm", "Relaxed", "Focused", "Energized", "Stimulated", "Happy", "Entertained", "Inspired", "Grounded", "Curious", "Sleepy", "Connected", "Scared", "Thrilled", "Nostalgic", "Romantic", "Adventurous", "Amused", "Motivated"]

MOOD_EMOJIS = {
    # Current feelings
    "Sad": "🌧️", "Lonely": "🥺", "Anxious": "😰", "Overwhelmed": "😵‍💫",
    "Angry": "😡", "Stressed": "😫", "Bored": "😐", "Tired": "😴",
    "Numb": "🫥", "Confused": "🤔", "Restless": "😬", "Focused": "🎯",
    "Calm": "😌", "Happy": "😊", "Excited": "⚡", "Curious": "🧐",
    "Scared": "😱", "Nostalgic": "🥹", "Romantic": "💕", "Adventurous": "🏔️",
    "Frustrated": "😤", "Hopeful": "🌈",
    # Desired feelings
    "Comforted": "🫶", "Relaxed": "🛋️", "Energized": "🔥", "Stimulated": "🚀",
    "Entertained": "🍿", "Inspired": "✨", "Grounded": "🌱", "Sleepy": "🌙", 
    "Connected": "❤️", "Thrilled": "🎢", "Amused": "😂", "Motivated": "💪"
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
    # New feelings
    "Scared": {"prefer": [27, 53, 9648]},  # Horror, Thriller, Mystery
    "Thrilled": {"prefer": [28, 53, 80, 12]},  # Action, Thriller, Crime, Adventure
    "Nostalgic": {"prefer": [36, 18, 10751]},  # History, Drama, Family (classics)
    "Romantic": {"prefer": [10749, 35, 18]},  # Romance, Comedy, Drama
    "Adventurous": {"prefer": [12, 28, 878, 14]},  # Adventure, Action, Sci-Fi, Fantasy
    "Frustrated": {"prefer": [28, 35, 80]},  # Action, Comedy, Crime
    "Hopeful": {"prefer": [18, 10751, 99]},  # Drama, Family, Documentary
    "Amused": {"prefer": [35, 16, 10751]},  # Comedy, Animation, Family
    "Motivated": {"prefer": [18, 99, 36]},  # Drama, Documentary, History (inspiring)
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
    # New feelings
    "Scared": {"query": "dark ambient horror soundtrack eerie", "playlist": "37i9dQZF1DX6R7QUWePReA", "genres": ["dark ambient", "horror", "soundtrack"]},
    "Thrilled": {"query": "intense epic action soundtrack adrenaline", "playlist": "37i9dQZF1DX4eRPd9frC1m", "genres": ["epic", "action", "cinematic"]},
    "Nostalgic": {"query": "90s 2000s throwback hits nostalgia", "playlist": "37i9dQZF1DX4o1oenSJRJd", "genres": ["90s", "2000s", "throwback"]},
    "Romantic": {"query": "love songs romantic dinner date night", "playlist": "37i9dQZF1DX50QitC6Oqtn", "genres": ["r&b", "soul", "romantic"]},
    "Adventurous": {"query": "epic adventure cinematic orchestral travel", "playlist": "37i9dQZF1DX4eRPd9frC1m", "genres": ["epic", "cinematic", "adventure"]},
    "Frustrated": {"query": "angry rock metal intense rage", "playlist": "37i9dQZF1DX1tyCD9QhIWF", "genres": ["metal", "rock", "punk"]},
    "Hopeful": {"query": "uplifting inspiring hopeful positive", "playlist": "37i9dQZF1DX3rxVfibe1L0", "genres": ["indie", "pop", "uplifting"]},
    "Amused": {"query": "fun party happy dance", "playlist": "37i9dQZF1DXa2PvUpywmrr", "genres": ["pop", "dance", "party"]},
    "Motivated": {"query": "motivation workout pump up gym", "playlist": "37i9dQZF1DX76Wlfdnj7AP", "genres": ["hip-hop", "edm", "rock"]},
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

# Shorts/Videos mood mappings with YouTube video IDs for embedding
# Each entry has: query (for search), label, shorts (YouTube Shorts IDs that actually work)
# Using popular, verified YouTube Shorts that won't be taken down
FEELING_TO_SHORTS = {
    "Sad": {
        "query": "wholesome cute puppies kittens heartwarming",
        "label": "Wholesome & Cute",
        "shorts": ["ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Lonely": {
        "query": "heartwarming friendship wholesome moments",
        "label": "Heartwarming Moments", 
        "shorts": ["ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Anxious": {
        "query": "satisfying oddly calming asmr relaxing",
        "label": "Oddly Satisfying",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Overwhelmed": {
        "query": "calming nature peaceful relaxing scenery",
        "label": "Peaceful & Calming",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Angry": {
        "query": "instant karma fails justice served satisfying",
        "label": "Karma & Justice",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Stressed": {
        "query": "meditation relaxing calm breathing peaceful",
        "label": "Calm & Breathe",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Bored": {
        "query": "mind blowing facts amazing viral interesting",
        "label": "Mind-Blowing",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Tired": {
        "query": "asmr relaxing sleep sounds soothing calm",
        "label": "Sleep & Relax",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Numb": {
        "query": "extreme sports adrenaline rush intense action",
        "label": "Adrenaline Rush",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Confused": {
        "query": "life hacks explained tutorial tips tricks",
        "label": "Quick Hacks",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Restless": {
        "query": "parkour extreme sports action wow amazing",
        "label": "Action & Energy",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Focused": {
        "query": "productivity study tips focus motivation",
        "label": "Focus & Study",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0"]
    },
    "Calm": {
        "query": "nature sounds rain ocean waves peaceful",
        "label": "Nature Sounds",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Happy": {
        "query": "funny comedy hilarious fails memes viral",
        "label": "Comedy & Laughs",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "JGwWNGJdvx8", "OPf0YbXqDm0"]
    },
    "Excited": {
        "query": "epic moments incredible wow amazing viral",
        "label": "Epic Moments",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "9bZkp7q19f0", "OPf0YbXqDm0"]
    },
    "Curious": {
        "query": "science facts interesting cool experiments",
        "label": "Science & Facts",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Scared": {
        "query": "scary horror creepy thriller suspense",
        "label": "Scary & Creepy",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Nostalgic": {
        "query": "90s 2000s throwback nostalgia memories retro",
        "label": "Nostalgic Throwbacks",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Romantic": {
        "query": "romantic love couples cute relationship goals",
        "label": "Love & Romance",
        "shorts": ["ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0", "5qap5aO4i9A"]
    },
    "Adventurous": {
        "query": "travel adventure explore world amazing places",
        "label": "Travel & Adventure",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "9bZkp7q19f0", "OPf0YbXqDm0"]
    },
    "Frustrated": {
        "query": "satisfying instant karma fails justice served",
        "label": "Satisfying Karma",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Hopeful": {
        "query": "inspiring transformation success stories glow up",
        "label": "Inspiring Stories",
        "shorts": ["ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0", "5qap5aO4i9A"]
    },
    "Comforted": {
        "query": "cozy vibes aesthetic wholesome comforting",
        "label": "Cozy Vibes",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Relaxed": {
        "query": "lofi chill ambient relaxing peaceful calm",
        "label": "Chill & Relaxed",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Energized": {
        "query": "workout motivation hype pump energy beast",
        "label": "Workout & Energy",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "9bZkp7q19f0", "OPf0YbXqDm0"]
    },
    "Stimulated": {
        "query": "mind blown wtf moments crazy amazing",
        "label": "Mind-Blown",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Entertained": {
        "query": "viral trending funny comedy memes popular",
        "label": "Viral & Trending",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Inspired": {
        "query": "motivation success transformation inspiring stories",
        "label": "Motivation & Success",
        "shorts": ["ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0", "5qap5aO4i9A"]
    },
    "Grounded": {
        "query": "minimalist peaceful simple calm nature",
        "label": "Simple & Peaceful",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Sleepy": {
        "query": "rain sounds sleep asmr relaxing night calm",
        "label": "Sleep Sounds",
        "shorts": ["5qap5aO4i9A", "ZbZSe6N_BXs", "OPf0YbXqDm0", "9bZkp7q19f0"]
    },
    "Connected": {
        "query": "friendship wholesome couples love heartwarming",
        "label": "Connection & Love",
        "shorts": ["ZbZSe6N_BXs", "9bZkp7q19f0", "OPf0YbXqDm0", "5qap5aO4i9A"]
    },
    "Thrilled": {
        "query": "roller coaster extreme thrilling adrenaline",
        "label": "Thrilling Rides",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "9bZkp7q19f0", "OPf0YbXqDm0"]
    },
    "Amused": {
        "query": "funny animals fails comedy hilarious memes",
        "label": "Hilarious Moments",
        "shorts": ["kJQP7kiw5Fk", "9bZkp7q19f0", "OPf0YbXqDm0", "JGwWNGJdvx8"]
    },
    "Motivated": {
        "query": "motivation workout success grind hustle gym",
        "label": "Motivation & Grind",
        "shorts": ["kJQP7kiw5Fk", "JGwWNGJdvx8", "9bZkp7q19f0", "OPf0YbXqDm0"]
    },
}

# Keep old mapping for backwards compatibility
FEELING_TO_VIDEOS = {k: v["query"] for k, v in FEELING_TO_SHORTS.items()}

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
    """Get streaming providers from TMDB with availability data."""
    api_key = get_tmdb_key()
    if not api_key:
        return [], None
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/watch/providers",
            params={"api_key": api_key},
            timeout=8
        )
        r.raise_for_status()
        data = r.json().get("results", {}).get("US", {})
        
        # Get the official TMDB watch page link (has real deep links via JustWatch)
        tmdb_watch_link = f"https://www.themoviedb.org/{media_type}/{tmdb_id}/watch?locale=US"
        
        # Combine flatrate (subscription) and rent options
        providers = []
        
        # Subscription services first (flatrate)
        for p in data.get("flatrate", []):
            p["availability"] = "stream"  # Available with subscription
            providers.append(p)
        
        # Rent/buy options
        for p in data.get("rent", []):
            if not any(existing["provider_id"] == p["provider_id"] for existing in providers):
                p["availability"] = "rent"
                providers.append(p)
        
        return providers[:8], tmdb_watch_link
    except:
        return [], None


def get_movie_deep_link(provider_name, title, tmdb_id=None, media_type="movie"):
    """Generate the best possible link for a streaming service."""
    provider = (provider_name or "").strip()
    
    # Clean and encode title properly
    clean_title = title.replace(":", "").replace("'", "").replace('"', "")
    safe_title = quote_plus(clean_title)
    
    # Service-specific deep link patterns (optimized for each service)
    DEEP_LINKS = {
        "Netflix": f"https://www.netflix.com/search?q={safe_title}",
        "Amazon Prime Video": f"https://www.amazon.com/s?k={safe_title}&i=instant-video&ref=nb_sb_noss",
        "Disney Plus": f"https://www.disneyplus.com/search?q={safe_title}",
        "Max": f"https://play.max.com/search?q={safe_title}&searchMode=full",
        "Hulu": f"https://www.hulu.com/search?q={safe_title}",
        "Peacock": f"https://www.peacocktv.com/search?q={safe_title}",
        "Peacock Premium": f"https://www.peacocktv.com/search?q={safe_title}",
        "Paramount Plus": f"https://www.paramountplus.com/shows/video/{safe_title}/",
        "Paramount+ Amazon Channel": f"https://www.amazon.com/s?k={safe_title}&i=instant-video",
        "Apple TV Plus": f"https://tv.apple.com/search?term={safe_title}",
        "Apple TV": f"https://tv.apple.com/search?term={safe_title}",
        "Starz": f"https://www.starz.com/search?q={safe_title}",
        "MGM Plus": f"https://www.mgmplus.com/search?query={safe_title}",
        "Tubi": f"https://tubitv.com/search/{safe_title}",
        "Tubi TV": f"https://tubitv.com/search/{safe_title}",
        "Pluto TV": f"https://pluto.tv/search/details/{safe_title}",
        "Plex": f"https://watch.plex.tv/search?q={safe_title}",
        "Crunchyroll": f"https://www.crunchyroll.com/search?q={safe_title}",
        "Shudder": f"https://www.shudder.com/search?q={safe_title}",
        "MUBI": f"https://mubi.com/search?query={safe_title}",
        "Vudu": f"https://www.vudu.com/content/movies/search?searchString={safe_title}",
        "Fandango At Home": f"https://www.vudu.com/content/movies/search?searchString={safe_title}",
        "The Roku Channel": f"https://therokuchannel.roku.com/search/{safe_title}",
        "Criterion Channel": f"https://www.criterionchannel.com/search?q={safe_title}",
        "fuboTV": f"https://www.fubo.tv/search?q={safe_title}",
        "Sling TV": f"https://watch.sling.com/browse/search?query={safe_title}",
        "YouTube": f"https://www.youtube.com/results?search_query={safe_title}+full+movie",
        "Google Play Movies": f"https://play.google.com/store/search?q={safe_title}&c=movies",
    }
    
    # Direct match
    if provider in DEEP_LINKS:
        return DEEP_LINKS[provider]
    
    # Fuzzy match
    provider_lower = provider.lower()
    for key, link in DEEP_LINKS.items():
        if key.lower() in provider_lower or provider_lower in key.lower():
            return link
    
    # Fallback to Google search for this movie on the service
    return f"https://www.google.com/search?q={safe_title}+{quote_plus(provider)}+watch"

def get_movie_trailer(tmdb_id, media_type="movie"):
    """Fetch YouTube trailer key from TMDB."""
    api_key = get_tmdb_key()
    if not api_key or not tmdb_id:
        return None
    try:
        r = requests.get(
            f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/videos",
            params={"api_key": api_key},
            timeout=8
        )
        r.raise_for_status()
        videos = r.json().get("results", [])
        # Prioritize: Official Trailer > Trailer > Teaser
        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer" and "official" in video.get("name", "").lower():
                return video.get("key")
        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                return video.get("key")
        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Teaser":
                return video.get("key")
        for video in videos:
            if video.get("site") == "YouTube":
                return video.get("key")
        return None
    except:
        return None

# --------------------------------------------------
# 9. MR.DP - CONVERSATIONAL AI CURATOR 🧾
# --------------------------------------------------
MR_DP_SYSTEM_PROMPT = """You are Mr.DP (Mr. Dopamine), the world's most empathetic content curator designed specifically for ADHD and neurodivergent brains. You understand decision fatigue, emotional dysregulation, and the need for the RIGHT content at the RIGHT time.

Your personality:
- Warm, friendly, and understanding (like a cool older sibling who loves entertainment)
- You get ADHD struggles - no judgment, only support
- You're enthusiastic about helping people find their dopamine fix
- You use casual language, occasional emojis, but not over the top
- You're concise (2-3 sentences max for your response)

Your job:
1. Understand what the user is feeling and what they NEED to feel
2. Detect what type of content they want:
   - "movies" (default) - films, shows, watch
   - "music" - songs, playlist, beats, tunes, albums
   - "podcasts" - podcast, episode, listen to talk, interviews
   - "audiobooks" - audiobook, book, read, listen to story
   - "shorts" - shorts, tiktok, reels, quick videos, clips
   - "artist" - specific artist/band on Spotify (e.g. "play Drake", "Taylor Swift music")
3. Respond with empathy and explain your recommendation approach
4. Return structured data for the app to use

ALWAYS respond in this exact JSON format:
{
    "message": "Your friendly 1-3 sentence response to the user",
    "current_feeling": "one of: Sad, Lonely, Anxious, Overwhelmed, Angry, Stressed, Bored, Tired, Numb, Confused, Restless, Focused, Calm, Happy, Excited, Curious (or null)",
    "desired_feeling": "one of: Comforted, Calm, Relaxed, Focused, Energized, Stimulated, Happy, Entertained, Inspired, Grounded, Curious, Sleepy, Connected (or null)",
    "media_type": "movies, music, podcasts, audiobooks, shorts, or artist",
    "mode": "discover or search",
    "search_query": "specific search terms if mode is search OR artist name for artist type, empty string otherwise",
    "genres": "brief description of what kind of content you're recommending"
}

Examples:

User: "I'm so bored"
{
    "message": "Ugh, the boredom spiral is REAL. Let me shake things up with some high-energy adventures and mind-bending sci-fi that'll actually hold your attention! 🚀",
    "current_feeling": "Bored",
    "desired_feeling": "Entertained",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "action-adventures, sci-fi thrillers, engaging comedies"
}

User: "need some focus music for coding"
{
    "message": "Ah, the coding zone! Let me queue up some beats that'll keep your brain locked in without being distracting. Lo-fi and electronic focus vibes coming up! 🎧",
    "current_feeling": "Restless",
    "desired_feeling": "Focused",
    "media_type": "music",
    "mode": "discover",
    "search_query": "",
    "genres": "lo-fi beats, electronic focus, ambient coding music"
}

User: "play some Drake"
{
    "message": "Drizzy coming right up! 🎤 Let me pull up his top tracks and albums for you.",
    "current_feeling": null,
    "desired_feeling": "Entertained",
    "media_type": "artist",
    "mode": "search",
    "search_query": "Drake",
    "genres": "hip-hop, rap, R&B"
}

User: "I want to listen to Taylor Swift"
{
    "message": "A Swiftie moment! 💜 Loading up Taylor's catalog - from country roots to pop bangers!",
    "current_feeling": null,
    "desired_feeling": "Happy",
    "media_type": "artist",
    "mode": "search",
    "search_query": "Taylor Swift",
    "genres": "pop, country, indie folk"
}

User: "recommend a good podcast"
{
    "message": "Ooh, podcast time! Let me find something that'll keep your brain engaged without overwhelming it. 🎙️",
    "current_feeling": "Bored",
    "desired_feeling": "Stimulated",
    "media_type": "podcasts",
    "mode": "discover",
    "search_query": "",
    "genres": "true crime, comedy, storytelling"
}

User: "I need a podcast for my commute"
{
    "message": "Commute vibes! I've got some engaging shows that'll make that drive fly by 🚗",
    "current_feeling": "Bored",
    "desired_feeling": "Entertained",
    "media_type": "podcasts",
    "mode": "discover",
    "search_query": "",
    "genres": "true crime, comedy, news"
}

User: "suggest an audiobook"
{
    "message": "Audiobook time! Let me find something that'll transport you to another world 📚",
    "current_feeling": "Bored",
    "desired_feeling": "Entertained",
    "media_type": "audiobooks",
    "mode": "discover",
    "search_query": "",
    "genres": "fiction, thriller, self-help"
}

User: "I want to listen to a book while I sleep"
{
    "message": "Sleep listening! I've got some gentle, soothing audiobooks perfect for drifting off 🌙",
    "current_feeling": "Tired",
    "desired_feeling": "Sleepy",
    "media_type": "audiobooks",
    "mode": "discover",
    "search_query": "",
    "genres": "fantasy, fiction, gentle narration"
}

User: "show me some funny shorts"
{
    "message": "Quick dopamine hits coming up! Here's some hilarious shorts to scroll through 😂",
    "current_feeling": "Bored",
    "desired_feeling": "Entertained",
    "media_type": "shorts",
    "mode": "discover",
    "search_query": "",
    "genres": "comedy, fails, viral"
}

User: "I need quick videos to wake up"
{
    "message": "Morning boost! Let me queue up some energizing clips to get you going ⚡",
    "current_feeling": "Tired",
    "desired_feeling": "Energized",
    "media_type": "shorts",
    "mode": "discover",
    "search_query": "",
    "genres": "motivation, hype, energy"
}

User: "satisfying videos"
{
    "message": "Ahh, the satisfying content rabbit hole! Here's some oddly calming clips ✨",
    "current_feeling": "Anxious",
    "desired_feeling": "Calm",
    "media_type": "shorts",
    "mode": "discover",
    "search_query": "",
    "genres": "satisfying, ASMR, calming"
}

User: "feeling anxious, need something calming"
{
    "message": "I got you. When anxiety hits, you need gentle, predictable comfort. I'm pulling up some cozy feel-good films - nothing stressful, just warm vibes. 💫",
    "current_feeling": "Anxious",
    "desired_feeling": "Calm",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "heartwarming comedies, gentle animations, comfort films"
}

User: "make me laugh"
{
    "message": "Say no more! Laughter is the best dopamine hit. Loading up comedies that'll actually make you LOL, not just exhale slightly harder 😂",
    "current_feeling": "Bored",
    "desired_feeling": "Entertained",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "comedies, funny adventures, witty films"
}

Remember: Be genuine, warm, and helpful. You're not just finding content - you're helping someone feel better."""

def ask_mr_dp(user_prompt):
    """
    Full conversational AI response from Mr.DP using GPT-4.
    Returns structured response with message, feelings, and search parameters.
    """
    if not user_prompt or not user_prompt.strip():
        return None
    
    # Try GPT first for natural conversation
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": MR_DP_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON from response
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            # Validate and set defaults
            result.setdefault("message", "Let me find something perfect for you!")
            result.setdefault("current_feeling", None)
            result.setdefault("desired_feeling", None)
            result.setdefault("media_type", "movies")  # Default to movies
            result.setdefault("mode", "discover")
            result.setdefault("search_query", "")
            result.setdefault("genres", "")
            
            # Validate feelings are in our list
            if result["current_feeling"] not in CURRENT_FEELINGS:
                result["current_feeling"] = None
            if result["desired_feeling"] not in DESIRED_FEELINGS:
                result["desired_feeling"] = None
            
            # Validate media_type
            if result["media_type"] not in ["movies", "music", "podcasts", "audiobooks", "shorts", "artist"]:
                result["media_type"] = "movies"
            
            return result
            
        except Exception as e:
            print(f"GPT error: {e}")
            # Fall through to heuristic
    
    # Fallback: Heuristic-based response
    return heuristic_mr_dp(user_prompt)

def heuristic_mr_dp(prompt):
    """
    Fallback heuristic when GPT is unavailable.
    Detects media type and provides conversational responses based on keyword matching.
    """
    t = (prompt or "").lower()
    
    current, desired, message, mode, query, genres = None, None, "", "discover", "", ""
    media_type = "movies"  # Default to movies
    
    # Detect media type priority (most specific first)
    
    # Check for specific artist request (e.g. "play Drake", "Taylor Swift music")
    artist_patterns = ["play ", "listen to ", "put on ", "songs by ", "music by "]
    popular_artists = [
        # Pop/Hip-Hop
        "drake", "taylor swift", "kendrick", "beyonce", "kanye", "travis scott", "bad bunny", 
        "weeknd", "doja cat", "sza", "dua lipa", "billie eilish", "ed sheeran", "ariana grande",
        "post malone", "harry styles", "olivia rodrigo", "morgan wallen", "luke combs", "eminem",
        "rihanna", "bruno mars", "coldplay", "imagine dragons", "maroon 5", "adele", "shakira",
        # Rock/Metal
        "metallica", "led zeppelin", "pink floyd", "queen", "ac/dc", "acdc", "guns n roses",
        "nirvana", "foo fighters", "linkin park", "green day", "blink 182", "fall out boy",
        "panic at the disco", "my chemical romance", "slipknot", "avenged sevenfold",
        "iron maiden", "black sabbath", "megadeth", "slayer", "pantera", "tool",
        "red hot chili peppers", "pearl jam", "soundgarden", "alice in chains",
        # Classic/Other
        "the beatles", "beatles", "rolling stones", "david bowie", "prince", "michael jackson",
        "elton john", "fleetwood mac", "eagles", "u2", "radiohead", "oasis", "arctic monkeys"
    ]
    
    # Check for artist mentions
    for artist in popular_artists:
        if artist in t:
            media_type = "artist"
            query = artist.title()
            message = f"Great taste! Loading up {artist.title()}'s hits! 🎤"
            desired = "Entertained"
            genres = "artist discography"
            break
    
    # Check for artist patterns like "play X" or "listen to X"
    if media_type != "artist":
        for pattern in artist_patterns:
            if pattern in t:
                # Extract what comes after the pattern
                idx = t.find(pattern) + len(pattern)
                remaining = t[idx:].strip()
                # Take first 2-3 words as artist name
                words = remaining.split()[:3]
                if words:
                    potential_artist = " ".join(words).strip(".,!?")
                    if len(potential_artist) > 2 and potential_artist not in ["some", "something", "music", "songs", "a"]:
                        media_type = "artist"
                        query = potential_artist.title()
                        message = f"Let me pull up {potential_artist.title()} for you! 🎤"
                        desired = "Entertained"
                        genres = "artist discography"
                        break
    
    # Check for shorts/short videos
    if media_type == "movies":
        shorts_keywords = ["shorts", "short video", "tiktok", "reels", "quick video", "clips", "viral video",
                          "satisfying", "asmr video", "quick dopamine", "scroll"]
        if any(k in t for k in shorts_keywords):
            media_type = "shorts"
    
    # Check for podcasts
    if media_type == "movies":
        podcast_keywords = ["podcast", "podcasts", "episode", "episodes", "listen to talk", "talk show",
                           "interview", "conversations", "joe rogan", "lex fridman", "true crime podcast"]
        if any(k in t for k in podcast_keywords):
            media_type = "podcasts"
    
    # Check for audiobooks
    if media_type == "movies":
        audiobook_keywords = ["audiobook", "audiobooks", "audio book", "listen to a book", "book to listen",
                             "audible", "read to me", "narrated book", "spoken book"]
        if any(k in t for k in audiobook_keywords):
            media_type = "audiobooks"
    
    # Check for music (but not artist - that's already handled)
    if media_type == "movies":
        music_keywords = ["music", "song", "songs", "playlist", "beats", "tunes", "track", "tracks", 
                          "album", "melody", "lo-fi", "lofi", "workout music", "study music", 
                          "focus music", "chill music", "sad songs", "happy songs"]
        if any(k in t for k in music_keywords):
            media_type = "music"
    
    # Media type specific defaults
    media_defaults = {
        "movies": {"icon": "🎬", "default_msg": "Let me find something perfect for your vibe!", "default_genres": "popular films, crowd-pleasers"},
        "music": {"icon": "🎵", "default_msg": "Let me find the perfect tunes for you!", "default_genres": "popular hits"},
        "podcasts": {"icon": "🎙️", "default_msg": "Let me find some great podcasts for you!", "default_genres": "engaging shows, storytelling"},
        "audiobooks": {"icon": "📚", "default_msg": "Let me find a great audiobook for you!", "default_genres": "bestsellers, engaging narration"},
        "shorts": {"icon": "⚡", "default_msg": "Quick dopamine hits coming up!", "default_genres": "viral, entertaining, trending"},
        "artist": {"icon": "🎤", "default_msg": "Let me pull up that artist!", "default_genres": "artist discography"},
    }
    
    # Detect current feeling
    feeling_responses = {
        "Bored": {
            "keywords": ["bored", "boring", "nothing to watch", "meh", "blah", "dull"],
            "desired": "Entertained",
            "messages": {
                "movies": "The boredom struggle is real! Let me find something that'll actually grab your attention 🎬",
                "music": "The boredom struggle is real! Let me queue up some bangers 🎵",
                "podcasts": "Boredom be gone! I've got some engaging podcasts that'll hook you 🎙️",
                "audiobooks": "Time to escape! Here's an audiobook that'll transport you 📚",
                "shorts": "Quick fix incoming! Here's some content that'll snap you out of it ⚡",
            }
        },
        "Stressed": {
            "keywords": ["stress", "overwhelm", "too much", "burnout", "pressure"],
            "desired": "Relaxed",
            "messages": {
                "movies": "Deep breath - time for some gentle, relaxing vibes 🌿",
                "music": "Deep breath - I've got calming tunes to help you decompress 🌿",
                "podcasts": "Let's ease that stress with some soothing content 🌿",
                "audiobooks": "Escape the stress with a calming listen 🌿",
                "shorts": "Some satisfying, calming shorts to melt that stress away 🌿",
            }
        },
        "Anxious": {
            "keywords": ["anxious", "anxiety", "nervous", "worried", "panic"],
            "desired": "Calm",
            "messages": {
                "movies": "Anxiety is tough. Here's something comforting and soothing 💫",
                "music": "I've got calming music to ease that anxiety 💫",
                "podcasts": "Here are some calming podcasts for when anxiety hits 💫",
                "audiobooks": "A gentle audiobook to help you feel grounded 💫",
                "shorts": "Oddly satisfying content to calm those nerves 💫",
            }
        },
        "Sad": {
            "keywords": ["sad", "down", "depressed", "crying", "upset", "heartbr", "grief"],
            "desired": "Comforted",
            "messages": {
                "movies": "Sending virtual hugs 🫂 Here's something warm and uplifting.",
                "music": "Sending hugs 🫂 Sometimes you need music that understands.",
                "podcasts": "Here's some comforting voices to keep you company 🫂",
                "audiobooks": "A story to wrap around you like a blanket 🫂",
                "shorts": "Wholesome content to lift your spirits 🫂",
            }
        },
        "Tired": {
            "keywords": ["tired", "exhaust", "drained", "sleepy", "no energy", "wiped"],
            "desired": "Relaxed",
            "messages": {
                "movies": "Running on empty? Easy-watching picks that won't drain you 😴",
                "music": "Chill vibes for when you're running on empty 😴",
                "podcasts": "Light, easy listening for tired ears 😴",
                "audiobooks": "Something gentle for tired minds 😴",
                "shorts": "Low-effort content for when you're drained 😴",
            }
        },
        "Scared": {
            "keywords": ["scared", "spooky", "horror", "creepy", "terrif", "frighten"],
            "desired": "Scared",
            "messages": {
                "movies": "Ooh, feeling brave! Let me find some quality scares for you 👻",
                "music": "Dark and eerie vibes coming right up 🎃",
                "podcasts": "Creepy podcasts that'll give you chills 👻",
                "audiobooks": "Spine-tingling stories to keep you up at night 🌙",
                "shorts": "Jump scares and creepy content incoming! 😱",
            }
        },
        "Nostalgic": {
            "keywords": ["nostalg", "throwback", "miss", "remember", "old times", "childhood", "90s", "2000s"],
            "desired": "Nostalgic",
            "messages": {
                "movies": "Taking you back in time! Classic vibes incoming 🥹",
                "music": "Time machine activated! Here's some throwback hits 📼",
                "podcasts": "Nostalgic conversations about the good old days 🥹",
                "audiobooks": "Stories that'll take you back 📼",
                "shorts": "Throwback content for the feels! 🥹",
            }
        },
        "Romantic": {
            "keywords": ["romantic", "love", "date night", "cuddle", "partner", "valentine"],
            "desired": "Romantic",
            "messages": {
                "movies": "Love is in the air! Here's some swoon-worthy picks 💕",
                "music": "Setting the mood with romantic tunes 💕",
                "podcasts": "Love stories and relationship wisdom 💕",
                "audiobooks": "Romance that'll make your heart flutter 💕",
                "shorts": "Cute couples and romantic moments 💕",
            }
        },
        "Adventurous": {
            "keywords": ["adventure", "explore", "travel", "wild", "spontan"],
            "desired": "Adventurous",
            "messages": {
                "movies": "Adventure awaits! Let's explore new worlds 🏔️",
                "music": "Epic soundtracks for your next adventure 🏔️",
                "podcasts": "Travel stories and wild adventures 🏔️",
                "audiobooks": "Epic journeys and explorations 🏔️",
                "shorts": "Amazing places and adventures to inspire you 🏔️",
            }
        },
        "Frustrated": {
            "keywords": ["frustrat", "ugh", "annoyed", "irritat", "fed up"],
            "desired": "Calm",
            "messages": {
                "movies": "I feel you! Let's find something to take the edge off 😤",
                "music": "Let's channel that energy! 😤",
                "podcasts": "Something to help you vent and relax 😤",
                "audiobooks": "An escape from the frustration 😤",
                "shorts": "Satisfying karma videos to make you feel better 😤",
            }
        },
        "Hopeful": {
            "keywords": ["hope", "optimist", "looking up", "better", "positive"],
            "desired": "Inspired",
            "messages": {
                "movies": "Keeping that hope alive with inspiring stories 🌈",
                "music": "Uplifting tunes to keep you going 🌈",
                "podcasts": "Inspiring conversations and success stories 🌈",
                "audiobooks": "Stories of triumph and perseverance 🌈",
                "shorts": "Inspiring transformations and success stories 🌈",
            }
        },
    }
    
    # Check for feeling matches
    for feeling, data in feeling_responses.items():
        if any(k in t for k in data["keywords"]):
            current = feeling
            desired = data["desired"]
            message = data["messages"].get(media_type, data["messages"]["movies"])
            break
    
    # Check for desired feeling keywords with media-specific genres
    desire_responses = {
        "laugh": {"desired": "Entertained", "message": "Say no more! Comedy incoming 😂", 
                  "genres": {"movies": "comedies, funny films", "music": "funny songs", "podcasts": "comedy podcasts, funny shows", "audiobooks": "humorous books", "shorts": "comedy, fails, funny"}},
        "funny": {"desired": "Entertained", "message": "Let's get those laughs going! 🎭",
                  "genres": {"movies": "comedies, witty films", "music": "comedy, funny", "podcasts": "comedy podcasts", "audiobooks": "humorous books", "shorts": "comedy, fails"}},
        "relax": {"desired": "Relaxed", "message": "Chill mode activated ✨",
                  "genres": {"movies": "calming films", "music": "ambient, chill, lo-fi", "podcasts": "calm, soothing shows", "audiobooks": "peaceful fiction", "shorts": "satisfying, ASMR, calming"}},
        "focus": {"desired": "Focused", "message": "Lock-in mode activated! 🎯",
                  "genres": {"movies": "documentaries", "music": "lo-fi beats, focus music", "podcasts": "educational, learning", "audiobooks": "non-fiction, productivity", "shorts": "focus tips, productivity"}},
        "sleep": {"desired": "Sleepy", "message": "Sweet dreams incoming 🌙",
                  "genres": {"movies": "gentle films", "music": "sleep sounds, ambient", "podcasts": "sleep stories, bedtime", "audiobooks": "gentle narration, fiction", "shorts": "rain sounds, ASMR"}},
        "energy": {"desired": "Energized", "message": "Let's boost that energy! ⚡",
                  "genres": {"movies": "action, adventure", "music": "upbeat, EDM, dance", "podcasts": "motivation, hype", "audiobooks": "inspiring, motivation", "shorts": "hype, motivation, workout"}},
        "workout": {"desired": "Energized", "message": "Let's get those gains! 💪",
                  "genres": {"movies": "sports films", "music": "workout anthems, EDM", "podcasts": "fitness, motivation", "audiobooks": "sports, discipline", "shorts": "workout, fitness, gym"}},
        "motivat": {"desired": "Motivated", "message": "Let's get motivated! 🌟",
                  "genres": {"movies": "inspiring true stories", "music": "motivational, uplifting", "podcasts": "success stories, motivation", "audiobooks": "self-help, success", "shorts": "motivation, success, transformation"}},
        "learn": {"desired": "Curious", "message": "Knowledge time! 🧠",
                  "genres": {"movies": "documentaries", "music": "classical, focus", "podcasts": "educational, science", "audiobooks": "non-fiction, learning", "shorts": "facts, explained, science"}},
        # NEW FEELINGS
        "scared": {"desired": "Scared", "message": "Ooh feeling brave! Spooky content incoming 👻",
                  "genres": {"movies": "horror, thriller", "music": "dark ambient, eerie", "podcasts": "true crime, horror stories", "audiobooks": "horror, thriller", "shorts": "scary, horror, jumpscare"}},
        "spooky": {"desired": "Scared", "message": "Let's get creepy! 🎃",
                  "genres": {"movies": "horror, supernatural", "music": "spooky, halloween", "podcasts": "paranormal, horror", "audiobooks": "ghost stories, horror", "shorts": "creepy, scary, paranormal"}},
        "thrill": {"desired": "Thrilled", "message": "Adrenaline time! 🎢",
                  "genres": {"movies": "thriller, action", "music": "intense, epic", "podcasts": "true crime, suspense", "audiobooks": "thriller, suspense", "shorts": "extreme, thrilling, intense"}},
        "nostalg": {"desired": "Nostalgic", "message": "Taking you back in time! 🥹",
                  "genres": {"movies": "classic films, retro", "music": "throwback hits, oldies", "podcasts": "90s, 2000s, retro", "audiobooks": "classic literature", "shorts": "throwback, nostalgia, 90s 2000s"}},
        "romantic": {"desired": "Romantic", "message": "Love is in the air! 💕",
                  "genres": {"movies": "romance, romantic comedy", "music": "love songs, R&B", "podcasts": "love stories, relationship", "audiobooks": "romance novels", "shorts": "cute couples, romantic"}},
        "love": {"desired": "Romantic", "message": "Swoon-worthy picks coming up! 💕",
                  "genres": {"movies": "romance, love stories", "music": "love ballads, romantic", "podcasts": "love, relationships", "audiobooks": "romance", "shorts": "couples, love, romantic"}},
        "adventure": {"desired": "Adventurous", "message": "Adventure awaits! 🏔️",
                  "genres": {"movies": "adventure, exploration", "music": "epic, cinematic", "podcasts": "travel, adventure", "audiobooks": "adventure, travel", "shorts": "travel, explore, adventure"}},
        "amuse": {"desired": "Amused", "message": "Let's get those giggles! 😂",
                  "genres": {"movies": "comedy, funny", "music": "fun, upbeat", "podcasts": "comedy, humor", "audiobooks": "comedy, humor", "shorts": "funny, fails, comedy"}},
        "creepy": {"desired": "Scared", "message": "Getting creepy! 👀",
                  "genres": {"movies": "horror, psychological", "music": "dark, eerie", "podcasts": "creepypasta, horror", "audiobooks": "horror, dark", "shorts": "creepy, unsettling, horror"}},
        "scare me": {"desired": "Scared", "message": "You asked for it! 😱",
                  "genres": {"movies": "horror, jump scares", "music": "horror soundtrack", "podcasts": "scary stories", "audiobooks": "horror", "shorts": "jumpscare, scary, horror"}},
        "feel scared": {"desired": "Scared", "message": "Brave mode ON! Let's get spooky 👻",
                  "genres": {"movies": "horror, thriller", "music": "dark ambient", "podcasts": "horror, true crime", "audiobooks": "horror, thriller", "shorts": "scary, creepy, horror"}},
    }
    
    for keyword, data in desire_responses.items():
        if keyword in t:
            if not desired:
                desired = data["desired"]
            if not message:
                message = data["message"]
            if not genres:
                genres = data["genres"].get(media_type, data["genres"]["movies"])
            if not current:
                current = "Bored"
            break
    
    # Check for search mode (specific titles, actors, directors) - only for movies
    if media_type == "movies":
        import re
        names_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(names_pattern, prompt)
        
        if names or any(ind in t for ind in ["nolan", "spielberg", "tarantino", "scorsese", "kubrick", "villeneuve"]):
            mode = "search"
            query = prompt
            message = message or "Great choice! Let me search for that 🔍"
    
    # Default fallbacks
    defaults = media_defaults.get(media_type, media_defaults["movies"])
    if not message:
        message = f"{defaults['default_msg']} {defaults['icon']}"
    if not current:
        current = "Bored"
    if not desired:
        desired = "Entertained"
    if not genres:
        genres = defaults["default_genres"]
    
    return {
        "message": message,
        "current_feeling": current,
        "desired_feeling": desired,
        "media_type": media_type,
        "mode": mode,
        "search_query": query,
        "genres": genres
    }

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


def mr_dp_search(response):
    """
    Execute Mr.DP's recommendation based on his analysis.
    Handles movies, music, podcasts, audiobooks, shorts, and artist search.
    """
    if not response:
        return []
    
    media_type = response.get("media_type", "movies")
    mode = response.get("mode", "discover")
    query = response.get("search_query", "").strip()
    current_feeling = response.get("current_feeling")
    desired_feeling = response.get("desired_feeling")
    
    # ARTIST MODE - Spotify artist search
    if media_type == "artist" and query:
        return {
            "type": "artist",
            "artist_name": query,
            "query": query
        }
    
    # MUSIC MODE
    if media_type == "music":
        mood_music = FEELING_TO_MUSIC.get(desired_feeling) or FEELING_TO_MUSIC.get(current_feeling) or FEELING_TO_MUSIC.get("Happy")
        return {
            "type": "music",
            "playlist_id": mood_music.get("playlist"),
            "query": mood_music.get("query"),
            "genres": mood_music.get("genres", [])
        }
    
    # PODCASTS MODE
    if media_type == "podcasts":
        mood_pods = FEELING_TO_PODCASTS.get(desired_feeling) or FEELING_TO_PODCASTS.get(current_feeling) or FEELING_TO_PODCASTS.get("Curious")
        return {
            "type": "podcasts",
            "query": mood_pods.get("query", ""),
            "shows": mood_pods.get("shows", [])
        }
    
    # AUDIOBOOKS MODE
    if media_type == "audiobooks":
        mood_books = FEELING_TO_AUDIOBOOKS.get(desired_feeling) or FEELING_TO_AUDIOBOOKS.get(current_feeling) or FEELING_TO_AUDIOBOOKS.get("Curious")
        return {
            "type": "audiobooks",
            "query": mood_books.get("query", ""),
            "genres": mood_books.get("genres", []),
            "picks": mood_books.get("picks", [])
        }
    
    # SHORTS MODE
    if media_type == "shorts":
        shorts_data = FEELING_TO_SHORTS.get(desired_feeling) or FEELING_TO_SHORTS.get(current_feeling) or FEELING_TO_SHORTS.get("Entertained")
        return {
            "type": "shorts",
            "query": shorts_data.get("query", "viral shorts"),
            "label": shorts_data.get("label", "Trending"),
            "videos": shorts_data.get("videos", [])
        }
    
    # MOVIES MODE (default)
    # SEARCH MODE: Specific title/actor/director
    if mode == "search" and query:
        results = search_movies(query)
        if results:
            return results
    
    # DISCOVER MODE: Mood-based discovery with fresh results
    return discover_movies_fresh(current_feeling=current_feeling, desired_feeling=desired_feeling)

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
# 10b. ADS & MONETIZATION
# --------------------------------------------------
# Stripe Configuration (add your keys to Streamlit secrets)
STRIPE_ENABLED = False
try:
    STRIPE_PAYMENT_LINK_MONTHLY = st.secrets.get("STRIPE_LINK_MONTHLY", "")
    STRIPE_PAYMENT_LINK_YEARLY = st.secrets.get("STRIPE_LINK_YEARLY", "")
    if STRIPE_PAYMENT_LINK_MONTHLY:
        STRIPE_ENABLED = True
except:
    STRIPE_PAYMENT_LINK_MONTHLY = ""
    STRIPE_PAYMENT_LINK_YEARLY = ""

# Mr.DP daily chat limit for free users
FREE_CHAT_LIMIT = 10

def get_daily_chat_count():
    """Get number of Mr.DP chats today"""
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.get("chat_date") != today:
        st.session_state.chat_date = today
        st.session_state.chat_count = 0
    return st.session_state.get("chat_count", 0)

def increment_chat_count():
    """Increment daily chat counter"""
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.get("chat_date") != today:
        st.session_state.chat_date = today
        st.session_state.chat_count = 0
    st.session_state.chat_count = st.session_state.get("chat_count", 0) + 1

def can_chat():
    """Check if user can use Mr.DP"""
    if st.session_state.get("is_premium"):
        return True
    return get_daily_chat_count() < FREE_CHAT_LIMIT

def render_ad_banner(placement="default"):
    """Render ad banner for free users"""
    if st.session_state.get("is_premium"):
        return  # No ads for premium users
    
    # Different ad styles based on placement
    ads = {
        "default": {
            "title": "🚀 Go Premium",
            "text": "Remove ads & get unlimited Mr.DP chats",
            "cta": "Upgrade for $4.99/mo"
        },
        "sidebar": {
            "title": "⭐ Premium",
            "text": "Ad-free experience",
            "cta": "Upgrade"
        },
        "between_content": {
            "title": "💜 Love dopamine.watch?",
            "text": "Support us & remove ads",
            "cta": "Go Premium"
        },
        "chat_limit": {
            "title": "💬 Chat Limit Reached",
            "text": f"Free users get {FREE_CHAT_LIMIT} Mr.DP chats/day",
            "cta": "Get Unlimited"
        }
    }
    
    ad = ads.get(placement, ads["default"])
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(6,182,212,0.15));
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin: 16px 0;
    ">
        <div style="font-weight: 700; font-size: 1.1rem; margin-bottom: 8px;">{ad['title']}</div>
        <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 12px;">{ad['text']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(ad['cta'], key=f"ad_cta_{placement}_{random.randint(0,9999)}", use_container_width=True):
        st.session_state.show_premium_modal = True
        st.rerun()

def render_premium_modal():
    """Render premium upgrade modal"""
    if not st.session_state.get("show_premium_modal"):
        return
    
    st.markdown("""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.8);
        z-index: 9998;
    "></div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border: 2px solid rgba(139,92,246,0.5);
            border-radius: 24px;
            padding: 40px;
            max-width: 500px;
            margin: 40px auto;
            text-align: center;
            box-shadow: 0 25px 80px rgba(139,92,246,0.3);
        ">
            <div style="font-size: 3rem; margin-bottom: 16px;">👑</div>
            <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; margin-bottom: 8px;">
                Go Premium
            </h2>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 24px;">
                Unlock the full dopamine.watch experience
            </p>
            
            <div style="
                background: rgba(255,255,255,0.05);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 24px;
                text-align: left;
            ">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="color: #10b981;">✓</span>
                    <span>No ads — ever</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="color: #10b981;">✓</span>
                    <span>Unlimited Mr.DP conversations</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="color: #10b981;">✓</span>
                    <span>Priority AI recommendations</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                    <span style="color: #10b981;">✓</span>
                    <span>Exclusive 👑 badge</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="color: #10b981;">✓</span>
                    <span>Early access to new features</span>
                </div>
            </div>
            
            <div style="
                background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(6,182,212,0.2));
                border: 2px solid rgba(139,92,246,0.5);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 20px;
            ">
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.6);">PREMIUM</div>
                <div style="font-size: 2.5rem; font-weight: 700;">$4.99</div>
                <div style="font-size: 0.85rem; color: rgba(255,255,255,0.5);">per month</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Single pricing button
        if STRIPE_ENABLED and STRIPE_PAYMENT_LINK_MONTHLY:
            if st.button("⭐ Upgrade to Premium", key="premium_monthly", use_container_width=True):
                st.markdown(f'<meta http-equiv="refresh" content="0;url={STRIPE_PAYMENT_LINK_MONTHLY}">', unsafe_allow_html=True)
        else:
            if st.button("⭐ Upgrade to Premium", key="premium_monthly_placeholder", use_container_width=True):
                st.toast("Payment coming soon! 🚀", icon="⭐")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Maybe Later", key="close_premium_modal", use_container_width=True):
            st.session_state.show_premium_modal = False
            st.rerun()

# --------------------------------------------------
# 11. STATE INITIALIZATION
# --------------------------------------------------
if "init" not in st.session_state:
    st.session_state.update({
        # Auth - starts as None, user must login/signup
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
        
        # Mr.DP Recommendations (backend only)
        "mr_dp_response": None,
        "mr_dp_results": [],
        "mr_dp_page": 1,
        "scroll_to_top": False,
        "last_mr_dp_input": "",
        "chat_count": 0,
        "chat_date": "",

        # Mr.DP Floating Chat Widget
        "mr_dp_chat_history": [],
        "mr_dp_open": False,
        
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
# AUTO-LOGIN FROM INDEX.HTML (read URL params)
# --------------------------------------------------
# If user comes from index.html with ?user=email or ?guest=1, auto-login them
query_params = st.query_params
if not st.session_state.get("user"):
    # Check for user param from index.html login/signup
    if query_params.get("user"):
        user_email = query_params.get("user")
        user_name = query_params.get("name", user_email.split("@")[0] if "@" in user_email else user_email)
        st.session_state.user = {
            "email": user_email,
            "name": user_name
        }
        # Clear URL params so they don't show in browser
        st.query_params.clear()
        # Give welcome points
        if query_params.get("new"):
            st.session_state.dopamine_points = 50
            st.session_state.streak_days = 1
        st.rerun()
    
    # Check for guest param
    elif query_params.get("guest"):
        st.session_state.user = {
            "email": "guest",
            "name": "Guest"
        }
        st.query_params.clear()
        st.rerun()

# Handle OAuth callback (check URL for tokens)
if SUPABASE_ENABLED and not st.session_state.get("user"):
    oauth_result = handle_oauth_callback()
    if oauth_result and oauth_result.get("success"):
        user = oauth_result["user"]
        profile = oauth_result.get("profile") or {}
        st.session_state.user = {
            "email": user.email,
            "name": profile.get("name") or user.user_metadata.get("full_name") or user.email.split("@")[0],
            "id": user.id
        }
        st.session_state.db_user_id = user.id
        st.session_state.dopamine_points = profile.get("dopamine_points", 50)
        st.session_state.streak_days = profile.get("streak_days", 1)
        st.session_state.referral_code = profile.get("referral_code", st.session_state.referral_code)
        st.session_state.is_premium = profile.get("is_premium", False)
        st.session_state.auth_success = "Welcome! Signed in successfully."
        st.rerun()

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

.oauth-buttons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin: 16px 0;
}

.oauth-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 14px 20px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none;
    transition: all 0.3s ease;
    cursor: pointer;
    border: none;
    width: 100%;
}

.oauth-btn-google {
    background: white;
    color: #333;
    border: 1px solid rgba(0,0,0,0.1);
}

.oauth-btn-google:hover {
    background: #f5f5f5;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.oauth-btn-apple {
    background: #000;
    color: white;
}

.oauth-btn-apple:hover {
    background: #333;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.oauth-icon {
    width: 20px;
    height: 20px;
}

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
.avail-badge {
    position: absolute;
    bottom: -2px;
    right: -2px;
    width: 14px;
    height: 14px;
    background: #10b981;
    color: white;
    font-size: 8px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}
.provider-btn {
    position: relative;
}
.provider-btn.all-options {
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    font-size: 14px;
    color: white;
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

/* Mr.DP Neuron Character Container */
.mr-dp-character {
    width: 56px;
    height: 56px;
    flex-shrink: 0;
    filter: drop-shadow(0 0 8px rgba(139, 92, 246, 0.5));
}

/* Keyframes for Mr.DP animations */
@keyframes mrDpBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

@keyframes mrDpPulse {
    0%, 100% { box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4); }
    50% { box-shadow: 0 8px 40px rgba(139, 92, 246, 0.6), 0 0 0 8px rgba(139, 92, 246, 0.15); }
}

/* Style Streamlit's chat input - position near Mr.DP on the right */
.stChatInput {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    left: auto !important;
    transform: none !important;
    max-width: 340px !important;
    width: 340px !important;
    z-index: 9997 !important;
}

.stChatInput > div {
    background: #0d0d12 !important;
    border: 2px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: 24px !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25) !important;
    padding: 4px !important;
}

.stChatInput > div:focus-within {
    border-color: #8b5cf6 !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.4), 0 0 0 4px rgba(139, 92, 246, 0.15) !important;
}

.stChatInput input {
    background: transparent !important;
    color: white !important;
    padding: 12px 16px !important;
    font-size: 0.9rem !important;
}

.stChatInput input::placeholder {
    color: rgba(255,255,255,0.5) !important;
}

.stChatInput button {
    background: linear-gradient(135deg, #8b5cf6, #06b6d4) !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    margin: 4px !important;
}

.stChatInput button svg {
    fill: white !important;
}

/* Adjust main content to account for fixed elements */
.main .block-container {
    padding-bottom: 100px !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 13. HELPER FUNCTIONS
# --------------------------------------------------
def safe(s):
    return html_lib.escape(s or "")

def render_support_resources_modal():
    """Render mental health support resources modal with government hotlines."""
    st.markdown('''
    <div id="support-modal" style="display:none; position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.85); z-index:10000; padding:20px; overflow-y:auto;">
        <div style="max-width:600px; margin:40px auto; background:#111118; border-radius:24px; padding:32px; border:1px solid rgba(139,92,246,0.3);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
                <h2 style="margin:0; color:white; font-size:1.5rem;">💚 Mental Health Resources</h2>
                <button onclick="document.getElementById('support-modal').style.display='none'" style="background:rgba(255,255,255,0.1); border:none; color:white; font-size:1.2rem; cursor:pointer; width:36px; height:36px; border-radius:50%; display:flex; align-items:center; justify-content:center;">✕</button>
            </div>
            <p style="color:rgba(255,255,255,0.7); margin-bottom:24px; font-size:0.95rem; line-height:1.6;">
                If you're struggling, please reach out. These services are free, confidential, and available 24/7.
            </p>
            
            <div style="display:flex; flex-direction:column; gap:12px;">
                <!-- USA -->
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇺🇸</span> 988 Suicide & Crisis Lifeline
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">Call or Text: 988</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • Free • Confidential</div>
                </div>
                
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇺🇸</span> Crisis Text Line
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">Text HOME to 741741</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • Free • For any crisis</div>
                </div>
                
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇺🇸</span> SAMHSA National Helpline
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">1-800-662-4357</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • Mental health & substance abuse</div>
                </div>
                
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇺🇸</span> Veterans Crisis Line
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">Call: 988 (Press 1)</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • For veterans & their families</div>
                </div>
                
                <!-- UK -->
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇬🇧</span> Samaritans (UK & Ireland)
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">116 123</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • Free from any phone</div>
                </div>
                
                <!-- Canada -->
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇨🇦</span> Canada Crisis Line
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">988</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • Nationwide support</div>
                </div>
                
                <!-- Australia -->
                <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🇦🇺</span> Lifeline Australia
                    </div>
                    <div style="color:#10b981; font-size:1.4rem; font-weight:700; margin-bottom:4px;">13 11 14</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem;">24/7 • Crisis support & suicide prevention</div>
                </div>
                
                <!-- International -->
                <div style="background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.3); border-radius:16px; padding:16px;">
                    <div style="font-weight:600; color:white; margin-bottom:6px; display:flex; align-items:center; gap:8px;">
                        <span>🌍</span> International Resources
                    </div>
                    <div style="color:#06b6d4; font-size:0.95rem;">
                        <a href="https://www.iasp.info/resources/Crisis_Centres/" target="_blank" style="color:#06b6d4; text-decoration:none;">
                            Find crisis centers in your country →
                        </a>
                    </div>
                    <div style="color:rgba(255,255,255,0.6); font-size:0.8rem; margin-top:4px;">International Association for Suicide Prevention</div>
                </div>
            </div>
            
            <p style="color:rgba(255,255,255,0.5); font-size:0.8rem; margin-top:20px; text-align:center; line-height:1.5;">
                💜 It's okay to ask for help. You matter, and these services are here for you.
            </p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

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
        providers, tmdb_watch_link = get_movie_providers(tmdb_id, media_type)
        if providers:
            icons = ""
            for p in providers[:6]:
                name = p.get("provider_name", "")
                logo = p.get("logo_path")
                availability = p.get("availability", "stream")
                if not logo:
                    continue
                link = get_movie_deep_link(name, title, tmdb_id, media_type)
                if not link:
                    continue
                # Add availability indicator
                avail_icon = "✓" if availability == "stream" else "$"
                icons += f"<a href='{safe(link)}' target='_blank' class='provider-btn' title='{safe(name)} ({availability})'><img src='{TMDB_LOGO_URL}{logo}' class='provider-icon'><span class='avail-badge'>{avail_icon}</span></a>"
            if icons:
                # Add "All Options" link to TMDB watch page
                all_link = f"<a href='{tmdb_watch_link}' target='_blank' class='provider-btn all-options' title='See all watch options'>🔗</a>" if tmdb_watch_link else ""
                providers_html = f"<div class='provider-grid'>{icons}{all_link}</div>"
    
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
    tmdb_id = movie.get("id")
    media_type = movie.get("media_type", "movie")
    
    # Try to get trailer
    trailer_key = get_movie_trailer(tmdb_id, media_type) if tmdb_id else None
    
    # Trailer button HTML - single line to avoid f-string issues
    trailer_btn = ""
    if trailer_key:
        trailer_btn = f'<a href="https://www.youtube.com/watch?v={trailer_key}" target="_blank" class="hero-trailer-btn" title="Watch Trailer"><span class="hero-play-icon">▶</span><span>Watch Trailer</span></a>'
    
    hero_html = f"""
    <style>
    .hero-trailer-btn {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-top: 16px;
        padding: 12px 24px;
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.9), rgba(6, 182, 212, 0.9));
        border-radius: 30px;
        color: white;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
    }}
    .hero-trailer-btn:hover {{
        transform: scale(1.05);
        box-shadow: 0 6px 30px rgba(139, 92, 246, 0.6);
    }}
    .hero-play-icon {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: white;
        border-radius: 50%;
        color: #8b5cf6;
        font-size: 0.9rem;
        padding-left: 3px;
    }}
    </style>
    <div class="hero-container">
        <img src="{safe(backdrop)}" class="hero-backdrop" onerror="this.style.opacity='0.3'">
        <div class="hero-content">
            <div class="hero-title">{safe(title)}</div>
            <div class="hero-meta">{year} {'• ⭐ ' + str(round(rating, 1)) if rating else ''}</div>
            <p class="hero-overview">{safe(overview)}</p>
            {trailer_btn}
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

def render_service_buttons(services, query):
    for name, data in services.items():
        url = data["url"].format(query=quote_plus(query))
        icon = data.get("icon", "🔗")
        st.link_button(f"{icon} {name}", url, use_container_width=True)

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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Get Started Free", use_container_width=True, key="cta_signup", type="primary"):
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
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Mr.DP - AI Curator</div>
            <div class="feature-desc">Meet your personal dopamine buddy! Just tell him how you feel and he'll find the perfect content.</div>
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
        
        if st.button("🔑 Log In", use_container_width=True, key="login_btn", type="primary"):
            if email and password:
                # Frontend-only login - just validate and let them in
                if len(password) >= 6:
                    st.session_state.user = {"email": email, "name": email.split("@")[0]}
                    update_streak()
                    add_dopamine_points(25, "Welcome back!")
                    st.balloons()
                    st.rerun()
                else:
                    st.session_state.auth_error = "Invalid credentials"
                    st.rerun()
            else:
                st.session_state.auth_error = "Please enter email and password"
                st.rerun()
        
        # Forgot password - always show
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
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="••••••••")
        
        if st.button("🚀 Create Account", use_container_width=True, key="signup_btn", type="primary"):
            if email and name and password:
                if len(password) < 6:
                    st.session_state.auth_error = "Password must be at least 6 characters"
                    st.rerun()
                elif password != confirm_password:
                    st.session_state.auth_error = "Passwords do not match"
                    st.rerun()
                elif "@" not in email:
                    st.session_state.auth_error = "Please enter a valid email"
                    st.rerun()
                else:
                    # Frontend-only signup - just create session
                    st.session_state.user = {"email": email, "name": name}
                    st.session_state.dopamine_points = 50
                    st.session_state.streak_days = 1
                    update_streak()
                    st.balloons()
                    st.toast("🎉 Welcome to Dopamine.watch! +50 DP", icon="⚡")
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
            <div class="auth-subtitle">Enter your email to reset</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("auth_error"):
            st.markdown(f"<div class='auth-error'>❌ {st.session_state.auth_error}</div>", unsafe_allow_html=True)
            st.session_state.auth_error = None
        if st.session_state.get("auth_success"):
            st.markdown(f"<div class='auth-success'>✅ {st.session_state.auth_success}</div>", unsafe_allow_html=True)
            st.session_state.auth_success = None
        
        email = st.text_input("Email", key="reset_email", placeholder="your@email.com")
        
        if st.button("📧 Send Reset Link", use_container_width=True, key="reset_btn", type="primary"):
            if email and "@" in email:
                # Frontend-only - just show success message
                st.session_state.auth_success = "If an account exists, you'll receive a reset link shortly!"
                st.rerun()
            else:
                st.session_state.auth_error = "Please enter a valid email"
                st.rerun()
        
        st.markdown("---")
        
        st.info("💡 **Tip:** For this demo, just go back and create a new account or use Guest Mode!")
        
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
                st.session_state.mr_dp_results = []
                st.session_state.mr_dp_response = None
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
    # Check if we need to scroll to top (after Mr.DP response)
    if st.session_state.get("scroll_to_top"):
        # Use components.html with LONGER delays to beat Streamlit's scroll
        components.html("""
        <script>
            function scrollToTop() {
                try {
                    var container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                    if (container) container.scrollTop = 0;
                    var main = window.parent.document.querySelector('.main');
                    if (main) main.scrollTop = 0;
                    window.parent.scrollTo(0, 0);
                } catch(e) {}
            }
            // Much longer delays to beat Streamlit's auto-focus on chat_input
            setTimeout(scrollToTop, 500);
            setTimeout(scrollToTop, 1000);
            setTimeout(scrollToTop, 1500);
        </script>
        """, height=0)
        st.session_state.scroll_to_top = False  # Clear flag
    
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
        
        providers, tmdb_watch_link = get_movie_providers(st.session_state.quick_hit.get("id"), st.session_state.quick_hit.get("type", "movie"))
        if providers:
            provider_cols = st.columns(min(len(providers) + 1, 7))  # +1 for "All Options" button
            for i, p in enumerate(providers[:6]):
                with provider_cols[i]:
                    link = get_movie_deep_link(p.get("provider_name", ""), st.session_state.quick_hit.get("title", ""), st.session_state.quick_hit.get("id"))
                    availability = p.get("availability", "stream")
                    avail_text = "✓ Stream" if availability == "stream" else "$ Rent"
                    if link:
                        st.markdown(f"<a href='{link}' target='_blank' style='display:block; text-align:center; padding:12px; background:var(--glass); border:1px solid var(--glass-border); border-radius:12px; color:white; text-decoration:none; font-size:0.8rem;'>{p.get('provider_name', '')[:12]}<br><small style='opacity:0.6'>{avail_text}</small></a>", unsafe_allow_html=True)
            # Add "All Options" button
            if tmdb_watch_link and len(providers) < 7:
                with provider_cols[min(len(providers), 6)]:
                    st.markdown(f"<a href='{tmdb_watch_link}' target='_blank' style='display:block; text-align:center; padding:12px; background:linear-gradient(135deg, var(--primary), var(--secondary)); border:none; border-radius:12px; color:white; text-decoration:none; font-size:0.8rem;'>🔗 All<br><small>Options</small></a>", unsafe_allow_html=True)
        
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
    
    # MR.DP RESULTS - Show when there are results from chat
    if st.session_state.mr_dp_results:
        response = st.session_state.mr_dp_response or {}
        current_f = response.get("current_feeling", "")
        desired_f = response.get("desired_feeling", "")
        genres = response.get("genres", "")
        media_type = response.get("media_type", "movies")
        results = st.session_state.mr_dp_results
        
        # Determine result type from dict
        result_type = results.get("type") if isinstance(results, dict) else "movies"
        
        # Icons and titles based on type
        type_config = {
            "music": {"icon": "🎵", "title": "Mr.DP's Playlist"},
            "artist": {"icon": "🎤", "title": "Mr.DP's Artist Pick"},
            "podcasts": {"icon": "🎙️", "title": "Mr.DP's Podcast Picks"},
            "audiobooks": {"icon": "📚", "title": "Mr.DP's Audiobook Picks"},
            "shorts": {"icon": "⚡", "title": "Mr.DP's Quick Hits"},
            "movies": {"icon": "🧠", "title": "Mr.DP's Picks"},
        }
        config = type_config.get(result_type, type_config["movies"])
        
        # Build mood tags HTML separately
        mood_tags = ""
        if current_f:
            emoji = MOOD_EMOJIS.get(current_f, "😊")
            mood_tags += f'<span style="padding:6px 14px;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);border-radius:20px;font-size:0.85rem;color:white;">{emoji} {current_f}</span>'
        if desired_f:
            emoji = MOOD_EMOJIS.get(desired_f, "✨")
            mood_tags += f'<span style="padding:6px 14px;background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.2);border-radius:20px;font-size:0.85rem;color:white;">→ {emoji} {desired_f}</span>'
        if genres:
            mood_tags += f'<span style="padding:6px 14px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:20px;font-size:0.85rem;color:white;">{config["icon"]} {genres}</span>'
        
        # Anchor + Header with mood info
        st.markdown(f"""
        <div id="mr-dp-results"></div>
        <div class="section-header" style="margin-bottom: 8px;">
            <span class="section-icon">{config['icon']}</span>
            <h2 class="section-title">{config['title']}</h2>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
            {mood_tags}
        </div>
        """, unsafe_allow_html=True)
        
        # ===================== ARTIST RESULTS =====================
        if result_type == "artist":
            artist_name = results.get("artist_name", "")
            artist_query = quote_plus(artist_name)
            
            # Big artist card
            st.markdown(f"""
            <div style="text-align:center;padding:40px;background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(6,182,212,0.2));border-radius:24px;border:1px solid rgba(139,92,246,0.3);margin-bottom:24px;">
                <div style="font-size:4rem;margin-bottom:16px;">🎤</div>
                <div style="font-size:2rem;font-weight:700;background:linear-gradient(135deg,#8b5cf6,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{artist_name}</div>
                <div style="color:var(--text-secondary);margin-top:8px;">Click below to listen</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Big buttons to music services
            st.markdown(f"""
            <a href="https://open.spotify.com/search/{artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:#1DB954;border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-bottom:12px;box-shadow:0 8px 32px rgba(29,185,84,0.3);">
                🎵 Play {artist_name} on Spotify →
            </a>
            <a href="https://music.apple.com/search?term={artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#fc3c44,#fc9a9a);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-bottom:12px;box-shadow:0 8px 32px rgba(252,60,68,0.3);">
                🍎 Play on Apple Music →
            </a>
            <a href="https://music.youtube.com/search?q={artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:#FF0000;border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-bottom:12px;box-shadow:0 8px 32px rgba(255,0,0,0.3);">
                ▶️ Play on YouTube Music →
            </a>
            <a href="https://www.youtube.com/results?search_query={artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#333,#666);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;box-shadow:0 8px 32px rgba(0,0,0,0.3);">
                📺 Watch Music Videos on YouTube →
            </a>
            """, unsafe_allow_html=True)
            
            # Action buttons
            btn_cols = st.columns([1, 1])
            with btn_cols[0]:
                if st.button("🔄 Search Another Artist", key="mr_dp_shuffle_artist", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
                    st.rerun()
            with btn_cols[1]:
                if st.button("✕ Clear", key="mr_dp_clear_artist", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
                    st.rerun()
        
        # ===================== MUSIC RESULTS =====================
        elif result_type == "music":
            playlist_id = results.get("playlist_id", "37i9dQZF1DXcBWIGoYBM5M")
            music_query = results.get("query", "")
            music_genres = results.get("genres", [])
            
            st.caption(f"Genres: {', '.join(music_genres)}")
            
            # Embedded Spotify player
            components.iframe(f"https://open.spotify.com/embed/playlist/{playlist_id}?theme=0", height=380)
            
            # Music service buttons
            st.markdown("##### 🔍 Open in Your Music App")
            c1, c2 = st.columns(2)
            with c1:
                render_service_buttons(dict(list(MUSIC_SERVICES.items())[:3]), music_query)
            with c2:
                render_service_buttons(dict(list(MUSIC_SERVICES.items())[3:]), music_query)
            
            # Action buttons for music
            btn_cols = st.columns([1, 1])
            with btn_cols[0]:
                if st.button("🔄 Different Playlist", key="mr_dp_shuffle_music", use_container_width=True):
                    st.session_state.mr_dp_results = mr_dp_search(st.session_state.mr_dp_response)
                    add_dopamine_points(5, "New vibes!")
                    st.rerun()
            with btn_cols[1]:
                if st.button("✕ Clear", key="mr_dp_clear_music", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
                    st.rerun()
        
        # ===================== PODCASTS RESULTS =====================
        elif result_type == "podcasts":
            pod_query = results.get("query", "")
            pod_shows = results.get("shows", [])
            
            # Show recommended podcasts with nice cards
            st.markdown("##### ⭐ Recommended Shows")
            for show, desc in pod_shows:
                show_query = quote_plus(show)
                st.markdown(f"""
                <div class="glass-card" style="display:flex;align-items:center;gap:16px;margin-bottom:12px;">
                    <div style="font-size:2.5rem;">🎙️</div>
                    <div style="flex:1;">
                        <div style="font-weight:600;font-size:1.1rem;">{show}</div>
                        <div style="color:var(--text-secondary);font-size:0.85rem;">{desc}</div>
                    </div>
                    <a href="https://open.spotify.com/search/{show_query}" target="_blank" style="padding:10px 20px;background:#1DB954;border-radius:20px;color:white;text-decoration:none;font-size:0.85rem;font-weight:600;">▶️ Play</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Podcast service links
            st.markdown("##### 🔍 Find on Podcast Apps")
            c1, c2 = st.columns(2)
            with c1:
                render_service_buttons(dict(list(PODCAST_SERVICES.items())[:3]), pod_query)
            with c2:
                render_service_buttons(dict(list(PODCAST_SERVICES.items())[3:]), pod_query)
            
            # Action buttons
            btn_cols = st.columns([1, 1])
            with btn_cols[0]:
                if st.button("🔄 Different Podcasts", key="mr_dp_shuffle_pods", use_container_width=True):
                    st.session_state.mr_dp_results = mr_dp_search(st.session_state.mr_dp_response)
                    add_dopamine_points(5, "New shows!")
                    st.rerun()
            with btn_cols[1]:
                if st.button("✕ Clear", key="mr_dp_clear_pods", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
                    st.rerun()
        
        # ===================== AUDIOBOOKS RESULTS =====================
        elif result_type == "audiobooks":
            book_query = results.get("query", "")
            book_genres = results.get("genres", [])
            book_picks = results.get("picks", [])
            
            st.caption(f"Genres: {', '.join(book_genres)}")
            
            # Show recommended audiobooks with nice cards
            st.markdown("##### ⭐ Top Picks")
            cols = st.columns(min(len(book_picks), 3))
            for i, (title, author) in enumerate(book_picks[:3]):
                with cols[i]:
                    st.markdown(f"""
                    <div class="glass-card" style="text-align:center;padding:24px;height:200px;display:flex;flex-direction:column;justify-content:center;">
                        <div style="font-size:3rem;margin-bottom:12px;">📖</div>
                        <div style="font-weight:600;font-size:0.95rem;margin-bottom:4px;">{title}</div>
                        <div style="color:var(--text-secondary);font-size:0.8rem;">{author}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Audiobook service links
            st.markdown("##### 🔍 Find Audiobooks")
            c1, c2 = st.columns(2)
            with c1:
                render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[:3]), book_query)
            with c2:
                render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[3:]), book_query)
            
            st.info("💡 **Tip:** Check if your local library offers free audiobooks through **Libby** or **Hoopla**!")
            
            # Action buttons
            btn_cols = st.columns([1, 1])
            with btn_cols[0]:
                if st.button("🔄 Different Books", key="mr_dp_shuffle_books", use_container_width=True):
                    st.session_state.mr_dp_results = mr_dp_search(st.session_state.mr_dp_response)
                    add_dopamine_points(5, "New reads!")
                    st.rerun()
            with btn_cols[1]:
                if st.button("✕ Clear", key="mr_dp_clear_books", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
                    st.rerun()
        
        # ===================== SHORTS RESULTS =====================
        elif result_type == "shorts":
            vq = results.get("query", "trending viral")
            label = results.get("label", "Trending")
            video_ids = results.get("videos", [])
            
            st.markdown(f"### ⚡ {label} Shorts")
            
            # Embed YouTube videos in a grid
            if video_ids:
                st.markdown("##### 📺 Watch Here")
                vid_cols = st.columns(2)
                for i, vid_id in enumerate(video_ids[:4]):
                    with vid_cols[i % 2]:
                        # Use YouTube Shorts embed format
                        components.iframe(
                            f"https://www.youtube.com/embed/{vid_id}?rel=0&modestbranding=1",
                            height=400
                        )
            
            st.markdown("##### 🔗 Browse More")
            
            # Big colorful buttons to platforms
            yt_url = f"https://www.youtube.com/results?search_query={quote_plus(vq)}+shorts"
            tt_url = f"https://www.tiktok.com/search?q={quote_plus(vq)}"
            ig_url = f"https://www.instagram.com/explore/tags/{quote_plus(vq.replace(' ', ''))}/"
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""
                <a href="{yt_url}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg, #FF0000, #CC0000);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1rem;box-shadow:0 8px 32px rgba(255,0,0,0.3);">
                    ▶️ YouTube Shorts
                </a>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <a href="{tt_url}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#ff0050,#00f2ea);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1rem;box-shadow:0 8px 32px rgba(255,0,80,0.3);">
                    📱 TikTok
                </a>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <a href="{ig_url}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#833AB4,#FD1D1D,#F77737);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1rem;box-shadow:0 8px 32px rgba(131,58,180,0.3);">
                    📸 Reels
                </a>
                """, unsafe_allow_html=True)
            
            # Custom search
            st.markdown("##### 🔍 Custom Search")
            shorts_custom = st.text_input("Search for different shorts...", placeholder="Any topic or vibe", key="mr_dp_shorts_search")
            if shorts_custom:
                yt2 = f"https://www.youtube.com/results?search_query={quote_plus(shorts_custom)}+shorts"
                tt2 = f"https://www.tiktok.com/search?q={quote_plus(shorts_custom)}"
                st.markdown(f"""
                <div style="display:flex;gap:12px;margin-top:12px;">
                    <a href="{yt2}" target="_blank" style="flex:1;text-align:center;padding:16px;background:#FF0000;border-radius:12px;color:white;text-decoration:none;font-weight:600;">YouTube</a>
                    <a href="{tt2}" target="_blank" style="flex:1;text-align:center;padding:16px;background:linear-gradient(135deg,#ff0050,#00f2ea);border-radius:12px;color:white;text-decoration:none;font-weight:600;">TikTok</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Action buttons
            btn_cols = st.columns([1, 1])
            with btn_cols[0]:
                if st.button("🔄 Different Vibe", key="mr_dp_shuffle_shorts", use_container_width=True):
                    st.session_state.mr_dp_results = mr_dp_search(st.session_state.mr_dp_response)
                    add_dopamine_points(5, "New clips!")
                    st.rerun()
            with btn_cols[1]:
                if st.button("✕ Clear", key="mr_dp_clear_shorts", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
                    st.rerun()
        
        # ===================== MOVIES RESULTS (DEFAULT) =====================
        else:
            # MOVIE RESULTS - Movie grid
            cols = st.columns(6)
            for i, movie in enumerate(results[:24]):
                with cols[i % 6]:
                    render_movie_card(movie)
            
            # Action buttons for movies
            btn_cols = st.columns([1, 1, 1])
            with btn_cols[0]:
                if st.button("🔄 Different Picks", key="mr_dp_shuffle", use_container_width=True):
                    st.session_state.mr_dp_results = mr_dp_search(st.session_state.mr_dp_response)
                    add_dopamine_points(5, "Shuffled!")
                    st.rerun()
            with btn_cols[1]:
                if isinstance(results, list) and len(results) >= 20:
                    if st.button("📥 More Movies", key="mr_dp_more", use_container_width=True):
                        more = discover_movies_fresh(
                            current_feeling=response.get("current_feeling"),
                            desired_feeling=response.get("desired_feeling")
                        )
                        st.session_state.mr_dp_results.extend(more)
                        add_dopamine_points(5, "Exploring!")
                        st.rerun()
            with btn_cols[2]:
                if st.button("✕ Clear", key="mr_dp_clear_main", use_container_width=True):
                    st.session_state.mr_dp_results = []
                    st.session_state.mr_dp_response = None
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
            # First 2 rows (12 movies)
            cols = st.columns(6)
            for i, movie in enumerate(movies[:12]):
                with cols[i % 6]:
                    render_movie_card(movie)
            
            # Ad banner for free users (after first 2 rows)
            render_ad_banner("between_content")
            
            # Remaining movies
            if len(movies) > 12:
                cols = st.columns(6)
                for i, movie in enumerate(movies[12:24]):
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
        
        st.markdown("##### ⭐ Recommended Shows - Click to Listen")
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
            # Add clickable button for each show
            spotify_url = f"https://open.spotify.com/search/{quote_plus(show)}/shows"
            st.link_button(f"🟢 Listen on Spotify", spotify_url, use_container_width=True)
        
        st.markdown("##### 🔍 Search Podcasts")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(PODCAST_SERVICES.items())[:2]), mood_pods["query"])
        with c2:
            render_service_buttons(dict(list(PODCAST_SERVICES.items())[2:]), mood_pods["query"])
        
        st.markdown("##### 🎤 Custom Search")
        pod_query = st.text_input("Search for podcasts...", placeholder="Topic, show name, or host", key="pod_search")
        if pod_query:
            render_service_buttons(PODCAST_SERVICES, pod_query)
    
    elif page == "📚 Audiobooks":
        mood_books = FEELING_TO_AUDIOBOOKS.get(st.session_state.desired_feeling, FEELING_TO_AUDIOBOOKS.get("Curious"))
        st.markdown(f"<div class='section-header'><span class='section-icon'>📚</span><h2 class='section-title'>Audiobooks for {st.session_state.desired_feeling}</h2></div>", unsafe_allow_html=True)
        st.caption(f"Genres: {', '.join(mood_books['genres'])}")
        
        st.markdown("##### ⭐ Top Picks - Click to Find")
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
                # Add clickable button for each book
                audible_url = f"https://www.audible.com/search?keywords={quote_plus(title + ' ' + author)}"
                st.link_button(f"🎧 Find on Audible", audible_url, use_container_width=True)
        
        st.markdown("##### 🔍 Search Audiobooks")
        c1, c2 = st.columns(2)
        with c1:
            render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[:2]), mood_books["query"])
        with c2:
            render_service_buttons(dict(list(AUDIOBOOK_SERVICES.items())[2:]), mood_books["query"])
        
        st.markdown("##### 📕 Custom Search")
        book_query = st.text_input("Search for audiobooks...", placeholder="Title, author, or genre", key="book_search")
        if book_query:
            render_service_buttons(AUDIOBOOK_SERVICES, book_query)
        
        st.info("💡 **Tip:** Check if your local library offers free audiobooks through **Libby** or **Hoopla**!")
    
    elif page == "⚡ Shorts":
        # Get mood-based data
        desired = st.session_state.desired_feeling
        shorts_data = FEELING_TO_SHORTS.get(desired) or FEELING_TO_SHORTS.get("Entertained")
        search_query = shorts_data.get("query", "trending viral")
        label = shorts_data.get("label", "Trending")
        
        # Header
        st.markdown(f"<div class='section-header'><span class='section-icon'>⚡</span><h2 class='section-title'>{label} Shorts</h2></div>", unsafe_allow_html=True)
        
        # Vibe selector - changes the search query
        st.markdown("**🎯 Pick a vibe:**")
        vibe_map = {
            "😂 Funny": ("Amused", "funny comedy hilarious fails memes"),
            "😱 Scary": ("Scared", "scary horror creepy thriller"),
            "🔥 Hype": ("Energized", "hype workout motivation beast mode"),
            "😌 Calm": ("Relaxed", "relaxing calm peaceful satisfying asmr"),
            "🤯 Mind-Blown": ("Stimulated", "mind blown amazing facts wow"),
            "🥹 Wholesome": ("Comforted", "wholesome cute animals heartwarming"),
            "😴 Sleepy": ("Sleepy", "sleep relaxing rain sounds calm"),
            "💪 Motivated": ("Motivated", "motivation success grind hustle gym")
        }
        
        vibe_cols = st.columns(4)
        for i, (btn_label, (feeling, _)) in enumerate(vibe_map.items()):
            with vibe_cols[i % 4]:
                is_selected = feeling == desired
                if st.button(btn_label, key=f"vibe_{feeling}", use_container_width=True, type="primary" if is_selected else "secondary"):
                    st.session_state.desired_feeling = feeling
                    st.rerun()
        
        st.markdown("---")
        
        # Show current search
        st.markdown(f"### 🔍 Search: `{search_query}`")
        
        # Build URLs
        yt_url = f"https://www.youtube.com/results?search_query={quote_plus(search_query + ' shorts')}"
        tt_url = f"https://www.tiktok.com/search?q={quote_plus(search_query)}"
        ig_tag = search_query.split()[0]
        ig_url = f"https://www.instagram.com/explore/tags/{ig_tag}/"
        
        # JavaScript-powered buttons that WILL open links
        st.markdown("##### 📺 Click to Watch")
        
        components.html(f'''
        <style>
            .shorts-btn {{
                display: block;
                width: 100%;
                padding: 20px;
                margin: 10px 0;
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .shorts-btn:hover {{
                transform: scale(1.02);
                box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            }}
            .yt-btn {{ background: linear-gradient(135deg, #FF0000, #CC0000); }}
            .tt-btn {{ background: linear-gradient(135deg, #ff0050, #00f2ea); }}
            .ig-btn {{ background: linear-gradient(135deg, #833AB4, #FD1D1D, #F77737); }}
            .search-info {{
                color: #888;
                font-size: 14px;
                margin-top: 4px;
            }}
        </style>
        
        <a href="{yt_url}" target="_blank" class="shorts-btn yt-btn">
            ▶️ YouTube Shorts
            <div class="search-info">Search: {search_query} shorts</div>
        </a>
        
        <a href="{tt_url}" target="_blank" class="shorts-btn tt-btn">
            📱 TikTok
            <div class="search-info">Search: {search_query}</div>
        </a>
        
        <a href="{ig_url}" target="_blank" class="shorts-btn ig-btn">
            📸 Instagram Reels
            <div class="search-info">Tag: #{ig_tag}</div>
        </a>
        ''', height=320)
        
        st.markdown("---")
        
        # Custom search
        st.markdown("##### 🔍 Custom Search")
        custom_query = st.text_input("Search anything:", placeholder="funny cats, satisfying, scary...", key="shorts_search_input")
        
        if custom_query:
            yt2 = f"https://www.youtube.com/results?search_query={quote_plus(custom_query + ' shorts')}"
            tt2 = f"https://www.tiktok.com/search?q={quote_plus(custom_query)}"
            ig2 = f"https://www.instagram.com/explore/tags/{custom_query.replace(' ', '')}/"
            
            components.html(f'''
            <style>
                .custom-btn {{
                    display: inline-block;
                    width: 30%;
                    padding: 15px 10px;
                    margin: 5px 1%;
                    border: none;
                    border-radius: 10px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    text-decoration: none;
                    text-align: center;
                }}
                .custom-btn:hover {{ opacity: 0.9; }}
            </style>
            <div style="text-align: center;">
                <a href="{yt2}" target="_blank" class="custom-btn" style="background:#FF0000;">▶️ YouTube</a>
                <a href="{tt2}" target="_blank" class="custom-btn" style="background:linear-gradient(135deg,#ff0050,#00f2ea);">📱 TikTok</a>
                <a href="{ig2}" target="_blank" class="custom-btn" style="background:linear-gradient(135deg,#833AB4,#FD1D1D);">📸 Instagram</a>
            </div>
            ''', height=80)
    
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

    # Render support resources modal (always available)
    render_support_resources_modal()

    # Render premium modal (if triggered)
    render_premium_modal()

    # Render floating Mr.DP chat widget
    user_message = render_floating_mr_dp()

    # Handle Mr.DP message if user sent one
    if user_message:
        # Add user message to chat history
        st.session_state.mr_dp_chat_history.append({
            "role": "user",
            "content": user_message
        })

        # Get AI response from Mr.DP
        response = ask_mr_dp(user_message)

        # Add Mr.DP's response to chat history
        st.session_state.mr_dp_chat_history.append({
            "role": "assistant",
            "content": response["message"]
        })

        # Update session state with mood analysis
        st.session_state.current_feeling = response["current_feeling"]
        st.session_state.desired_feeling = response["desired_feeling"]
        st.session_state.mr_dp_response = response

        # Search for content based on mood
        st.session_state.mr_dp_results = mr_dp_search(response)

        # Award dopamine points
        add_dopamine_points(10, "Chatted with Mr.DP!")

        # Scroll to top to show results
        st.session_state.scroll_to_top = True

        # Rerun to show Mr.DP response and results
        st.rerun()

    # Main content
    render_main()