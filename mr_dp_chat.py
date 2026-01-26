"""
Mr.DP Chat Widget - Fixed Implementation
Icon and chat both on RIGHT side, using actual neuron SVG
"""

import streamlit as st


def render_mr_dp_widget():
    """
    Render Mr.DP floating chat widget on RIGHT side
    Icon + chat popup together (not across screen)
    """

    # Get/initialize chat history
    if "mr_dp_chat_history" not in st.session_state:
        st.session_state.mr_dp_chat_history = []

    if "mr_dp_open" not in st.session_state:
        st.session_state.mr_dp_open = False

    chat_history = st.session_state.mr_dp_chat_history
    is_open = st.session_state.mr_dp_open

    # Build messages HTML
    messages_html = ""
    if chat_history:
        for msg in chat_history[-6:]:  # Last 6 messages
            if msg["role"] == "user":
                messages_html += f'''
                <div class="mr-dp-msg user">{msg['content']}</div>
                '''
            else:
                messages_html += f'''
                <div class="mr-dp-msg assistant">{msg['content']}</div>
                '''
    else:
        messages_html = '''
        <div class="mr-dp-empty">
            <div class="mr-dp-empty-icon">🧠</div>
            <div>Hey! I'm Mr.DP. Tell me how you're feeling and I'll find the perfect content for you!</div>
        </div>
        '''

    # Neuron SVG (from index.html - happy expression)
    neuron_svg = '''
    <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
    <linearGradient id="ng" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#a78bfa"/>
    <stop offset="50%" style="stop-color:#8b5cf6"/>
    <stop offset="100%" style="stop-color:#7c3aed"/>
    </linearGradient>
    <linearGradient id="ag" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" style="stop-color:#8b5cf6"/>
    <stop offset="100%" style="stop-color:#06b6d4"/>
    </linearGradient>
    </defs>
    <g>
    <path d="M32 12 Q28 4 20 2" stroke="url(#ag)" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="20" cy="2" r="3" fill="#06b6d4"/>
    <path d="M32 12 Q36 4 44 2" stroke="url(#ag)" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="44" cy="2" r="3" fill="#06b6d4"/>
    <path d="M32 12 Q32 6 32 0" stroke="url(#ag)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <circle cx="32" cy="0" r="2.5" fill="#10b981"/>
    <path d="M12 28 Q4 24 0 20" stroke="url(#ag)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <circle cx="0" cy="20" r="2.5" fill="#f59e0b"/>
    <path d="M52 28 Q60 24 64 20" stroke="url(#ag)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <circle cx="64" cy="20" r="2.5" fill="#f59e0b"/>
    </g>
    <path d="M32 52 Q32 58 28 62" stroke="url(#ag)" stroke-width="4" fill="none" stroke-linecap="round"/>
    <circle cx="28" cy="62" r="3" fill="#10b981"/>
    <ellipse cx="32" cy="32" rx="22" ry="20" fill="url(#ng)"/>
    <ellipse cx="26" cy="24" rx="8" ry="5" fill="white" opacity="0.3"/>
    <text x="22" y="32" font-size="10" fill="white" text-anchor="middle" font-family="Arial">◠</text>
    <text x="42" y="32" font-size="10" fill="white" text-anchor="middle" font-family="Arial">◠</text>
    <path d="M18 24 Q22 22 26 24" stroke="white" stroke-width="1.5" fill="none" opacity="0.8"/>
    <path d="M38 24 Q42 22 46 24" stroke="white" stroke-width="1.5" fill="none" opacity="0.8"/>
    <path d="M24 38 Q32 46 40 38" stroke="#ff6b9d" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="18" cy="36" r="5" fill="#ff6b9d" opacity="0.3"/>
    <circle cx="46" cy="36" r="5" fill="#ff6b9d" opacity="0.3"/>
    <text x="54" y="14" font-size="8" fill="#ffd700" opacity="0.8">✦</text>
    <text x="8" y="18" font-size="6" fill="#ffd700" opacity="0.6">✦</text>
    </svg>
    '''

    # Render floating widget HTML/CSS on RIGHT side
    popup_class = "mr-dp-popup open" if is_open else "mr-dp-popup"

    st.markdown(f"""
    <style>
    /* Mr.DP Container - RIGHT SIDE */
    .mr-dp-container {{
        position: fixed;
        top: 80px;
        right: 24px;
        z-index: 99999;
    }}

    /* Floating Avatar Button */
    .mr-dp-avatar {{
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
        transition: transform 0.2s;
    }}

    .mr-dp-avatar:hover {{
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
        animation: none;
    }}

    .mr-dp-avatar svg {{
        width: 48px;
        height: 48px;
    }}

    @keyframes mrDpBounce {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-8px); }}
    }}

    /* Chat Popup - BELOW avatar on RIGHT */
    .mr-dp-popup {{
        position: absolute;
        top: 80px;
        right: 0;
        width: 340px;
        max-height: 420px;
        background: rgba(15, 15, 20, 0.98);
        border: 1px solid rgba(139, 92, 246, 0.4);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
        display: none;
        flex-direction: column;
        backdrop-filter: blur(20px);
    }}

    .mr-dp-popup.open {{
        display: flex;
    }}

    /* Header */
    .mr-dp-header {{
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(6, 182, 212, 0.2));
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 1px solid rgba(139, 92, 246, 0.25);
    }}

    .mr-dp-header svg {{
        width: 40px;
        height: 40px;
    }}

    .mr-dp-header-name {{
        font-weight: 700;
        font-size: 1rem;
        background: linear-gradient(135deg, #a78bfa, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .mr-dp-header-status {{
        font-size: 0.7rem;
        color: #10b981;
    }}

    /* Messages */
    .mr-dp-messages {{
        padding: 16px;
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-height: 280px;
    }}

    .mr-dp-msg {{
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 0.9rem;
        line-height: 1.6;
        max-width: 85%;
        word-wrap: break-word;
    }}

    .mr-dp-msg.user {{
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 6px;
    }}

    .mr-dp-msg.assistant {{
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.25);
        color: #f5f5f7;
        margin-right: auto;
        border-bottom-left-radius: 6px;
    }}

    /* Empty State */
    .mr-dp-empty {{
        text-align: center;
        padding: 30px 20px;
        color: rgba(255, 255, 255, 0.5);
        line-height: 1.6;
    }}

    .mr-dp-empty-icon {{
        font-size: 2.5rem;
        margin-bottom: 12px;
    }}

    /* Mobile */
    @media (max-width: 500px) {{
        .mr-dp-container {{
            top: 70px;
            right: 12px;
        }}
        .mr-dp-popup {{
            width: 300px;
        }}
    }}
    </style>

    <div class="mr-dp-container">
        <!-- Chat Popup -->
        <div class="{popup_class}">
            <div class="mr-dp-header">
                {neuron_svg}
                <div>
                    <div class="mr-dp-header-name">Mr.DP</div>
                    <div class="mr-dp-header-status">● Online - Your Dopamine Buddy</div>
                </div>
            </div>
            <div class="mr-dp-messages">
                {messages_html}
            </div>
        </div>

        <!-- Floating Avatar -->
        <div class="mr-dp-avatar" title="Chat with Mr.DP" id="mrDpToggle">
            {neuron_svg}
        </div>
    </div>

    <script>
    // Toggle popup on avatar click
    const avatar = document.getElementById('mrDpToggle');
    if (avatar) {{
        avatar.onclick = () => {{
            // Tell Streamlit to toggle
            window.parent.postMessage({{type: 'mr_dp_toggle'}}, '*');
        }};
    }}
    </script>
    """, unsafe_allow_html=True)

    # Handle toggle (button to open/close)
    if st.button("Toggle Mr.DP Chat", key="mr_dp_toggle_btn", type="secondary"):
        st.session_state.mr_dp_open = not st.session_state.mr_dp_open
        st.rerun()

    # Input form (only show when open)
    if is_open:
        with st.form(key="mr_dp_form", clear_on_submit=True):
            cols = st.columns([5, 1])
            with cols[0]:
                user_input = st.text_input(
                    "How are you feeling?",
                    placeholder="I'm feeling anxious...",
                    label_visibility="collapsed",
                    key="mr_dp_input_field"
                )
            with cols[1]:
                submit = st.form_submit_button("Send", use_container_width=True)

            if submit and user_input.strip():
                return user_input.strip()

    return None
