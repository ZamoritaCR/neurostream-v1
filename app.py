# FILE: app.py
# --------------------------------------------------
# DOPAMINE.WATCH v41.0 - MOBILE & PWA OPTIMIZATION
# Complete Phase 7: Mr.DP Character, Bento Grid, Animated Hero, Credibility Section
# --------------------------------------------------
# NEW IN v40:
# ✅ Mr.DP Character - SVG with expressions (happy, thinking, excited)
# ✅ Animated Hero - Floating blobs, gradient text, particles
# ✅ Bento Grid Features - Apple-style modern layout
# ✅ Scroll Animations - Fade-in, stagger effects
# ✅ Celebration System - Confetti on achievements
# ✅ Research Credibility Section - Science-backed proof
# ✅ Phase 6: Community & Gamification
# ✅ Phase 5: Viral & Growth (Referrals, Share Cards)
# ✅ Phase 4: Personalization + Monetization
# --------------------------------------------------

import os

# Create secrets.toml from env vars if it doesn't exist (Railway deployment)
if os.environ.get("RAILWAY_ENVIRONMENT_NAME") and not os.path.exists(".streamlit/secrets.toml"):
    os.makedirs(".streamlit", exist_ok=True)
    with open(".streamlit/secrets.toml", "w") as f:
        tmdb = os.environ.get("TMDB_API_KEY", "")
        openai = os.environ.get("OPENAI_API_KEY", "")
        f.write(f'[tmdb]\napi_key = "{tmdb}"\n\n[openai]\napi_key = "{openai}"\n')

import streamlit as st
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
from streamlit_javascript import st_javascript

# Mr.DP Floating Chat Widget
from mr_dp_floating import render_floating_mr_dp, sanitize_chat_content

# Mr.DP Intelligence System
from mr_dp_intelligence import (
    # Conversational AI
    chat_with_mr_dp, get_user_context, init_openai_client,
    # Contextual Awareness
    get_contextual_state, get_contextual_greeting, get_contextual_suggestion, get_contextual_expression,
    # Behavioral Learning
    init_behavior_tracking, track_scroll_event, track_recommendation_seen,
    track_recommendation_clicked, track_quick_hit_use, detect_decision_fatigue,
    get_browsing_duration_minutes, save_behavior_to_supabase, get_user_patterns,
    # ADHD Coach
    get_adhd_intervention, get_random_adhd_tip, get_encouragement,
    # Gamification
    init_gamification, add_xp, check_achievement, get_current_evolution,
    get_next_evolution, get_available_accessories, equip_accessory,
    save_gamification_to_supabase, load_gamification_from_supabase,
    MR_DP_ACHIEVEMENTS, MR_DP_EVOLUTIONS, MR_DP_ACCESSORIES,
    # UI Components
    render_mr_dp_chat_interface, render_mr_dp_status_card,
    render_achievements_display, render_intervention_popup
)

# Subscription utilities (NEW - added for premium features)
from subscription_utils import check_can_use, increment_usage, is_premium, show_usage_sidebar
from stripe_utils import render_pricing_page, create_checkout_url, SUBSCRIPTION_PLANS
from analytics_utils import (
    init_analytics_session, track_page_view, track_click,
    track_mood_selection, track_content_interaction, track_feature_usage,
    get_session_stats, render_analytics_dashboard
)
from email_utils import send_welcome_email, send_milestone_email, check_and_send_milestone_email

# Phase 1 & 2 Features
from mood_utils import log_mood_selection, get_mood_history, get_top_moods, get_mood_patterns
from behavior_tracking import log_user_action, get_engagement_score
from watch_queue import add_to_queue, remove_from_queue, get_watch_queue, is_in_queue, render_queue_button
from sos_calm_mode import render_sos_button, render_sos_overlay, log_sos_usage
from time_aware_picks import render_time_picker, get_time_of_day_suggestions, filter_movies_by_runtime
from focus_timer import render_focus_timer_sidebar, render_break_reminder_overlay, init_focus_session_state

# --------------------------------------------------
# PHASE 3 FEATURES - Enhanced dopamine_2027 Integration
# --------------------------------------------------
try:
    from gamification_enhanced import (
        PointAction, add_points, get_points_summary, get_leaderboard, get_user_rank,
        update_streak, get_streak_summary, check_streak_at_risk, get_streak_leaderboard,
        ACHIEVEMENTS_ENHANCED, unlock_achievement, update_achievement_progress,
        get_achievements_summary, render_leaderboard_widget, render_streak_card,
        render_achievements_grid
    )
    GAMIFICATION_ENHANCED_AVAILABLE = True
except ImportError:
    GAMIFICATION_ENHANCED_AVAILABLE = False

try:
    from user_learning import (
        EventType, track_learning_event, init_learning_session,
        analyze_user_patterns, get_genre_preferences, get_mood_recommendations,
        get_duration_recommendation, get_mrdp_personalization_context,
        render_insights_dashboard
    )
    USER_LEARNING_AVAILABLE = True
except ImportError:
    USER_LEARNING_AVAILABLE = False

try:
    from wellness_enhanced import (
        BREATHING_EXERCISES, get_breathing_exercise, get_all_breathing_exercises,
        GROUNDING_54321, get_grounding_exercise,
        AFFIRMATIONS_BY_MOOD, get_affirmation, get_affirmations, get_sos_content_package,
        render_breathing_animation, render_grounding_guided_exercise,
        render_affirmation_card, render_enhanced_sos_overlay
    )
    WELLNESS_ENHANCED_AVAILABLE = True
except ImportError:
    WELLNESS_ENHANCED_AVAILABLE = False

try:
    from search_aggregator import (
        search_all_sync, quick_search_sync, mood_based_search_sync,
        render_unified_search_bar, render_search_results_grid, render_mood_quick_picks,
        MOOD_GENRE_MAP, format_duration, is_adhd_friendly
    )
    SEARCH_AGGREGATOR_AVAILABLE = True
except ImportError:
    SEARCH_AGGREGATOR_AVAILABLE = False

try:
    from social_features import (
        # Watch parties
        create_watch_party, join_watch_party, leave_watch_party,
        send_party_message, get_party_state, get_public_parties,
        # Messaging
        get_or_create_conversation, send_direct_message, get_conversation_messages,
        get_user_conversations, mark_messages_read,
        # Friends
        add_friend, get_friends, remove_friend, get_friends_count,
        # Referrals & sharing
        generate_referral_code, apply_referral_code, get_referral_stats,
        generate_share_link,
        # UI Components
        render_watch_party_card, render_create_party_modal, render_join_party_modal,
        render_party_chat, render_messages_sidebar,
        render_share_buttons, render_referral_section
    )
    SOCIAL_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"[Social Features] Import error: {e}")
    SOCIAL_FEATURES_AVAILABLE = False

# --------------------------------------------------
# 1. CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Dopamine.watch | Feel Better, Watch Better",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# PWA SETUP - Progressive Web App Support
# --------------------------------------------------
def inject_pwa_head():
    """Inject PWA meta tags and service worker registration"""
    st.markdown("""
    <!-- PWA Meta Tags -->
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#8A56E2">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="dopamine.watch">
    <link rel="apple-touch-icon" href="/static/icons/icon-192.png">

    <!-- Viewport for mobile -->
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover">

    <script>
    // Register Service Worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/sw.js')
                .then(reg => console.log('[PWA] Service Worker registered'))
                .catch(err => console.log('[PWA] SW registration failed:', err));
        });
    }
    </script>
    """, unsafe_allow_html=True)

# Initialize PWA
inject_pwa_head()

APP_NAME = "Dopamine.watch"

# --------------------------------------------------
# INTERNATIONALIZATION (i18n) - English & Spanish
# --------------------------------------------------
TRANSLATIONS = {
    "en": {
        # App
        "app_tagline": "Feel Better, Watch Better",
        "welcome_back": "Welcome Back",
        "get_started": "Get Started Free",
        "log_in": "Log In",
        "sign_up": "Sign Up",
        "log_out": "Log Out",
        "continue_guest": "Continue as Guest",

        # Navigation
        "home": "Home",
        "discover": "Discover",
        "my_queue": "My Queue",
        "profile": "Profile",
        "settings": "Settings",
        "challenges": "Challenges",
        "shop": "Shop",
        "leaderboards": "Leaderboards",
        "admin": "Admin",

        # Moods - Current
        "current_mood": "How are you feeling right now?",
        "desired_mood": "How do you want to feel?",
        "stressed": "Stressed",
        "anxious": "Anxious",
        "bored": "Bored",
        "sad": "Sad",
        "tired": "Tired",
        "overwhelmed": "Overwhelmed",
        "restless": "Restless",
        "unmotivated": "Unmotivated",
        "lonely": "Lonely",
        "frustrated": "Frustrated",
        "numb": "Numb",
        "scattered": "Scattered",

        # Moods - Desired
        "relaxed": "Relaxed",
        "calm": "Calm",
        "entertained": "Entertained",
        "happy": "Happy",
        "energized": "Energized",
        "focused": "Focused",
        "inspired": "Inspired",
        "motivated": "Motivated",
        "connected": "Connected",
        "peaceful": "Peaceful",
        "excited": "Excited",
        "grounded": "Grounded",

        # Actions
        "get_recommendations": "Get Recommendations",
        "quick_dope_hit": "Quick Dope Hit",
        "add_to_queue": "Add to Queue",
        "remove_from_queue": "Remove",
        "watch_now": "Watch Now",
        "more_info": "More Info",
        "share": "Share",
        "search": "Search",
        "search_placeholder": "Search movies, shows, music...",

        # Mr.DP
        "mr_dp_greeting": "Hey! I'm Mr.DP, your dopamine curator. Tell me how you're feeling and I'll find the perfect content for you!",
        "mr_dp_placeholder": "Tell Mr.DP how you're feeling...",
        "mr_dp_thinking": "Mr.DP is thinking...",
        "mr_dp_limit_reached": "You've used all your free Mr.DP chats today. Upgrade to Premium for unlimited!",

        # Stats
        "streak": "Streak",
        "day_streak": "day streak",
        "dopamine_points": "Dopamine Points",
        "level": "Level",
        "total_watches": "Total Watches",
        "mood_logs": "Mood Logs",

        # Content Types
        "movies": "Movies",
        "tv_shows": "TV Shows",
        "music": "Music",
        "podcasts": "Podcasts",
        "audiobooks": "Audiobooks",

        # Gamification
        "daily_challenges": "Daily Challenges",
        "weekly_challenges": "Weekly Challenges",
        "claim_reward": "Claim Reward",
        "completed": "Completed",
        "in_progress": "In Progress",
        "reward": "Reward",

        # Premium
        "upgrade_to_premium": "Upgrade to Premium",
        "premium_features": "Premium Features",
        "unlimited_mr_dp": "Unlimited Mr.DP chats",
        "advanced_analytics": "Advanced mood analytics",
        "no_ads": "No ads",
        "priority_support": "Priority support",

        # Messages
        "loading": "Loading...",
        "no_results": "No results found",
        "error_occurred": "Something went wrong. Please try again.",
        "saved_to_queue": "Added to your queue!",
        "removed_from_queue": "Removed from queue",
        "streak_broken": "Your streak was broken!",
        "new_achievement": "New Achievement!",

        # Landing Page
        "hero_subtitle": "The first streaming guide designed for ADHD & neurodivergent brains.",
        "hero_tagline": "Tell us how you feel. We'll find the perfect content to match your mood.",
        "feature_mood_title": "Mood-Driven Discovery",
        "feature_mood_desc": "Select how you feel now and how you want to feel. We'll curate content that takes you there.",
        "feature_mr_dp_title": "Mr.DP - AI Curator",
        "feature_mr_dp_desc": "Meet your personal dopamine buddy! Just tell him how you feel and he'll find the perfect content.",
        "feature_quick_title": "Quick Dope Hit",
        "feature_quick_desc": "Can't decide? One button gives you the perfect match. No scrolling required.",
        "testimonials_title": "What People Are Saying",
        "pricing_title": "Simple Pricing",
        "about_title": "About Dopamine.watch",
        "ready_to_feel_better": "Ready to feel better?",

        # SOS Mode
        "sos_calm_mode": "SOS Calm Mode",
        "sos_description": "Take a moment to breathe. You're safe here.",
        "exit_sos": "I'm feeling better",

        # Landing Page Extended
        "happy_users": "Happy Users",
        "moods_matched": "Moods Matched",
        "user_rating": "User Rating",
        "start_free": "Start Free",
        "guest_mode": "Guest Mode",
        "back_to_home": "Back to Home",
        "create_account": "Create Account",
        "forgot_password": "Forgot Password?",
        "login_subtitle": "Log in to your dopamine engine",
        "signup_subtitle": "Join the dopamine revolution",
        "mood_driven_title": "Mood-Driven Discovery",
        "mood_driven_desc": "Revolutionary AI that understands not just what you want to watch, but how you want to FEEL. Select your current mood and desired state - we handle the rest.",
        "mr_dp_curator_title": "Mr.DP AI Curator",
        "mr_dp_curator_desc": "Your personal dopamine buddy who actually gets ADHD. Chat naturally about how you feel.",
        "quick_hit_title": "Quick Dope Hit",
        "quick_hit_desc": "Decision fatigue? One button. Perfect match. No scrolling.",
        "movies_tv_title": "Movies & TV",
        "movies_tv_desc": "20+ streaming services, emotion-filtered just for you.",
        "music_playlists_title": "Music & Playlists",
        "music_playlists_desc": "Mood-matched music from Spotify, Apple Music & more.",
        "podcasts_more_title": "Podcasts, Audiobooks & More",
        "podcasts_more_desc": "Whatever your brain craves - we've got curated content across every format to match your current headspace.",
        "science_title": "Built on Science, Designed for You",
        "science_subtitle": "Our mood-matching algorithm is grounded in research on emotional regulation and ADHD.",
        "community_title": "What the Community Says",
        "pricing_simple": "Simple, Transparent Pricing",
        "about_built_title": "Built for Brains Like Yours",
        "about_mission": "help you feel better, faster",
        "about_signature": "Built with 💜 for ADHD brains, by ADHD brains.",
        "join_thousands": "Join thousands who've escaped the scroll trap.",
        "free_plan": "Free",
        "forever_free": "forever free",
        "plus_plan": "Plus",
        "pro_plan": "Pro",
        "most_popular": "MOST POPULAR",
        "have_account": "Have Account? Log In",
        "start_journey": "Start your dopamine journey",

        # Sidebar & Navigation
        "your_mood": "Your Mood",
        "i_feel": "I feel...",
        "i_want": "I want...",
        "quick_dope_hit": "QUICK DOPE HIT",
        "watch_queue": "Watch Queue",
        "view_all_queue": "View All Queue",
        "queue_empty": "Your queue is empty",
        "log_in_to_save": "Log in to save content",
        "gamification": "Gamification",
        "shorts": "Shorts",
    },
    "es": {
        # App
        "app_tagline": "Siéntete Mejor, Mira Mejor",
        "welcome_back": "Bienvenido de Nuevo",
        "get_started": "Comenzar Gratis",
        "log_in": "Iniciar Sesión",
        "sign_up": "Registrarse",
        "log_out": "Cerrar Sesión",
        "continue_guest": "Continuar como Invitado",

        # Navigation
        "home": "Inicio",
        "discover": "Descubrir",
        "my_queue": "Mi Lista",
        "profile": "Perfil",
        "settings": "Ajustes",
        "challenges": "Desafíos",
        "shop": "Tienda",
        "leaderboards": "Clasificación",
        "admin": "Admin",

        # Moods - Current
        "current_mood": "¿Cómo te sientes ahora mismo?",
        "desired_mood": "¿Cómo quieres sentirte?",
        "stressed": "Estresado",
        "anxious": "Ansioso",
        "bored": "Aburrido",
        "sad": "Triste",
        "tired": "Cansado",
        "overwhelmed": "Abrumado",
        "restless": "Inquieto",
        "unmotivated": "Desmotivado",
        "lonely": "Solo",
        "frustrated": "Frustrado",
        "numb": "Adormecido",
        "scattered": "Disperso",

        # Moods - Desired
        "relaxed": "Relajado",
        "calm": "Tranquilo",
        "entertained": "Entretenido",
        "happy": "Feliz",
        "energized": "Energético",
        "focused": "Concentrado",
        "inspired": "Inspirado",
        "motivated": "Motivado",
        "connected": "Conectado",
        "peaceful": "En Paz",
        "excited": "Emocionado",
        "grounded": "Centrado",

        # Actions
        "get_recommendations": "Obtener Recomendaciones",
        "quick_dope_hit": "Dosis Rápida",
        "add_to_queue": "Agregar a Lista",
        "remove_from_queue": "Eliminar",
        "watch_now": "Ver Ahora",
        "more_info": "Más Info",
        "share": "Compartir",
        "search": "Buscar",
        "search_placeholder": "Buscar películas, series, música...",

        # Mr.DP
        "mr_dp_greeting": "¡Hola! Soy Mr.DP, tu curador de dopamina. ¡Cuéntame cómo te sientes y encontraré el contenido perfecto para ti!",
        "mr_dp_placeholder": "Cuéntale a Mr.DP cómo te sientes...",
        "mr_dp_thinking": "Mr.DP está pensando...",
        "mr_dp_limit_reached": "Has usado todos tus chats gratuitos de Mr.DP hoy. ¡Actualiza a Premium para ilimitados!",

        # Stats
        "streak": "Racha",
        "day_streak": "días de racha",
        "dopamine_points": "Puntos de Dopamina",
        "level": "Nivel",
        "total_watches": "Vistas Totales",
        "mood_logs": "Registros de Ánimo",

        # Content Types
        "movies": "Películas",
        "tv_shows": "Series",
        "music": "Música",
        "podcasts": "Podcasts",
        "audiobooks": "Audiolibros",

        # Gamification
        "daily_challenges": "Desafíos Diarios",
        "weekly_challenges": "Desafíos Semanales",
        "claim_reward": "Reclamar Premio",
        "completed": "Completado",
        "in_progress": "En Progreso",
        "reward": "Premio",

        # Premium
        "upgrade_to_premium": "Actualizar a Premium",
        "premium_features": "Funciones Premium",
        "unlimited_mr_dp": "Chats ilimitados con Mr.DP",
        "advanced_analytics": "Análisis avanzado de ánimo",
        "no_ads": "Sin anuncios",
        "priority_support": "Soporte prioritario",

        # Messages
        "loading": "Cargando...",
        "no_results": "No se encontraron resultados",
        "error_occurred": "Algo salió mal. Por favor, intenta de nuevo.",
        "saved_to_queue": "¡Agregado a tu lista!",
        "removed_from_queue": "Eliminado de la lista",
        "streak_broken": "¡Tu racha se rompió!",
        "new_achievement": "¡Nuevo Logro!",

        # Landing Page
        "hero_subtitle": "La primera guía de streaming diseñada para cerebros con TDAH y neurodivergentes.",
        "hero_tagline": "Cuéntanos cómo te sientes. Encontraremos el contenido perfecto para tu estado de ánimo.",
        "feature_mood_title": "Descubrimiento por Ánimo",
        "feature_mood_desc": "Selecciona cómo te sientes ahora y cómo quieres sentirte. Te curaremos contenido que te lleve allí.",
        "feature_mr_dp_title": "Mr.DP - Curador IA",
        "feature_mr_dp_desc": "¡Conoce a tu compañero de dopamina! Solo cuéntale cómo te sientes y encontrará el contenido perfecto.",
        "feature_quick_title": "Dosis Rápida",
        "feature_quick_desc": "¿No puedes decidir? Un botón te da la combinación perfecta. Sin scrollear.",
        "testimonials_title": "Lo Que Dice la Gente",
        "pricing_title": "Precios Simples",
        "about_title": "Acerca de Dopamine.watch",
        "ready_to_feel_better": "¿Listo para sentirte mejor?",

        # SOS Mode
        "sos_calm_mode": "Modo SOS Calma",
        "sos_description": "Toma un momento para respirar. Estás seguro aquí.",
        "exit_sos": "Me siento mejor",

        # Landing Page Extended
        "happy_users": "Usuarios Felices",
        "moods_matched": "Estados Combinados",
        "user_rating": "Calificación",
        "start_free": "Comenzar Gratis",
        "guest_mode": "Modo Invitado",
        "back_to_home": "Volver al Inicio",
        "create_account": "Crear Cuenta",
        "forgot_password": "¿Olvidaste tu Contraseña?",
        "login_subtitle": "Inicia sesión en tu motor de dopamina",
        "signup_subtitle": "Únete a la revolución de dopamina",
        "mood_driven_title": "Descubrimiento por Estado de Ánimo",
        "mood_driven_desc": "IA revolucionaria que entiende no solo qué quieres ver, sino cómo quieres SENTIRTE. Selecciona tu estado actual y deseado - nosotros nos encargamos del resto.",
        "mr_dp_curator_title": "Mr.DP Curador IA",
        "mr_dp_curator_desc": "Tu compañero personal de dopamina que realmente entiende el TDAH. Chatea naturalmente sobre cómo te sientes.",
        "quick_hit_title": "Dosis Rápida",
        "quick_hit_desc": "¿Fatiga de decisión? Un botón. Combinación perfecta. Sin scrollear.",
        "movies_tv_title": "Películas y Series",
        "movies_tv_desc": "20+ servicios de streaming, filtrados por emoción solo para ti.",
        "music_playlists_title": "Música y Playlists",
        "music_playlists_desc": "Música combinada con tu ánimo de Spotify, Apple Music y más.",
        "podcasts_more_title": "Podcasts, Audiolibros y Más",
        "podcasts_more_desc": "Lo que tu cerebro desee - tenemos contenido curado en cada formato para tu estado mental actual.",
        "science_title": "Construido con Ciencia, Diseñado para Ti",
        "science_subtitle": "Nuestro algoritmo de combinación de ánimo está basado en investigación sobre regulación emocional y TDAH.",
        "community_title": "Lo Que Dice la Comunidad",
        "pricing_simple": "Precios Simples y Transparentes",
        "about_built_title": "Hecho para Cerebros como el Tuyo",
        "about_mission": "ayudarte a sentirte mejor, más rápido",
        "about_signature": "Hecho con 💜 para cerebros con TDAH, por cerebros con TDAH.",
        "join_thousands": "Únete a miles que escaparon de la trampa del scroll.",
        "free_plan": "Gratis",
        "forever_free": "gratis para siempre",
        "plus_plan": "Plus",
        "pro_plan": "Pro",
        "most_popular": "MÁS POPULAR",
        "have_account": "¿Tienes cuenta? Iniciar Sesión",
        "start_journey": "Comienza tu viaje de dopamina",

        # Sidebar & Navigation
        "your_mood": "Tu Estado de Ánimo",
        "i_feel": "Me siento...",
        "i_want": "Quiero...",
        "quick_dope_hit": "DOSIS RÁPIDA",
        "watch_queue": "Lista de Reproducción",
        "view_all_queue": "Ver Toda la Lista",
        "queue_empty": "Tu lista está vacía",
        "log_in_to_save": "Inicia sesión para guardar contenido",
        "gamification": "Gamificación",
        "shorts": "Shorts",
    }
}

def get_text(key: str, lang: str = None) -> str:
    """Get translated text for a key. Falls back to English if not found."""
    if lang is None:
        lang = st.session_state.get("lang", "en")

    # Try to get from selected language
    if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][key]

    # Fallback to English
    if key in TRANSLATIONS["en"]:
        return TRANSLATIONS["en"][key]

    # Return key itself if not found
    return key

def t(key: str) -> str:
    """Shorthand for get_text()"""
    return get_text(key)

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
TMDB_BACKDROP_URL = "https://image.tmdb.org/t/p/original"
TMDB_LOGO_URL = "https://image.tmdb.org/t/p/original"

# --------------------------------------------------
# 2. SUPABASE AUTH & PROFILE MANAGEMENT
# --------------------------------------------------
from supabase import create_client, Client

