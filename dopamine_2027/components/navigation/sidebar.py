"""
Dopamine.watch 2027 - Sidebar Navigation
Modern sidebar with navigation items and user menu.
"""

import streamlit as st
from core.session import get_user, navigate_to, get_state, is_premium
from config.settings import PAGES


def render_sidebar():
    """Render the navigation sidebar."""

    with st.sidebar:
        # Logo/Brand
        st.markdown("""
        <div class="sidebar-brand">
            <span class="brand-icon">🧠</span>
            <span class="brand-text">dopamine.watch</span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Navigation items
        current_page = get_state("current_page", "home")

        for page_key, page_info in PAGES.items():
            if page_info.get("auth_required", True):
                is_active = current_page == page_key

                if st.button(
                    f"{page_info['icon']} {page_info['label']}",
                    key=f"nav_{page_key}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary"
                ):
                    navigate_to(page_key)
                    st.rerun()

        st.divider()

        # User section
        render_user_section()


def render_user_section():
    """Render the user section at bottom of sidebar."""

    user = get_user()

    if user:
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="user-avatar">{user.get('display_name', 'U')[0].upper()}</div>
            <div class="user-info">
                <span class="user-name">{user.get('display_name', 'User')}</span>
                <span class="user-level">Level {get_state('level', 1)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Premium badge
        if is_premium():
            st.markdown('<span class="premium-badge">⭐ Premium</span>', unsafe_allow_html=True)

        # Logout button
        if st.button("Sign Out", key="logout_btn", use_container_width=True):
            from config.database import sign_out
            sign_out()
            st.session_state.clear()
            st.rerun()
