"""
Mr.DP Floating Chat Widget
Simplified version that definitely renders
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

    # Simple floating avatar with inline styles
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
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .mr-dp-floating-avatar:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
    }
    </style>

    <div class="mr-dp-floating-avatar" title="Chat with Mr.DP">
        🧠
    </div>
    """, unsafe_allow_html=True)

    # Show chat in sidebar when open
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🧠 Mr.DP Chat")

        # Toggle button
        if st.button("Close Chat" if is_open else "Open Chat", key="mr_dp_toggle"):
            st.session_state.mr_dp_open = not is_open
            st.rerun()

        # Show chat interface when open
        if is_open:
            # Display chat history
            if chat_history:
                for msg in chat_history[-5:]:  # Show last 5 messages
                    if msg["role"] == "user":
                        st.markdown(f"**You:** {msg['content']}")
                    else:
                        st.markdown(f"**Mr.DP:** {msg['content']}")
            else:
                st.info("👋 Hey! Tell me how you're feeling and I'll find the perfect content for you!")

            # Chat input
            with st.form(key="mr_dp_chat_form"):
                user_input = st.text_input("How are you feeling?", key="mr_dp_input")
                submitted = st.form_submit_button("Send 🚀")

                if submitted and user_input:
                    return user_input

    return None
