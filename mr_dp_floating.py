"""
Mr.DP Floating Chat Widget
Using Streamlit's native chat components with SVG neuron character
"""

import streamlit as st
import streamlit.components.v1 as components


def get_mr_dp_svg(expression='happy'):
    """Generate SVG for Mr.DP neuron character with different expressions"""
    expressions = {
        'happy': {'left_eye': '◠', 'right_eye': '◠', 'mouth': 'smile', 'blush': True},
        'sleeping': {'left_eye': '−', 'right_eye': '−', 'mouth': 'sleeping', 'blush': False},
        'thinking': {'left_eye': '•', 'right_eye': '•', 'mouth': 'hmm', 'blush': False},
        'excited': {'left_eye': '★', 'right_eye': '★', 'mouth': 'big_smile', 'blush': True}
    }

    expr = expressions.get(expression, expressions['happy'])

    mouths = {
        'smile': '<path d="M24 38 Q32 46 40 38" stroke="#ff6b9d" stroke-width="3" fill="none" stroke-linecap="round"/>',
        'sleeping': '<path d="M26 40 L38 40" stroke="#ff6b9d" stroke-width="2" fill="none" stroke-linecap="round"/>',
        'hmm': '<path d="M26 40 L38 38" stroke="#ff6b9d" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
        'big_smile': '<path d="M22 36 Q32 48 42 36" stroke="#ff6b9d" stroke-width="3" fill="none" stroke-linecap="round"/>'
    }

    blush = '<circle cx="18" cy="36" r="5" fill="#ff6b9d" opacity="0.3"/><circle cx="46" cy="36" r="5" fill="#ff6b9d" opacity="0.3"/>' if expr['blush'] else ''

    return f'''<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%;">
<defs>
<linearGradient id="ng-{expression}" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#a78bfa"/>
<stop offset="50%" style="stop-color:#8b5cf6"/>
<stop offset="100%" style="stop-color:#7c3aed"/>
</linearGradient>
<linearGradient id="ag-{expression}" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" style="stop-color:#8b5cf6"/>
<stop offset="100%" style="stop-color:#06b6d4"/>
</linearGradient>
</defs>
<g>
<path d="M32 12 Q28 4 20 2" stroke="url(#ag-{expression})" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="20" cy="2" r="3" fill="#06b6d4"/>
<path d="M32 12 Q36 4 44 2" stroke="url(#ag-{expression})" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="44" cy="2" r="3" fill="#06b6d4"/>
<path d="M32 12 Q32 6 32 0" stroke="url(#ag-{expression})" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="32" cy="0" r="2.5" fill="#10b981"/>
<path d="M12 28 Q4 24 0 20" stroke="url(#ag-{expression})" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="0" cy="20" r="2.5" fill="#f59e0b"/>
<path d="M52 28 Q60 24 64 20" stroke="url(#ag-{expression})" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="64" cy="20" r="2.5" fill="#f59e0b"/>
</g>
<path d="M32 52 Q32 58 28 62" stroke="url(#ag-{expression})" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="28" cy="62" r="3" fill="#10b981"/>
<ellipse cx="32" cy="32" rx="22" ry="20" fill="url(#ng-{expression})"/>
<ellipse cx="26" cy="24" rx="8" ry="5" fill="white" opacity="0.3"/>
<text x="22" y="32" font-size="10" fill="white" text-anchor="middle" font-family="Arial">{expr['left_eye']}</text>
<text x="42" y="32" font-size="10" fill="white" text-anchor="middle" font-family="Arial">{expr['right_eye']}</text>
<path d="M18 24 Q22 22 26 24" stroke="white" stroke-width="1.5" fill="none" opacity="0.8"/>
<path d="M38 24 Q42 22 46 24" stroke="white" stroke-width="1.5" fill="none" opacity="0.8"/>
{mouths[expr['mouth']]}
{blush}
<text x="54" y="14" font-size="8" fill="#ffd700" opacity="0.8">✦</text>
<text x="8" y="18" font-size="6" fill="#ffd700" opacity="0.6">✦</text>
</svg>'''


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

    # Get SVG for Mr.DP with appropriate expression
    expression = 'happy' if is_open else 'sleeping'
    mr_dp_svg = get_mr_dp_svg(expression)

    # Render floating Mr.DP avatar with components.html for proper display
    avatar_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
            }}
            .mr-dp-floating-avatar {{
                position: fixed;
                top: 80px;
                right: 24px;
                width: 80px;
                height: 80px;
                border-radius: 50%;
                box-shadow: 0 8px 32px rgba(139, 92, 246, 0.5);
                cursor: pointer;
                z-index: 999999;
                animation: bounce 3s ease-in-out infinite;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 8px;
            }}
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-8px); }}
            }}
            .mr-dp-floating-avatar:hover {{
                transform: scale(1.1);
                box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
            }}
        </style>
    </head>
    <body>
        <div class="mr-dp-floating-avatar" title="Chat with Mr.DP (click to toggle)" onclick="toggleChat()">
            {mr_dp_svg}
        </div>
        <script>
            function toggleChat() {{
                const url = new URL(window.top.location.href);
                url.searchParams.set('mr_dp_toggle', Date.now().toString());
                window.top.location.href = url.toString();
            }}
        </script>
    </body>
    </html>
    """

    components.html(avatar_html, height=0, scrolling=False)

    # Check for toggle in query params
    if "mr_dp_toggle" in st.query_params:
        st.session_state.mr_dp_open = not is_open
        # Clear the param
        st.query_params.pop("mr_dp_toggle", None)
        st.rerun()

    # Show chat in sidebar when open (reliable Streamlit approach)
    if is_open:
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🧠 Mr.DP Chat")
            st.markdown('<p style="color: #10b981; font-size: 0.85rem; margin-top: -10px;">● Online - Your Dopamine Buddy</p>', unsafe_allow_html=True)
            st.markdown("---")

            # Display chat history using Streamlit's native chat components
            if chat_history:
                for msg in chat_history[-8:]:  # Show last 8 messages
                    with st.chat_message(msg["role"], avatar=get_mr_dp_svg('happy') if msg["role"] == "assistant" else "😊"):
                        st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar=get_mr_dp_svg('happy')):
                    st.write("👋 Hey! Tell me how you're feeling and I'll find the perfect content for you!")

            # Chat input using Streamlit's native chat_input
            user_input = st.chat_input("How are you feeling?", key="mr_dp_chat_input")

            # Return the user's message if they sent one
            if user_input:
                return user_input

    return None
