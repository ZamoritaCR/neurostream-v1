"""
Dopamine.watch 2027 - Chat Interface
Full-screen Mr.DP chat interface.
"""

import streamlit as st
from core.session import (
    get_state, add_mr_dp_message, mr_dp_start_thinking,
    mr_dp_done_thinking, add_points
)
from services.mr_dp.agent import get_mr_dp_response


def render_chat():
    """Render the full chat interface with Mr.DP."""

    st.markdown("""
    <div class="chat-container animate-fade-in">
        <div class="chat-header">
            <div class="chat-avatar">🧠</div>
            <div class="chat-info">
                <h2>Mr.DP</h2>
                <span class="chat-status">Your Dopamine Curator</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat messages container
    chat_container = st.container()

    with chat_container:
        render_chat_messages()

    # Input area at bottom
    render_chat_input()


def render_chat_messages():
    """Render the chat message history."""

    history = get_state("mr_dp_chat_history", [])

    if not history:
        # Welcome message
        st.markdown("""
        <div class="chat-welcome">
            <div class="welcome-avatar animate-float">🧠</div>
            <h3>Hey there! I'm Mr.DP</h3>
            <p>Your personal dopamine curator. Tell me how you're feeling or what you're in the mood for, and I'll find something perfect!</p>
            <div class="suggestion-chips">
                <span class="chip">I'm stressed</span>
                <span class="chip">I'm bored</span>
                <span class="chip">Cheer me up</span>
                <span class="chip">Quick pick</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-bubble user-bubble">{content}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="message-avatar">🧠</div>
                    <div class="message-bubble assistant-bubble">{content}</div>
                </div>
                """, unsafe_allow_html=True)

    # Show thinking indicator
    if get_state("mr_dp_thinking"):
        st.markdown("""
        <div class="chat-message assistant-message">
            <div class="message-avatar">🧠</div>
            <div class="message-bubble assistant-bubble">
                <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_chat_input():
    """Render the chat input area."""

    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])

        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Tell me how you're feeling...",
                label_visibility="collapsed"
            )

        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted and user_input:
            process_message(user_input)


def process_message(user_message: str):
    """Process a user message and get Mr.DP response."""

    # Add user message
    add_mr_dp_message("user", user_message)

    # Set thinking state
    mr_dp_start_thinking()

    # Get response
    user_context = {
        "recent_moods": [get_state("current_mood")],
        "saved_content": get_state("user_queue", [])[:5]
    }

    response = get_mr_dp_response(
        user_message,
        get_state("mr_dp_chat_history", []),
        user_context
    )

    # Add assistant message
    add_mr_dp_message("assistant", response.get("message", ""))

    # Store full response for UI
    st.session_state.mr_dp_v2_response = response

    # Update mood if detected
    mood_update = response.get("mood_update", {})
    if mood_update.get("current"):
        st.session_state.current_mood = mood_update["current"]

    # Done thinking
    mr_dp_done_thinking()

    # Add points
    add_points(10, "Chatted with Mr.DP")

    st.rerun()
