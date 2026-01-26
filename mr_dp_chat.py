"""
Mr.DP Chat Widget - Clean Implementation
Matches front-end index.html exactly, using Streamlit for backend
"""

import streamlit as st


def render_mr_dp_widget():
    """
    Render Mr.DP floating chat widget
    Uses sidebar for chat interface (reliable) + floating indicator (visual)
    """

    # Get/initialize chat history
    if "mr_dp_chat_history" not in st.session_state:
        st.session_state.mr_dp_chat_history = []

    chat_history = st.session_state.mr_dp_chat_history

    # Floating visual indicator (top-right)
    st.markdown("""
    <style>
    .mr-dp-indicator {
        position: fixed;
        top: 80px;
        right: 24px;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 50%, #10b981 100%);
        box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        animation: mrDpBounce 3s ease-in-out infinite;
        z-index: 9999;
        font-size: 2rem;
    }

    @keyframes mrDpBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .mr-dp-indicator:hover {
        transform: scale(1.1);
        animation: none;
    }
    </style>

    <div class="mr-dp-indicator" title="Mr.DP - Check sidebar to chat!">
        🧠
    </div>
    """, unsafe_allow_html=True)

    # Chat interface in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🧠 Mr.DP Chat")
        st.caption("● Online - Your Dopamine Buddy")

        # Chat history container
        chat_container = st.container()

        with chat_container:
            if not chat_history:
                st.info("👋 Hey! Tell me how you're feeling and I'll find the perfect content for you!")
            else:
                for msg in chat_history[-8:]:  # Show last 8 messages
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                                    color: white; padding: 12px 16px; border-radius: 18px 18px 6px 18px;
                                    margin: 8px 0; margin-left: auto; max-width: 85%; text-align: right;">
                            {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(139, 92, 246, 0.15);
                                    border: 1px solid rgba(139, 92, 246, 0.25);
                                    color: #f5f5f7; padding: 12px 16px; border-radius: 18px 18px 18px 6px;
                                    margin: 8px 0; max-width: 85%;">
                            {msg['content']}
                        </div>
                        """, unsafe_allow_html=True)

        # Input area
        with st.form(key="mr_dp_form", clear_on_submit=True):
            user_input = st.text_input(
                "How are you feeling?",
                placeholder="I'm feeling anxious...",
                label_visibility="collapsed",
                key="mr_dp_input_field"
            )
            submit = st.form_submit_button("Send 🚀", use_container_width=True)

            if submit and user_input.strip():
                return user_input.strip()

    return None