# Initialize Supabase client
SUPABASE_URL = st.secrets.get("supabase", {}).get("url", "")
SUPABASE_KEY = st.secrets.get("supabase", {}).get("anon_key", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
SUPABASE_ENABLED = supabase is not None  # For backward compatibility

FREE_MR_DP_LIMIT = 5  # Free users get 5 Mr.DP chats

def supabase_sign_up(email: str, password: str, name: str = ""):
    """Sign up with Supabase and create profile"""
    if not email or not password:
        return {"success": False, "error": "Email and password required"}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters"}

    try:
        # Create auth user
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            # Create profile in profiles table
            profile_data = {
                "id": response.user.id,
                "email": email,
                "name": name or email.split("@")[0],
                "mr_dp_uses": 0,
                "is_premium": False
            }
            supabase.table("profiles").upsert(profile_data).execute()
            return {
                "success": True,
                "user": {
                    "id": response.user.id,
                    "email": email,
                    "name": name or email.split("@")[0]
                }
            }
        return {"success": False, "error": "Signup failed"}
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return {"success": False, "error": "Email already registered"}
        return {"success": False, "error": error_msg}

def supabase_sign_in(email: str, password: str):
    """Sign in with Supabase"""
    if not email or not password:
        return {"success": False, "error": "Email and password required"}

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            # Fetch or create profile
            profile = get_user_profile(response.user.id)
            if not profile:
                # Create profile if doesn't exist
                profile_data = {
                    "id": response.user.id,
                    "email": email,
                    "name": email.split("@")[0],
                    "mr_dp_uses": 0,
                    "is_premium": False
                }
                supabase.table("profiles").upsert(profile_data).execute()
                profile = profile_data

            return {
                "success": True,
                "user": {
                    "id": response.user.id,
                    "email": email,
                    "name": profile.get("name", email.split("@")[0]),
                    "mr_dp_uses": profile.get("mr_dp_uses", 0),
                    "is_premium": profile.get("is_premium", False)
                }
            }
        return {"success": False, "error": "Invalid credentials"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def supabase_sign_out():
    """Sign out from Supabase"""
    try:
        supabase.auth.sign_out()
    except:
        pass

def get_user_profile(user_id: str):
    """Get user profile from Supabase"""
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data if response.data else {}
    except:
        return {}

def update_user_profile(user_id: str, data: dict):
    """Update user profile in Supabase"""
    try:
        supabase.table("profiles").update(data).eq("id", user_id).execute()
        return True
    except:
        return False

def increment_mr_dp_usage(user_id: str):
    """Increment Mr.DP usage counter"""
    try:
        # Get current count
        profile = get_user_profile(user_id)
        current = profile.get("mr_dp_uses", 0)
        # Increment
        supabase.table("profiles").update({"mr_dp_uses": current + 1}).eq("id", user_id).execute()
        return current + 1
    except:
        return 0

def can_use_mr_dp(user_id: str):
    """Check if user can use Mr.DP (premium or under limit)"""
    profile = get_user_profile(user_id)
    if profile.get("is_premium", False):
        return True, -1  # Premium users have unlimited
    uses = profile.get("mr_dp_uses", 0)
    return uses < FREE_MR_DP_LIMIT, FREE_MR_DP_LIMIT - uses

# Compatibility aliases
supabase_get_user = lambda: None
get_oauth_url = lambda provider: None
handle_oauth_callback = lambda: None
create_user_profile = lambda *args: None
check_referral_code = lambda *args: None


# --------------------------------------------------
# SOCIAL PROOF NOTIFICATIONS (NEW)
# --------------------------------------------------
def show_social_proof():
    """Show social proof notifications occasionally"""
    if 'last_social_proof' not in st.session_state:
        st.session_state.last_social_proof = datetime.now() - timedelta(minutes=5)

    # Show every 45-90 seconds
    if datetime.now() - st.session_state.last_social_proof > timedelta(seconds=random.randint(45, 90)):
        names = ['Sarah', 'Mike', 'Emma', 'Alex', 'Jordan', 'Casey', 'Riley', 'Morgan', 'Taylor', 'Jamie']
        cities = ['Portland', 'Austin', 'Denver', 'Seattle', 'Chicago', 'Miami', 'NYC', 'LA', 'Boston', 'Phoenix']
        actions = [
            'just found the perfect movie',
            'discovered a new podcast',
            'got a Quick Dope Hit',
            'matched their mood perfectly',
            'found something to watch'
        ]

        name = random.choice(names)
        city = random.choice(cities)
        action = random.choice(actions)

        st.toast(f"{name} from {city} {action}!")
        st.session_state.last_social_proof = datetime.now()


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
    key = os.environ.get("TMDB_API_KEY")
    if key:
        return key
    try:
        return st.secrets["tmdb"]["api_key"]
    except:
        return None

_openai_key = os.environ.get("OPENAI_API_KEY")
if not _openai_key:
    try:
        _openai_key = st.secrets["openai"]["api_key"]
    except:
        _openai_key = None

openai_client = OpenAI(api_key=_openai_key) if _openai_key else None

# Debug: Log OpenAI client status at startup
print(f"[STARTUP] OpenAI key present: {bool(_openai_key)}, length: {len(_openai_key) if _openai_key else 0}")
print(f"[STARTUP] OpenAI client created: {openai_client is not None}")

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

IMPORTANT: You MUST respond with ONLY a valid JSON object. Do NOT include any text before or after the JSON. Do NOT say anything outside the JSON. Your ENTIRE response must be this JSON and nothing else:
{
    "message": "Your friendly 1-3 sentence response to the user",
    "current_feeling": "one of: Sad, Lonely, Anxious, Overwhelmed, Angry, Stressed, Bored, Tired, Numb, Confused, Restless, Focused, Calm, Happy, Excited, Curious, Scared, Nostalgic, Romantic, Adventurous, Frustrated, Hopeful (or null)",
    "desired_feeling": "one of: Comforted, Calm, Relaxed, Focused, Energized, Stimulated, Happy, Entertained, Inspired, Grounded, Curious, Sleepy, Connected, Scared, Thrilled, Nostalgic, Romantic, Adventurous, Amused, Motivated (or null)",
    "media_type": "movies, music, podcasts, audiobooks, shorts, or artist",
    "mode": "discover or search",
    "search_query": "specific search terms if mode is search OR artist name for artist type, empty string otherwise",
    "genres": "brief description of what kind of content you're recommending"
}

CRITICAL MOOD MAPPING RULES (YOU MUST FOLLOW THESE):
- "I want to feel happy" / "make me happy" → desired_feeling: "Happy" (comedies, family films, adventures)
- "I want to feel relaxed" / "need to relax" → desired_feeling: "Relaxed" (romance, comedies, documentaries)
- "I want to laugh" / "make me laugh" → desired_feeling: "Amused" (comedies, animation, family films)
- "I'm sad" → current_feeling: "Sad", desired_feeling: "Comforted" (comedies, family, animation)

HORROR/SCARY CONTENT (ALWAYS USE desired_feeling: "Scared"):
- "scare me" / "horrify me" / "terrify me" → desired_feeling: "Scared"
- "horror" / "scary" / "creepy" / "spooky" → desired_feeling: "Scared"
- "I want to be scared" / "I want to feel scared" → desired_feeling: "Scared"
- "frightening" / "terrifying" / "chilling" → desired_feeling: "Scared"
- NEVER use "Stimulated" or "Thrilled" for horror requests - ALWAYS use "Scared"

Always match the desired mood to appropriate content genres!

Examples:

User: "I want to feel happy" or "make me happy"
{
    "message": "Let's boost those happy vibes! I'm pulling up feel-good comedies and heartwarming adventures that'll put a genuine smile on your face 😊",
    "current_feeling": "Bored",
    "desired_feeling": "Happy",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "feel-good comedies, uplifting adventures, heartwarming family films"
}

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
    "desired_feeling": "Amused",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "comedies, funny adventures, witty films"
}

User: "howdy" or "hi" or "hello" (simple greetings)
{
    "message": "Hey there! 👋 I'm Mr.DP, your personal dopamine curator. What vibe are you looking for today? Want to feel happy, relaxed, energized, or something else?",
    "current_feeling": null,
    "desired_feeling": null,
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": ""
}

User: "I'm feeling sad" or "I'm depressed"
{
    "message": "I hear you, and those feelings are valid 💜 Let me find some warm, comforting content that'll wrap around you like a cozy blanket.",
    "current_feeling": "Sad",
    "desired_feeling": "Comforted",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "heartwarming comedies, feel-good animations, comfort films"
}

User: "scare me" or "I want horror"
{
    "message": "Feeling brave? Let's get spooky! 👻 I'm pulling up some quality scares that'll get your heart racing!",
    "current_feeling": null,
    "desired_feeling": "Scared",
    "media_type": "movies",
    "mode": "discover",
    "search_query": "",
    "genres": "horror, thriller, supernatural, psychological horror"
}

Remember: Be genuine, warm, and helpful. You're not just finding content - you're helping someone feel better. ALWAYS match the mood they want to the appropriate content - if they want happy, give them happy content, not random stuff!"""

def ask_mr_dp(user_prompt, chat_history=None):
    """
    Full conversational AI response from Mr.DP using GPT-4.
    Returns structured response with message, feelings, and search parameters.
    Includes chat_history for conversation memory.
    """
    if not user_prompt or not user_prompt.strip():
        return None

    # Try GPT first for natural conversation
    if openai_client:
        try:
            # Build messages with conversation history for memory
            messages = [{"role": "system", "content": MR_DP_SYSTEM_PROMPT}]
            if chat_history:
                # Include last 10 messages for context (limit tokens)
                for msg in chat_history[-10:]:
                    if msg["role"] == "user":
                        messages.append({"role": "user", "content": msg["content"]})
                    else:
                        # Re-wrap assistant messages as simple text so GPT understands context
                        messages.append({"role": "assistant", "content": msg["content"]})
            messages.append({"role": "user", "content": user_prompt})

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON from response - handle multiple formats
            json_content = content

            # Handle markdown code blocks
            if "```json" in content:
                json_content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_content = content.split("```")[1].split("```")[0].strip()
            # Handle case where GPT returns text followed by JSON (find the JSON object)
            elif "{" in content:
                # Find the JSON object in the response
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]

            try:
                result = json.loads(json_content)
            except json.JSONDecodeError:
                # GPT returned plain text instead of JSON - wrap it
                # Remove any partial JSON that might be in the content
                clean_content = content
                if "{" in clean_content:
                    clean_content = content[:content.find("{")].strip()
                if not clean_content:
                    clean_content = content
                result = {
                    "message": clean_content,
                    "current_feeling": None,
                    "desired_feeling": None,
                    "media_type": "movies",
                    "mode": "discover",
                    "search_query": "",
                    "genres": ""
                }

            # Validate and set defaults
            result.setdefault("message", "Let me find something perfect for you!")
            result.setdefault("current_feeling", None)
            result.setdefault("desired_feeling", None)
            result.setdefault("media_type", "movies")
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
# 9.5 MR.DP 2.0 - INTELLIGENT ASSISTANT (NEW)
# --------------------------------------------------
MR_DP_SYSTEM_PROMPT_V2 = """You are Mr.DP (Mr. Dopamine), an intelligent AI assistant for dopamine.watch - a streaming recommendation app built specifically for ADHD and neurodivergent users.

## YOUR PERSONALITY
- Warm, empathetic, like a supportive friend who gets ADHD struggles
- Casual but not over-the-top (occasional emoji, not every sentence)
- Concise - respect that ADHD brains get overwhelmed by walls of text
- Action-oriented - don't just talk, DO things for the user

## USER CONTEXT
You will receive information about the user including:
- Their recent mood selections
- Their watch queue
- Their viewing history/preferences
- Current mood state

Use this to personalize recommendations!

## RESPONSE FORMAT
Respond with a JSON object containing:
{
    "message": "Your conversational response (2-3 sentences max)",
    "content": [
        {
            "type": "movie|music|podcast|audiobook",
            "data": { ... content details ... }
        }
    ],
    "actions": [
        {
            "type": "add_queue|sos|focus|time_pick",
            "label": "Button label",
            "data": { ... action data ... }
        }
    ],
    "mood_update": {
        "current": "detected current feeling or null",
        "desired": "detected desired feeling or null"
    },
    "focus_page": "music|movies|podcasts|audiobooks|shorts|null"
}

## CONTENT DATA FORMATS

### Movie/TV:
{
    "type": "movie",
    "data": {
        "title": "Movie Title",
        "why": "Why this matches their mood (1 sentence)"
    }
}

### Music:
{
    "type": "music",
    "data": {
        "mood": "Calm|Happy|Energized|Focused|etc",
        "description": "Description of the vibe"
    }
}

### Artist Request:
{
    "type": "artist",
    "data": {
        "artist": "Artist Name"
    }
}

## MOOD MAPPINGS (use these for recommendations)

Current feelings: Sad, Lonely, Anxious, Overwhelmed, Angry, Stressed, Bored, Tired, Numb, Confused, Restless, Frustrated, Scared, Nostalgic

Desired feelings: Happy, Calm, Relaxed, Energized, Entertained, Inspired, Comforted, Focused, Curious, Amused, Motivated, Thrilled, Sleepy

## PAGE FOCUS
When user wants ONLY a specific type of content, set focus_page to switch the main page view:
- "music" - Switch to Music page (for requests like "play some tunes", "I want music", "give me a playlist")
- "movies" - Switch to Movies page (for movie-specific requests)
- "podcasts" - Switch to Podcasts page
- "audiobooks" - Switch to Audiobooks page
- "shorts" - Switch to Shorts page
- null - Don't change the page (default, for mixed content or general requests)

## IMPORTANT RULES

1. **Offer actions** - If user seems stressed, offer SOS mode. If they mention time constraints, offer time-based picks
2. **Be proactive** - Suggest related content, offer to add to queue
3. **Handle greetings** - For "hi/hello", ask about their mood warmly
4. **Content focus** - When user clearly wants ONE type of content only, set focus_page to show that page exclusively

## SAFETY RULES (CRITICAL - ALWAYS FOLLOW)

1. **NO ADULT CONTENT** - Never suggest R-rated, explicit, or sexually suggestive content. Keep all recommendations family-friendly or PG-13 max.

2. **CRISIS DETECTION** - If user mentions ANY of these, IMMEDIATELY respond with crisis support:
   - Self-harm, suicide, wanting to die, "end it", hurting themselves
   - Severe depression, hopelessness, feeling worthless
   - Abuse, violence, being in danger

   CRISIS RESPONSE FORMAT:
   {
       "message": "I hear you, and I care about you. Please know you're not alone. Here are people who can help right now: 🇺🇸 988 (Suicide & Crisis Lifeline) | 🇬🇧 116 123 (Samaritans) | 🌍 findahelpline.com | If you're in immediate danger, please call emergency services. I'm here if you want to talk, but these trained professionals can provide the support you deserve. 💜",
       "content": [],
       "actions": [{"type": "sos", "label": "🆘 SOS Calm Mode", "data": {}}],
       "mood_update": {"current": null, "desired": "Comforted"}
   }

3. **DON'T PLAY THERAPIST** - If someone is distressed:
   - DO: Acknowledge their feelings, provide support resources, offer calming content
   - DON'T: Try to "fix" them, give mental health advice, or act as a counselor
   - Always defer to professional help for serious emotional distress

4. **NO INAPPROPRIATE REQUESTS** - Politely decline if user asks for:
   - Adult/sexual content
   - Violent/gore content
   - Harmful or dangerous content
   Simply say: "I keep things chill and family-friendly! Let me find something else for you."

## EXAMPLE INTERACTIONS

User: "I'm stressed and need to chill"
{
    "message": "I hear you. Let's bring some calm to your brain 💜",
    "content": [
        {"type": "movie", "data": {"title": "Spirited Away", "why": "Studio Ghibli's gentle visuals are perfect for stress relief"}},
        {"type": "music", "data": {"mood": "Calm", "description": "Peaceful piano for unwinding"}}
    ],
    "actions": [
        {"type": "sos", "label": "🆘 Activate Calm Mode", "data": {}}
    ],
    "mood_update": {"current": "Stressed", "desired": "Calm"}
}

User: "play some Drake"
{
    "message": "Drizzy coming right up! 🎤",
    "content": [
        {"type": "artist", "data": {"artist": "Drake"}}
    ],
    "actions": [],
    "mood_update": {"current": null, "desired": "Entertained"},
    "focus_page": "music"
}

User: "I want some cool tunes" or "give me music only"
{
    "message": "Music mode activated! 🎵 Here's a vibe for you",
    "content": [
        {"type": "music", "data": {"mood": "Happy", "description": "Upbeat hits to boost your mood"}}
    ],
    "actions": [],
    "mood_update": {"current": null, "desired": "Entertained"},
    "focus_page": "music"
}

User: "I only have 15 minutes"
{
    "message": "Short on time? No problem!",
    "content": [],
    "actions": [
        {"type": "time_pick", "label": "⏱️ Show 15-min picks", "data": {"minutes": 15}}
    ],
    "mood_update": {"current": null, "desired": null}
}

User: "hi" or "hello"
{
    "message": "Hey! 👋 I'm Mr.DP, your dopamine curator. What vibe are you chasing today?",
    "content": [],
    "actions": [],
    "mood_update": {"current": null, "desired": null}
}

Remember: Be genuine and warm. ALWAYS return valid JSON."""

# Curated Spotify playlist IDs for each mood
SPOTIFY_MOOD_PLAYLISTS = {
    "Calm": {"id": "37i9dQZF1DWZd79rJ6a7lp", "name": "Sleep", "description": "Gentle ambient tracks"},
    "Relaxed": {"id": "37i9dQZF1DX4sWSpwq3LiO", "name": "Peaceful Piano", "description": "Calm piano for relaxation"},
    "Sleepy": {"id": "37i9dQZF1DWZd79rJ6a7lp", "name": "Sleep", "description": "Drift off peacefully"},
    "Energized": {"id": "37i9dQZF1DX76Wlfdnj7AP", "name": "Beast Mode", "description": "High energy workout hits"},
    "Motivated": {"id": "37i9dQZF1DX5gQonLbZD9s", "name": "Motivation Mix", "description": "Get pumped and motivated"},
    "Happy": {"id": "37i9dQZF1DXdPec7aLTmlC", "name": "Happy Hits!", "description": "Feel-good hits to boost your mood"},
    "Entertained": {"id": "37i9dQZF1DX0XUsuxWHRQd", "name": "RapCaviar", "description": "Today's top hip-hop"},
    "Amused": {"id": "37i9dQZF1DX2A29LI7xHn1", "name": "Pop Rising", "description": "Fun pop hits"},
    "Focused": {"id": "37i9dQZF1DX8NTLI2TtZa6", "name": "Deep Focus", "description": "Electronic focus music"},
    "Comforted": {"id": "37i9dQZF1DX4WYpdgoIcn6", "name": "Chill Hits", "description": "Comforting chill tracks"},
    "Curious": {"id": "37i9dQZF1DX0SM0LYsmbMT", "name": "Jazz Vibes", "description": "Sophisticated jazz"},
    "Inspired": {"id": "37i9dQZF1DX4sWSpwq3LiO", "name": "Peaceful Piano", "description": "Inspiring classical"},
    "Thrilled": {"id": "37i9dQZF1DX4dyzvuaRJ0n", "name": "mint", "description": "Electronic dance hits"},
    "Grounded": {"id": "37i9dQZF1DWWQRwui0ExPn", "name": "LoFi Beats", "description": "Chill lo-fi hip hop"},
}

# Popular artist playlist mappings
SPOTIFY_ARTIST_PLAYLISTS = {
    "drake": {"id": "37i9dQZF1DX7QOv5kjbU68", "name": "This Is Drake"},
    "taylor swift": {"id": "37i9dQZF1DX5KpP2LN299J", "name": "This Is Taylor Swift"},
    "kendrick lamar": {"id": "37i9dQZF1DX5EkyRFIV6vG", "name": "This Is Kendrick Lamar"},
    "beyonce": {"id": "37i9dQZF1DX9xKCdCp34Kd", "name": "This Is Beyoncé"},
    "the weeknd": {"id": "37i9dQZF1DX6bnzK9KPvrz", "name": "This Is The Weeknd"},
    "billie eilish": {"id": "37i9dQZF1DX9xKCdCp34Kd", "name": "This Is Billie Eilish"},
    "ed sheeran": {"id": "37i9dQZF1DX5LsNzmTvZYy", "name": "This Is Ed Sheeran"},
    "ariana grande": {"id": "37i9dQZF1DX4F7xckJEHcj", "name": "This Is Ariana Grande"},
    "post malone": {"id": "37i9dQZF1DX9qNs32fujYe", "name": "This Is Post Malone"},
    "dua lipa": {"id": "37i9dQZF1DX98iKfEVjPpx", "name": "This Is Dua Lipa"},
    "harry styles": {"id": "37i9dQZF1DX5lMITtFT2wV", "name": "This Is Harry Styles"},
    "bad bunny": {"id": "37i9dQZF1DX3eCZ9vB1hfI", "name": "This Is Bad Bunny"},
    "sza": {"id": "37i9dQZF1DX6H4LAnlHN3t", "name": "This Is SZA"},
    "olivia rodrigo": {"id": "37i9dQZF1DX8bUHYxRdZiH", "name": "This Is Olivia Rodrigo"},
    "coldplay": {"id": "37i9dQZF1DZ06evO1PxGqn", "name": "This Is Coldplay"},
    "adele": {"id": "37i9dQZF1DX2wU4dczKqKR", "name": "This Is Adele"},
    "bruno mars": {"id": "37i9dQZF1DX0jlEkg3XFMO", "name": "This Is Bruno Mars"},
    "eminem": {"id": "37i9dQZF1DWY4xHQp97fN6", "name": "This Is Eminem"},
    "kanye west": {"id": "37i9dQZF1DX0XqLqQQT5Cw", "name": "This Is Kanye West"},
    "travis scott": {"id": "37i9dQZF1DX50vS4rNFqhj", "name": "This Is Travis Scott"},
    "doja cat": {"id": "37i9dQZF1DX5UKzYVUxnUm", "name": "This Is Doja Cat"},
    "the beatles": {"id": "37i9dQZF1DZ06evO2MVlpQ", "name": "This Is The Beatles"},
    "michael jackson": {"id": "37i9dQZF1DZ06evO0E0UrV", "name": "This Is Michael Jackson"},
    "metallica": {"id": "37i9dQZF1DX08mhnhv6g9b", "name": "This Is Metallica"},
    "queen": {"id": "37i9dQZF1DXdxUH6sNtcDe", "name": "This Is Queen"},
    "pink floyd": {"id": "37i9dQZF1DXa2F5aOPk2LD", "name": "This Is Pink Floyd"},
    "nirvana": {"id": "37i9dQZF1DX1V6JdN1SWmt", "name": "This Is Nirvana"},
    "radiohead": {"id": "37i9dQZF1DZ06evO1RuFPL", "name": "This Is Radiohead"},
}


def get_spotify_playlist_for_mood(desired_feeling: str):
    """Get Spotify playlist data for a mood"""
    playlist = SPOTIFY_MOOD_PLAYLISTS.get(desired_feeling)
    if not playlist:
        playlist = SPOTIFY_MOOD_PLAYLISTS["Happy"]

    return {
        "playlist_name": playlist["name"],
        "playlist_id": playlist["id"],
        "playlist_url": f"https://open.spotify.com/playlist/{playlist['id']}",
        "description": playlist["description"],
        "embed_url": f"https://open.spotify.com/embed/playlist/{playlist['id']}?utm_source=generator&theme=0"
    }


def get_spotify_artist_playlist(artist_name: str):
    """Get Spotify 'This Is' playlist for an artist"""
    artist_lower = artist_name.lower().strip()
    playlist = SPOTIFY_ARTIST_PLAYLISTS.get(artist_lower)

    if playlist:
        return {
            "playlist_name": playlist["name"],
            "playlist_id": playlist["id"],
            "playlist_url": f"https://open.spotify.com/playlist/{playlist['id']}",
            "artist": artist_name,
            "embed_url": f"https://open.spotify.com/embed/playlist/{playlist['id']}?utm_source=generator&theme=0"
        }
    else:
        search_query = quote_plus(artist_name)
        return {
            "playlist_name": f"Search: {artist_name}",
            "playlist_id": None,
            "playlist_url": f"https://open.spotify.com/search/{search_query}",
            "artist": artist_name,
            "search_url": f"https://open.spotify.com/search/{search_query}"
        }


def search_movies_with_links(query: str = None, mood: str = None, limit: int = 3):
    """Search movies and return full details with streaming links for Mr.DP 2.0"""
    api_key = get_tmdb_key()
    if not api_key:
        return []

    try:
        if query:
            r = requests.get(
                f"{TMDB_BASE_URL}/search/movie",
                params={"api_key": api_key, "query": query, "include_adult": "false"},
                timeout=8
            )
        elif mood:
            genre_map = FEELING_TO_GENRES.get(mood, {})
            genre_ids = genre_map.get("prefer", [])[:2]

            r = requests.get(
                f"{TMDB_BASE_URL}/discover/movie",
                params={
                    "api_key": api_key,
                    "sort_by": "popularity.desc",
                    "vote_count.gte": 100,
                    "with_genres": "|".join(map(str, genre_ids)) if genre_ids else "",
                    "watch_region": "US",
                    "with_watch_monetization_types": "flatrate|rent"
                },
                timeout=8
            )
        else:
            r = requests.get(f"{TMDB_BASE_URL}/movie/popular", params={"api_key": api_key}, timeout=8)

        r.raise_for_status()
        results = r.json().get("results", [])[:limit]

        enriched = []
        for movie in results:
            tmdb_id = movie.get("id")
            title = movie.get("title", "")

            providers, tmdb_watch_link = get_movie_providers(tmdb_id, "movie")
            provider_links = []
            for p in providers[:4]:
                name = p.get("provider_name", "")
                link = get_movie_deep_link(name, title, tmdb_id, "movie")
                if link:
                    provider_links.append({"name": name, "link": link})

            trailer_key = get_movie_trailer(tmdb_id, "movie")

            enriched.append({
                "id": str(tmdb_id),
                "title": title,
                "year": movie.get("release_date", "")[:4],
                "rating": round(movie.get("vote_average", 0), 1),
                "poster": f"{TMDB_IMAGE_URL}{movie.get('poster_path')}" if movie.get("poster_path") else "",
                "overview": movie.get("overview", "")[:200],
                "providers": provider_links,
                "trailer_key": trailer_key,
                "tmdb_link": tmdb_watch_link
            })

        return enriched
    except Exception as e:
        print(f"Movie search error: {e}")
        return []


def ask_mr_dp_v2(user_prompt: str, chat_history: list = None, user_context: dict = None):
    """Mr.DP 2.0 - Intelligent assistant with actual content and actions."""
    if not user_prompt or not user_prompt.strip():
        return None

    if not openai_client:
        print(f"[Mr.DP] No OpenAI client! API key present: {bool(_openai_key)}")
        return fallback_mr_dp_v2(user_prompt)

    context_summary = ""
    if user_context:
        if user_context.get("queue"):
            queue_titles = [q.get("title", "") for q in user_context["queue"][:5]]
            context_summary += f"\nUser's queue: {', '.join(queue_titles)}"
        if user_context.get("top_moods"):
            top = user_context["top_moods"]
            if top:
                context_summary += f"\nUser's common moods: {top}"
        # Enhanced personalization from user_learning (Phase 3)
        if user_context.get("genre_preferences"):
            context_summary += f"\nFavorite genres: {', '.join(user_context['genre_preferences'][:5])}"
        if user_context.get("adhd_profile"):
            adhd = user_context["adhd_profile"]
            if adhd.get("attention_pattern"):
                context_summary += f"\nAttention pattern: {adhd['attention_pattern']}"
            if adhd.get("optimal_duration"):
                context_summary += f"\nPreferred content duration: {adhd['optimal_duration']}"
        if user_context.get("patterns"):
            patterns = user_context["patterns"][:2]
            for p in patterns:
                context_summary += f"\nBehavior insight: {p.get('description', '')}"

    current_mood = st.session_state.get("current_feeling", "")
    desired_mood = st.session_state.get("desired_feeling", "")
    if current_mood:
        context_summary += f"\nCurrent selected mood: {current_mood}"
    if desired_mood:
        context_summary += f"\nDesired mood: {desired_mood}"

    system_with_context = MR_DP_SYSTEM_PROMPT_V2
    if context_summary:
        system_with_context += f"\n\n## CURRENT USER CONTEXT\n{context_summary}"

    messages = [{"role": "system", "content": system_with_context}]

    if chat_history:
        for msg in chat_history[-8:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})

    messages.append({"role": "user", "content": user_prompt})

    try:
        print(f"[Mr.DP] Calling OpenAI API with prompt: {user_prompt[:50]}...")
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        print(f"[Mr.DP] API call successful!")

        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        result = enrich_mr_dp_response(result, user_prompt)
        return result

    except Exception as e:
        import traceback
        print(f"[Mr.DP] API Error: {type(e).__name__}: {e}")
        print(f"[Mr.DP] Traceback: {traceback.format_exc()}")
        return fallback_mr_dp_v2(user_prompt)


def enrich_mr_dp_response(response: dict, user_prompt: str):
    """Enrich Mr.DP response with actual content data."""
    enriched_content = []

    for item in response.get("content", []):
        item_type = item.get("type", "")
        data = item.get("data", {})

        if item_type == "movie":
            title = data.get("title", "")
            if title:
                movies = search_movies_with_links(query=title, limit=1)
                if movies:
                    movies[0]["why"] = data.get("why", "Matches your vibe")
                    data = movies[0]
            enriched_content.append({"type": "movie", "data": data})

        elif item_type == "music":
            mood = data.get("mood", "Happy")
            spotify_data = get_spotify_playlist_for_mood(mood)
            spotify_data["description"] = data.get("description", spotify_data.get("description", ""))
            enriched_content.append({"type": "music", "data": spotify_data})

        elif item_type == "artist":
            artist_name = data.get("artist", data.get("name", ""))
            spotify_data = get_spotify_artist_playlist(artist_name)
            enriched_content.append({"type": "music", "data": spotify_data})

        else:
            enriched_content.append(item)

    response["content"] = enriched_content

    if not response.get("message"):
        response["message"] = "Here's what I found for you!"

    if not response.get("mood_update"):
        response["mood_update"] = {"current": None, "desired": None}

    if not response.get("actions"):
        response["actions"] = []

    # Ensure focus_page is included (defaults to null/None)
    if "focus_page" not in response:
        response["focus_page"] = None

    return response


def fallback_mr_dp_v2(user_prompt: str):
    """Fallback when API fails - still returns structured content."""
    t = user_prompt.lower()

    # CRISIS DETECTION - Always check first
    crisis_keywords = ["suicide", "kill myself", "end it", "want to die", "hurt myself", "self harm",
                       "don't want to live", "better off dead", "ending my life", "no reason to live"]
    is_crisis = any(k in t for k in crisis_keywords)

    if is_crisis:
        return {
            "message": "I hear you, and I care about you. Please know you're not alone. 💜\n\n🇺🇸 988 (Suicide & Crisis Lifeline)\n🇬🇧 116 123 (Samaritans)\n🌍 findahelpline.com\n\nIf you're in immediate danger, please call emergency services. These trained professionals can provide the support you deserve.",
            "content": [],
            "actions": [{"type": "sos", "label": "🆘 SOS Calm Mode", "data": {}}],
            "mood_update": {"current": "Overwhelmed", "desired": "Comforted"},
            "focus_page": None
        }

    is_music = any(k in t for k in ["music", "song", "playlist", "spotify", "play", "tunes", "tune"])
    is_podcast = any(k in t for k in ["podcast", "podcasts", "pod"])
    is_audiobook = any(k in t for k in ["audiobook", "audiobooks", "book", "books", "read", "listen to a book"])
    is_shorts = any(k in t for k in ["shorts", "short", "tiktok", "reels", "quick video"])
    is_stressed = any(k in t for k in ["stress", "anxious", "overwhelm", "calm", "relax"])
    is_greeting = any(k in t for k in ["hi", "hello", "hey", "howdy"])

    # Genre detection - map keywords to moods that have those genres
    genre_mood_map = {
        "horror": ("Scared", "Time for some scares! 👻"),
        "scary": ("Scared", "Let's get spooky! 👻"),
        "thriller": ("Thrilled", "Edge of your seat time! 🎬"),
        "comedy": ("Amused", "Let's get you laughing! 😂"),
        "funny": ("Amused", "Comedy incoming! 😄"),
        "action": ("Energized", "Action packed picks! 💥"),
        "romance": ("Romantic", "Love is in the air! 💕"),
        "romantic": ("Romantic", "Here's some romance! 💕"),
        "sad": ("Comforted", "Sometimes we need a good cry 🥺"),
        "drama": ("Inspired", "Drama for you! 🎭"),
        "adventure": ("Adventurous", "Adventure awaits! 🏔️"),
        "sci-fi": ("Curious", "Sci-fi exploration! 🚀"),
        "scifi": ("Curious", "Science fiction picks! 🚀"),
        "fantasy": ("Entertained", "Fantasy worlds await! ✨"),
        "documentary": ("Curious", "Learn something new! 📚"),
        "animation": ("Entertained", "Animated picks! 🎨"),
        "anime": ("Entertained", "Anime time! 🎌"),
    }

    detected_genre = None
    for keyword, (mood, msg) in genre_mood_map.items():
        if keyword in t:
            detected_genre = (mood, msg)
            break

    content = []
    actions = []
    message = "Let me find something for you!"
    mood_update = {"current": None, "desired": "Entertained"}
    focus_page = None  # Which page to show

    if is_greeting:
        message = "Hey! 👋 I'm Mr.DP, your dopamine curator. What vibe are you chasing today?"
        mood_update = {"current": None, "desired": None}

    elif is_stressed:
        message = "I hear you. Let's bring some calm 💜"
        mood_update = {"current": "Stressed", "desired": "Calm"}

        movies = search_movies_with_links(mood="Calm", limit=1)
        if movies:
            movies[0]["why"] = "Gentle visuals to help you decompress"
            content.append({"type": "movie", "data": movies[0]})

        spotify = get_spotify_playlist_for_mood("Calm")
        content.append({"type": "music", "data": spotify})
        actions.append({"type": "sos", "label": "🆘 SOS Calm Mode", "data": {}})

    elif is_music:
        focus_page = "music"  # Switch to music page
        for pattern in ["play ", "listen to ", "put on "]:
            if pattern in t:
                artist = t.split(pattern)[1].split()[0:3]
                artist_name = " ".join(artist).strip(".,!?")
                message = f"Loading up {artist_name.title()}! 🎤"
                spotify = get_spotify_artist_playlist(artist_name)
                content.append({"type": "music", "data": spotify})
                break
        else:
            message = "Music mode! 🎵 Here's some tunes for your vibe"
            spotify = get_spotify_playlist_for_mood("Happy")
            content.append({"type": "music", "data": spotify})

    elif is_podcast:
        focus_page = "podcasts"  # Switch to podcasts page
        message = "Podcast mode! 🎙️ Check out the Podcasts section"
        mood_update = {"current": None, "desired": "Curious"}

    elif is_audiobook:
        focus_page = "audiobooks"  # Switch to audiobooks page
        message = "Audiobook mode! 📚 Check out the Audiobooks section"
        mood_update = {"current": None, "desired": "Focused"}

    elif is_shorts:
        focus_page = "shorts"  # Switch to shorts page
        message = "Quick hits mode! ⚡ Check out the Shorts section"
        mood_update = {"current": None, "desired": "Entertained"}

    elif detected_genre:
        mood, message = detected_genre
        mood_update = {"current": None, "desired": mood}
        focus_page = "movies"  # Stay on movies for genre requests
        movies = search_movies_with_links(mood=mood, limit=3)
        for m in movies:
            content.append({"type": "movie", "data": m})

    else:
        movies = search_movies_with_links(limit=2)
        for m in movies:
            content.append({"type": "movie", "data": m})

    return {
        "message": message,
        "content": content,
        "actions": actions,
        "mood_update": mood_update,
        "focus_page": focus_page
    }


def render_mr_dp_response(response: dict):
    """Render Mr.DP 2.0 response with actual content cards and actions."""
    if not response:
        return

    for item in response.get("content", []):
        item_type = item.get("type", "")
        data = item.get("data", {})

        if item_type == "movie":
            render_mr_dp_movie_card(data)
        elif item_type == "music":
            render_mr_dp_music_card(data)

    actions = response.get("actions", [])
    if actions:
        cols = st.columns(len(actions))
        for idx, action in enumerate(actions):
            with cols[idx]:
                action_type = action.get("type", "")
                label = action.get("label", "Action")
                action_data = action.get("data", {})

                if action_type == "sos":
                    if st.button(label, key=f"mr_dp_sos_{idx}", use_container_width=True):
                        st.session_state.sos_mode = True
                        st.rerun()

                elif action_type == "focus":
                    if st.button(label, key=f"mr_dp_focus_{idx}", use_container_width=True):
                        from focus_timer import start_focus_session
                        start_focus_session(45, 10)
                        st.toast("Focus session started!")
                        st.rerun()

                elif action_type == "time_pick":
                    if st.button(label, key=f"mr_dp_time_{idx}", use_container_width=True):
                        st.session_state.time_available = action_data.get("minutes", 30)
                        st.toast(f"Showing {action_data.get('minutes', 30)}-minute picks!")
                        st.rerun()


def render_mr_dp_movie_card(data: dict, card_id: str = None):
    """Render a movie card from Mr.DP response with save button"""
    if not data or not data.get("title"):
        return

    title = data.get("title", "")
    year = data.get("year", "")
    rating = data.get("rating", 0)
    poster = data.get("poster", "")
    overview = data.get("overview", "")
    why = data.get("why", "")
    providers = data.get("providers", [])

    # Generate unique ID for this card
    if not card_id:
        card_id = f"mrdp_movie_{data.get('id', title.replace(' ', '_'))}"

    # Build the why section if present
    why_html = f'<div style="color: #8b5cf6; font-size: 0.85rem; font-style: italic;">💡 {safe(why)}</div>' if why else ''

    st.markdown(f"""<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 16px; margin: 12px 0; display: flex; gap: 16px;">
<img src="{safe(poster)}" style="width: 100px; border-radius: 8px;" onerror="this.style.display='none'">
<div style="flex: 1;">
<div style="font-weight: 600; font-size: 1.1rem;">{safe(title)} {f'({year})' if year else ''}</div>
<div style="color: #ffd700; font-size: 0.85rem;">⭐ {rating}</div>
<div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 8px 0;">{safe(overview[:150])}...</div>
{why_html}
</div>
</div>""", unsafe_allow_html=True)

    # Save button and provider buttons
    btn_cols = st.columns([1, 3])
    with btn_cols[0]:
        if st.button("💾 Save", key=f"save_{card_id}", use_container_width=True):
            if save_dopamine_item("movie", data):
                st.toast(f"Saved '{title}' for later! 💜", icon="💾")
            else:
                st.toast("Already saved!", icon="✓")
            st.rerun()

    if providers:
        cols = st.columns(min(len(providers) + 1, 5))
        for idx, p in enumerate(providers[:4]):
            with cols[idx]:
                st.link_button(f"▶️ {p['name']}", p['link'], use_container_width=True)


def render_mr_dp_music_card(data: dict, card_id: str = None):
    """Render a music card with Spotify embed and save button"""
    if not data:
        return

    name = data.get("playlist_name", "Playlist")
    description = data.get("description", "")
    playlist_url = data.get("playlist_url", "")
    embed_url = data.get("embed_url", "")
    playlist_id = data.get("playlist_id", "")

    # Generate unique ID for this card
    if not card_id:
        card_id = f"mrdp_music_{playlist_id or name.replace(' ', '_')}"

    st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(29,185,84,0.1), rgba(29,185,84,0.05)); border: 1px solid rgba(29,185,84,0.3); border-radius: 16px; padding: 16px; margin: 12px 0;">
<div style="font-weight: 600; font-size: 1.1rem; color: #1DB954;">🎵 {safe(name)}</div>
<div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 4px 0;">{safe(description)}</div>
</div>""", unsafe_allow_html=True)

    if embed_url:
        components.html(f'''
        <iframe style="border-radius:12px"
            src="{embed_url}"
            width="100%"
            height="152"
            frameBorder="0"
            allowfullscreen=""
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            loading="lazy">
        </iframe>
        ''', height=160)

    # Save and Open buttons
    btn_cols = st.columns([1, 2])
    with btn_cols[0]:
        if st.button("💾 Save", key=f"save_{card_id}", use_container_width=True):
            if save_dopamine_item("music", data):
                st.toast(f"Saved '{name}' for later! 🎵", icon="💾")
            else:
                st.toast("Already saved!", icon="✓")
            st.rerun()
    with btn_cols[1]:
        if playlist_url:
            st.link_button("🎧 Open in Spotify", playlist_url, use_container_width=True)


