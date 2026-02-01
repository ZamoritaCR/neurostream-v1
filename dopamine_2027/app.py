"""
═══════════════════════════════════════════════════════════════════════════════
DOPAMINE.WATCH 2027
Your AI-Powered Dopamine Curator
Built for ADHD brains, with love.
═══════════════════════════════════════════════════════════════════════════════

Main entry point for the Streamlit application.
This file should remain under 200 lines - all logic is in modules.
"""

import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import configuration
from config.settings import get_page_config, FEATURES, APP_NAME

# Import core modules
from core.session import init_session_state, is_authenticated, get_state

# Import feature pages
from features.landing.hero import render_landing_page
from features.home.dashboard import render_home
from features.discover.mood_selector import render_discover
from features.chat.interface import render_chat
from features.profile.view import render_profile
from features.auth.login import render_auth_modal

# Import components
from components.navigation.sidebar import render_sidebar
from components.mr_dp_ui.floating_widget import render_floating_mr_dp
from components.modern_ui.toasts import render_toasts
from components.modern_ui.modals import render_modal


def load_css():
    """Load the design system CSS."""
    css_path = project_root / "styles" / "design_system.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════

    st.set_page_config(**get_page_config())

    # ═══════════════════════════════════════════════════════════════════════════
    # INITIALIZATION
    # ═══════════════════════════════════════════════════════════════════════════

    # Load CSS
    load_css()

    # Initialize session state
    init_session_state()

    # ═══════════════════════════════════════════════════════════════════════════
    # ROUTING
    # ═══════════════════════════════════════════════════════════════════════════

    current_page = get_state("current_page", "home")

    # Check authentication
    authenticated = is_authenticated()

    # If not authenticated, show landing page
    if not authenticated:
        render_landing_page()
        render_auth_modal()
        return

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATED LAYOUT
    # ═══════════════════════════════════════════════════════════════════════════

    # Render sidebar navigation
    render_sidebar()

    # Main content area
    main_container = st.container()

    with main_container:
        # Route to appropriate page
        if current_page == "home":
            render_home()
        elif current_page == "discover":
            render_discover()
        elif current_page == "chat":
            render_chat()
        elif current_page == "profile":
            render_profile()
        elif current_page == "queue":
            from features.queue.personal import render_queue
            render_queue()
        elif current_page == "friends":
            from features.social.friends_list import render_friends
            render_friends()
        elif current_page == "settings":
            from features.profile.settings import render_settings
            render_settings()
        elif current_page == "premium":
            from features.premium.pricing import render_premium
            render_premium()
        else:
            render_home()

    # ═══════════════════════════════════════════════════════════════════════════
    # FLOATING ELEMENTS (Always visible)
    # ═══════════════════════════════════════════════════════════════════════════

    # Mr.DP floating widget
    render_floating_mr_dp()

    # Toast notifications
    render_toasts()

    # Modal dialogs
    render_modal()


# ═══════════════════════════════════════════════════════════════════════════════
# RUN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
