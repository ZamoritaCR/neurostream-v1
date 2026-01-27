"""
Mr.DP Floating Chat Widget
Using Streamlit's native chat components
"""

import streamlit as st


def render_floating_mr_dp():
    """
    Render floating Mr.DP chatbot that stays on screen while scrolling.
    Only shows when user is logged in.
    Returns user message if sent, None otherwise.
    """

    # Only show if user is logged in
    if not st.session_state.get("user"):
        return None

    # Get state
    is_open = st.session_state.get("mr_dp_open", False)
    chat_history = st.session_state.get("mr_dp_chat_history", [])

    # Floating brain emoji avatar with CSS
    st.markdown("""
    <style>
    .mr-dp-floating-avatar {
        position: fixed;
        top: 80px;
        right: 24px;
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
        border-radius: 50%;
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 999999;
        font-size: 2rem;
        animation: bounce 3s ease-in-out infinite;
        transition: all 0.3s ease;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .mr-dp-floating-avatar:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
    }

    /* Style the chat container to float in top-right */
    .mr-dp-chat-container {
        position: fixed !important;
        top: 160px !important;
        right: 24px !important;
        width: 380px !important;
        max-height: 600px !important;
        background: rgba(13, 13, 20, 0.98) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        z-index: 999998 !important;
        padding: 20px !important;
        overflow-y: auto !important;
    }

    /* Hide chat container when closed */
    .mr-dp-chat-container.hidden {
        display: none !important;
    }

    /* Style Streamlit chat messages for Mr.DP */
    .mr-dp-chat-container [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 8px 0 !important;
    }

    .mr-dp-chat-container [data-testid="stChatMessage"][data-testid-user="user"] {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4) !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin-left: 40px !important;
    }

    .mr-dp-chat-container [data-testid="stChatMessage"][data-testid-user="assistant"] {
        background: rgba(139, 92, 246, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin-right: 40px !important;
    }

    /* Style chat input */
    .mr-dp-chat-container [data-testid="stChatInput"] {
        background: rgba(139, 92, 246, 0.1) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
    }

    .mr-dp-chat-container [data-testid="stChatInput"]:focus-within {
        border-color: #8b5cf6 !important;
        background: rgba(139, 92, 246, 0.15) !important;
    }
    </style>

    <div class="mr-dp-floating-avatar" title="Chat with Mr.DP (click to toggle)">
        🧠
    </div>
    """, unsafe_allow_html=True)

    # Toggle button
    col1, col2, col3 = st.columns([6, 1, 1])
    with col3:
        if st.button("✕" if is_open else "💬", key="mr_dp_toggle", help="Toggle Mr.DP Chat"):
            st.session_state.mr_dp_open = not is_open
            st.rerun()

    # Show chat in a container when open
    if is_open:
        # Create a container div with custom class
        st.markdown('<div class="mr-dp-chat-container">', unsafe_allow_html=True)

        # Chat header
        st.markdown("### 🧠 Mr.DP Chat")
        st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -10px;">● Online - Your Dopamine Buddy</p>', unsafe_allow_html=True)
        st.markdown("---")

        # Display chat history using Streamlit's native chat components
        if chat_history:
            for msg in chat_history[-8:]:  # Show last 8 messages
                with st.chat_message(msg["role"], avatar="🧠" if msg["role"] == "assistant" else "😊"):
                    st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🧠"):
                st.write("👋 Hey! Tell me how you're feeling and I'll find the perfect content for you!")

        # Chat input using Streamlit's native chat_input
        user_input = st.chat_input("How are you feeling?", key="mr_dp_chat_input")

        st.markdown('</div>', unsafe_allow_html=True)

        # Return the user's message if they sent one
        if user_input:
            return user_input

    return None