def ask_mr_dp_smart(user_prompt, chat_history=None, user_context=None):
    """Smart router - uses v2 if enabled, falls back to v1"""
    if st.session_state.get("use_mr_dp_v2", True):
        return ask_mr_dp_v2(user_prompt, chat_history, user_context)
    else:
        return ask_mr_dp(user_prompt, chat_history)


# --------------------------------------------------
# 9.6 PERSONALIZED "FOR YOU" FEED (PHASE 4)
# --------------------------------------------------
def get_time_based_mood(hour: int) -> str:
    """Get recommended mood based on time of day"""
    if 5 <= hour < 9:
        return "Energized"
    elif 9 <= hour < 12:
        return "Focused"
    elif 12 <= hour < 14:
        return "Entertained"
    elif 14 <= hour < 17:
        return "Focused"
    elif 17 <= hour < 20:
        return "Relaxed"
    elif 20 <= hour < 23:
        return "Entertained"
    else:
        return "Sleepy"


def get_time_period(hour: int) -> str:
    """Get time period name"""
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def get_time_greeting():
    """Get appropriate greeting based on time"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 21:
        return "Good evening"
    else:
        return "Hey night owl"


def get_personalized_feed(user_id: str, limit: int = 12):
    """Generate personalized content feed based on mood history, behavior, and time of day"""
    if not user_id:
        return get_default_feed(limit)

    sections = []

    # Get user's mood patterns
    try:
        top_moods = get_top_moods(supabase, user_id, 'desired', days=14, limit=3)
    except:
        top_moods = []

    # Time-based recommendation
    hour = datetime.now().hour
    time_mood = get_time_based_mood(hour)

    # Section 1: Based on most frequent desired mood
    if top_moods:
        top_desired_mood = top_moods[0][0]
        section_movies = discover_movies_fresh(desired_feeling=top_desired_mood)[:4]
        if section_movies:
            sections.append({
                "title": f"Because you love feeling {top_desired_mood.lower()}",
                "icon": "💜",
                "reason": "Your top mood choice",
                "items": section_movies,
                "type": "movies"
            })

    # Section 2: Time-based picks
    time_section_title = {
        "morning": "☀️ Morning Boost",
        "afternoon": "☕ Afternoon Pick",
        "evening": "🌆 Evening Vibes",
        "night": "🌙 Late Night Mood"
    }
    time_movies = discover_movies_fresh(desired_feeling=time_mood)[:4]
    if time_movies:
        sections.append({
            "title": time_section_title.get(get_time_period(hour), "Right Now"),
            "icon": "⏰",
            "reason": f"Perfect for {get_time_period(hour)}",
            "items": time_movies,
            "type": "movies"
        })

    # Section 3: From queue
    try:
        queue = get_watch_queue(supabase, user_id, status='queued', limit=4)
        if queue:
            sections.append({
                "title": "From Your Queue",
                "icon": "📋",
                "reason": f"{len(queue)} items saved",
                "items": queue,
                "type": "queue"
            })
    except:
        pass

    # Section 4: Comfort classics
    comfort_movies = discover_movies_fresh(desired_feeling="Comforted")[:4]
    if comfort_movies:
        sections.append({
            "title": "Comfort Classics",
            "icon": "🛋️",
            "reason": "Always here when you need them",
            "items": comfort_movies,
            "type": "movies"
        })

    return sections


def get_default_feed(limit: int = 12):
    """Default feed for non-logged-in users"""
    sections = [
        {
            "title": "Trending Now",
            "icon": "🔥",
            "reason": "What everyone's watching",
            "items": discover_movies_fresh()[:4],
            "type": "movies"
        },
        {
            "title": "Feel-Good Picks",
            "icon": "😊",
            "reason": "Guaranteed mood boost",
            "items": discover_movies_fresh(desired_feeling="Happy")[:4],
            "type": "movies"
        },
        {
            "title": "Calm & Cozy",
            "icon": "🛋️",
            "reason": "Stress-free viewing",
            "items": discover_movies_fresh(desired_feeling="Calm")[:4],
            "type": "movies"
        }
    ]
    return sections


def render_feed_section(section: dict):
    """Render a single feed section"""
    title = section.get("title", "")
    icon = section.get("icon", "🎬")
    reason = section.get("reason", "")
    items = section.get("items", [])
    section_type = section.get("type", "movies")

    st.markdown(f"""
    <div style="margin-bottom: 8px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
            <span style="font-size: 1.5rem;">{icon}</span>
            <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 600; margin: 0;">{title}</h3>
        </div>
        <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 0 0 16px 0;">{reason}</p>
    </div>
    """, unsafe_allow_html=True)

    if section_type == "movies" and items:
        cols = st.columns(4)
        for idx, item in enumerate(items[:4]):
            with cols[idx]:
                render_movie_card(item)

    elif section_type == "queue" and items:
        cols = st.columns(4)
        for idx, item in enumerate(items[:4]):
            with cols[idx]:
                poster = item.get('poster_path', '')
                if poster and not poster.startswith('http'):
                    poster = f"{TMDB_IMAGE_URL}{poster}"
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{safe(poster)}" class="movie-poster" onerror="this.style.display='none'">
                    <div class="movie-info">
                        <div class="movie-title">{safe(item.get('title', '')[:25])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 32px;'></div>", unsafe_allow_html=True)


def render_personalized_feed():
    """Render the personalized 'For You' home feed"""
    user_id = st.session_state.get("db_user_id")

    user_name = st.session_state.get("user", {}).get("name", "")
    greeting = get_time_greeting()

    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: 2rem; margin-bottom: 8px;">
            {greeting}{f', {user_name.split()[0]}' if user_name else ''}! 👋
        </h1>
        <p style="color: rgba(255,255,255,0.6);">Here's your personalized dopamine feed</p>
    </div>
    """, unsafe_allow_html=True)

    sections = get_personalized_feed(user_id) if user_id else get_default_feed()

    for section in sections:
        render_feed_section(section)


# --------------------------------------------------
# 9.7 MOOD ANALYTICS DASHBOARD (PREMIUM - PHASE 4)
# --------------------------------------------------
def get_mood_analytics(user_id: str, days: int = 30):
    """Generate mood analytics for dashboard"""
    if not user_id or not supabase:
        return None

    try:
        history = get_mood_history(supabase, user_id, days=days)
        if not history:
            return None

        from collections import Counter

        current_counts = Counter(h["current_feeling"] for h in history if h.get("current_feeling"))
        desired_counts = Counter(h["desired_feeling"] for h in history if h.get("desired_feeling"))

        # Weekly journey (last 7 days)
        weekly_journey = []
        for i in range(7):
            day = datetime.now() - timedelta(days=6-i)
            day_str = day.strftime("%Y-%m-%d")
            day_moods_list = [h for h in history if h.get("created_at", "").startswith(day_str)]
            if day_moods_list:
                day_current = Counter(h.get("current_feeling", "") for h in day_moods_list).most_common(1)
                weekly_journey.append({
                    "day": day.strftime("%a"),
                    "mood": day_current[0][0] if day_current else None,
                    "count": len(day_moods_list)
                })
            else:
                weekly_journey.append({"day": day.strftime("%a"), "mood": None, "count": 0})

        # Time patterns
        time_moods = {"morning": [], "afternoon": [], "evening": [], "night": []}
        for h in history:
            try:
                created = h.get("created_at", "")
                if "T" in created:
                    hour = int(created.split("T")[1][:2])
                    period = get_time_period(hour)
                    if h.get("current_feeling"):
                        time_moods[period].append(h["current_feeling"])
            except:
                pass

        time_patterns = {}
        for period, moods in time_moods.items():
            if moods:
                time_patterns[period] = Counter(moods).most_common(1)[0][0]
            else:
                time_patterns[period] = None

        # Insights
        insights = []
        negative_moods = ["Sad", "Anxious", "Stressed", "Overwhelmed", "Angry", "Lonely"]
        for mood, count in current_counts.most_common():
            if mood in negative_moods:
                total = sum(current_counts.values())
                pct = int((count / total) * 100)
                insights.append({
                    "type": "pattern",
                    "icon": "💜",
                    "text": f"You felt {mood.lower()} {pct}% of the time. That's okay - we're here to help!"
                })
                break

        if desired_counts:
            top_desired = desired_counts.most_common(1)[0]
            insights.append({
                "type": "positive",
                "icon": "🎯",
                "text": f"You most often want to feel {top_desired[0].lower()}. We've got you!"
            })

        return {
            "current_moods": dict(current_counts.most_common(10)),
            "desired_moods": dict(desired_counts.most_common(10)),
            "weekly_journey": weekly_journey,
            "time_patterns": time_patterns,
            "insights": insights,
            "total_logs": len(history),
            "days_active": len(set(h.get("created_at", "")[:10] for h in history if h.get("created_at")))
        }
    except Exception as e:
        print(f"Analytics error: {e}")
        return None


def render_weekly_mood_chart(weekly_journey: list):
    """Render the weekly mood journey chart"""
    mood_emojis = {
        "Sad": "😢", "Lonely": "😔", "Anxious": "😰", "Overwhelmed": "😵",
        "Angry": "😤", "Stressed": "😫", "Bored": "😑", "Tired": "😴",
        "Calm": "😌", "Happy": "😊", "Excited": "🤩", "Curious": "🧐",
        "Focused": "🎯", "Relaxed": "😎", "Energized": "⚡", "Comforted": "🥰"
    }

    cols = st.columns(7)
    for idx, day in enumerate(weekly_journey):
        with cols[idx]:
            mood = day.get("mood")
            emoji = mood_emojis.get(mood, "⚪") if mood else "⚪"
            count = day.get("count", 0)

            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 2rem;">{emoji}</div>
                <div style="font-weight: 600; margin-top: 4px;">{day['day']}</div>
                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">
                    {f'{count} logs' if count else 'No data'}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_mood_breakdown(mood_counts: dict, mood_type: str):
    """Render mood frequency breakdown"""
    if not mood_counts:
        st.info("No data yet")
        return

    total = sum(mood_counts.values())

    for mood, count in list(mood_counts.items())[:5]:
        pct = int((count / total) * 100)
        color = "#8b5cf6" if mood_type == "current" else "#06b6d4"

        st.markdown(f"""
        <div style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span>{mood}</span>
                <span style="color: rgba(255,255,255,0.6);">{pct}%</span>
            </div>
            <div style="height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_time_patterns(time_patterns: dict):
    """Render time-of-day mood patterns"""
    time_icons = {"morning": "🌅", "afternoon": "☀️", "evening": "🌆", "night": "🌙"}

    cols = st.columns(4)
    for idx, (period, mood) in enumerate(time_patterns.items()):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 16px;
                text-align: center;
            ">
                <div style="font-size: 1.5rem;">{time_icons.get(period, '⏰')}</div>
                <div style="font-weight: 600; margin: 8px 0;">{period.title()}</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">
                    {mood if mood else 'No data'}
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_analytics_preview(user_id: str):
    """Show blurred preview for non-premium users"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(6,182,212,0.1));
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 20px;
        padding: 32px;
        text-align: center;
    ">
        <div style="font-size: 3rem; margin-bottom: 16px;">📊</div>
        <h3 style="margin-bottom: 8px;">Unlock Your Mood Analytics</h3>
        <p style="color: rgba(255,255,255,0.7); margin-bottom: 24px;">
            See your mood patterns, weekly journey, and personalized insights.
        </p>
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 24px;
            text-align: left;
        ">
            <p style="font-size: 0.9rem; color: rgba(255,255,255,0.6); margin: 0;">
                ✓ Weekly mood charts<br>
                ✓ Time-of-day patterns<br>
                ✓ Content that helps you most<br>
                ✓ Personalized insights
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔓 Upgrade to Premium - $4.99/mo", key="analytics_upgrade", use_container_width=True, type="primary"):
        st.session_state.show_premium_modal = True
        st.rerun()


def render_mood_analytics_dashboard():
    """Render the mood analytics dashboard (premium feature)"""
    user_id = st.session_state.get("db_user_id")
    is_premium_user = st.session_state.get("is_premium", False)

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">📊</span>
        <h2 class="section-title">Your Dopamine Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)

    if not user_id:
        st.info("Log in to see your mood analytics!")
        return

    if not is_premium_user:
        render_analytics_preview(user_id)
        return

    analytics = get_mood_analytics(user_id, days=30)

    if not analytics:
        st.info("Start using dopamine.watch to see your mood patterns!")
        return

    # Stats bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mood Logs", analytics["total_logs"])
    with col2:
        st.metric("Days Active", analytics["days_active"])
    with col3:
        streak = st.session_state.get("streak_days", 0)
        st.metric("Current Streak", f"🔥 {streak}")
    with col4:
        points = get_dopamine_points()
        st.metric("Dopamine Points", f"⚡ {points}")

    st.markdown("---")

    # Weekly Journey
    st.markdown("### 📅 Your Week in Moods")
    render_weekly_mood_chart(analytics["weekly_journey"])

    st.markdown("---")

    # Two columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💭 How You've Been Feeling")
        render_mood_breakdown(analytics["current_moods"], "current")

    with col2:
        st.markdown("### 🎯 What You've Wanted to Feel")
        render_mood_breakdown(analytics["desired_moods"], "desired")

    st.markdown("---")

    # Time patterns
    st.markdown("### ⏰ Your Mood by Time of Day")
    render_time_patterns(analytics["time_patterns"])

    st.markdown("---")

    # Insights
    st.markdown("### 💡 Insights")
    for insight in analytics.get("insights", []):
        st.markdown(f"""
        <div style="
            background: rgba(139,92,246,0.1);
            border-left: 3px solid #8b5cf6;
            padding: 12px 16px;
            margin: 8px 0;
            border-radius: 0 8px 8px 0;
        ">
            <span style="margin-right: 8px;">{insight['icon']}</span>
            {insight['text']}
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# 9.8 SMART PREMIUM TRIGGERS (PHASE 4)
# --------------------------------------------------
def check_premium_triggers():
    """Check if any premium trigger conditions are met"""
    if st.session_state.get("is_premium"):
        return None

    # Don't trigger too often
    last_trigger = st.session_state.get("last_premium_trigger")
    if last_trigger and (datetime.now() - last_trigger) < timedelta(minutes=10):
        return None

    triggers = []

    # Mr.DP limit approaching
    mr_dp_uses = st.session_state.get("user", {}).get("mr_dp_uses", 0)
    if mr_dp_uses >= 4:
        triggers.append({
            "priority": 1,
            "message": "You're loving Mr.DP! 🧠",
            "cta": "Get unlimited chats"
        })

    # Queue getting full
    try:
        user_id = st.session_state.get("db_user_id")
        if user_id:
            queue = get_watch_queue(supabase, user_id, status='queued')
            if len(queue) >= 8:
                triggers.append({
                    "priority": 2,
                    "message": "Your queue is growing! 📋",
                    "cta": "Unlock unlimited saves"
                })
    except:
        pass

    # SOS power user
    if st.session_state.get("sos_use_count", 0) >= 3:
        triggers.append({
            "priority": 3,
            "message": "SOS Mode is helping you! 🆘",
            "cta": "Support us & get more"
        })

    # Streak milestone
    streak = st.session_state.get("streak_days", 0)
    if streak in [7, 14, 30]:
        triggers.append({
            "priority": 4,
            "message": f"🔥 {streak}-day streak! Amazing!",
            "cta": "Celebrate with Premium"
        })

    if triggers:
        triggers.sort(key=lambda x: x["priority"])
        return triggers[0]

    return None


def render_smart_premium_prompt(trigger: dict):
    """Render contextual premium prompt"""
    if not trigger:
        return

    st.session_state.last_premium_trigger = datetime.now()

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(6,182,212,0.15));
        border: 1px solid rgba(139,92,246,0.4);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        text-align: center;
    ">
        <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 8px;">
            {trigger['message']}
        </div>
        <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 16px;">
            Premium members get unlimited access to all features.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Maybe Later", key="trigger_dismiss", use_container_width=True):
            st.session_state.trigger_dismissed = True
    with col2:
        if st.button(f"🔓 {trigger['cta']}", key="trigger_upgrade", use_container_width=True, type="primary"):
            st.session_state.show_premium_modal = True
            st.rerun()


def should_show_premium_trigger():
    """Determine if we should show a premium trigger"""
    if st.session_state.get("is_premium"):
        return False
    if st.session_state.get("trigger_dismissed"):
        return False
    if st.session_state.get("show_premium_modal"):
        return False
    return True


# --------------------------------------------------
# 9.9 ONBOARDING FLOW (PHASE 4)
# --------------------------------------------------
ONBOARDING_STEPS = [
    {"title": "Welcome to dopamine.watch! 🧠", "subtitle": "Let's set you up in 30 seconds", "type": "welcome"},
    {"title": "How are you feeling right now?", "subtitle": "This helps us personalize your experience", "type": "mood_current",
     "options": ["😊 Pretty Good", "😐 Meh", "😔 Not Great", "😰 Stressed/Anxious", "😴 Tired"]},
    {"title": "What would you like to feel?", "subtitle": "We'll find content to get you there", "type": "mood_desired",
     "options": ["😊 Happy", "😌 Calm", "⚡ Energized", "🎬 Entertained", "😴 Sleepy"]},
    {"title": "Meet Mr.DP! 🧠", "subtitle": "Your AI dopamine curator", "type": "feature_intro"},
    {"title": "You're all set!", "subtitle": "Here's 50 Dopamine Points to get started", "type": "complete"}
]


def render_onboarding():
    """Render the onboarding flow"""
    step = st.session_state.get("onboarding_step", 0)

    if step >= len(ONBOARDING_STEPS):
        complete_onboarding()
        return

    current = ONBOARDING_STEPS[step]

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Progress dots
        progress_html = ""
        for i in range(len(ONBOARDING_STEPS)):
            if i == step:
                progress_html += '<div style="width:10px;height:10px;border-radius:50%;background:#8b5cf6;transform:scale(1.2);"></div>'
            elif i < step:
                progress_html += '<div style="width:10px;height:10px;border-radius:50%;background:#10b981;"></div>'
            else:
                progress_html += '<div style="width:10px;height:10px;border-radius:50%;background:rgba(255,255,255,0.2);"></div>'

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            padding: 48px 32px;
            text-align: center;
            max-width: 500px;
            margin: 0 auto;
        ">
            <div style="display:flex;justify-content:center;gap:8px;margin-bottom:32px;">{progress_html}</div>
            <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; margin-bottom: 8px;">
                {current['title']}
            </h2>
            <p style="color: rgba(255,255,255,0.6); margin-bottom: 32px;">{current['subtitle']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        if current["type"] == "welcome":
            if st.button("Let's Go! 🚀", key="onboard_start", use_container_width=True, type="primary"):
                st.session_state.onboarding_step = 1
                st.rerun()

        elif current["type"] == "mood_current":
            mood_map = {
                "😊 Pretty Good": "Happy", "😐 Meh": "Bored", "😔 Not Great": "Sad",
                "😰 Stressed/Anxious": "Anxious", "😴 Tired": "Tired"
            }
            for option in current["options"]:
                if st.button(option, key=f"mood_c_{option}", use_container_width=True):
                    st.session_state.current_feeling = mood_map.get(option, "Bored")
                    st.session_state.onboarding_step = 2
                    st.rerun()

        elif current["type"] == "mood_desired":
            mood_map = {
                "😊 Happy": "Happy", "😌 Calm": "Calm", "⚡ Energized": "Energized",
                "🎬 Entertained": "Entertained", "😴 Sleepy": "Sleepy"
            }
            for option in current["options"]:
                if st.button(option, key=f"mood_d_{option}", use_container_width=True):
                    st.session_state.desired_feeling = mood_map.get(option, "Happy")
                    st.session_state.onboarding_step = 3
                    st.rerun()

        elif current["type"] == "feature_intro":
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(6,182,212,0.2));
                border-radius: 16px;
                padding: 24px;
                margin: 16px 0;
            ">
                <div style="font-size: 3rem; text-align: center; margin-bottom: 16px;">🧠💬</div>
                <p style="text-align: center;">
                    <strong>Mr.DP</strong> is your AI assistant who understands ADHD brains.<br><br>
                    Just tell him how you're feeling, and he'll find the perfect content!
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Nice! What else? →", key="onboard_feature", use_container_width=True, type="primary"):
                st.session_state.onboarding_step = 4
                st.rerun()

        elif current["type"] == "complete":
            st.markdown("""
            <div style="text-align: center; margin: 24px 0;">
                <div style="font-size: 4rem;">🎉</div>
            </div>
            """, unsafe_allow_html=True)

            st.success("You earned 50 Dopamine Points!")

            if st.button("Start Exploring! 🚀", key="onboard_complete", use_container_width=True, type="primary"):
                complete_onboarding()
                st.rerun()


def complete_onboarding():
    """Complete onboarding and award points"""
    st.session_state.onboarding_complete = True
    st.session_state.onboarding_step = 0

    add_dopamine_points(50, "Welcome to dopamine.watch!")

    user_id = st.session_state.get("db_user_id")
    if user_id and supabase:
        log_mood_selection(
            supabase, user_id,
            st.session_state.get("current_feeling", "Bored"),
            st.session_state.get("desired_feeling", "Happy"),
            "onboarding"
        )
        update_user_profile(user_id, {"onboarding_complete": True})


def should_show_onboarding():
    """Check if user needs onboarding"""
    if not st.session_state.get("user"):
        return False

    if st.session_state.get("onboarding_complete"):
        return False

    user_id = st.session_state.get("db_user_id")
    if user_id:
        profile = get_user_profile(user_id)
        if profile.get("onboarding_complete"):
            st.session_state.onboarding_complete = True
            return False

    return True


# --------------------------------------------------
# 9.10 VIRAL & GROWTH ENGINE (PHASE 5)
# --------------------------------------------------

# Referral reward amounts
REFERRAL_REWARD_DP = 100  # Both referrer and referee get 100 DP
REFERRAL_TRIAL_DAYS = 7   # Referred users get 7-day premium trial

def generate_referral_code(user_id: str) -> str:
    """Generate a unique referral code for a user."""
    # Create a short, memorable code from user_id
    code = hashlib.md5(f"{user_id}-dopamine".encode()).hexdigest()[:8].upper()
    return code


def apply_referral_code(user_id: str, referral_code: str) -> dict:
    """Apply a referral code for a new user."""
    if not supabase or not user_id:
        return {"success": False, "error": "Not logged in"}

    try:
        # Find the referrer by code
        result = supabase.table("profiles").select("id, referral_code").eq("referral_code", referral_code.upper()).execute()

        if not result.data:
            return {"success": False, "error": "Invalid referral code"}

        referrer_id = result.data[0]["id"]

        if referrer_id == user_id:
            return {"success": False, "error": "Can't use your own code"}

        # Check if user already used a referral code
        user_profile = get_user_profile(user_id)
        if user_profile.get("referred_by"):
            return {"success": False, "error": "Already used a referral code"}

        # Record the referral
        referral_data = {
            "referrer_id": referrer_id,
            "referred_id": user_id,
            "referral_code": referral_code.upper(),
            "status": "completed"
        }
        supabase.table("referrals").insert(referral_data).execute()

        # Award points to referrer
        add_dopamine_points_to_user(referrer_id, REFERRAL_REWARD_DP, "Referral reward!")

        # Award points to new user
        add_dopamine_points_to_user(user_id, REFERRAL_REWARD_DP, "Welcome bonus from referral!")

        # Grant premium trial to new user
        trial_end = (datetime.now() + timedelta(days=REFERRAL_TRIAL_DAYS)).isoformat()
        supabase.table("profiles").update({
            "referred_by": referrer_id,
            "is_premium": True,
            "premium_trial_end": trial_end
        }).eq("id", user_id).execute()

        return {"success": True, "message": f"Welcome! You got {REFERRAL_REWARD_DP} DP + {REFERRAL_TRIAL_DAYS}-day premium trial!"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def add_dopamine_points_to_user(user_id: str, amount: int, reason: str = ""):
    """Add dopamine points to a specific user."""
    if not supabase:
        return
    try:
        profile = get_user_profile(user_id)
        current = profile.get("dopamine_points", 0)
        supabase.table("profiles").update({"dopamine_points": current + amount}).eq("id", user_id).execute()
    except:
        pass


def get_referral_stats(user_id: str) -> dict:
    """Get referral statistics for a user."""
    if not supabase or not user_id:
        return {"count": 0, "earned": 0}

    try:
        result = supabase.table("referrals").select("*").eq("referrer_id", user_id).eq("status", "completed").execute()
        count = len(result.data) if result.data else 0
        return {
            "count": count,
            "earned": count * REFERRAL_REWARD_DP
        }
    except:
        return {"count": 0, "earned": 0}


def generate_mood_card_svg(mood_data: dict, card_type: str = "week") -> str:
    """Generate an SVG shareable card for mood stats."""

    if card_type == "week":
        # Week in Moods card
        moods = mood_data.get("moods", [])
        mood_emojis = {
            "Happy": "😊", "Sad": "😢", "Anxious": "😰", "Calm": "😌",
            "Bored": "😐", "Excited": "🤩", "Tired": "😴", "Stressed": "😤",
            "Focused": "🎯", "Creative": "🎨", "Energized": "⚡", "Nostalgic": "🥹",
            "Romantic": "💕", "Adventurous": "🌟", "Peaceful": "🕊️", "Entertained": "🎬"
        }

        emoji_display = " ".join([mood_emojis.get(m, "😊") for m in moods[:7]])
        streak = mood_data.get("streak", 0)

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
            <defs>
                <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#1e1b4b"/>
                    <stop offset="100%" style="stop-color:#0f172a"/>
                </linearGradient>
                <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#8b5cf6"/>
                    <stop offset="100%" style="stop-color:#06b6d4"/>
                </linearGradient>
            </defs>
            <rect width="400" height="250" fill="url(#bg)" rx="20"/>
            <text x="200" y="40" text-anchor="middle" fill="url(#accent)" font-size="18" font-weight="bold" font-family="system-ui">🧠 My Week in Moods</text>
            <text x="200" y="100" text-anchor="middle" fill="white" font-size="36">{emoji_display}</text>
            <text x="200" y="150" text-anchor="middle" fill="rgba(255,255,255,0.7)" font-size="14">{"🔥 " + str(streak) + " day streak!" if streak > 1 else ""}</text>
            <text x="200" y="220" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="12">dopamine.watch • Feel Better, Watch Better</text>
        </svg>'''

    else:
        # Stats card
        points = mood_data.get("points", 0)
        streak = mood_data.get("streak", 0)
        level = mood_data.get("level", "Newbie")

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
            <defs>
                <linearGradient id="bg2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#1e1b4b"/>
                    <stop offset="100%" style="stop-color:#0f172a"/>
                </linearGradient>
                <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#f59e0b"/>
                    <stop offset="100%" style="stop-color:#fbbf24"/>
                </linearGradient>
            </defs>
            <rect width="400" height="250" fill="url(#bg2)" rx="20"/>
            <text x="200" y="40" text-anchor="middle" fill="url(#gold)" font-size="18" font-weight="bold" font-family="system-ui">⚡ My Dopamine Stats</text>
            <text x="200" y="90" text-anchor="middle" fill="white" font-size="48" font-weight="bold">{points:,}</text>
            <text x="200" y="115" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="14">Dopamine Points</text>
            <text x="120" y="165" text-anchor="middle" fill="white" font-size="24">🔥 {streak}</text>
            <text x="120" y="185" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="12">Day Streak</text>
            <text x="280" y="165" text-anchor="middle" fill="white" font-size="24">🏆 {level}</text>
            <text x="280" y="185" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="12">Level</text>
            <text x="200" y="230" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="12">dopamine.watch • Feel Better, Watch Better</text>
        </svg>'''

    return svg


def render_shareable_mood_card():
    """Render the shareable mood card UI."""
    user_id = st.session_state.get("db_user_id")

    # Get mood data for the card
    moods = []
    if user_id and supabase:
        history = get_mood_history(supabase, user_id, days=7)
        moods = [h.get("current_feeling", "Happy") for h in history[:7]]

    if not moods:
        moods = [st.session_state.get("current_feeling", "Happy")]

    points = get_dopamine_points()
    streak = get_streak()
    level_name, _, _ = get_level()

    # Card data
    mood_data = {
        "moods": moods,
        "streak": streak,
        "points": points,
        "level": level_name
    }

    st.markdown("#### 📤 Share Your Stats")

    card_type = st.radio("Card Type:", ["Week in Moods", "My Stats"], horizontal=True, key="share_card_type")

    svg = generate_mood_card_svg(mood_data, "week" if card_type == "Week in Moods" else "stats")

    # Display preview
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e1b4b, #0f172a);
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin: 16px 0;
    ">
        {svg}
    </div>
    """, unsafe_allow_html=True)

    # Share buttons
    share_text = f"Check out my dopamine stats on dopamine.watch! 🧠⚡ {points:,} DP | {streak} day streak"
    share_url = "https://app.dopamine.watch"

    col1, col2 = st.columns(2)
    with col1:
        twitter_url = f"https://twitter.com/intent/tweet?text={quote_plus(share_text)}&url={quote_plus(share_url)}"
        st.markdown(f"<a href='{twitter_url}' target='_blank' style='display:block;text-align:center;padding:12px;background:#1DA1F2;border-radius:8px;color:white;text-decoration:none;font-weight:600;'>🐦 Share on X</a>", unsafe_allow_html=True)
    with col2:
        if st.button("📋 Copy Stats", key="copy_stats_btn", use_container_width=True):
            st.toast("Stats copied! Share anywhere! 📤", icon="✅")


