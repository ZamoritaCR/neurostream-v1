"""
Dopamine.watch 2027 - Authentication
Login, signup, and social auth modals.
"""

import streamlit as st
from core.session import get_state, hide_modal, set_user
from config.database import sign_in, sign_up, sign_in_with_google


def render_auth_modal():
    """Render authentication modal if needed."""

    modal_type = get_state("show_modal")

    if modal_type not in ["login", "signup"]:
        return

    # Modal overlay
    st.markdown("""
    <div class="modal-backdrop" onclick="window.dispatchEvent(new CustomEvent('close-modal'))">
        <div class="modal" onclick="event.stopPropagation()">
    """, unsafe_allow_html=True)

    if modal_type == "signup":
        render_signup_form()
    else:
        render_login_form()

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_login_form():
    """Render the login form."""

    st.markdown("""
    <div class="auth-header">
        <h2>Welcome back! 👋</h2>
        <p>Sign in to continue your dopamine journey</p>
    </div>
    """, unsafe_allow_html=True)

    # Google Sign In
    if st.button("Continue with Google", key="google_login", use_container_width=True):
        url = sign_in_with_google()
        if url:
            st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">', unsafe_allow_html=True)

    st.markdown("<div class='auth-divider'><span>or</span></div>", unsafe_allow_html=True)

    # Email/Password form
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if email and password:
                result = sign_in(email, password)
                if result.get("user"):
                    set_user(result["user"])
                    hide_modal()
                    st.rerun()
                else:
                    st.error(result.get("error", "Sign in failed"))
            else:
                st.warning("Please enter email and password")

    # Switch to signup
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Don't have an account? Sign up", key="switch_signup"):
            st.session_state.show_modal = "signup"
            st.rerun()
    with col2:
        if st.button("Close", key="close_login"):
            hide_modal()
            st.rerun()


def render_signup_form():
    """Render the signup form."""

    st.markdown("""
    <div class="auth-header">
        <h2>Join dopamine.watch 🧠</h2>
        <p>Start your personalized content journey</p>
    </div>
    """, unsafe_allow_html=True)

    # Google Sign Up
    if st.button("Continue with Google", key="google_signup", use_container_width=True):
        url = sign_in_with_google()
        if url:
            st.markdown(f'<meta http-equiv="refresh" content="0;url={url}">', unsafe_allow_html=True)

    st.markdown("<div class='auth-divider'><span>or</span></div>", unsafe_allow_html=True)

    # Email/Password form
    with st.form("signup_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")

        submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            if email and password and confirm:
                if password != confirm:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    result = sign_up(email, password)
                    if result.get("user"):
                        set_user(result["user"])
                        hide_modal()
                        st.success("Account created! Welcome to dopamine.watch!")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Sign up failed"))
            else:
                st.warning("Please fill in all fields")

    # Switch to login
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Already have an account? Sign in", key="switch_login"):
            st.session_state.show_modal = "login"
            st.rerun()
    with col2:
        if st.button("Close", key="close_signup"):
            hide_modal()
            st.rerun()