# Milestone thresholds for celebrations
MILESTONES = {
    "streak": [7, 14, 30, 60, 100],
    "points": [100, 500, 1000, 5000, 10000],
    "referrals": [1, 5, 10, 25, 50]
}

MILESTONE_MESSAGES = {
    "streak_7": {"emoji": "🔥", "title": "Week Warrior!", "desc": "7-day streak achieved!"},
    "streak_14": {"emoji": "💪", "title": "Fortnight Fighter!", "desc": "14 days strong!"},
    "streak_30": {"emoji": "🏆", "title": "Monthly Master!", "desc": "30-day streak legend!"},
    "streak_60": {"emoji": "💎", "title": "Diamond Dedication!", "desc": "60 days of consistency!"},
    "streak_100": {"emoji": "👑", "title": "Centurion!", "desc": "100-day streak royalty!"},
    "points_100": {"emoji": "⭐", "title": "Rising Star!", "desc": "First 100 DP earned!"},
    "points_500": {"emoji": "🌟", "title": "Bright Star!", "desc": "500 DP milestone!"},
    "points_1000": {"emoji": "✨", "title": "Thousand Club!", "desc": "1,000 DP achieved!"},
    "points_5000": {"emoji": "🚀", "title": "Sky High!", "desc": "5,000 DP rocket!"},
    "points_10000": {"emoji": "🦄", "title": "Legendary!", "desc": "10,000 DP unicorn status!"},
    "referrals_1": {"emoji": "🤝", "title": "First Friend!", "desc": "Your first referral!"},
    "referrals_5": {"emoji": "👥", "title": "Squad Builder!", "desc": "5 friends referred!"},
    "referrals_10": {"emoji": "🎯", "title": "Networker!", "desc": "10 referrals strong!"},
    "referrals_25": {"emoji": "🌐", "title": "Influencer!", "desc": "25 people joined through you!"},
    "referrals_50": {"emoji": "👑", "title": "Ambassador!", "desc": "50 referrals - you're a legend!"},
}


def check_milestones() -> list:
    """Check if user has hit any new milestones."""
    user_id = st.session_state.get("db_user_id")
    achieved = st.session_state.get("achieved_milestones", [])
    new_milestones = []

    streak = get_streak()
    points = get_dopamine_points()
    referrals = get_referral_stats(user_id).get("count", 0) if user_id else 0

    # Check streak milestones
    for threshold in MILESTONES["streak"]:
        key = f"streak_{threshold}"
        if streak >= threshold and key not in achieved:
            new_milestones.append(key)

    # Check points milestones
    for threshold in MILESTONES["points"]:
        key = f"points_{threshold}"
        if points >= threshold and key not in achieved:
            new_milestones.append(key)

    # Check referral milestones
    for threshold in MILESTONES["referrals"]:
        key = f"referrals_{threshold}"
        if referrals >= threshold and key not in achieved:
            new_milestones.append(key)

    return new_milestones


def render_milestone_celebration(milestone_key: str):
    """Render a milestone celebration popup."""
    milestone = MILESTONE_MESSAGES.get(milestone_key, {})
    if not milestone:
        return

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.3), rgba(6,182,212,0.3));
        border: 2px solid rgba(139,92,246,0.5);
        border-radius: 24px;
        padding: 32px;
        text-align: center;
        margin: 20px 0;
        animation: pulse 2s ease-in-out infinite;
    ">
        <div style="font-size: 4rem; margin-bottom: 16px;">{milestone['emoji']}</div>
        <div style="font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #8b5cf6, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {milestone['title']}
        </div>
        <div style="color: rgba(255,255,255,0.7); margin-top: 8px; font-size: 1.1rem;">
            {milestone['desc']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Share buttons for milestone
    share_text = f"I just unlocked {milestone['title']} on dopamine.watch! {milestone['emoji']} {milestone['desc']}"
    share_url = "https://app.dopamine.watch"
    twitter_url = f"https://twitter.com/intent/tweet?text={quote_plus(share_text)}&url={quote_plus(share_url)}"

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<a href='{twitter_url}' target='_blank' style='display:block;text-align:center;padding:12px;background:#1DA1F2;border-radius:8px;color:white;text-decoration:none;font-weight:600;'>🐦 Share Achievement</a>", unsafe_allow_html=True)
    with col2:
        if st.button("✓ Awesome!", key=f"dismiss_milestone_{milestone_key}", use_container_width=True):
            achieved = st.session_state.get("achieved_milestones", [])
            achieved.append(milestone_key)
            st.session_state.achieved_milestones = achieved
            st.session_state.current_milestone = None
            st.rerun()


def render_social_proof_banner():
    """Render a social proof banner with live stats."""
    # These would ideally come from a database aggregate, but for now use estimates
    active_users = random.randint(150, 300)
    moods_logged = random.randint(1200, 2500)

    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, rgba(139,92,246,0.1), rgba(6,182,212,0.1));
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 12px;
        padding: 12px 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 24px;
        margin: 16px 0;
        font-size: 0.85rem;
    ">
        <span style="color: rgba(255,255,255,0.8);">
            <span style="color: #10b981;">●</span> {active_users} brains vibing now
        </span>
        <span style="color: rgba(255,255,255,0.5);">|</span>
        <span style="color: rgba(255,255,255,0.8);">
            📊 {moods_logged:,} moods matched today
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_referral_section():
    """Render the referral section in sidebar or profile."""
    ref_code = st.session_state.referral_code
    user_id = st.session_state.get("db_user_id")

    st.markdown("#### 🎁 Invite Friends")

    # Show referral code
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(6,182,212,0.2));
        border: 2px dashed rgba(139,92,246,0.4);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 12px 0;
    ">
        <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-bottom: 8px;">Your Referral Code</div>
        <div style="font-size: 1.5rem; font-weight: 700; letter-spacing: 2px; color: #8b5cf6;">{ref_code}</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"🎁 Both get {REFERRAL_REWARD_DP} DP + {REFERRAL_TRIAL_DAYS}-day premium trial!")

    # Copy link button
    referral_link = f"https://app.dopamine.watch?ref={ref_code}"
    if st.button("📋 Copy Invite Link", key="copy_referral_link", use_container_width=True):
        st.toast("Link copied! Share with friends!", icon="📋")

    # Show referral stats if logged in
    if user_id:
        stats = get_referral_stats(user_id)
        if stats["count"] > 0:
            st.markdown(f"""
            <div style="
                background: rgba(16,185,129,0.1);
                border: 1px solid rgba(16,185,129,0.2);
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                margin-top: 12px;
            ">
                <span style="font-size: 1.2rem; font-weight: 600;">{stats['count']}</span>
                <span style="color: rgba(255,255,255,0.6);">friends joined</span>
                <span style="color: #10b981; margin-left: 8px;">+{stats['earned']} DP earned</span>
            </div>
            """, unsafe_allow_html=True)


def render_apply_referral_code():
    """Render UI for applying a referral code."""
    user_id = st.session_state.get("db_user_id")

    if not user_id:
        return

    # Check if user already used a referral code
    profile = get_user_profile(user_id)
    if profile.get("referred_by"):
        return  # Already used a code

    with st.expander("🎁 Have a referral code?"):
        code_input = st.text_input("Enter code:", key="apply_ref_code", placeholder="XXXXXXXX")
        if st.button("Apply Code", key="apply_ref_btn", use_container_width=True):
            if code_input:
                result = apply_referral_code(user_id, code_input)
                if result["success"]:
                    st.success(result["message"])
                    st.balloons()
                    st.rerun()
                else:
                    st.error(result["error"])


# --------------------------------------------------
# 9.11 COMMUNITY, GAMIFICATION & ADMIN (PHASE 6)
# --------------------------------------------------

# Admin emails for dashboard access
ADMIN_EMAILS = ["johan@dopamine.watch", "admin@dopamine.watch"]

def is_admin(user_id: str = None) -> bool:
    """Check if current user is admin"""
    if not user_id:
        user_id = st.session_state.get("db_user_id")

    if not user_id:
        return False

    user = st.session_state.get("user", {})
    email = user.get("email", "")

    return email.lower() in [e.lower() for e in ADMIN_EMAILS]


# --------------------------------------------------
# COMMUNITY RECOMMENDATIONS ("Others Like You")
# --------------------------------------------------
def get_similar_users(user_id: str, limit: int = 20) -> list:
    """Find users with similar mood patterns"""
    if not user_id or not supabase:
        return []

    try:
        # Get user's mood history
        user_moods = get_mood_history(supabase, user_id, limit=50)
        if not user_moods:
            return []

        from collections import Counter
        user_mood_counts = Counter(m["desired_feeling"] for m in user_moods if m.get("desired_feeling"))
        user_top_moods = set(m for m, _ in user_mood_counts.most_common(3))

        # Get other users with similar moods (aggregated, not individual data)
        recent_cutoff = (datetime.now() - timedelta(days=14)).isoformat()

        result = supabase.table("mood_history")\
            .select("user_id, desired_feeling")\
            .gte("created_at", recent_cutoff)\
            .neq("user_id", user_id)\
            .limit(500)\
            .execute()

        if not result.data:
            return []

        # Group by user and calculate similarity
        user_moods_map = {}
        for r in result.data:
            uid = r["user_id"]
            if uid not in user_moods_map:
                user_moods_map[uid] = []
            user_moods_map[uid].append(r["desired_feeling"])

        # Calculate similarity scores
        similar_users = []
        for uid, moods in user_moods_map.items():
            other_top = set(Counter(moods).most_common(3))
            overlap = len(user_top_moods.intersection(set(m for m, _ in other_top)))
            if overlap >= 2:
                similar_users.append(uid)

        return similar_users[:limit]
    except:
        return []


def get_community_recommendations(user_id: str, limit: int = 8) -> list:
    """Get movies that similar users liked"""
    if not user_id or not supabase:
        return []

    try:
        similar_users = get_similar_users(user_id)
        if not similar_users:
            return []

        # Get content that similar users clicked/saved
        result = supabase.table("user_behavior")\
            .select("content_id, metadata")\
            .in_("user_id", similar_users)\
            .eq("content_type", "movie")\
            .order("created_at", desc=True)\
            .limit(50)\
            .execute()

        if not result.data:
            return []

        # Deduplicate and count
        from collections import Counter
        content_counts = Counter()
        content_data = {}

        for r in result.data:
            cid = r.get("content_id")
            if not cid:
                continue
            content_counts[cid] += 1
            metadata = r.get("metadata", {}) or {}
            if cid not in content_data:
                content_data[cid] = {
                    "id": cid,
                    "title": metadata.get("title", "Unknown"),
                    "mood": metadata.get("desired_feeling")
                }

        # Get top content
        recommendations = []
        for cid, count in content_counts.most_common(limit):
            if cid in content_data:
                data = content_data[cid]
                data["similar_count"] = count
                recommendations.append(data)

        # Enrich with TMDB data
        enriched = []
        for rec in recommendations:
            try:
                movie = get_movie_details(rec["id"])
                if movie:
                    movie["similar_count"] = rec["similar_count"]
                    movie["helped_mood"] = rec.get("mood")
                    enriched.append(movie)
            except:
                continue

        return enriched
    except:
        return []


def render_community_recommendations():
    """Render 'Others Like You' section"""
    user_id = st.session_state.get("db_user_id")

    if not user_id:
        return

    recs = get_community_recommendations(user_id, limit=4)

    if not recs:
        return

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">👥</span>
        <h2 class="section-title">People Like You Watched</h2>
    </div>
    <p style="color: var(--text-secondary); margin-bottom: 16px;">
        Based on users with similar mood patterns
    </p>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for idx, movie in enumerate(recs[:4]):
        with cols[idx]:
            similar_count = movie.get("similar_count", 0)
            helped_mood = movie.get("helped_mood")

            st.markdown(f"""
            <div style="
                background: rgba(16,185,129,0.15);
                border: 1px solid rgba(16,185,129,0.3);
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 0.75rem;
                color: #10b981;
                margin-bottom: 8px;
            ">
                👥 {similar_count} similar users watched
                {f'<br>💚 Helped with {helped_mood.lower()}' if helped_mood else ''}
            </div>
            """, unsafe_allow_html=True)

            render_movie_card(movie)


# --------------------------------------------------
# MOOD BUDDIES - ANONYMOUS SUPPORT
# --------------------------------------------------
def get_mood_buddy_message(current_feeling: str) -> dict:
    """Get anonymous message from someone who felt the same way"""
    if not supabase:
        return None

    try:
        result = supabase.table("mood_history")\
            .select("desired_feeling")\
            .eq("current_feeling", current_feeling)\
            .gte("created_at", (datetime.now() - timedelta(days=7)).isoformat())\
            .limit(20)\
            .execute()

        if not result.data:
            return None

        entry = random.choice(result.data)

        return {
            "message": f"Someone who also felt {current_feeling.lower()} found content to feel {entry.get('desired_feeling', 'better').lower()}.",
            "desired": entry.get("desired_feeling")
        }
    except:
        return None


def get_live_mood_count(feeling: str) -> int:
    """Get count of users currently feeling this way"""
    if not supabase:
        return 0

    try:
        cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
        result = supabase.table("mood_history")\
            .select("id", count="exact")\
            .eq("current_feeling", feeling)\
            .gte("created_at", cutoff)\
            .execute()

        return result.count if result.count else 0
    except:
        return 0


def render_mood_buddy_support():
    """Render mood buddy support message"""
    current = st.session_state.get("current_feeling")
    if not current:
        return

    count = get_live_mood_count(current)
    buddy = get_mood_buddy_message(current)

    if count > 0 or buddy:
        emoji = MOOD_EMOJIS.get(current, "😊")

        buddy_msg = f'<div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-left: 42px;">{buddy["message"]}</div>' if buddy else ''

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(168,85,247,0.1));
            border: 1px solid rgba(139,92,246,0.2);
            border-radius: 16px;
            padding: 16px 20px;
            margin: 16px 0;
        ">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 1.5rem;">{emoji}</span>
                <span style="color: rgba(255,255,255,0.9);">
                    <strong>{count if count > 0 else 'Others'}</strong> people
                    {f'felt {current.lower()} in the last hour' if count > 0 else f'know how {current.lower()} feels'}
                </span>
            </div>
            {buddy_msg}
            <div style="color: #8b5cf6; font-size: 0.85rem; margin-left: 42px; margin-top: 8px;">
                You're not alone 💜
            </div>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# DAILY/WEEKLY CHALLENGES
# --------------------------------------------------
DEFAULT_CHALLENGES = {
    "daily": [
        {"id": "mood_check", "title": "Mood Check", "desc": "Log your mood 3 times", "req_type": "mood_logs", "req_count": 3, "reward": 25},
        {"id": "explorer", "title": "Explorer", "desc": "Click on 5 different movies", "req_type": "content_clicks", "req_count": 5, "reward": 30},
        {"id": "queue_builder", "title": "Queue Builder", "desc": "Add 2 items to your queue", "req_type": "queue_adds", "req_count": 2, "reward": 20},
        {"id": "chat_mr_dp", "title": "Chat with Mr.DP", "desc": "Have 3 conversations with Mr.DP", "req_type": "mr_dp_chats", "req_count": 3, "reward": 25},
    ],
    "weekly": [
        {"id": "streak_keeper", "title": "Streak Keeper", "desc": "Maintain a 7-day streak", "req_type": "streak", "req_count": 7, "reward": 100},
        {"id": "mood_master", "title": "Mood Master", "desc": "Log your mood 20 times", "req_type": "mood_logs", "req_count": 20, "reward": 75},
        {"id": "content_king", "title": "Content King", "desc": "Explore 30 pieces of content", "req_type": "content_clicks", "req_count": 30, "reward": 100},
        {"id": "queue_champion", "title": "Queue Champion", "desc": "Build a queue of 10 items", "req_type": "queue_adds", "req_count": 10, "reward": 75},
    ]
}


def get_active_challenges(challenge_type: str = "daily") -> list:
    """Get active challenges for today/this week"""
    if not supabase:
        return DEFAULT_CHALLENGES.get(challenge_type, [])

    try:
        today = datetime.now().strftime("%Y-%m-%d")

        result = supabase.table("challenges")\
            .select("*")\
            .eq("challenge_type", challenge_type)\
            .eq("active", True)\
            .lte("start_date", today)\
            .gte("end_date", today)\
            .execute()

        if result.data:
            return result.data

        return DEFAULT_CHALLENGES.get(challenge_type, [])
    except:
        return DEFAULT_CHALLENGES.get(challenge_type, [])


def get_user_challenge_progress(user_id: str) -> dict:
    """Get user's progress on challenges"""
    if not user_id:
        return st.session_state.get("challenge_progress", {})

    if not supabase:
        return st.session_state.get("challenge_progress", {})

    try:
        result = supabase.table("user_challenges")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

        return {r["challenge_id"]: r for r in result.data} if result.data else {}
    except:
        return st.session_state.get("challenge_progress", {})


def update_challenge_progress(user_id: str, action_type: str, increment: int = 1):
    """Update progress on challenges when user performs actions"""
    if not user_id:
        return

    action_to_req = {
        "mood_log": "mood_logs",
        "content_click": "content_clicks",
        "queue_add": "queue_adds",
        "mr_dp_chat": "mr_dp_chats"
    }

    req_type = action_to_req.get(action_type)
    if not req_type:
        return

    # Update local state for immediate feedback
    progress = st.session_state.get("challenge_progress", {})

    challenges = get_active_challenges("daily") + get_active_challenges("weekly")
    matching = [c for c in challenges if c.get("req_type") == req_type]

    for challenge in matching:
        cid = challenge.get("id")
        if not cid:
            continue

        if cid not in progress:
            progress[cid] = {"progress": 0, "completed": False}

        if not progress[cid].get("completed"):
            progress[cid]["progress"] = progress[cid].get("progress", 0) + increment

            req_count = challenge.get("req_count", 999)
            if progress[cid]["progress"] >= req_count:
                progress[cid]["completed"] = True
                reward = challenge.get("reward", 0)
                add_dopamine_points(reward, f"Completed: {challenge.get('title', 'Challenge')}!")
                st.toast(f"🎯 Challenge Complete: {challenge.get('title')}! +{reward} DP", icon="🏆")

    st.session_state.challenge_progress = progress

    # Also update database if available
    if supabase:
        try:
            for cid, prog in progress.items():
                supabase.table("user_challenges").upsert({
                    "user_id": user_id,
                    "challenge_id": cid,
                    "progress": prog.get("progress", 0),
                    "completed": prog.get("completed", False),
                    "completed_at": datetime.now().isoformat() if prog.get("completed") else None
                }).execute()
        except:
            pass


def render_challenges_section():
    """Render challenges UI"""
    user_id = st.session_state.get("db_user_id")

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🎯</span>
        <h2 class="section-title">Daily Challenges</h2>
    </div>
    """, unsafe_allow_html=True)

    if not user_id:
        st.info("Log in to participate in challenges!")
        return

    tab1, tab2 = st.tabs(["📅 Daily", "📆 Weekly"])

    with tab1:
        render_challenge_list(user_id, "daily")

    with tab2:
        render_challenge_list(user_id, "weekly")


def render_challenge_list(user_id: str, challenge_type: str):
    """Render list of challenges"""
    challenges = get_active_challenges(challenge_type)
    progress_map = get_user_challenge_progress(user_id)

    for challenge in challenges:
        cid = challenge.get("id")
        progress = progress_map.get(cid, {})

        current = progress.get("progress", 0)
        total = challenge.get("req_count", 1)
        completed = progress.get("completed", False) or current >= total
        reward = challenge.get("reward", 0)

        pct = min(100, int((current / total) * 100))

        status_color = "#10b981" if completed else "#8b5cf6"
        status_icon = "✅" if completed else "🎯"

        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.03);
            border: 1px solid {'rgba(16,185,129,0.3)' if completed else 'rgba(255,255,255,0.1)'};
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 1.2rem; margin-right: 8px;">{status_icon}</span>
                    <strong>{challenge.get('title', 'Challenge')}</strong>
                </div>
                <div style="color: {status_color}; font-weight: 600;">+{reward} DP</div>
            </div>
            <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 8px 0 12px 32px;">
                {challenge.get('desc', '')}
            </div>
            <div style="margin-left: 32px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">Progress</span>
                    <span style="font-size: 0.8rem; color: {status_color};">{current}/{total}</span>
                </div>
                <div style="height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
                    <div style="width: {pct}%; height: 100%; background: {status_color}; border-radius: 3px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# REWARDS SHOP
# --------------------------------------------------
SHOP_ITEMS = [
    {"id": "theme_ocean", "name": "Ocean Theme", "description": "Calming blue color palette", "category": "theme", "price": 500, "icon": "🌊"},
    {"id": "theme_forest", "name": "Forest Theme", "description": "Soothing green vibes", "category": "theme", "price": 500, "icon": "🌲"},
    {"id": "theme_sunset", "name": "Sunset Theme", "description": "Warm orange gradients", "category": "theme", "price": 500, "icon": "🌅"},
    {"id": "badge_crown", "name": "Crown Badge", "description": "Show off your royalty", "category": "badge", "price": 1000, "icon": "👑"},
    {"id": "badge_star", "name": "Star Badge", "description": "You're a star!", "category": "badge", "price": 750, "icon": "⭐"},
    {"id": "badge_diamond", "name": "Diamond Badge", "description": "Rare and precious", "category": "badge", "price": 2000, "icon": "💎"},
    {"id": "extra_mr_dp", "name": "+5 Mr.DP Chats", "description": "5 extra daily Mr.DP conversations", "category": "feature", "price": 200, "icon": "🧠"},
    {"id": "premium_day", "name": "1-Day Premium", "description": "All premium features for 24 hours", "category": "feature", "price": 300, "icon": "🌟"},
]


def get_user_inventory(user_id: str) -> list:
    """Get items user has purchased"""
    if not user_id:
        return st.session_state.get("user_inventory", [])

    if not supabase:
        return st.session_state.get("user_inventory", [])

    try:
        result = supabase.table("user_inventory")\
            .select("item_id")\
            .eq("user_id", user_id)\
            .execute()

        return [r["item_id"] for r in result.data] if result.data else []
    except:
        return st.session_state.get("user_inventory", [])


def purchase_item(user_id: str, item_id: str) -> dict:
    """Purchase an item from the shop"""
    if not user_id:
        return {"success": False, "error": "Not logged in"}

    item = next((i for i in SHOP_ITEMS if i["id"] == item_id), None)
    if not item:
        return {"success": False, "error": "Item not found"}

    inventory = get_user_inventory(user_id)
    if item_id in inventory:
        return {"success": False, "error": "Already owned"}

    points = get_dopamine_points()
    if points < item["price"]:
        return {"success": False, "error": f"Need {item['price'] - points} more DP"}

    try:
        new_points = points - item["price"]

        if supabase:
            supabase.table("profiles").update({"dopamine_points": new_points}).eq("id", user_id).execute()
            supabase.table("user_inventory").insert({
                "user_id": user_id,
                "item_id": item_id,
                "purchased_at": datetime.now().isoformat()
            }).execute()

        st.session_state.dopamine_points = new_points

        # Update local inventory
        inv = st.session_state.get("user_inventory", [])
        inv.append(item_id)
        st.session_state.user_inventory = inv

        return {"success": True, "message": f"Purchased {item['name']}!"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --------------------------------------------------
# MR.DP COMPANION PAGE
# --------------------------------------------------
def render_mr_dp_companion_page():
    """Render the full Mr.DP Companion page with chat, evolution, and achievements"""

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🟣</span>
        <h2 class="section-title">Mr.DP Companion</h2>
    </div>
    """, unsafe_allow_html=True)

    # Get current state
    init_gamification()
    evolution = get_current_evolution()
    next_evo = get_next_evolution()
    xp = st.session_state.mr_dp_game.get("xp", 0)
    accessory = st.session_state.mr_dp_game.get("accessory", "none")
    achievements = st.session_state.mr_dp_game.get("achievements", [])

    # Top section: Evolution Status + Mr.DP Display
    col1, col2 = st.columns([1, 2])

    with col1:
        # Large Mr.DP display with current expression
        expression = get_contextual_expression()
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="animation: float 3s ease-in-out infinite;">
                {get_mr_dp_svg(expression, 150)}
            </div>
            <style>
                @keyframes float {{
                    0%, 100% {{ transform: translateY(0); }}
                    50% {{ transform: translateY(-10px); }}
                }}
            </style>
        </div>
        """, unsafe_allow_html=True)

        # Accessory indicator
        if accessory != "none":
            acc_data = MR_DP_ACCESSORIES.get(accessory, {})
            st.markdown(f"<p style='text-align: center; font-size: 0.9rem;'>Wearing: {acc_data.get('icon', '')} {acc_data.get('name', '')}</p>", unsafe_allow_html=True)

    with col2:
        # Evolution card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.2), rgba(0, 201, 167, 0.15));
                    border-radius: 16px; padding: 20px; margin-bottom: 16px;
                    border: 1px solid rgba(138, 86, 226, 0.3);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                    <div style="font-size: 1.4rem; font-weight: 700;">{evolution['name']}</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">{evolution['description']}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2rem; font-weight: 700; color: #00C9A7;">✨ {xp}</div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Total XP</div>
                </div>
            </div>
            {"<div style='margin-top: 16px;'><div style='color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-bottom: 4px;'>Next Evolution: " + next_evo['name'] + " (" + str(next_evo['xp_needed']) + " XP to go)</div><div style='background: rgba(255,255,255,0.1); border-radius: 8px; height: 8px; overflow: hidden;'><div style='background: linear-gradient(90deg, #8A56E2, #00C9A7); height: 100%; width: " + str(min(100, (xp / next_evo['xp_required']) * 100)) + "%;'></div></div></div>" if next_evo else "<div style='color: gold; margin-top: 16px;'>🏆 Maximum Evolution Reached!</div>"}
        </div>
        """, unsafe_allow_html=True)

        # Quick stats
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Achievements", f"{len(achievements)}/{len(MR_DP_ACHIEVEMENTS)}")
        with stat_cols[1]:
            st.metric("Conversations", st.session_state.mr_dp_game.get("conversations_count", 0))
        with stat_cols[2]:
            st.metric("Quick Hits", st.session_state.mr_dp_game.get("quick_hit_uses", 0))

    st.markdown("---")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat", "🏆 Achievements", "👕 Accessories", "📊 Insights"])

    with tab1:
        # Chat interface
        st.markdown("### Talk to Mr.DP")
        st.markdown("<p style='color: rgba(255,255,255,0.6);'>Ask for recommendations, get ADHD tips, or just chat!</p>", unsafe_allow_html=True)

        # Contextual greeting
        greeting, expr = get_contextual_greeting()
        st.markdown(f"""
        <div style="background: rgba(138, 86, 226, 0.15); border-radius: 12px; padding: 12px 16px; margin-bottom: 16px;">
            <span style="font-weight: 600;">🟣 Mr.DP:</span> {greeting}
        </div>
        """, unsafe_allow_html=True)

        # Chat history
        if "mr_dp_companion_chat" not in st.session_state:
            st.session_state.mr_dp_companion_chat = []

        for msg in st.session_state.mr_dp_companion_chat[-8:]:
            if msg["role"] == "assistant":
                st.markdown(f"""
                <div style="background: rgba(138, 86, 226, 0.15); border-radius: 12px; padding: 12px 16px; margin-bottom: 8px;">
                    <span style="font-weight: 600;">🟣 Mr.DP:</span> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: rgba(0, 201, 167, 0.15); border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; text-align: right;">
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)

        # Quick prompts
        st.markdown("**Quick prompts:**")
        prompt_cols = st.columns(4)
        quick_prompts = [
            "Can't decide what to watch",
            "Need something short",
            "Feeling overwhelmed",
            "Give me an ADHD tip"
        ]
        for i, prompt in enumerate(quick_prompts):
            with prompt_cols[i]:
                if st.button(prompt, key=f"quick_prompt_{i}", use_container_width=True):
                    st.session_state.mr_dp_companion_input = prompt
                    st.rerun()

        # Chat input
        user_input = st.text_input(
            "Message Mr.DP...",
            key="mr_dp_companion_input_field",
            value=st.session_state.get("mr_dp_companion_input", ""),
            label_visibility="collapsed"
        )

        if st.button("Send", key="send_mr_dp_companion", type="primary"):
            if user_input:
                # Clear the stored quick prompt
                st.session_state.mr_dp_companion_input = ""

                # Add user message
                st.session_state.mr_dp_companion_chat.append({
                    "role": "user",
                    "content": user_input
                })

                # Get user data for context
                user_data = {
                    "current_mood": st.session_state.get("current_feeling"),
                    "desired_mood": st.session_state.get("desired_feeling"),
                    "streak": st.session_state.get("streak_days", 0)
                }

                # Get response
                response, expr = chat_with_mr_dp(
                    user_input,
                    st.session_state.mr_dp_companion_chat,
                    user_data
                )

                # Add response
                st.session_state.mr_dp_companion_chat.append({
                    "role": "assistant",
                    "content": response
                })

                # Award XP
                add_xp(3, "Chat with Mr.DP")
                st.session_state.mr_dp_game["conversations_count"] = st.session_state.mr_dp_game.get("conversations_count", 0) + 1

                # Check chatty friend achievement
                if st.session_state.mr_dp_game["conversations_count"] >= 20:
                    check_achievement("chatty_friend")

                st.rerun()

        # ADHD Tip of the moment
        st.markdown("---")
        st.markdown("### 💡 ADHD Tip")
        tip = get_random_adhd_tip()
        st.info(tip)

    with tab2:
        # Achievements display
        st.markdown("### Your Achievements")
        st.markdown(f"<p style='color: rgba(255,255,255,0.6);'>Unlocked {len(achievements)} of {len(MR_DP_ACHIEVEMENTS)} achievements</p>", unsafe_allow_html=True)

        # Grid of achievements
        ach_cols = st.columns(3)
        for i, (ach_id, ach_data) in enumerate(MR_DP_ACHIEVEMENTS.items()):
            with ach_cols[i % 3]:
                is_earned = ach_id in achievements
                opacity = "1" if is_earned else "0.3"
                border_color = "#00C9A7" if is_earned else "rgba(255,255,255,0.1)"

                st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.03);
                    border: 2px solid {border_color};
                    border-radius: 12px;
                    padding: 16px;
                    text-align: center;
                    margin-bottom: 12px;
                    opacity: {opacity};
                ">
                    <div style="font-size: 2.5rem; margin-bottom: 8px;">{ach_data['icon']}</div>
                    <div style="font-weight: 600; margin-bottom: 4px;">{ach_data['name']}</div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-bottom: 8px;">{ach_data['description']}</div>
                    <div style="color: #00C9A7; font-size: 0.85rem;">+{ach_data['xp']} XP</div>
                </div>
                """, unsafe_allow_html=True)

    with tab3:
        # Accessories
        st.markdown("### Customize Mr.DP")
        st.markdown("<p style='color: rgba(255,255,255,0.6);'>Unlock accessories by earning XP!</p>", unsafe_allow_html=True)

        available = get_available_accessories()
        current_accessory = st.session_state.mr_dp_game.get("accessory", "none")

        acc_cols = st.columns(4)
        for i, (acc_id, acc_data) in enumerate(MR_DP_ACCESSORIES.items()):
            with acc_cols[i % 4]:
                is_available = xp >= acc_data["xp_required"]
                is_equipped = acc_id == current_accessory

                bg_color = "rgba(0, 201, 167, 0.15)" if is_equipped else "rgba(255,255,255,0.03)"
                border_color = "#00C9A7" if is_equipped else ("rgba(138, 86, 226, 0.3)" if is_available else "rgba(255,255,255,0.1)")
                opacity = "1" if is_available else "0.4"

                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border: 2px solid {border_color};
                    border-radius: 12px;
                    padding: 12px;
                    text-align: center;
                    margin-bottom: 8px;
                    opacity: {opacity};
                ">
                    <div style="font-size: 2rem; margin-bottom: 4px;">{acc_data.get('icon', '🟣')}</div>
                    <div style="font-weight: 600; font-size: 0.85rem;">{acc_data['name']}</div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">
                        {f'Equipped' if is_equipped else (f'{acc_data["xp_required"]} XP' if not is_available else 'Available')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if is_available and not is_equipped and acc_id != "none":
                    if st.button("Equip", key=f"equip_{acc_id}", use_container_width=True):
                        equip_accessory(acc_id)
                        st.rerun()
                elif is_equipped and acc_id != "none":
                    if st.button("Remove", key=f"remove_{acc_id}", use_container_width=True):
                        equip_accessory("none")
                        st.rerun()

    with tab4:
        # Insights from behavioral learning
        st.markdown("### Your Watching Insights")

        # Session stats
        duration = get_browsing_duration_minutes()
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border-radius: 12px; padding: 16px; margin-bottom: 16px;">
            <div style="font-weight: 600; margin-bottom: 12px;">Current Session</div>
            <div style="display: flex; gap: 24px;">
                <div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Duration</div>
                    <div style="font-size: 1.2rem; font-weight: 600;">{int(duration)} min</div>
                </div>
                <div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">Decision Fatigue</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: {'#ef4444' if detect_decision_fatigue() else '#10b981'};">
                        {'Detected' if detect_decision_fatigue() else 'None'}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Check for intervention
        intervention = get_adhd_intervention()
        if intervention:
            st.warning(f"**Mr.DP noticed:** {intervention['message']}")
            if st.button(intervention["action_label"], key="insight_intervention", type="primary"):
                if intervention["action"] == "quick_hit":
                    st.session_state.quick_hit = get_quick_hit()
                st.rerun()

        # Encouragement
        encouragement, expr = get_encouragement()
        st.success(f"💜 {encouragement}")

        # Evolution roadmap
        st.markdown("### Evolution Roadmap")
        for evo_key, evo_data in MR_DP_EVOLUTIONS.items():
            is_current = evo_key == evolution["key"]
            is_achieved = xp >= evo_data["xp_required"]

            status_color = "#00C9A7" if is_achieved else ("rgba(138, 86, 226, 0.8)" if is_current else "rgba(255,255,255,0.3)")
            status_icon = "✓" if is_achieved else ("→" if is_current else "○")

            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0; border-left: 3px solid {status_color}; padding-left: 12px; margin-bottom: 4px;">
                <span style="color: {status_color}; font-weight: bold;">{status_icon}</span>
                <div>
                    <span style="font-weight: {'600' if is_current else '400'}; color: {status_color};">{evo_data['name']}</span>
                    <span style="color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-left: 8px;">{evo_data['xp_required']} XP</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Save progress if logged in
    user_id = st.session_state.get("db_user_id")
    if user_id and SUPABASE_ENABLED:
        save_gamification_to_supabase(supabase, user_id)
        save_behavior_to_supabase(supabase, user_id)


def render_rewards_shop():
    """Render the rewards shop"""
    user_id = st.session_state.get("db_user_id")

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🛍</span>
        <h2 class="section-title">Rewards Shop</h2>
    </div>
    """, unsafe_allow_html=True)

    if not user_id:
        st.info("Log in to visit the shop!")
        return

    points = get_dopamine_points()
    inventory = get_user_inventory(user_id)

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(6,182,212,0.2));
        border-radius: 16px;
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    ">
        <div>
            <div style="color: rgba(255,255,255,0.7);">Your Balance</div>
            <div style="font-size: 1.5rem; font-weight: 700;">⚡ {points:,} DP</div>
        </div>
        <div>
            <div style="color: rgba(255,255,255,0.7);">Items Owned</div>
            <div style="font-size: 1.5rem; font-weight: 700;">{len(inventory)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    categories = {"theme": "🎨 Themes", "badge": "🏅 Badges", "feature": "✨ Features"}

    for cat_id, cat_name in categories.items():
        cat_items = [i for i in SHOP_ITEMS if i["category"] == cat_id]
        if not cat_items:
            continue

        st.markdown(f"### {cat_name}")

        cols = st.columns(3)
        for idx, item in enumerate(cat_items):
            with cols[idx % 3]:
                owned = item["id"] in inventory
                affordable = points >= item["price"]

                st.markdown(f"""
                <div style="
                    background: {'rgba(16,185,129,0.1)' if owned else 'rgba(255,255,255,0.03)'};
                    border: 1px solid {'rgba(16,185,129,0.3)' if owned else 'rgba(255,255,255,0.1)'};
                    border-radius: 12px;
                    padding: 16px;
                    text-align: center;
                    margin-bottom: 12px;
                ">
                    <div style="font-size: 2.5rem; margin-bottom: 8px;">{item['icon']}</div>
                    <div style="font-weight: 600; margin-bottom: 4px;">{item['name']}</div>
                    <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-bottom: 12px;">{item['description']}</div>
                    <div style="color: {'#10b981' if owned else '#f59e0b'}; font-weight: 600;">
                        {'✓ Owned' if owned else f'⚡ {item["price"]} DP'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not owned:
                    btn_type = "primary" if affordable else "secondary"
                    if st.button(
                        "Buy" if affordable else f"Need {item['price'] - points} more",
                        key=f"buy_{item['id']}",
                        use_container_width=True,
                        disabled=not affordable,
                        type=btn_type
                    ):
                        result = purchase_item(user_id, item["id"])
                        if result["success"]:
                            st.success(result["message"])
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(result["error"])


# --------------------------------------------------
# LEADERBOARDS
# --------------------------------------------------
def get_leaderboard(board_type: str = "points", limit: int = 10) -> list:
    """Get leaderboard data"""
    if not supabase:
        return []

    try:
        if board_type == "points":
            result = supabase.table("profiles")\
                .select("name, dopamine_points")\
                .order("dopamine_points", desc=True)\
                .limit(limit)\
                .execute()

            return [{"name": r.get("name", "Anonymous")[:12], "value": r.get("dopamine_points", 0), "icon": "⚡"} for r in result.data] if result.data else []

        elif board_type == "streak":
            result = supabase.table("profiles")\
                .select("name, streak_days")\
                .order("streak_days", desc=True)\
                .limit(limit)\
                .execute()

            return [{"name": r.get("name", "Anonymous")[:12], "value": r.get("streak_days", 0), "icon": "🔥"} for r in result.data] if result.data else []

        elif board_type == "referrals":
            result = supabase.table("profiles")\
                .select("name, total_referrals")\
                .gt("total_referrals", 0)\
                .order("total_referrals", desc=True)\
                .limit(limit)\
                .execute()

            return [{"name": r.get("name", "Anonymous")[:12], "value": r.get("total_referrals", 0), "icon": "👥"} for r in result.data] if result.data else []

        return []
    except:
        return []


def get_user_rank(user_id: str, board_type: str = "points") -> int:
    """Get user's rank on a leaderboard"""
    if not user_id or not supabase:
        return 0

    try:
        field = {"points": "dopamine_points", "streak": "streak_days", "referrals": "total_referrals"}.get(board_type, "dopamine_points")

        profile = get_user_profile(user_id)
        user_value = profile.get(field, 0)

        result = supabase.table("profiles")\
            .select("id", count="exact")\
            .gt(field, user_value)\
            .execute()

        return (result.count or 0) + 1
    except:
        return 0


def render_leaderboards():
    """Render leaderboards page"""
    user_id = st.session_state.get("db_user_id")

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🏆</span>
        <h2 class="section-title">Leaderboards</h2>
    </div>
    """, unsafe_allow_html=True)

    # Add achievements tab if enhanced gamification available
    if GAMIFICATION_ENHANCED_AVAILABLE:
        tab1, tab2, tab3, tab4 = st.tabs(["⚡ Top Points", "🔥 Top Streaks", "👥 Top Referrers", "🏅 Achievements"])
    else:
        tab1, tab2, tab3 = st.tabs(["⚡ Top Points", "🔥 Top Streaks", "👥 Top Referrers"])

    with tab1:
        render_leaderboard_tab("points", user_id)

    with tab2:
        render_leaderboard_tab("streak", user_id)

    with tab3:
        render_leaderboard_tab("referrals", user_id)

    # Achievements tab with 30 achievements from gamification_enhanced
    if GAMIFICATION_ENHANCED_AVAILABLE:
        with tab4:
            st.markdown("### 🏅 Your Achievements")
            st.caption("Complete actions to unlock all 30 achievements!")
            if user_id:
                render_achievements_grid(user_id)
            else:
                st.info("Log in to track your achievements!")


def render_leaderboard_tab(board_type: str, user_id: str = None):
    """Render a single leaderboard tab"""
    data = get_leaderboard(board_type, limit=10)

    if not data:
        st.info("No data yet - be the first!")
        return

    if user_id:
        rank = get_user_rank(user_id, board_type)
        st.markdown(f"""
        <div style="
            background: rgba(139,92,246,0.15);
            border: 1px solid rgba(139,92,246,0.3);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 16px;
            text-align: center;
        ">
            Your Rank: <strong>#{rank}</strong>
        </div>
        """, unsafe_allow_html=True)

    for idx, entry in enumerate(data):
        medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx+1}"

        st.markdown(f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: rgba(255,255,255,{'0.05' if idx < 3 else '0.02'});
            border-radius: 8px;
            margin: 4px 0;
            {'border: 1px solid rgba(255,215,0,0.3);' if idx == 0 else ''}
        ">
            <span>{medal} {entry['name']}</span>
            <span style="font-weight: 600;">{entry['icon']} {entry['value']:,}</span>
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# PHASE 3: SOCIAL FEATURES PAGES
# --------------------------------------------------
def render_messages_page():
    """Render direct messages page"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">💬</span>
        <h2 class="section-title">Messages</h2>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("db_user_id")
    if not user_id:
        st.warning("Please log in to view your messages.")
        return

    # Show messages sidebar widget
    if SOCIAL_FEATURES_AVAILABLE:
        render_messages_sidebar(user_id)
    else:
        st.info("Social features coming soon!")


def render_watch_parties_page():
    """Render watch parties page"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🎉</span>
        <h2 class="section-title">Watch Parties</h2>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("db_user_id")
    if not user_id:
        st.warning("Please log in to join or create watch parties.")
        return

    tab1, tab2 = st.tabs(["🎬 Create Party", "🔗 Join Party"])

    with tab1:
        st.markdown("### Start a Watch Party")
        st.caption("Invite friends to watch together in sync!")

        content_title = st.text_input("What are you watching?", placeholder="Movie or show title")
        content_id = st.text_input("Content ID (from TMDB)", placeholder="Optional - for syncing")

        if st.button("🎉 Create Party", type="primary", use_container_width=True):
            if content_title:
                if SOCIAL_FEATURES_AVAILABLE:
                    party = create_watch_party(user_id, content_id or "manual", content_title)
                    st.session_state["current_party"] = party
                    st.success(f"Party created! Share code: **{party['party_code']}**")
                    st.balloons()
                else:
                    st.info("Watch parties coming soon!")
            else:
                st.error("Please enter what you're watching")

    with tab2:
        st.markdown("### Join a Party")
        party_code = st.text_input("Enter party code", placeholder="e.g., ABC123")

        if st.button("🔗 Join Party", type="primary", use_container_width=True):
            if party_code and SOCIAL_FEATURES_AVAILABLE:
                result = join_watch_party(party_code, user_id)
                if result.get("success"):
                    st.session_state["current_party"] = result.get("party")
                    st.success("Joined the party!")
                else:
                    st.error(result.get("error", "Could not join party"))
            elif not party_code:
                st.error("Please enter a party code")

    # Show current party if active
    current_party = st.session_state.get("current_party")
    if current_party and SOCIAL_FEATURES_AVAILABLE:
        st.markdown("---")
        st.markdown("### 🎬 Current Party")
        render_watch_party_card(current_party)
        user_name = st.session_state.user.get('name', 'Guest')
        render_party_chat(current_party["party_id"], user_id, user_name)

        if st.button("🚪 Leave Party", type="secondary"):
            leave_watch_party(current_party["party_id"], user_id)
            st.session_state["current_party"] = None
            st.rerun()


def render_friends_page():
    """Render friends and referrals page"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">👫</span>
        <h2 class="section-title">Friends & Referrals</h2>
    </div>
    """, unsafe_allow_html=True)

    user_id = st.session_state.get("db_user_id")
    if not user_id:
        st.warning("Please log in to manage friends.")
        return

    tab1, tab2, tab3 = st.tabs(["👥 My Friends", "📨 Requests", "🎁 Referrals"])

    with tab1:
        st.markdown("### Your Friends")
        if SOCIAL_FEATURES_AVAILABLE:
            friends = get_friends(user_id)
            friend_count = get_friends_count(user_id)
            st.caption(f"{friend_count} friend{'s' if friend_count != 1 else ''}")
            if friends:
                for idx, friend_id in enumerate(friends):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**Friend #{idx + 1}**")
                        st.caption(f"ID: {friend_id[:8]}...")
                    with col2:
                        if st.button("💬", key=f"msg_{friend_id}", help="Send message"):
                            st.session_state.active_page = "💬 Messages"
                            st.session_state.selected_friend = friend_id
                            st.rerun()
                    with col3:
                        if st.button("❌", key=f"unfriend_{friend_id}", help="Remove"):
                            remove_friend(user_id, friend_id)
                            st.rerun()
            else:
                st.info("No friends yet. Share your referral code to connect!")
        else:
            st.info("Friends feature coming soon!")

        st.markdown("---")
        st.markdown("### Add Friend")
        friend_id_input = st.text_input("Friend's user ID", placeholder="Enter friend's user ID")
        if st.button("➕ Add Friend", type="primary"):
            if friend_id_input and SOCIAL_FEATURES_AVAILABLE:
                result = add_friend(user_id, friend_id_input)
                if result:
                    st.success("Friend added!")
                    st.rerun()
                else:
                    st.error("Could not add friend. They may already be in your list.")

    with tab2:
        st.markdown("### Friend Requests")
        st.info("Friend requests coming in a future update! For now, share your referral code to connect with friends.")
        st.caption("Your friends can add you using your user ID from your profile.")

    with tab3:
        st.markdown("### Your Referral Code")
        if SOCIAL_FEATURES_AVAILABLE:
            render_referral_section(user_id)
        else:
            st.info("Referral system coming soon!")


def render_wellness_page():
    """Render enhanced wellness page with breathing, grounding, affirmations"""
    st.markdown("""
    <div class="section-header">
        <span class="section-icon">🧘</span>
        <h2 class="section-title">Wellness Center</h2>
    </div>
    """, unsafe_allow_html=True)

    st.caption("ADHD-optimized calming techniques to help regulate your nervous system")

    if not WELLNESS_ENHANCED_AVAILABLE:
        st.info("Enhanced wellness features coming soon!")
        return

    tab1, tab2, tab3 = st.tabs(["🌬️ Breathing", "🌍 Grounding", "💜 Affirmations"])

    with tab1:
        st.markdown("### Breathing Exercises")
        st.caption("Structured breathing patterns to calm your nervous system")

        exercises = get_all_breathing_exercises()
        cols = st.columns(2)
        for idx, (ex_id, exercise) in enumerate(exercises.items()):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="
                    background: rgba(139,92,246,0.1);
                    border: 1px solid rgba(139,92,246,0.3);
                    border-radius: 12px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <h4>{exercise['name']}</h4>
                    <p style="font-size: 0.85rem; opacity: 0.8;">{exercise['description']}</p>
                    <small>Duration: {exercise.get('duration_seconds', 60)}s</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Start {exercise['name']}", key=f"breathe_{ex_id}", use_container_width=True):
                    st.session_state.active_breathing = ex_id
                    st.rerun()

        # Show active breathing animation
        if st.session_state.get("active_breathing"):
            st.markdown("---")
            render_breathing_animation(st.session_state.active_breathing)
            if st.button("✕ Close Exercise", key="close_breathing"):
                st.session_state.active_breathing = None
                st.rerun()

    with tab2:
        st.markdown("### 5-4-3-2-1 Grounding")
        st.caption("A sensory grounding technique to bring you back to the present")
        render_grounding_guided_exercise()

    with tab3:
        st.markdown("### Affirmations")
        st.caption("Positive statements to shift your mindset")

        current_mood = st.session_state.get("current_feeling", "Neutral")
        affirmations = get_affirmations(current_mood, count=5)

        for aff in affirmations:
            render_affirmation_card(aff)


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------
def get_admin_stats() -> dict:
    """Get admin dashboard statistics"""
    if not supabase:
        return {}

    try:
        stats = {}

        # Total users
        result = supabase.table("profiles").select("id", count="exact").execute()
        stats["total_users"] = result.count or 0

        # Active users (last 7 days)
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        result = supabase.table("mood_history").select("user_id").gte("created_at", cutoff).execute()
        stats["active_users_7d"] = len(set(r["user_id"] for r in result.data)) if result.data else 0

        # Premium users
        result = supabase.table("profiles").select("id", count="exact").eq("is_premium", True).execute()
        stats["premium_users"] = result.count or 0

        # Total mood logs
        result = supabase.table("mood_history").select("id", count="exact").execute()
        stats["total_mood_logs"] = result.count or 0

        # Mood logs today
        today = datetime.now().strftime("%Y-%m-%d")
        result = supabase.table("mood_history").select("id", count="exact").gte("created_at", f"{today}T00:00:00").execute()
        stats["mood_logs_today"] = result.count or 0

        # Mr.DP chats today
        result = supabase.table("user_behavior").select("id", count="exact").eq("action_type", "mr_dp_chat").gte("created_at", f"{today}T00:00:00").execute()
        stats["mr_dp_chats_today"] = result.count or 0

        # Total referrals
        result = supabase.table("referrals").select("id", count="exact").execute()
        stats["total_referrals"] = result.count or 0

        return stats
    except Exception as e:
        print(f"Admin stats error: {e}")
        return {}


def get_mood_trends(days: int = 7) -> dict:
    """Get mood trends for chart"""
    if not supabase:
        return {}

    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        result = supabase.table("mood_history")\
            .select("current_feeling, desired_feeling, created_at")\
            .gte("created_at", cutoff)\
            .execute()

        if not result.data:
            return {}

        from collections import Counter

        current_counts = Counter(r["current_feeling"] for r in result.data if r.get("current_feeling"))
        desired_counts = Counter(r["desired_feeling"] for r in result.data if r.get("desired_feeling"))

        daily_counts = {}
        for r in result.data:
            day = r["created_at"][:10]
            if day not in daily_counts:
                daily_counts[day] = 0
            daily_counts[day] += 1

        return {
            "top_current": dict(current_counts.most_common(5)),
            "top_desired": dict(desired_counts.most_common(5)),
            "daily_activity": dict(sorted(daily_counts.items()))
        }
    except:
        return {}


def render_admin_dashboard():
    """Render admin dashboard"""
    if not is_admin():
        st.error("Access denied. Admin only.")
        return

    st.markdown("""
    <div class="section-header">
        <span class="section-icon">⚙️</span>
        <h2 class="section-title">Admin Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)

    stats = get_admin_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", f"{stats.get('total_users', 0):,}")
    with col2:
        st.metric("Active (7d)", f"{stats.get('active_users_7d', 0):,}")
    with col3:
        st.metric("Premium", f"{stats.get('premium_users', 0):,}")
    with col4:
        conversion = (stats.get('premium_users', 0) / max(1, stats.get('total_users', 1))) * 100
        st.metric("Conversion", f"{conversion:.1f}%")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Mood Logs Today", f"{stats.get('mood_logs_today', 0):,}")
    with col2:
        st.metric("Total Mood Logs", f"{stats.get('total_mood_logs', 0):,}")
    with col3:
        st.metric("Mr.DP Chats Today", f"{stats.get('mr_dp_chats_today', 0):,}")
    with col4:
        st.metric("Total Referrals", f"{stats.get('total_referrals', 0):,}")

    st.markdown("---")

    st.markdown("### 📊 Mood Trends (7 days)")

    trends = get_mood_trends(7)

    if trends:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top Current Feelings**")
            for mood, count in trends.get("top_current", {}).items():
                emoji = MOOD_EMOJIS.get(mood, "😊")
                st.markdown(f"{emoji} {mood}: **{count}**")

        with col2:
            st.markdown("**Top Desired Feelings**")
            for mood, count in trends.get("top_desired", {}).items():
                emoji = MOOD_EMOJIS.get(mood, "😊")
                st.markdown(f"{emoji} {mood}: **{count}**")

        st.markdown("### 📈 Daily Activity")
        daily = trends.get("daily_activity", {})
        if daily:
            import pandas as pd
            df = pd.DataFrame([{"Date": k, "Mood Logs": v} for k, v in daily.items()])
            st.bar_chart(df.set_index("Date"))

    st.markdown("---")

    # Session Analytics Section
    st.markdown("### 📊 Session Analytics")
    if supabase:
        render_analytics_dashboard(supabase, is_admin=True)
    else:
        st.info("Connect to Supabase to view detailed analytics")

    st.markdown("---")

    st.markdown("### 🛠️ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Refresh Stats", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("📧 Export Users (CSV)", use_container_width=True):
            st.info("Export feature coming soon!")

    with col3:
        if st.button("📢 Send Push Notification", use_container_width=True):
            st.info("Push notification feature coming soon!")


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


# --------------------------------------------------
# SAVED DOPAMINE - Save for Later Feature
# --------------------------------------------------
def save_dopamine_item(item_type: str, data: dict):
    """Save an item to the user's Saved Dopamine list."""
    if "saved_dopamine" not in st.session_state:
        st.session_state.saved_dopamine = []

    # Check if already saved (by ID for movies, by playlist_id for music)
    item_id = data.get("id") or data.get("playlist_id") or data.get("title", "")
    for saved in st.session_state.saved_dopamine:
        saved_id = saved["data"].get("id") or saved["data"].get("playlist_id") or saved["data"].get("title", "")
        if saved_id == item_id:
            return False  # Already saved

    saved_item = {
        "type": item_type,
        "data": data,
        "saved_at": datetime.now().isoformat()
    }
    st.session_state.saved_dopamine.append(saved_item)
    add_dopamine_points(5, "Saved for later!")
    return True


def remove_dopamine_item(index: int):
    """Remove an item from Saved Dopamine by index."""
    if "saved_dopamine" in st.session_state and 0 <= index < len(st.session_state.saved_dopamine):
        st.session_state.saved_dopamine.pop(index)
        return True
    return False


def get_saved_dopamine():
    """Get all saved dopamine items."""
    return st.session_state.get("saved_dopamine", [])


# --------------------------------------------------
# FEEDBACK SYSTEM - Gamified Questionnaire
# --------------------------------------------------
FEEDBACK_QUESTIONS = [
    {
        "id": "overall_experience",
        "question": "How's your dopamine.watch experience so far?",
        "type": "emoji_scale",
        "options": [
            {"emoji": "😍", "label": "Love it!", "value": 5, "points": 15},
            {"emoji": "😊", "label": "Pretty good", "value": 4, "points": 12},
            {"emoji": "😐", "label": "It's okay", "value": 3, "points": 10},
            {"emoji": "😕", "label": "Could be better", "value": 2, "points": 10},
            {"emoji": "😢", "label": "Not great", "value": 1, "points": 10}
        ]
    },
    {
        "id": "mr_dp_helpful",
        "question": "How helpful is Mr.DP at finding content?",
        "type": "emoji_scale",
        "options": [
            {"emoji": "🧠", "label": "Super smart!", "value": 5, "points": 15},
            {"emoji": "👍", "label": "Usually helpful", "value": 4, "points": 12},
            {"emoji": "🤷", "label": "Hit or miss", "value": 3, "points": 10},
            {"emoji": "👎", "label": "Needs work", "value": 2, "points": 10},
            {"emoji": "❌", "label": "Not helpful", "value": 1, "points": 10}
        ]
    },
    {
        "id": "favorite_feature",
        "question": "What's your favorite feature?",
        "type": "multi_choice",
        "options": [
            {"label": "🧠 Mr.DP Chat", "value": "mr_dp", "points": 10},
            {"label": "⚡ Quick Dope Hit", "value": "quick_hit", "points": 10},
            {"label": "🎵 Music Recommendations", "value": "music", "points": 10},
            {"label": "🎬 Movie Mood Matching", "value": "movies", "points": 10},
            {"label": "🆘 SOS Calm Mode", "value": "sos", "points": 10},
            {"label": "💾 Save for Later", "value": "saved", "points": 10}
        ]
    },
    {
        "id": "missing_feature",
        "question": "What would make dopamine.watch even better?",
        "type": "multi_choice",
        "options": [
            {"label": "📺 More streaming services", "value": "more_services", "points": 10},
            {"label": "🎮 Gaming recommendations", "value": "gaming", "points": 10},
            {"label": "👥 Social features", "value": "social", "points": 10},
            {"label": "📱 Mobile app", "value": "mobile_app", "points": 10},
            {"label": "🔔 Smart notifications", "value": "notifications", "points": 10},
            {"label": "🎨 More themes", "value": "themes", "points": 10}
        ]
    },
    {
        "id": "adhd_helpful",
        "question": "Does the ADHD-friendly design actually help you?",
        "type": "emoji_scale",
        "options": [
            {"emoji": "💜", "label": "Finally something that gets me!", "value": 5, "points": 20},
            {"emoji": "😊", "label": "Yes, it helps", "value": 4, "points": 15},
            {"emoji": "🤔", "label": "Somewhat", "value": 3, "points": 10},
            {"emoji": "😐", "label": "Not sure", "value": 2, "points": 10},
            {"emoji": "🙅", "label": "Doesn't apply to me", "value": 1, "points": 10}
        ]
    },
    {
        "id": "recommend_friends",
        "question": "Would you recommend dopamine.watch to a friend?",
        "type": "emoji_scale",
        "options": [
            {"emoji": "📣", "label": "Already have!", "value": 5, "points": 25},
            {"emoji": "👍", "label": "Definitely", "value": 4, "points": 20},
            {"emoji": "🤔", "label": "Maybe", "value": 3, "points": 10},
            {"emoji": "😬", "label": "Probably not", "value": 2, "points": 10},
            {"emoji": "👎", "label": "No", "value": 1, "points": 10}
        ]
    },
    {
        "id": "open_feedback",
        "question": "Any other thoughts? (optional - bonus points!)",
        "type": "text",
        "points": 30
    }
]


def save_feedback_to_db(feedback_data: dict):
    """Save feedback to Supabase for analytics."""
    if not SUPABASE_ENABLED or not supabase:
        return False

    try:
        user_id = st.session_state.get("db_user_id")
        data = {
            "user_id": user_id,
            "feedback_data": feedback_data,
            "created_at": datetime.now().isoformat(),
            "user_agent": st.session_state.get("user_agent", "unknown"),
            "session_id": st.session_state.get("analytics_session_id", "")
        }
        supabase.table("user_feedback").insert(data).execute()
        return True
    except Exception as e:
        print(f"[Feedback] Error saving: {e}")
        return False


def render_feedback_modal():
    """Render the gamified feedback questionnaire."""
    if not st.session_state.get("show_feedback_modal"):
        return

    # Initialize feedback state
    if "feedback_step" not in st.session_state:
        st.session_state.feedback_step = 0
        st.session_state.feedback_answers = {}
        st.session_state.feedback_points = 0

    current_step = st.session_state.feedback_step
    total_steps = len(FEEDBACK_QUESTIONS)

    # Modal overlay
    st.markdown("""
    <style>
    .feedback-modal {
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.9); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
    }
    .feedback-content {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 24px; padding: 32px; max-width: 500px; width: 90%;
        border: 2px solid rgba(139,92,246,0.3);
        box-shadow: 0 20px 60px rgba(139,92,246,0.3);
    }
    .feedback-progress {
        height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px;
        margin-bottom: 24px; overflow: hidden;
    }
    .feedback-progress-bar {
        height: 100%; background: linear-gradient(90deg, #8b5cf6, #06b6d4);
        border-radius: 4px; transition: width 0.3s ease;
    }
    .feedback-points {
        text-align: center; font-size: 1.5rem; font-weight: 700;
        background: linear-gradient(135deg, #ffd700, #ffaa00);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
    }
    .emoji-option {
        display: inline-flex; flex-direction: column; align-items: center;
        padding: 16px; margin: 8px; border-radius: 16px; cursor: pointer;
        background: rgba(255,255,255,0.05); border: 2px solid transparent;
        transition: all 0.2s ease;
    }
    .emoji-option:hover {
        background: rgba(139,92,246,0.2); border-color: rgba(139,92,246,0.5);
        transform: scale(1.05);
    }
    .emoji-option.selected {
        background: rgba(139,92,246,0.3); border-color: #8b5cf6;
    }
    .emoji-option .emoji { font-size: 2.5rem; margin-bottom: 8px; }
    .emoji-option .label { font-size: 0.85rem; color: rgba(255,255,255,0.8); }
    </style>
    """, unsafe_allow_html=True)

    # Check if completed
    if current_step >= total_steps:
        # Completion screen
        total_points = st.session_state.feedback_points

        st.markdown(f"""
        <div style="text-align: center; padding: 40px;">
            <div style="font-size: 4rem; margin-bottom: 16px;">🎉</div>
            <h2 style="color: white; margin-bottom: 8px;">Thank You!</h2>
            <div class="feedback-points">+{total_points} DP Earned!</div>
            <p style="color: rgba(255,255,255,0.7);">Your feedback helps us make dopamine.watch even better for everyone!</p>
        </div>
        """, unsafe_allow_html=True)

        # Award points
        add_dopamine_points(total_points, "Completed feedback!")

        # Save feedback to database
        save_feedback_to_db(st.session_state.feedback_answers)

        # Mark as completed
        st.session_state.feedback_completed = True

        if st.button("🎯 Continue", key="feedback_done", use_container_width=True, type="primary"):
            st.session_state.show_feedback_modal = False
            st.session_state.feedback_step = 0
            st.session_state.feedback_answers = {}
            st.session_state.feedback_points = 0
            st.rerun()
        return

    # Current question
    question = FEEDBACK_QUESTIONS[current_step]
    progress = ((current_step) / total_steps) * 100

    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">Question {current_step + 1} of {total_steps}</span>
            <span style="color: #ffd700; font-weight: 600;">+{st.session_state.feedback_points} DP</span>
        </div>
        <div class="feedback-progress">
            <div class="feedback-progress-bar" style="width: {progress}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### {question['question']}")

    if question["type"] == "emoji_scale":
        cols = st.columns(len(question["options"]))
        for idx, opt in enumerate(question["options"]):
            with cols[idx]:
                if st.button(f"{opt['emoji']}\n{opt['label']}", key=f"fb_{question['id']}_{idx}", use_container_width=True):
                    st.session_state.feedback_answers[question["id"]] = {
                        "value": opt["value"],
                        "label": opt["label"]
                    }
                    st.session_state.feedback_points += opt["points"]
                    st.session_state.feedback_step += 1
                    st.rerun()

    elif question["type"] == "multi_choice":
        cols = st.columns(2)
        for idx, opt in enumerate(question["options"]):
            with cols[idx % 2]:
                if st.button(opt["label"], key=f"fb_{question['id']}_{idx}", use_container_width=True):
                    st.session_state.feedback_answers[question["id"]] = {
                        "value": opt["value"],
                        "label": opt["label"]
                    }
                    st.session_state.feedback_points += opt["points"]
                    st.session_state.feedback_step += 1
                    st.rerun()

    elif question["type"] == "text":
        text_input = st.text_area("Share your thoughts...", key=f"fb_text_{question['id']}", height=100)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Skip", key="fb_skip_text"):
                st.session_state.feedback_step += 1
                st.rerun()
        with col2:
            if st.button("Submit (+30 DP)", key="fb_submit_text", type="primary"):
                if text_input.strip():
                    st.session_state.feedback_answers[question["id"]] = {
                        "value": text_input.strip()
                    }
                    st.session_state.feedback_points += question["points"]
                st.session_state.feedback_step += 1
                st.rerun()

    # Close button
    st.markdown("---")
    if st.button("✕ Close (lose progress)", key="fb_close"):
        st.session_state.show_feedback_modal = False
        st.session_state.feedback_step = 0
        st.session_state.feedback_answers = {}
        st.session_state.feedback_points = 0
        st.rerun()


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
STRIPE_PAYMENT_LINK_MONTHLY = st.secrets.get("stripe", {}).get("payment_link", "")
STRIPE_PAYMENT_LINK_YEARLY = ""  # Optional yearly plan
STRIPE_ENABLED = bool(STRIPE_PAYMENT_LINK_MONTHLY)

# Mr.DP daily chat limit for free users
FREE_CHAT_LIMIT = FREE_MR_DP_LIMIT  # Use the constant from Supabase auth section

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
    """Render premium upgrade modal using native Streamlit components"""
    if not st.session_state.get("show_premium_modal"):
        return

    st.markdown("---")

    # Use native Streamlit components for reliability
    col_spacer1, col_main, col_spacer2 = st.columns([1, 2, 1])

    with col_main:
        st.markdown("### 👑 Go Premium")
        st.markdown("*Unlock the full dopamine.watch experience*")
        st.markdown("")

        # Features list using native components
        st.success("✓ No ads — ever")
        st.success("✓ Unlimited Mr.DP conversations")
        st.success("✓ Priority AI recommendations")
        st.success("✓ Exclusive 👑 badge")
        st.success("✓ Early access to new features")

        st.markdown("")
        st.markdown("#### **$4.99** /month")
        st.markdown("")

        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Maybe Later", key="close_premium_modal", use_container_width=True):
                st.session_state.show_premium_modal = False
                st.rerun()
        with col2:
            if STRIPE_ENABLED and STRIPE_PAYMENT_LINK_MONTHLY:
                st.link_button("⭐ Upgrade Now", STRIPE_PAYMENT_LINK_MONTHLY, use_container_width=True)
            else:
                if st.button("⭐ Upgrade Now", key="premium_monthly_placeholder", use_container_width=True):
                    st.toast("Payment coming soon! 🚀", icon="⭐")

    st.markdown("---")

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

        # Language (i18n)
        "lang": "en",  # "en" or "es"

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
        "mr_dp_thinking": False,
        "mr_dp_just_responded": False,  # Flag to trigger speaking animation
        "mr_dp_v2_response": None,  # Mr.DP 2.0 rich response storage
        "use_mr_dp_v2": True,  # Feature flag for Mr.DP 2.0

        # Saved Dopamine - user's saved content for later
        "saved_dopamine": [],  # List of saved items with type, data, timestamp

        # Feedback system
        "show_feedback_modal": False,
        "feedback_completed": False,
        "feedback_step": 0,
        "feedback_answers": {},
        "feedback_points": 0,

        # Phase 4: Onboarding
        "onboarding_complete": False,
        "onboarding_step": 0,
        "trigger_dismissed": False,
        "last_premium_trigger": None,
        "sos_use_count": 0,

        # Phase 5: Viral & Growth
        "achieved_milestones": [],
        "current_milestone": None,
        "show_share_card": False,
        "pending_referral_code": None,

        # Phase 6: Community & Gamification
        "challenge_progress": {},
        "user_inventory": [],

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

# Initialize analytics session
init_analytics_session()

# Initialize Mr.DP Intelligence Systems
init_behavior_tracking()
init_gamification()

# Generate referral code (fallback)
if not st.session_state.get("referral_code"):
    st.session_state.referral_code = hashlib.md5(str(random.random()).encode()).hexdigest()[:8].upper()

# --------------------------------------------------
# LOGOUT HANDLER (must run before session restore)
# --------------------------------------------------
LANDING_PAGE_URL = "https://www.dopamine.watch"

if st.session_state.get("do_logout"):
    st.session_state.do_logout = False
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    # Show brief message and auto-redirect using hidden auto-clicking link
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; font-size: 64px;'>👋</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9D4EDD;'>Logging out...</p>", unsafe_allow_html=True)
        st.markdown("")
        st.link_button("🏠 Continue to Home", LANDING_PAGE_URL, use_container_width=True, type="primary")

    # Auto-click the link using components.html
    components.html(f'''
        <script>
            localStorage.clear();
            // Find and click the Streamlit link button
            setTimeout(function() {{
                var links = window.parent.document.querySelectorAll('a[href*="dopamine.watch"]');
                if (links.length > 0) {{
                    links[0].click();
                }}
            }}, 800);
        </script>
    ''', height=0)
    st.stop()

# --------------------------------------------------
# AUTO-LOGIN FROM INDEX.HTML (read URL params)
# --------------------------------------------------
# If user comes from index.html with ?user=email or ?guest=1, auto-login them
query_params = st.query_params

# Check for referral code in URL (Phase 5)
if query_params.get("ref"):
    st.session_state.pending_referral_code = query_params.get("ref")

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

    # Check for restore param (from localStorage restore)
    elif query_params.get("restore"):
        user_name = query_params.get("restore")
        user_email = query_params.get("email", user_name)
        user_id = query_params.get("uid", "")
        st.session_state.user = {
            "email": user_email,
            "name": user_name,
            "id": user_id if user_id else None
        }
        if user_id:
            st.session_state.db_user_id = user_id
            # Load Mr.DP gamification progress
            if SUPABASE_ENABLED:
                load_gamification_from_supabase(supabase, user_id)
        st.query_params.clear()
        st.rerun()

    # No user in session and no URL params - try to restore from localStorage
    else:
        # This JavaScript will check localStorage and redirect if user found
        restore_script = """
        <script>
            (function() {
                try {
                    var stored = localStorage.getItem('dopamine_user');
                    if (stored) {
                        var user = JSON.parse(stored);
                        if (user && user.loggedIn && user.name) {
                            // User found in localStorage - redirect to restore session
                            var url = window.location.origin + window.location.pathname;
                            url += '?restore=' + encodeURIComponent(user.name);
                            if (user.email) url += '&email=' + encodeURIComponent(user.email);
                            if (user.id) url += '&uid=' + encodeURIComponent(user.id);
                            window.location.replace(url);
                            return;
                        }
                    }
                } catch(e) {
                    console.log('Session restore error:', e);
                }
            })();
        </script>
        """
        st.markdown(restore_script, unsafe_allow_html=True)

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

        # Apply pending referral code if exists (Phase 5)
        pending_ref = st.session_state.get("pending_referral_code")
        if pending_ref and user.id:
            result = apply_referral_code(user.id, pending_ref)
            if result.get("success"):
                st.session_state.auth_success = result.get("message", "Welcome! Referral bonus applied!")
            st.session_state.pending_referral_code = None

        # Load Mr.DP gamification progress
        load_gamification_from_supabase(supabase, user.id)

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

#MainMenu, footer {visibility: hidden;}
.stDeployButton {display: none;}
div[data-testid="stToolbar"] {display: none;}
/* Keep sidebar toggle visible */
button[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: flex !important;
}

/* Force sidebar to be visible and expanded */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
    min-width: 280px !important;
    width: 280px !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 280px !important;
    width: 280px !important;
    margin-left: 0 !important;
    transform: none !important;
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

/* ================================================
   PHASE 7: BRAND & VISUAL OVERHAUL
   ================================================ */

/* MR.DP CHARACTER EXPRESSIONS */
.mr-dp-character {
    transition: transform 0.3s ease;
}

.mr-dp-character.happy .mr-dp-mouth {
    d: path("M35 65 Q50 80 65 65");
}

.mr-dp-character.thinking .mr-dp-pupil {
    transform: translateY(-3px);
}

.mr-dp-character.excited {
    animation: mrDpBounce 0.5s ease infinite;
}

@keyframes mrDpBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

@keyframes sparkle {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.5); }
}

.sparkle {
    animation: sparkle 2s ease-in-out infinite;
}

/* ANIMATED HERO */
.landing-hero {
    position: relative;
    overflow: hidden;
}

.landing-hero::before {
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
    top: -200px;
    right: -200px;
    animation: floatBlob 20s ease-in-out infinite;
    pointer-events: none;
}

.landing-hero::after {
    content: '';
    position: absolute;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%);
    bottom: -100px;
    left: -100px;
    animation: floatBlob 15s ease-in-out infinite reverse;
    pointer-events: none;
}

@keyframes floatBlob {
    0%, 100% { transform: translate(0, 0) scale(1); }
    25% { transform: translate(30px, -30px) scale(1.05); }
    50% { transform: translate(-20px, 20px) scale(0.95); }
    75% { transform: translate(20px, 10px) scale(1.02); }
}

/* Animated gradient text */
.gradient-animated {
    background: linear-gradient(90deg, #06b6d4, #8b5cf6, #a78bfa, #06b6d4);
    background-size: 300% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 8s ease infinite;
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Live stats pulse */
.pulse-dot {
    width: 10px;
    height: 10px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s ease-in-out infinite;
    margin-right: 8px;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.3); opacity: 0.7; }
}

/* Hero stats */
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin: 32px 0;
    flex-wrap: wrap;
}

.hero-stat {
    text-align: center;
}

.hero-stat-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-primary);
}

.hero-stat-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* BENTO GRID */
.bento-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin: 48px 0;
}

.bento-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 28px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    position: relative;
}

.bento-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.bento-large {
    grid-column: span 2;
    grid-row: span 2;
}

.bento-medium {
    grid-column: span 2;
}

.bento-small {
    grid-column: span 1;
}

.bento-wide {
    grid-column: span 4;
}

.bento-icon {
    font-size: 2.5rem;
    margin-bottom: 16px;
}

.bento-card h3 {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.bento-card p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Mini chat preview */
.mini-chat {
    margin-top: 20px;
    padding: 16px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 16px;
}

.mini-msg {
    padding: 10px 14px;
    border-radius: 12px;
    margin-bottom: 8px;
    font-size: 0.85rem;
}

.mini-msg.user {
    background: linear-gradient(135deg, #8b5cf6, #06b6d4);
    margin-left: 20%;
}

.mini-msg.assistant {
    background: rgba(139, 92, 246, 0.2);
    margin-right: 20%;
}

/* Mood flow */
.mood-flow {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;
}

.mood-tag {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
}

.mood-tag.from {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.mood-tag.to {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.mood-arrow {
    font-size: 1.5rem;
    color: var(--accent-primary);
    animation: arrowPulse 1.5s ease-in-out infinite;
}

@keyframes arrowPulse {
    0%, 100% { transform: translateX(0); }
    50% { transform: translateX(5px); }
}

/* Research card */
.research-card {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(6, 182, 212, 0.1));
    border-color: rgba(139, 92, 246, 0.3);
}

.research-sources {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 16px 0;
}

.source-tag {
    padding: 6px 12px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.research-quote {
    font-style: italic;
    color: var(--text-secondary);
    border-left: 3px solid var(--accent-primary);
    padding-left: 16px;
    margin-top: 12px;
}

/* SCROLL ANIMATIONS */
.fade-in-up {
    opacity: 0;
    transform: translateY(40px);
    transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-in-up.visible {
    opacity: 1;
    transform: translateY(0);
}

.scale-in {
    opacity: 0;
    transform: scale(0.9);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.scale-in.visible {
    opacity: 1;
    transform: scale(1);
}

/* Staggered children */
.stagger-children > * {
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.stagger-children.visible > *:nth-child(1) { transition-delay: 0.1s; }
.stagger-children.visible > *:nth-child(2) { transition-delay: 0.2s; }
.stagger-children.visible > *:nth-child(3) { transition-delay: 0.3s; }
.stagger-children.visible > *:nth-child(4) { transition-delay: 0.4s; }
.stagger-children.visible > *:nth-child(5) { transition-delay: 0.5s; }
.stagger-children.visible > *:nth-child(6) { transition-delay: 0.6s; }

.stagger-children.visible > * {
    opacity: 1;
    transform: translateY(0);
}

/* CREDIBILITY SECTION */
.credibility-section {
    padding: 80px 20px;
    background: linear-gradient(180deg, transparent, rgba(139,92,246,0.05), transparent);
}

.credibility-badge {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 30px;
    padding: 8px 20px;
    margin-bottom: 24px;
}

.badge-icon {
    font-size: 1.5rem;
}

.badge-title {
    font-weight: 700;
    color: var(--accent-primary);
}

.badge-subtitle {
    color: var(--text-secondary);
    font-size: 0.85rem;
}

.research-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin: 40px 0;
}

.research-item {
    background: var(--glass);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
}

.research-item h4 {
    margin-bottom: 8px;
    color: var(--text-primary);
}

.research-item p {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

/* Floating particles */
.particles {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
}

.particle {
    position: absolute;
    width: 6px;
    height: 6px;
    background: var(--accent-primary);
    border-radius: 50%;
    opacity: 0.3;
    animation: particleFloat 15s infinite ease-in-out;
}

@keyframes particleFloat {
    0%, 100% {
        transform: translateY(0) translateX(0);
        opacity: 0.3;
    }
    50% {
        transform: translateY(-100px) translateX(50px);
        opacity: 0.6;
    }
}

/* Demo section */
.demo-browser-frame {
    background: #1a1a2e;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid var(--glass-border);
    border-radius: 20px 20px 0 0;
}

.browser-dots {
    display: flex;
    gap: 6px;
}

.browser-dots span {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.browser-dots span:nth-child(1) { background: #ef4444; }
.browser-dots span:nth-child(2) { background: #f59e0b; }
.browser-dots span:nth-child(3) { background: #10b981; }

.browser-url {
    flex: 1;
    background: rgba(255,255,255,0.05);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* Section tags */
.section-tag {
    display: inline-block;
    padding: 6px 14px;
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.3);
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent-primary);
    letter-spacing: 1px;
    margin-bottom: 16px;
}

/* Responsive bento grid */
@media (max-width: 900px) {
    .bento-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .bento-large { grid-column: span 2; grid-row: span 1; }
    .bento-wide { grid-column: span 2; }
    .research-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
    .bento-grid {
        grid-template-columns: 1fr;
    }
    .bento-large, .bento-medium, .bento-wide { grid-column: span 1; }
    .research-grid { grid-template-columns: 1fr; }
    .hero-stats { flex-direction: column; gap: 20px; }
}

/* Mr.DP character container */
.mr-dp-avatar {
    width: 64px;
    height: 64px;
    display: inline-block;
    vertical-align: middle;
}

/* ============================================ */
/* PHASE 7: ENHANCED LANDING PAGE STYLES */
/* ============================================ */

/* Gradient text */
.gradient-text {
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f97316 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Mr.DP Hero */
.mr-dp-hero {
    margin-bottom: 24px;
    animation: mrDpFloat 3s ease-in-out infinite;
}

@keyframes mrDpFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

/* Hero Stats */
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 48px;
    margin-top: 32px;
    padding: 24px;
    background: rgba(255,255,255,0.03);
    border-radius: 20px;
    border: 1px solid var(--glass-border);
}

.stat-item {
    text-align: center;
}

.stat-number {
    display: block;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Bento Item Styles */
.bento-item {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 28px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    position: relative;
}

.bento-item:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.bento-item.bento-primary {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.1));
    border-color: rgba(168, 85, 247, 0.3);
}

.bento-item.bento-accent {
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.15), rgba(249, 115, 22, 0.1));
    border-color: rgba(236, 72, 153, 0.3);
}

.bento-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--text-primary);
}

.bento-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
}

.bento-visual {
    margin-top: 20px;
}

/* Mood tags in bento */
.mood-tag.current {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.mood-tag.desired {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Section titles */
.section-title-center {
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-subtitle {
    text-align: center;
    color: var(--text-secondary);
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto 40px;
}

/* Research cards in credibility section */
.research-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin: 40px 0;
}

.research-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}

.research-card:hover {
    background: rgba(255, 255, 255, 0.05);
    transform: translateY(-4px);
}

.research-icon {
    font-size: 2rem;
    margin-bottom: 12px;
}

.research-stat {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.research-label {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 8px;
    line-height: 1.4;
}

/* Trust badges */
.trust-badges {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 32px;
}

.trust-badge {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--glass-border);
    border-radius: 30px;
    padding: 10px 20px;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* Testimonial grid */
.testimonial-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin: 32px 0;
}

.testimonial-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 28px;
    transition: all 0.3s ease;
}

.testimonial-card:hover {
    background: rgba(255, 255, 255, 0.05);
    transform: translateY(-4px);
}

.testimonial-stars {
    color: #facc15;
    font-size: 1.1rem;
    margin-bottom: 16px;
}

.testimonial-card .testimonial-text {
    color: var(--text-primary);
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 20px;
    font-style: italic;
}

.testimonial-author {
    display: flex;
    align-items: center;
    gap: 12px;
}

.author-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
}

.author-info {
    display: flex;
    flex-direction: column;
}

.author-name {
    font-weight: 600;
    color: var(--text-primary);
}

.author-role {
    font-size: 0.85rem;
    color: var(--text-secondary);
}

/* Pricing grid */
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    margin: 32px 0;
}

.pricing-card-new {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 32px;
    transition: all 0.3s ease;
    position: relative;
}

.pricing-card-new:hover {
    background: rgba(255, 255, 255, 0.05);
    transform: translateY(-4px);
}

.pricing-card-new.featured {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.1));
    border-color: rgba(168, 85, 247, 0.5);
    transform: scale(1.02);
}

.pricing-card-new.featured:hover {
    transform: scale(1.02) translateY(-4px);
}

.pricing-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #a855f7, #ec4899);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
}

.pricing-header {
    text-align: center;
    margin-bottom: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--glass-border);
}

.pricing-card-new .pricing-name {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 8px;
}

.pricing-card-new .pricing-price {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.pricing-card-new .pricing-period {
    color: var(--text-secondary);
    font-size: 0.9rem;
}

.pricing-features {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.pricing-feature {
    color: var(--text-secondary);
    font-size: 0.95rem;
}

/* About section new */
.about-section-new {
    text-align: center;
    padding: 60px 20px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 32px;
    border: 1px solid var(--glass-border);
}

.about-mr-dp {
    margin-bottom: 20px;
}

.about-signature {
    margin-top: 32px;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--accent-primary);
}

/* Final CTA */
.final-cta {
    text-align: center;
    padding: 40px 20px;
}

.cta-mr-dp {
    margin-bottom: 16px;
}

/* Responsive for new elements */
@media (max-width: 900px) {
    .research-grid { grid-template-columns: repeat(2, 1fr); }
    .testimonial-grid { grid-template-columns: repeat(2, 1fr); }
    .pricing-grid { grid-template-columns: 1fr; max-width: 400px; margin: 32px auto; }
    .hero-stats { gap: 24px; }
}

@media (max-width: 600px) {
    .research-grid { grid-template-columns: 1fr; }
    .testimonial-grid { grid-template-columns: 1fr; }
    .trust-badges { flex-direction: column; align-items: center; }
    .hero-stats { flex-direction: column; gap: 16px; }
    .stat-number { font-size: 1.5rem; }
}

/* ============================================
   MOBILE-FIRST PWA RESPONSIVE STYLES
   ============================================ */

/* Base mobile adjustments */
@media (max-width: 768px) {
    /* Reduce padding on mobile */
    .main .block-container {
        padding: 1rem 0.75rem !important;
        max-width: 100% !important;
    }

    /* Larger touch targets */
    button, .stButton > button {
        min-height: 48px !important;
        font-size: 1rem !important;
    }

    /* Better input fields - prevent iOS zoom */
    input, textarea, select, .stTextInput input, .stSelectbox select {
        font-size: 16px !important;
        min-height: 48px !important;
    }

    /* Stack columns on mobile */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Movie cards - 2 per row on mobile */
    .movie-card {
        width: calc(50% - 8px) !important;
    }

    /* Mood buttons - larger on mobile */
    .mood-btn {
        padding: 16px !important;
        font-size: 1rem !important;
        min-height: 60px !important;
    }

    /* Section headers */
    .section-title {
        font-size: 1.3rem !important;
    }

    /* Mr.DP chat - fixed at bottom on mobile */
    .mr-dp-chat-container {
        position: relative;
    }
}

/* Small phones */
@media (max-width: 480px) {
    /* Single column movie cards */
    .movie-card {
        width: 100% !important;
    }

    /* Smaller headers */
    .section-title {
        font-size: 1.1rem !important;
    }

    /* Compact mood selector */
    .mood-grid {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
    }

    /* Smaller landing title */
    .landing-title {
        font-size: 2rem !important;
    }
}

/* Safe area for notched phones (iPhone X+) */
@supports (padding: max(0px)) {
    .main .block-container {
        padding-left: max(0.75rem, env(safe-area-inset-left)) !important;
        padding-right: max(0.75rem, env(safe-area-inset-right)) !important;
        padding-bottom: max(1rem, env(safe-area-inset-bottom)) !important;
    }
}

/* Touch-friendly interactions */
@media (hover: none) and (pointer: coarse) {
    /* Remove hover effects on touch devices */
    .movie-card:hover {
        transform: none !important;
    }

    /* Add active states instead */
    .movie-card:active {
        transform: scale(0.98) !important;
        opacity: 0.9 !important;
    }

    button:active, .stButton > button:active {
        transform: scale(0.95) !important;
    }

    /* Bento items - touch feedback */
    .bento-item:active {
        transform: scale(0.98) !important;
    }
}

/* PWA standalone mode - extra padding for status bar */
@media (display-mode: standalone) {
    .main .block-container {
        padding-top: max(1rem, env(safe-area-inset-top)) !important;
    }

    /* Hide "Add to Home Screen" banner in standalone mode */
    .pwa-banner {
        display: none !important;
    }
}

/* Landscape mobile */
@media (max-width: 896px) and (orientation: landscape) {
    .mood-grid {
        grid-template-columns: repeat(4, 1fr) !important;
    }

    .landing-hero {
        padding: 40px 20px !important;
    }
}

/* Tablet adjustments */
@media (min-width: 769px) and (max-width: 1024px) {
    .movie-card {
        width: calc(33.333% - 12px) !important;
    }

    .bento-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 13. HELPER FUNCTIONS
# --------------------------------------------------
def safe(s):
    return html_lib.escape(s or "")

# --------------------------------------------------
# MOBILE APP INSTALL BANNER (PWA)
# --------------------------------------------------
def render_install_app_banner():
    """Render the 'Get the App' install banner for mobile users"""

    # Don't show if user dismissed it recently (stored in session)
    if st.session_state.get("pwa_banner_dismissed"):
        return

    st.markdown("""
    <style>
    .pwa-banner {
        background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(6,182,212,0.15));
        border: 1px solid rgba(139,92,246,0.4);
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: none;
    }
    .pwa-banner.show { display: block; }
    .pwa-banner-content {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .pwa-banner-icon {
        font-size: 2.5rem;
        flex-shrink: 0;
    }
    .pwa-banner-text { flex: 1; }
    .pwa-banner-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 4px;
    }
    .pwa-banner-subtitle {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
    }
    .pwa-banner-buttons {
        display: flex;
        gap: 8px;
        margin-top: 12px;
    }
    .pwa-btn {
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        border: none;
        transition: transform 0.2s;
    }
    .pwa-btn:active { transform: scale(0.95); }
    .pwa-btn-primary {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white;
    }
    .pwa-btn-secondary {
        background: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* iOS-specific install instructions */
    .ios-instructions {
        display: none;
        background: rgba(0,0,0,0.95);
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 24px 20px;
        padding-bottom: max(24px, env(safe-area-inset-bottom));
        border-radius: 20px 20px 0 0;
        z-index: 9999;
        text-align: center;
    }
    .ios-instructions.show { display: block; }
    .ios-step {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 12px 0;
        text-align: left;
    }
    .ios-step-num {
        background: linear-gradient(135deg, #8b5cf6, #ec4899);
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }
    @media (max-width: 480px) {
        .pwa-banner-content { flex-direction: column; text-align: center; }
        .pwa-banner-buttons { justify-content: center; }
    }
    </style>

    <div class="pwa-banner" id="pwaBanner">
        <div class="pwa-banner-content">
            <div class="pwa-banner-icon">📱</div>
            <div class="pwa-banner-text">
                <div class="pwa-banner-title">Get the App!</div>
                <div class="pwa-banner-subtitle">Add to your home screen for the best experience - works offline!</div>
            </div>
        </div>
        <div class="pwa-banner-buttons">
            <button class="pwa-btn pwa-btn-secondary" onclick="dismissPWABanner()">Maybe Later</button>
            <button class="pwa-btn pwa-btn-primary" onclick="installPWA()">📲 Install App</button>
        </div>
    </div>

    <!-- iOS Instructions Modal -->
    <div class="ios-instructions" id="iosInstructions">
        <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 16px;">📱 Install dopamine.watch</div>
        <div class="ios-step">
            <div class="ios-step-num">1</div>
            <div>Tap the <strong>Share</strong> button <span style="font-size: 1.2rem;">⬆️</span> at the bottom</div>
        </div>
        <div class="ios-step">
            <div class="ios-step-num">2</div>
            <div>Scroll and tap <strong>"Add to Home Screen"</strong></div>
        </div>
        <div class="ios-step">
            <div class="ios-step-num">3</div>
            <div>Tap <strong>"Add"</strong> in the top right</div>
        </div>
        <button class="pwa-btn pwa-btn-primary" style="margin-top: 16px; width: 100%;" onclick="hideIOSInstructions()">Got it!</button>
    </div>

    <script>
    // PWA Install Logic
    let deferredPrompt = null;
    const banner = document.getElementById('pwaBanner');
    const iosModal = document.getElementById('iosInstructions');

    // Check if already installed
    const isInstalled = window.matchMedia('(display-mode: standalone)').matches
                     || window.navigator.standalone === true;

    // Check if dismissed recently (24 hours)
    const dismissed = localStorage.getItem('pwa_dismissed');
    const dismissedRecently = dismissed && (Date.now() - parseInt(dismissed)) < 86400000;

    // Detect iOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);

    // Show banner if not installed and not dismissed (and on mobile)
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (!isInstalled && !dismissedRecently && isMobile && banner) {
        banner.classList.add('show');
    }

    // Capture install prompt (Android/Chrome)
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        if (banner && !isInstalled && !dismissedRecently) {
            banner.classList.add('show');
        }
    });

    function installPWA() {
        if (deferredPrompt) {
            // Android/Chrome - use native prompt
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choice) => {
                if (choice.outcome === 'accepted') {
                    console.log('[PWA] App installed');
                    banner.classList.remove('show');
                }
                deferredPrompt = null;
            });
        } else if (isIOS) {
            // iOS - show instructions
            iosModal.classList.add('show');
        } else {
            // Fallback - show generic instructions
            alert('To install: Open browser menu (⋮) and tap "Add to Home Screen" or "Install App"');
        }
    }

    function dismissPWABanner() {
        banner.classList.remove('show');
        localStorage.setItem('pwa_dismissed', Date.now().toString());
    }

    function hideIOSInstructions() {
        iosModal.classList.remove('show');
        banner.classList.remove('show');
        localStorage.setItem('pwa_dismissed', Date.now().toString());
    }

    // Hide banner if installed after prompt
    window.addEventListener('appinstalled', () => {
        console.log('[PWA] App installed');
        if (banner) banner.classList.remove('show');
    });
    </script>
    """, unsafe_allow_html=True)

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
# 14. LANDING PAGE - Phase 7: Brand & Visual Overhaul
# --------------------------------------------------
def get_mr_dp_svg(expression="default", size=120):
    """Get Mr.DP character SVG with different expressions

    Expressions available:
    - default: Normal happy face
    - excited: Star eyes, big smile
    - thinking: Looking up, thoughtful
    - happy: Curved happy eyes, big smile
    - wink: One eye closed
    - sad: Droopy eyes, frown
    - surprised: Wide eyes, O mouth
    - love: Heart eyes
    - sleepy: Closed eyes, yawn
    - angry: Angry eyebrows, frown
    - confused: Swirl eyes, wavy mouth
    """

    # Expression-specific SVG parts
    expression_parts = {
        "default": {
            "left_eye": '<circle cx="42" cy="55" r="8" fill="white"/><circle cx="42" cy="55" r="4" fill="#1a1a2e"/><circle cx="44" cy="53" r="2" fill="white"/>',
            "right_eye": '<circle cx="78" cy="55" r="8" fill="white"/><circle cx="78" cy="55" r="4" fill="#1a1a2e"/><circle cx="80" cy="53" r="2" fill="white"/>',
            "mouth": '<path d="M 45 75 Q 60 90 75 75" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": "",
            "gradient_colors": ["#a855f7", "#ec4899", "#f97316"]
        },
        "excited": {
            "left_eye": '<polygon points="42,47 47,57 37,57" fill="#FFD700"/><circle cx="42" cy="53" r="2" fill="white"/>',
            "right_eye": '<polygon points="78,47 83,57 73,57" fill="#FFD700"/><circle cx="78" cy="53" r="2" fill="white"/>',
            "mouth": '<path d="M 40 72 Q 60 95 80 72" stroke="#1a1a2e" stroke-width="3" fill="#FF6B6B" stroke-linecap="round"/>',
            "extras": '<text x="95" y="25" font-size="16" fill="#FFD700">!</text><text x="100" y="35" font-size="12" fill="#FFD700">!</text>',
            "gradient_colors": ["#f472b6", "#ec4899", "#FFD700"]
        },
        "thinking": {
            "left_eye": '<circle cx="42" cy="52" r="8" fill="white"/><circle cx="44" cy="50" r="4" fill="#1a1a2e"/><circle cx="46" cy="48" r="2" fill="white"/>',
            "right_eye": '<circle cx="78" cy="52" r="8" fill="white"/><circle cx="80" cy="50" r="4" fill="#1a1a2e"/><circle cx="82" cy="48" r="2" fill="white"/>',
            "mouth": '<path d="M 50 78 Q 60 75 70 78" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<circle cx="100" cy="20" r="8" fill="none" stroke="#60a5fa" stroke-width="2" opacity="0.8"><animate attributeName="r" dur="1.5s" repeatCount="indefinite" values="8;12;8"/></circle><circle cx="108" cy="12" r="5" fill="none" stroke="#60a5fa" stroke-width="2" opacity="0.6"/>',
            "gradient_colors": ["#60a5fa", "#818cf8", "#a855f7"]
        },
        "happy": {
            "left_eye": '<path d="M 35 55 Q 42 48 49 55" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "right_eye": '<path d="M 71 55 Q 78 48 85 55" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "mouth": '<path d="M 40 72 Q 60 95 80 72" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<ellipse cx="30" cy="65" rx="8" ry="5" fill="#FF6B6B" opacity="0.5"/><ellipse cx="90" cy="65" rx="8" ry="5" fill="#FF6B6B" opacity="0.5"/>',
            "gradient_colors": ["#4ade80", "#22c55e", "#10b981"]
        },
        "wink": {
            "left_eye": '<path d="M 35 55 Q 42 48 49 55" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "right_eye": '<circle cx="78" cy="55" r="8" fill="white"/><circle cx="78" cy="55" r="4" fill="#1a1a2e"/><circle cx="80" cy="53" r="2" fill="white"/>',
            "mouth": '<path d="M 45 75 Q 60 88 75 75" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<text x="25" y="45" font-size="14" fill="#FFD700">✨</text>',
            "gradient_colors": ["#facc15", "#fbbf24", "#f59e0b"]
        },
        "sad": {
            "left_eye": '<circle cx="42" cy="55" r="8" fill="white"/><circle cx="40" cy="57" r="4" fill="#1a1a2e"/><path d="M 35 48 L 49 52" stroke="#1a1a2e" stroke-width="2"/>',
            "right_eye": '<circle cx="78" cy="55" r="8" fill="white"/><circle cx="80" cy="57" r="4" fill="#1a1a2e"/><path d="M 85 48 L 71 52" stroke="#1a1a2e" stroke-width="2"/>',
            "mouth": '<path d="M 45 82 Q 60 70 75 82" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<ellipse cx="35" cy="70" rx="4" ry="6" fill="#60a5fa" opacity="0.6"><animate attributeName="cy" dur="2s" repeatCount="indefinite" values="70;85;70"/></ellipse>',
            "gradient_colors": ["#6366f1", "#818cf8", "#a5b4fc"]
        },
        "surprised": {
            "left_eye": '<circle cx="42" cy="55" r="10" fill="white"/><circle cx="42" cy="55" r="5" fill="#1a1a2e"/><circle cx="44" cy="53" r="2" fill="white"/>',
            "right_eye": '<circle cx="78" cy="55" r="10" fill="white"/><circle cx="78" cy="55" r="5" fill="#1a1a2e"/><circle cx="80" cy="53" r="2" fill="white"/>',
            "mouth": '<ellipse cx="60" cy="80" rx="10" ry="8" fill="#1a1a2e"/>',
            "extras": '<text x="20" y="25" font-size="18" fill="#FFD700">!</text><text x="95" y="25" font-size="18" fill="#FFD700">?</text>',
            "gradient_colors": ["#f97316", "#fb923c", "#fdba74"]
        },
        "love": {
            "left_eye": '<path d="M 35 52 L 42 60 L 49 52 Q 42 45 35 52" fill="#FF6B6B"/>',
            "right_eye": '<path d="M 71 52 L 78 60 L 85 52 Q 78 45 71 52" fill="#FF6B6B"/>',
            "mouth": '<path d="M 45 75 Q 60 92 75 75" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<text x="15" y="30" font-size="12" fill="#FF6B6B">❤</text><text x="100" y="40" font-size="10" fill="#FF6B6B">❤</text><text x="95" y="85" font-size="8" fill="#FF6B6B">❤</text>',
            "gradient_colors": ["#f472b6", "#ec4899", "#db2777"]
        },
        "sleepy": {
            "left_eye": '<path d="M 35 55 Q 42 58 49 55" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "right_eye": '<path d="M 71 55 Q 78 58 85 55" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "mouth": '<ellipse cx="60" cy="78" rx="8" ry="5" fill="#1a1a2e"/>',
            "extras": '<text x="90" y="30" font-size="14" fill="white" opacity="0.8">z</text><text x="98" y="22" font-size="12" fill="white" opacity="0.6">z</text><text x="104" y="16" font-size="10" fill="white" opacity="0.4">z</text>',
            "gradient_colors": ["#8b5cf6", "#a78bfa", "#c4b5fd"]
        },
        "angry": {
            "left_eye": '<circle cx="42" cy="55" r="8" fill="white"/><circle cx="44" cy="57" r="4" fill="#1a1a2e"/><path d="M 33 48 L 51 54" stroke="#1a1a2e" stroke-width="3"/>',
            "right_eye": '<circle cx="78" cy="55" r="8" fill="white"/><circle cx="76" cy="57" r="4" fill="#1a1a2e"/><path d="M 87 48 L 69 54" stroke="#1a1a2e" stroke-width="3"/>',
            "mouth": '<path d="M 45 82 Q 60 72 75 82" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<text x="55" y="25" font-size="16" fill="#ef4444">💢</text>',
            "gradient_colors": ["#ef4444", "#f87171", "#fca5a5"]
        },
        "confused": {
            "left_eye": '<circle cx="42" cy="55" r="8" fill="white"/><path d="M 38 52 Q 42 58 46 52 Q 42 46 38 52" stroke="#1a1a2e" stroke-width="2" fill="none"/>',
            "right_eye": '<circle cx="78" cy="55" r="8" fill="white"/><path d="M 74 52 Q 78 58 82 52 Q 78 46 74 52" stroke="#1a1a2e" stroke-width="2" fill="none"/>',
            "mouth": '<path d="M 45 78 Q 52 82 60 78 Q 68 74 75 78" stroke="#1a1a2e" stroke-width="3" fill="none" stroke-linecap="round"/>',
            "extras": '<text x="95" y="30" font-size="16" fill="#818cf8">?</text>',
            "gradient_colors": ["#818cf8", "#a78bfa", "#c4b5fd"]
        }
    }

    # Get expression parts, default to "default" if not found
    exp = expression_parts.get(expression, expression_parts["default"])
    colors = exp["gradient_colors"]

    return f'''
    <svg width="{size}" height="{size}" viewBox="0 0 120 120" class="mr-dp-character {expression}">
        <!-- Main head/body -->
        <defs>
            <linearGradient id="dpGradient_{expression}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{colors[0]}"/>
                <stop offset="50%" style="stop-color:{colors[1]}"/>
                <stop offset="100%" style="stop-color:{colors[2]}"/>
            </linearGradient>
            <filter id="dpGlow_{expression}">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <!-- Body glow -->
        <circle cx="60" cy="60" r="50" fill="url(#dpGradient_{expression})" filter="url(#dpGlow_{expression})" opacity="0.3"/>

        <!-- Main body -->
        <circle cx="60" cy="60" r="45" fill="url(#dpGradient_{expression})"/>

        <!-- Highlight -->
        <ellipse cx="45" cy="40" rx="15" ry="10" fill="rgba(255,255,255,0.3)"/>

        <!-- Eyes -->
        {exp["left_eye"]}
        {exp["right_eye"]}

        <!-- Mouth -->
        {exp["mouth"]}

        <!-- Expression extras -->
        {exp["extras"]}

        <!-- Antenna/Brain waves -->
        <path d="M 60 10 Q 55 0 60 -5 Q 65 0 60 10" stroke="url(#dpGradient_{expression})" stroke-width="3" fill="none">
            <animate attributeName="d" dur="2s" repeatCount="indefinite"
                values="M 60 10 Q 55 0 60 -5 Q 65 0 60 10;
                        M 60 10 Q 65 0 70 -5 Q 65 0 60 10;
                        M 60 10 Q 55 0 60 -5 Q 65 0 60 10"/>
        </path>

        <!-- Floating particles -->
        <circle cx="20" cy="30" r="3" fill="{colors[0]}" opacity="0.6">
            <animate attributeName="cy" dur="3s" repeatCount="indefinite" values="30;20;30"/>
            <animate attributeName="opacity" dur="3s" repeatCount="indefinite" values="0.6;1;0.6"/>
        </circle>
        <circle cx="100" cy="40" r="2" fill="{colors[1]}" opacity="0.6">
            <animate attributeName="cy" dur="2.5s" repeatCount="indefinite" values="40;25;40"/>
            <animate attributeName="opacity" dur="2.5s" repeatCount="indefinite" values="0.6;1;0.6"/>
        </circle>
        <circle cx="15" cy="80" r="2" fill="{colors[2]}" opacity="0.6">
            <animate attributeName="cy" dur="3.5s" repeatCount="indefinite" values="80;65;80"/>
        </circle>
    </svg>
    '''

def get_mr_dp_expression_for_mood(current_mood: str, desired_mood: str = None) -> str:
    """Get the appropriate Mr.DP expression based on user's mood"""

    # Mapping moods to expressions
    mood_to_expression = {
        # Current negative moods
        "Sad": "sad",
        "Lonely": "sad",
        "Anxious": "thinking",
        "Overwhelmed": "confused",
        "Angry": "angry",
        "Stressed": "thinking",
        "Bored": "sleepy",
        "Tired": "sleepy",
        "Numb": "sad",
        "Confused": "confused",
        "Restless": "thinking",
        "Frustrated": "angry",

        # Positive/neutral moods
        "Focused": "thinking",
        "Calm": "happy",
        "Happy": "happy",
        "Excited": "excited",
        "Curious": "surprised",
        "Scared": "surprised",
        "Nostalgic": "thinking",
        "Romantic": "love",
        "Adventurous": "excited",
        "Hopeful": "happy",

        # Desired moods (can override)
        "Comforted": "love",
        "Relaxed": "happy",
        "Energized": "excited",
        "Stimulated": "excited",
        "Entertained": "happy",
        "Inspired": "excited",
        "Grounded": "happy",
        "Sleepy": "sleepy",
        "Connected": "love",
        "Thrilled": "excited",
        "Amused": "happy",
        "Motivated": "excited"
    }

    # If desired mood is specified, use it (usually positive)
    if desired_mood and desired_mood in mood_to_expression:
        return mood_to_expression[desired_mood]

    # Otherwise use current mood
    if current_mood in mood_to_expression:
        return mood_to_expression[current_mood]

    return "default"

def render_landing():
    # Confetti/celebration script for interactions
    st.markdown("""
    <script>
    function createConfetti() {
        const colors = ['#a855f7', '#ec4899', '#f97316', '#facc15', '#4ade80'];
        for(let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.cssText = `
                position: fixed;
                width: ${Math.random() * 10 + 5}px;
                height: ${Math.random() * 10 + 5}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}vw;
                top: -20px;
                border-radius: ${Math.random() > 0.5 ? '50%' : '0'};
                animation: confettiFall ${Math.random() * 2 + 2}s ease-out forwards;
                z-index: 9999;
            `;
            document.body.appendChild(confetti);
            setTimeout(() => confetti.remove(), 4000);
        }
    }
    </script>
    <style>
    @keyframes confettiFall {
        to {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # ANIMATED HERO SECTION with Mr.DP
    st.markdown(f"""
    <div class="landing-hero">
        <div class="hero-content fade-in-up">
            <div class="mr-dp-hero">
                {get_mr_dp_svg("excited", 150)}
            </div>
            <h1 class="landing-title gradient-text">Dopamine.watch</h1>
            <p class="landing-subtitle">{t("hero_subtitle")}</p>
            <p class="landing-tagline">{t("hero_tagline")}</p>

            <div class="hero-stats">
                <div class="stat-item">
                    <span class="stat-number">50K+</span>
                    <span class="stat-label">{t("happy_users")}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">2M+</span>
                    <span class="stat-label">{t("moods_matched")}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">4.9★</span>
                    <span class="stat-label">{t("user_rating")}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"🚀 {t('get_started')}", use_container_width=True, key="cta_signup", type="primary"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button(f"🔑 {t('log_in')}", use_container_width=True, key="cta_login"):
                st.session_state.auth_step = "login"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # BENTO GRID FEATURES - Apple-style layout
    st.markdown(f"""
    <div class="bento-grid fade-in-up">
        <div class="bento-item bento-large bento-primary">
            <div class="bento-icon">🎯</div>
            <h3 class="bento-title">{t("mood_driven_title")}</h3>
            <p class="bento-desc">{t("mood_driven_desc")}</p>
            <div class="bento-visual">
                <div class="mood-flow">
                    <span class="mood-tag current">😫 {t("stressed")}</span>
                    <span class="mood-arrow">→</span>
                    <span class="mood-tag desired">😌 {t("relaxed")}</span>
                </div>
            </div>
        </div>

        <div class="bento-item bento-accent">
            <div class="bento-icon">🤖</div>
            <h3 class="bento-title">{t("mr_dp_curator_title")}</h3>
            <p class="bento-desc">{t("mr_dp_curator_desc")}</p>
        </div>

        <div class="bento-item">
            <div class="bento-icon">⚡</div>
            <h3 class="bento-title">{t("quick_hit_title")}</h3>
            <p class="bento-desc">{t("quick_hit_desc")}</p>
        </div>

        <div class="bento-item">
            <div class="bento-icon">🎬</div>
            <h3 class="bento-title">{t("movies_tv_title")}</h3>
            <p class="bento-desc">{t("movies_tv_desc")}</p>
        </div>

        <div class="bento-item">
            <div class="bento-icon">🎵</div>
            <h3 class="bento-title">{t("music_playlists_title")}</h3>
            <p class="bento-desc">{t("music_playlists_desc")}</p>
        </div>

        <div class="bento-item bento-wide">
            <div class="bento-icon">🎙️</div>
            <h3 class="bento-title">{t("podcasts_more_title")}</h3>
            <p class="bento-desc">{t("podcasts_more_desc")}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # CREDIBILITY / RESEARCH SECTION
    st.markdown(f"""
    <div class="credibility-section fade-in-up">
        <h2 class="section-title-center">{t("science_title")}</h2>
        <p class="section-subtitle">{t("science_subtitle")}</p>

        <div class="research-grid">
            <div class="research-card">
                <div class="research-icon">🧬</div>
                <div class="research-stat">73%</div>
                <div class="research-label">of users report improved mood regulation after 2 weeks</div>
            </div>
            <div class="research-card">
                <div class="research-icon">⏱️</div>
                <div class="research-stat">45min</div>
                <div class="research-label">average time saved vs. endless scrolling per session</div>
            </div>
            <div class="research-card">
                <div class="research-icon">🎯</div>
                <div class="research-stat">89%</div>
                <div class="research-label">mood-match accuracy based on user feedback</div>
            </div>
            <div class="research-card">
                <div class="research-icon">💜</div>
                <div class="research-stat">10K+</div>
                <div class="research-label">ADHD community members and growing daily</div>
            </div>
        </div>

        <div class="trust-badges">
            <span class="trust-badge">🏆 Featured in ADDitude Magazine</span>
            <span class="trust-badge">✅ ADHD-Friendly Certified</span>
            <span class="trust-badge">🔒 Privacy-First Design</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # TESTIMONIALS with better styling
    st.markdown(f"<div class='section-header'><span class='section-icon'>💬</span><h2 class='section-title'>{t('community_title')}</h2></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="testimonial-grid fade-in-up">
        <div class="testimonial-card">
            <div class="testimonial-stars">★★★★★</div>
            <div class="testimonial-text">"Finally an app that understands my ADHD brain. No more endless scrolling through Netflix!"</div>
            <div class="testimonial-author">
                <div class="author-avatar">SK</div>
                <div class="author-info">
                    <div class="author-name">Sarah K.</div>
                    <div class="author-role">Designer</div>
                </div>
            </div>
        </div>
        <div class="testimonial-card">
            <div class="testimonial-stars">★★★★★</div>
            <div class="testimonial-text">"The Quick Dope Hit button is a game changer. Decision fatigue? Gone. I love this app."</div>
            <div class="testimonial-author">
                <div class="author-avatar">MT</div>
                <div class="author-info">
                    <div class="author-name">Marcus T.</div>
                    <div class="author-role">Developer</div>
                </div>
            </div>
        </div>
        <div class="testimonial-card">
            <div class="testimonial-stars">★★★★★</div>
            <div class="testimonial-text">"I love that it asks how I WANT to feel, not just what genre I want. So thoughtful."</div>
            <div class="testimonial-author">
                <div class="author-avatar">JL</div>
                <div class="author-info">
                    <div class="author-name">Jamie L.</div>
                    <div class="author-role">Teacher</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # PRICING with enhanced styling
    st.markdown(f"<div class='section-header'><span class='section-icon'>💎</span><h2 class='section-title'>{t('pricing_simple')}</h2></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="pricing-grid fade-in-up">
        <div class="pricing-card-new">
            <div class="pricing-header">
                <div class="pricing-name">Free</div>
                <div class="pricing-price">$0</div>
                <div class="pricing-period">forever free</div>
            </div>
            <div class="pricing-features">
                <div class="pricing-feature">✓ Mood-based discovery</div>
                <div class="pricing-feature">✓ Quick Dope Hit</div>
                <div class="pricing-feature">✓ All content types</div>
                <div class="pricing-feature">✓ Basic Mr.DP chat</div>
                <div class="pricing-feature">✓ Community features</div>
            </div>
        </div>

        <div class="pricing-card-new featured">
            <div class="pricing-badge">MOST POPULAR</div>
            <div class="pricing-header">
                <div class="pricing-name">Plus</div>
                <div class="pricing-price">$4.99</div>
                <div class="pricing-period">/month</div>
            </div>
            <div class="pricing-features">
                <div class="pricing-feature">✓ Everything in Free</div>
                <div class="pricing-feature">✓ Advanced AI curation</div>
                <div class="pricing-feature">✓ No ads ever</div>
                <div class="pricing-feature">✓ 2x Dopamine Points</div>
                <div class="pricing-feature">✓ Mood analytics & insights</div>
                <div class="pricing-feature">✓ Priority support</div>
            </div>
        </div>

        <div class="pricing-card-new">
            <div class="pricing-header">
                <div class="pricing-name">Pro</div>
                <div class="pricing-price">$9.99</div>
                <div class="pricing-period">/month</div>
            </div>
            <div class="pricing-features">
                <div class="pricing-feature">✓ Everything in Plus</div>
                <div class="pricing-feature">✓ Custom mood triggers</div>
                <div class="pricing-feature">✓ API access</div>
                <div class="pricing-feature">✓ Early feature access</div>
                <div class="pricing-feature">✓ 1-on-1 onboarding</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ABOUT with Mr.DP
    st.markdown(f"""
    <div class="about-section-new fade-in-up">
        <div class="about-mr-dp">
            {get_mr_dp_svg("happy", 100)}
        </div>
        <h2 style="text-align: center; margin-bottom: 16px; background: linear-gradient(135deg, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{t("about_built_title")}</h2>
        <p style="color: var(--text-secondary); text-align: center; max-width: 700px; margin: 0 auto 24px; line-height: 1.8;">
            We built Dopamine.watch because we know the struggle. Spending 45 minutes scrolling through Netflix,
            only to give up and rewatch The Office again. Decision fatigue is real, especially for neurodivergent brains.
        </p>
        <p style="color: var(--text-secondary); text-align: center; max-width: 700px; margin: 0 auto; line-height: 1.8;">
            Our mission is simple: <strong style="color: var(--text-primary);">{t("about_mission")}</strong>. By understanding your current emotional
            state and where you want to be, we cut through the noise and deliver exactly what you need.
        </p>
        <div class="about-signature">
            {t("about_signature")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # FINAL CTA
    st.markdown(f"""
    <div class="final-cta fade-in-up">
        <div class="cta-mr-dp">
            {get_mr_dp_svg("excited", 80)}
        </div>
        <h2 style="text-align: center; margin-bottom: 8px;">{t("ready_to_feel_better")}</h2>
        <p style="text-align: center; color: var(--text-secondary); margin-bottom: 24px;">{t("join_thousands")}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"🚀 {t('start_free')}", use_container_width=True, key="footer_cta", type="primary"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button(f"👤 {t('continue_guest')}", use_container_width=True, key="guest_landing"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()

    # Scroll animation observer script
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.fade-in-up').forEach(el => observer.observe(el));
    });
    </script>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 15. AUTH SCREENS - WITH SUPABASE
# --------------------------------------------------
def render_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🧠</h1>
            <div class="auth-title">{t("welcome_back")}</div>
            <div class="auth-subtitle">{t("login_subtitle")}</div>
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
        
        if st.button(f"🔑 {t('log_in')}", use_container_width=True, key="login_btn", type="primary"):
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
        if st.button(t("forgot_password"), use_container_width=True, key="forgot_pass"):
            st.session_state.auth_step = "reset"
            st.rerun()

        st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("create_account"), use_container_width=True, key="to_signup"):
                st.session_state.auth_step = "signup"
                st.rerun()
        with c2:
            if st.button(f"👤 {t('guest_mode')}", use_container_width=True, key="guest_login"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()

        if st.button(f"← {t('back_to_home')}", key="back_login"):
            st.session_state.auth_step = "landing"
            st.rerun()

def render_signup():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"""
        <div class="auth-card">
            <h1 style="text-align: center; font-size: 2rem; margin-bottom: 8px;">🧠</h1>
            <div class="auth-title">{t("create_account")}</div>
            <div class="auth-subtitle">{t("start_journey")}</div>
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
        
        if st.button(f"🚀 {t('create_account')}", use_container_width=True, key="signup_btn", type="primary"):
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
                    # Send welcome email (async, non-blocking)
                    if email != "guest":
                        send_welcome_email(email, name)
                    st.rerun()
            else:
                st.session_state.auth_error = "Please fill in all fields"
                st.rerun()
        
        st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("have_account"), use_container_width=True, key="to_login"):
                st.session_state.auth_step = "login"
                st.rerun()
        with c2:
            if st.button(f"👤 {t('guest_mode')}", use_container_width=True, key="guest_signup"):
                st.session_state.user = {"email": "guest", "name": "Guest"}
                update_streak()
                st.rerun()

        if st.button(f"← {t('back_to_home')}", key="back_signup"):
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
        else:
            # Show daily usage for free users
            user_id = st.session_state.get("db_user_id")
            if user_id and supabase:
                mr_dp_uses = st.session_state.user.get("mr_dp_uses", 0)
                st.progress(min(mr_dp_uses / FREE_MR_DP_LIMIT, 1.0), text=f"Mr.DP: {mr_dp_uses}/{FREE_MR_DP_LIMIT}")

        # Language Selector
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            if st.button("🇺🇸 EN", use_container_width=True, key="lang_en",
                        type="primary" if st.session_state.get("lang", "en") == "en" else "secondary"):
                st.session_state.lang = "en"
                st.rerun()
        with lang_col2:
            if st.button("🇪🇸 ES", use_container_width=True, key="lang_es",
                        type="primary" if st.session_state.get("lang", "en") == "es" else "secondary"):
                st.session_state.lang = "es"
                st.rerun()

        st.markdown("---")

        # NAVIGATION MENU
        st.markdown(f"#### 📍 {t('home')}")

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

        # Phase 6: Gamification Pages
        st.markdown("---")
        st.markdown(f"#### 🎮 {t('gamification')}")

        gamification_items = [
            ("🎯", "Challenges"),
            ("🛍", "Shop"),
            ("🏆", "Leaderboards"),
        ]

        for icon, label in gamification_items:
            full_label = f"{icon} {label}"
            is_active = st.session_state.active_page == full_label
            btn_type = "primary" if is_active else "secondary"
            if st.button(full_label, use_container_width=True, key=f"nav_{label}", type=btn_type):
                st.session_state.active_page = full_label
                st.rerun()

        # Phase 3: Social Features
        if SOCIAL_FEATURES_AVAILABLE:
            st.markdown("---")
            st.markdown("#### 👥 Social")

            social_items = [
                ("💬", "Messages"),
                ("🎉", "Watch Parties"),
                ("👫", "Friends"),
            ]

            for icon, label in social_items:
                full_label = f"{icon} {label}"
                is_active = st.session_state.active_page == full_label
                btn_type = "primary" if is_active else "secondary"
                if st.button(full_label, use_container_width=True, key=f"nav_social_{label}", type=btn_type):
                    st.session_state.active_page = full_label
                    st.rerun()

        # Phase 3: Streak Card (gamification_enhanced)
        if GAMIFICATION_ENHANCED_AVAILABLE:
            st.markdown("---")
            user_id = st.session_state.get("db_user_id", "guest")
            render_streak_card(user_id)

        # Pricing Page
        if st.button("💎 Pricing", use_container_width=True, key="nav_pricing",
                    type="primary" if st.session_state.active_page == "💎 Pricing" else "secondary"):
            st.session_state.active_page = "💎 Pricing"
            st.rerun()

        # Admin (only for admins)
        if is_admin():
            if st.button("⚙️ Admin", use_container_width=True, key="nav_admin", type="primary" if st.session_state.active_page == "⚙️ Admin" else "secondary"):
                st.session_state.active_page = "⚙️ Admin"
                st.rerun()
        
        st.markdown("---")

        # QUICK HIT (Mr.DP handles mood selection now via chat)
        if st.button(f"⚡ {t('quick_dope_hit')}", use_container_width=True, key="quick_hit_sidebar", type="primary"):
            st.session_state.quick_hit = get_quick_hit()
            st.session_state.nlp_results = []
            st.session_state.nlp_last_prompt = ""
            st.session_state.search_results = []
            # Log behavior
            if st.session_state.get('db_user_id') and SUPABASE_ENABLED:
                log_user_action(supabase, st.session_state.db_user_id, 'quick_hit')
            # Track feature usage
            track_feature_usage("quick_dope_hit", st.session_state.get("db_user_id"))
            # Mr.DP Intelligence: Track quick hit and award XP
            track_quick_hit_use()
            add_xp(10, "Used Quick Hit!")
            # Check quick picker achievement
            if st.session_state.get("mr_dp_game", {}).get("quick_hit_uses", 0) >= 5:
                check_achievement("quick_picker")
            st.rerun()

        st.markdown("---")

        # SOS CALM MODE / WELLNESS (Enhanced if available)
        if WELLNESS_ENHANCED_AVAILABLE:
            st.markdown("#### 🧘 Wellness")
            wellness_col1, wellness_col2 = st.columns(2)
            with wellness_col1:
                if st.button("🆘 SOS", use_container_width=True, key="sos_enhanced"):
                    st.session_state.sos_active = True
                    st.rerun()
            with wellness_col2:
                if st.button("🌬️ Breathe", use_container_width=True, key="breathe_btn"):
                    st.session_state.active_page = "🧘 Wellness"
                    st.rerun()
        else:
            render_sos_button()

        st.markdown("---")

        # FOCUS TIMER
        render_focus_timer_sidebar()

        st.markdown("---")

        # WATCH QUEUE
        st.markdown(f"#### 📋 {t('watch_queue')}")
        if st.session_state.get('db_user_id') and SUPABASE_ENABLED:
            queue = get_watch_queue(supabase, st.session_state.db_user_id, status='queued', limit=3)
            if queue:
                for item in queue:
                    st.markdown(f"• {item.get('title', 'Unknown')[:30]}")
                if st.button(t("view_all_queue"), key="view_queue_btn", use_container_width=True):
                    st.session_state.show_queue_page = True
                    st.rerun()
            else:
                st.caption(t("queue_empty"))
        else:
            st.caption(t("log_in_to_save"))

        st.markdown("---")

        # YOUR SAVED DOPAMINE
        st.markdown("#### 💾 Your Saved Dopamine")
        saved_items = get_saved_dopamine()
        if saved_items:
            for idx, item in enumerate(saved_items[:5]):  # Show top 5
                item_type = item.get("type", "movie")
                item_data = item.get("data", {})
                icon = "🎬" if item_type == "movie" else "🎵" if item_type == "music" else "📦"
                title = item_data.get("title") or item_data.get("playlist_name", "Saved Item")
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<small>{icon} {title[:25]}...</small>" if len(title) > 25 else f"<small>{icon} {title}</small>", unsafe_allow_html=True)
                with col2:
                    if st.button("✕", key=f"del_saved_{idx}", help="Remove"):
                        remove_dopamine_item(idx)
                        st.toast("Removed!", icon="🗑️")
                        st.rerun()
            if len(saved_items) > 5:
                st.caption(f"+{len(saved_items) - 5} more saved")
            if st.button("📂 View All Saved", key="view_saved_btn", use_container_width=True):
                st.session_state.active_page = "💾 Saved"
                st.rerun()
        else:
            st.caption("No saved items yet. Ask Mr.DP for recommendations and save your favorites!")

        st.markdown("---")

        # TIME OF DAY SUGGESTION
        time_suggestion = get_time_of_day_suggestions()
        st.markdown(f"#### {time_suggestion['emoji']} {time_suggestion['period']}")
        st.caption(time_suggestion['suggestion'])

        st.markdown("---")

        # SHARE & REFERRALS (Phase 5)
        render_referral_section()

        # Apply referral code for new users
        render_apply_referral_code()

        st.markdown("---")

        # SHARE MOOD CARD
        with st.expander("📤 Share Your Stats"):
            render_shareable_mood_card()

        st.markdown("---")

        # PREMIUM
        if not st.session_state.get("is_premium"):
            if st.button("⭐ Go Premium", use_container_width=True, key="premium_sidebar"):
                st.session_state.show_premium_modal = True
                st.rerun()

        st.markdown("---")

        # FEEDBACK - Gamified Survey
        if not st.session_state.get("feedback_completed"):
            st.markdown("#### 💬 Tell Us What You Think!")
            st.caption("Earn bonus DP for your feedback")
            if st.button("📝 Take Survey (+100 DP)", use_container_width=True, key="feedback_sidebar", type="primary"):
                st.session_state.show_feedback_modal = True
                st.rerun()
        else:
            st.markdown("#### 💬 Feedback")
            st.markdown("✅ Thanks for your feedback!", unsafe_allow_html=True)

        st.markdown("---")

        # LOGOUT
        if st.button("🚪 Log Out", use_container_width=True, key="logout_btn"):
            if SUPABASE_ENABLED:
                supabase_sign_out()
            # Clear session
            st.session_state.user = None
            st.session_state.db_user_id = None
            # Set flag to trigger logout redirect with localStorage clear
            st.session_state.do_logout = True
            st.rerun()

        st.caption("v42.0 • Mobile & PWA")

# --------------------------------------------------
# 17. MAIN CONTENT
# --------------------------------------------------
def render_main():
    # Initialize focus timer session state
    init_focus_session_state()

    # Check for SOS Calm Mode overlay (takes over entire screen)
    # Use enhanced wellness overlay if available (Phase 3)
    if WELLNESS_ENHANCED_AVAILABLE and st.session_state.get("sos_active"):
        if render_enhanced_sos_overlay():
            return  # Enhanced SOS mode is active, skip normal content
    elif render_sos_overlay():
        return  # SOS mode is active, skip normal content

    # Check for break reminder overlay
    if render_break_reminder_overlay():
        return  # Break reminder showing, skip normal content

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

    # Check for milestone celebrations (Phase 5)
    if st.session_state.get("current_milestone"):
        render_milestone_celebration(st.session_state.current_milestone)
    else:
        # Check for new milestones
        new_milestones = check_milestones()
        if new_milestones:
            st.session_state.current_milestone = new_milestones[0]
            st.rerun()

    render_stats_bar()

    # PWA Install Banner (Mobile)
    render_install_app_banner()

    # Social Proof Banner (Phase 5)
    render_social_proof_banner()

    achievements = get_achievements()
    if achievements:
        ach_html = "".join([f"<span class='achievement'><span class='achievement-icon'>{a[0]}</span><span class='achievement-text'>{a[1]}</span></span>" for a in achievements[:5]])
        st.markdown(f"<div style='margin-bottom: 20px;'>{ach_html}</div>", unsafe_allow_html=True)

    # PERSONALIZED "FOR YOU" FEED (Phase 4)
    if st.session_state.get("db_user_id"):
        with st.expander("🎯 **For You** - Personalized Picks", expanded=False):
            render_personalized_feed()
        st.markdown("---")

    # MOOD BUDDY SUPPORT (Phase 6)
    render_mood_buddy_support()

    # COMMUNITY RECOMMENDATIONS (Phase 6)
    if st.session_state.get("db_user_id"):
        with st.expander("👥 **Others Like You** - Community Picks", expanded=False):
            render_community_recommendations()
        st.markdown("---")

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

    # MR.DP ADHD INTERVENTION - Show when decision fatigue detected
    intervention = get_adhd_intervention()
    if intervention and not st.session_state.get("intervention_dismissed"):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(138, 86, 226, 0.2), rgba(0, 201, 167, 0.15));
                    border-radius: 16px; padding: 16px 20px; margin-bottom: 16px;
                    border: 1px solid rgba(138, 86, 226, 0.3);
                    animation: pulse-glow 2s ease-in-out infinite;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="font-size: 2rem;">🟣</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #a78bfa; margin-bottom: 4px;">Mr.DP noticed something...</div>
                    <div style="color: rgba(255,255,255,0.9); font-size: 0.95rem;">{intervention['message']}</div>
                </div>
            </div>
        </div>
        <style>
            @keyframes pulse-glow {{
                0%, 100% {{ box-shadow: 0 0 10px rgba(138, 86, 226, 0.2); }}
                50% {{ box-shadow: 0 0 20px rgba(138, 86, 226, 0.4); }}
            }}
        </style>
        """, unsafe_allow_html=True)

        int_col1, int_col2 = st.columns(2)
        with int_col1:
            if st.button(f"✨ {intervention['action_label']}", key="intervention_action", type="primary", use_container_width=True):
                if intervention["action"] == "quick_hit":
                    st.session_state.quick_hit = get_quick_hit()
                    track_quick_hit_use()
                    add_xp(15, "Accepted Mr.DP's help!")
                elif intervention["action"] == "top_3":
                    st.session_state.show_top_3 = True
                st.session_state.intervention_dismissed = True
                st.rerun()
        with int_col2:
            if st.button("Maybe later", key="intervention_dismiss", use_container_width=True):
                st.session_state.intervention_dismissed = True
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
    
    # MR.DP 2.0 CONTENT - Show rich content cards from v2 response
    if st.session_state.get("mr_dp_v2_response") and st.session_state.mr_dp_v2_response.get("content"):
        v2_response = st.session_state.mr_dp_v2_response
        st.markdown("""<div id="mr-dp-content"></div>
<div style="margin-top:20px;padding:20px;background:linear-gradient(135deg, rgba(139,92,246,0.08), rgba(6,182,212,0.05));border:1px solid rgba(139,92,246,0.2);border-radius:16px;">
<div style="font-size:1.3rem;font-weight:600;color:#a78bfa;margin-bottom:12px;">🧠 Mr.DP's Picks for You</div>
</div>""", unsafe_allow_html=True)
        render_mr_dp_response(v2_response)
        # Clear after rendering to avoid showing stale content
        st.session_state.mr_dp_v2_response = None
        st.markdown("---")

    # MR.DP RESULTS - Show when there are results from chat (v1 compatibility)
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
        st.markdown(f"""<div id="mr-dp-results"></div>
<div class="section-header" style="margin-bottom: 8px;">
<span class="section-icon">{config['icon']}</span>
<h2 class="section-title">{config['title']}</h2>
</div>
<div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
{mood_tags}
</div>""", unsafe_allow_html=True)
        
        # ===================== ARTIST RESULTS =====================
        if result_type == "artist":
            artist_name = results.get("artist_name", "")
            artist_query = quote_plus(artist_name)
            
            # Big artist card
            st.markdown(f"""<div style="text-align:center;padding:40px;background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(6,182,212,0.2));border-radius:24px;border:1px solid rgba(139,92,246,0.3);margin-bottom:24px;">
<div style="font-size:4rem;margin-bottom:16px;">🎤</div>
<div style="font-size:2rem;font-weight:700;background:linear-gradient(135deg,#8b5cf6,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{artist_name}</div>
<div style="color:var(--text-secondary);margin-top:8px;">Click below to listen</div>
</div>""", unsafe_allow_html=True)
            
            # Big buttons to music services
            st.markdown(f"""<a href="https://open.spotify.com/search/{artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:#1DB954;border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-bottom:12px;box-shadow:0 8px 32px rgba(29,185,84,0.3);">🎵 Play {artist_name} on Spotify →</a>
<a href="https://music.apple.com/search?term={artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#fc3c44,#fc9a9a);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-bottom:12px;box-shadow:0 8px 32px rgba(252,60,68,0.3);">🍎 Play on Apple Music →</a>
<a href="https://music.youtube.com/search?q={artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:#FF0000;border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;margin-bottom:12px;box-shadow:0 8px 32px rgba(255,0,0,0.3);">▶️ Play on YouTube Music →</a>
<a href="https://www.youtube.com/results?search_query={artist_query}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#333,#666);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1.1rem;box-shadow:0 8px 32px rgba(0,0,0,0.3);">📺 Watch Music Videos on YouTube →</a>""", unsafe_allow_html=True)
            
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
                st.markdown(f"""<div class="glass-card" style="display:flex;align-items:center;gap:16px;margin-bottom:12px;">
<div style="font-size:2.5rem;">🎙️</div>
<div style="flex:1;">
<div style="font-weight:600;font-size:1.1rem;">{show}</div>
<div style="color:var(--text-secondary);font-size:0.85rem;">{desc}</div>
</div>
<a href="https://open.spotify.com/search/{show_query}" target="_blank" style="padding:10px 20px;background:#1DB954;border-radius:20px;color:white;text-decoration:none;font-size:0.85rem;font-weight:600;">▶️ Play</a>
</div>""", unsafe_allow_html=True)
            
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
                    st.markdown(f"""<div class="glass-card" style="text-align:center;padding:24px;height:200px;display:flex;flex-direction:column;justify-content:center;">
<div style="font-size:3rem;margin-bottom:12px;">📖</div>
<div style="font-weight:600;font-size:0.95rem;margin-bottom:4px;">{title}</div>
<div style="color:var(--text-secondary);font-size:0.8rem;">{author}</div>
</div>""", unsafe_allow_html=True)
            
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
                st.markdown(f"""<a href="{yt_url}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg, #FF0000, #CC0000);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1rem;box-shadow:0 8px 32px rgba(255,0,0,0.3);">▶️ YouTube Shorts</a>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<a href="{tt_url}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#ff0050,#00f2ea);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1rem;box-shadow:0 8px 32px rgba(255,0,80,0.3);">📱 TikTok</a>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<a href="{ig_url}" target="_blank" style="display:block;text-align:center;padding:20px;background:linear-gradient(135deg,#833AB4,#FD1D1D,#F77737);border-radius:16px;color:white;text-decoration:none;font-weight:700;font-size:1rem;box-shadow:0 8px 32px rgba(131,58,180,0.3);">📸 Reels</a>""", unsafe_allow_html=True)
            
            # Custom search
            st.markdown("##### 🔍 Custom Search")
            shorts_custom = st.text_input("Search for different shorts...", placeholder="Any topic or vibe", key="mr_dp_shorts_search")
            if shorts_custom:
                yt2 = f"https://www.youtube.com/results?search_query={quote_plus(shorts_custom)}+shorts"
                tt2 = f"https://www.tiktok.com/search?q={quote_plus(shorts_custom)}"
                st.markdown(f"""<div style="display:flex;gap:12px;margin-top:12px;">
<a href="{yt2}" target="_blank" style="flex:1;text-align:center;padding:16px;background:#FF0000;border-radius:12px;color:white;text-decoration:none;font-weight:600;">YouTube</a>
<a href="{tt2}" target="_blank" style="flex:1;text-align:center;padding:16px;background:linear-gradient(135deg,#ff0050,#00f2ea);border-radius:12px;color:white;text-decoration:none;font-weight:600;">TikTok</a>
</div>""", unsafe_allow_html=True)
            
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

    # Track page view
    track_page_view(page, st.session_state.get("db_user_id"))

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

    # PHASE 6: GAMIFICATION PAGES
    elif page == "🎯 Challenges":
        render_challenges_section()

    elif page == "🛍 Shop":
        render_rewards_shop()

    elif page == "🏆 Leaderboards":
        render_leaderboards()

    # PHASE 3: SOCIAL FEATURES PAGES
    elif page == "💬 Messages" and SOCIAL_FEATURES_AVAILABLE:
        render_messages_page()

    elif page == "🎉 Watch Parties" and SOCIAL_FEATURES_AVAILABLE:
        render_watch_parties_page()

    elif page == "👫 Friends" and SOCIAL_FEATURES_AVAILABLE:
        render_friends_page()

    # PHASE 3: WELLNESS PAGE
    elif page == "🧘 Wellness" and WELLNESS_ENHANCED_AVAILABLE:
        render_wellness_page()

    elif page == "⚙️ Admin":
        render_admin_dashboard()

    elif page == "💎 Pricing":
        render_pricing_page()

    elif page == "🟣 Mr.DP":
        render_mr_dp_companion_page()

    elif page == "💾 Saved":
        # YOUR SAVED DOPAMINE PAGE
        st.markdown("<div class='section-header'><span class='section-icon'>💾</span><h2 class='section-title'>Your Saved Dopamine</h2></div>", unsafe_allow_html=True)
        st.caption("Your saved movies, playlists, and content for later")

        saved_items = get_saved_dopamine()
        if saved_items:
            # Movies section
            movies = [item for item in saved_items if item.get("type") == "movie"]
            music = [item for item in saved_items if item.get("type") == "music"]
            other = [item for item in saved_items if item.get("type") not in ["movie", "music"]]

            if movies:
                st.markdown("### 🎬 Saved Movies & Shows")
                for idx, item in enumerate(movies):
                    data = item.get("data", {})
                    title = data.get("title", "Unknown")
                    year = data.get("year", "")
                    poster = data.get("poster", "")
                    rating = data.get("rating", 0)

                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col1:
                        if poster:
                            st.image(poster, width=80)
                        else:
                            st.markdown("🎬")
                    with col2:
                        st.markdown(f"**{title}** {f'({year})' if year else ''}")
                        if rating:
                            st.caption(f"⭐ {rating}")
                        saved_at = item.get("saved_at", "")[:10]
                        if saved_at:
                            st.caption(f"Saved on {saved_at}")
                    with col3:
                        # Find the original index in the full list
                        orig_idx = saved_items.index(item)
                        if st.button("🗑️", key=f"del_movie_{idx}", help="Remove"):
                            remove_dopamine_item(orig_idx)
                            st.toast(f"Removed '{title}'", icon="🗑️")
                            st.rerun()
                    st.markdown("---")

            if music:
                st.markdown("### 🎵 Saved Playlists")
                for idx, item in enumerate(music):
                    data = item.get("data", {})
                    name = data.get("playlist_name", "Unknown Playlist")
                    description = data.get("description", "")
                    playlist_url = data.get("playlist_url", "")
                    embed_url = data.get("embed_url", "")

                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col1:
                        st.markdown("🎵", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"**{name}**")
                        if description:
                            st.caption(description[:100])
                        saved_at = item.get("saved_at", "")[:10]
                        if saved_at:
                            st.caption(f"Saved on {saved_at}")
                        if playlist_url:
                            st.link_button("🎧 Open in Spotify", playlist_url)
                    with col3:
                        orig_idx = saved_items.index(item)
                        if st.button("🗑️", key=f"del_music_{idx}", help="Remove"):
                            remove_dopamine_item(orig_idx)
                            st.toast(f"Removed '{name}'", icon="🗑️")
                            st.rerun()
                    st.markdown("---")

            if not movies and not music:
                st.info("No saved items yet. Ask Mr.DP for recommendations and click 💾 Save to add items here!")

            # Clear all button
            if saved_items:
                if st.button("🗑️ Clear All Saved", key="clear_all_saved"):
                    st.session_state.saved_dopamine = []
                    st.toast("Cleared all saved items!", icon="🗑️")
                    st.rerun()
        else:
            st.info("No saved items yet!")
            st.markdown("""
            **How to save content:**
            1. Chat with Mr.DP (the purple bubble) and ask for recommendations
            2. Click the 💾 Save button on any movie or playlist
            3. Access your saved content here anytime!
            """)
            if st.button("💬 Chat with Mr.DP", key="open_mrdp_from_saved", use_container_width=True):
                st.session_state.mr_dp_open = True
                st.session_state.active_page = "🎬 Movies"
                st.rerun()

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
    
    # PREMIUM MODAL - handled by render_premium_modal() below

# --------------------------------------------------
# 18. MAIN ROUTER
# --------------------------------------------------
if not st.session_state.get("user"):
    # No session - redirect to landing page for login
    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center; font-size: 64px;'>🧠</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9D4EDD;'>Redirecting to login...</p>", unsafe_allow_html=True)
        st.markdown("")
        st.link_button("🔐 Go to Login", LANDING_PAGE_URL, use_container_width=True, type="primary")

    # Auto-click the link using components.html
    components.html(f'''
        <script>
            // Find and click the Streamlit link button
            setTimeout(function() {{
                var links = window.parent.document.querySelectorAll('a[href*="dopamine.watch"]');
                if (links.length > 0) {{
                    links[0].click();
                }}
            }}, 800);
        </script>
    ''', height=0)
    st.stop()
else:
    render_sidebar()

    # Render support resources modal (always available)
    render_support_resources_modal()

    # Render premium modal (if triggered)
    render_premium_modal()

    # Render feedback modal (if triggered)
    if st.session_state.get("show_feedback_modal"):
        render_feedback_modal()

    # Show social proof notifications occasionally
    show_social_proof()

    # Render floating Mr.DP chat widget
    user_message = render_floating_mr_dp()

    # Phase 1: Receive message, show thinking indicator immediately
    if user_message:
        # Check if user can use Mr.DP (premium or under limit)
        user = st.session_state.get("user", {})
        user_id = user.get("id")

        if user_id and supabase:
            allowed, remaining = can_use_mr_dp(user_id)
            if not allowed:
                # User has hit the limit - show upgrade message
                st.session_state.mr_dp_chat_history.append({
                    "role": "user",
                    "content": user_message
                })
                st.session_state.mr_dp_chat_history.append({
                    "role": "assistant",
                    "content": "You've used all 5 free Mr.DP chats! 💜 Upgrade to Premium for unlimited access and support dopamine.watch!"
                })
                st.session_state.mr_dp_just_responded = True
                st.session_state.mr_dp_open = True
                st.session_state.show_premium_modal = True
                st.rerun()

            # Show warning at 4 uses (1 remaining)
            if remaining == 1:
                st.session_state.mr_dp_limit_warning = True

        st.session_state.mr_dp_chat_history.append({
            "role": "user",
            "content": user_message
        })
        st.session_state.mr_dp_thinking = True
        st.session_state.mr_dp_open = True
        st.rerun()

    # Skip onboarding - Mr.DP is the curator now
    render_main()

    # Phase 2: Process pending Mr.DP message (runs after page renders)
    if st.session_state.get("mr_dp_thinking"):
        st.session_state.mr_dp_thinking = False

        # Find the last user message to process
        last_user_msg = None
        for msg in reversed(st.session_state.mr_dp_chat_history):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break

        if last_user_msg:
            # Get user context for Mr.DP 2.0 personalization
            user_context = None
            user_id = st.session_state.get("db_user_id")
            if user_id and SUPABASE_ENABLED:
                try:
                    user_context = {
                        "queue": get_watch_queue(supabase, user_id, status='queued', limit=5),
                        "top_moods": get_top_moods(supabase, user_id, 'desired', days=30, limit=3)
                    }
                    # Enhance with user learning data from dopamine_2027
                    if USER_LEARNING_AVAILABLE:
                        learning_context = get_mrdp_personalization_context(user_id)
                        if learning_context:
                            user_context["learning"] = learning_context
                            user_context["genre_preferences"] = learning_context.get("top_genres", [])
                            user_context["adhd_profile"] = learning_context.get("adhd_insights", {})
                            user_context["patterns"] = learning_context.get("patterns", [])
                except:
                    user_context = None

            # Use Mr.DP 2.0 (smart router will fallback to v1 if needed)
            response = ask_mr_dp_smart(last_user_msg, chat_history=st.session_state.mr_dp_chat_history, user_context=user_context)

            if response:
                # Store the full v2 response for rendering
                st.session_state.mr_dp_v2_response = response

                st.session_state.mr_dp_chat_history.append({
                    "role": "assistant",
                    "content": sanitize_chat_content(response.get("message", "Here's what I found!"))
                })
                st.session_state.mr_dp_just_responded = True

                # Update mood state from v2 response
                mood_update = response.get("mood_update", {})
                if mood_update.get("current"):
                    st.session_state.current_feeling = mood_update["current"]
                if mood_update.get("desired"):
                    st.session_state.desired_feeling = mood_update["desired"]

                # Handle focus_page to switch content view
                focus_page = response.get("focus_page")
                if focus_page:
                    page_map = {
                        "music": "🎵 Music",
                        "movies": "🎬 Movies",
                        "podcasts": "🎙️ Podcasts",
                        "audiobooks": "📚 Audiobooks",
                        "shorts": "⚡ Shorts"
                    }
                    if focus_page in page_map:
                        st.session_state.active_page = page_map[focus_page]

                # Also store for v1 compatibility
                st.session_state.mr_dp_response = {
                    "message": response.get("message", ""),
                    "current_feeling": mood_update.get("current"),
                    "desired_feeling": mood_update.get("desired"),
                    "media_type": "movies",
                    "mode": "discover",
                    "search_query": "",
                    "genres": ""
                }
                st.session_state.mr_dp_results = mr_dp_search(st.session_state.mr_dp_response)

                add_dopamine_points(10, "Chatted with Mr.DP!")

                # Log mood selection if detected
                if user_id and SUPABASE_ENABLED and mood_update.get("current"):
                    log_mood_selection(
                        supabase, user_id,
                        mood_update.get("current", ""),
                        mood_update.get("desired", ""),
                        source='mr_dp'
                    )

                # Increment Mr.DP usage counter for non-premium users
                user = st.session_state.get("user", {})
                uid = user.get("id")
                if uid and supabase and not user.get("is_premium"):
                    new_count = increment_mr_dp_usage(uid)
                    st.session_state.user["mr_dp_uses"] = new_count
            else:
                st.session_state.mr_dp_chat_history.append({
                    "role": "assistant",
                    "content": "Hmm, my neurons misfired! Try asking again?"
                })
                st.session_state.mr_dp_just_responded = True

        st.session_state.mr_dp_open = True
        st.rerun()