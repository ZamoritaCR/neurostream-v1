"""
Mr.DP Floating Chat Widget
Professional floating chat popup injected via JavaScript.
Uses native Streamlit chat_input positioned at the popup via CSS.
"""

import streamlit as st
import streamlit.components.v1 as components
import json


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
<text x="54" y="14" font-size="8" fill="#ffd700" opacity="0.8">&#10022;</text>
<text x="8" y="18" font-size="6" fill="#ffd700" opacity="0.6">&#10022;</text>
</svg>'''


def render_floating_mr_dp():
    """
    Render floating Mr.DP chatbot as a professional chat popup.
    Uses JavaScript for the UI toggle and native st.chat_input for message input.
    The st.chat_input is repositioned via CSS to appear at the popup location.
    Returns user message if sent, None otherwise.
    """

    # Only show if user is logged in
    if not st.session_state.get("user"):
        return None

    # Get chat state
    chat_history = st.session_state.get("mr_dp_chat_history", [])
    is_open = st.session_state.get("mr_dp_open", False)
    is_thinking = st.session_state.get("mr_dp_thinking", False)

    # Reset mr_dp_open after reading (JS will manage open state from here)
    if is_open:
        st.session_state.mr_dp_open = False

    # Build chat HTML
    expression = 'thinking' if is_thinking else ('happy' if is_open else 'sleeping')
    mr_dp_svg = get_mr_dp_svg(expression)

    chat_html = ""
    if chat_history:
        for msg in chat_history[-8:]:
            content = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;").replace("\n", "<br>")
            if msg["role"] == "assistant":
                chat_html += f'<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai">{content}</div></div>'
            else:
                chat_html += f'<div class="mrdp-msg mrdp-user"><div class="mrdp-bubble mrdp-bubble-user">{content}</div></div>'
    else:
        chat_html = '<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai">&#128075; Hey! Tell me how you\'re feeling and I\'ll find the perfect content for you!</div></div>'

    # Add thinking indicator if processing
    if is_thinking:
        chat_html += '<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai"><span class="mrdp-thinking-dots"><span>.</span><span>.</span><span>.</span></span></div></div>'

    svg_escaped = json.dumps(mr_dp_svg)
    header_svg_escaped = json.dumps(get_mr_dp_svg("happy").replace("\n", ""))
    chat_html_escaped = json.dumps(chat_html)
    is_open_json = json.dumps(is_open)

    inject_script = f"""
    <script>
    (function() {{
        var pd = window.parent.document;

        // Clean up previous injection
        var old = pd.getElementById('mrdp-root');
        if (old) old.remove();
        var oldS = pd.getElementById('mrdp-css');
        if (oldS) oldS.remove();
        var oldJ = pd.getElementById('mrdp-js');
        if (oldJ) oldJ.remove();

        // Determine open state: Python says open OR JS was open
        var pythonOpen = {is_open_json};
        var jsOpen = pd.body.getAttribute('data-mrdp-open') === 'true';
        var shouldOpen = pythonOpen || jsOpen;

        // CSS
        var css = pd.createElement('style');
        css.id = 'mrdp-css';
        css.textContent = `
            #mrdp-root * {{ box-sizing: border-box; }}
            #mrdp-avatar {{
                position: fixed; bottom: 24px; right: 24px;
                width: 70px; height: 70px; border-radius: 50%;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                box-shadow: 0 8px 32px rgba(139,92,246,0.5);
                cursor: pointer; z-index: 2147483647;
                animation: mrdp-pulse 3s ease-in-out infinite;
                display: flex; align-items: center; justify-content: center;
                padding: 10px; transition: transform 0.3s;
            }}
            #mrdp-avatar:hover {{ transform: scale(1.1); }}
            @keyframes mrdp-pulse {{
                0%, 100% {{ box-shadow: 0 8px 32px rgba(139,92,246,0.5); }}
                50% {{ box-shadow: 0 8px 40px rgba(139,92,246,0.8); }}
            }}
            #mrdp-badge {{
                position: absolute; top: -2px; right: -2px;
                width: 18px; height: 18px; border-radius: 50%;
                background: #10b981; border: 2px solid #1a1a2e;
            }}
            #mrdp-popup {{
                position: fixed; bottom: 155px; right: 24px;
                width: 380px; height: 400px;
                background: #0d0d14; border: 1px solid rgba(139,92,246,0.3);
                border-bottom: none;
                border-radius: 16px 16px 0 0; z-index: 2147483645;
                box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 0 1px rgba(139,92,246,0.1);
                display: none; flex-direction: column;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                overflow: hidden;
            }}
            #mrdp-header {{
                padding: 16px 20px; display: flex; align-items: center; gap: 12px;
                border-bottom: 1px solid rgba(139,92,246,0.2);
                background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(6,182,212,0.05));
            }}
            #mrdp-header-avatar {{ width: 40px; height: 40px; flex-shrink: 0; }}
            #mrdp-header-info {{ flex: 1; }}
            #mrdp-header-name {{ color: #f5f5f7; font-weight: 600; font-size: 15px; }}
            #mrdp-header-status {{ color: #10b981; font-size: 12px; margin-top: 2px; }}
            #mrdp-close {{
                background: none; border: none; color: #888; font-size: 20px;
                cursor: pointer; padding: 4px 8px; border-radius: 8px;
                transition: all 0.2s;
            }}
            #mrdp-close:hover {{ background: rgba(139,92,246,0.2); color: #f5f5f7; }}
            #mrdp-messages {{
                flex: 1; overflow-y: auto; padding: 16px;
                display: flex; flex-direction: column; gap: 12px;
            }}
            #mrdp-messages::-webkit-scrollbar {{ width: 4px; }}
            #mrdp-messages::-webkit-scrollbar-thumb {{ background: rgba(139,92,246,0.3); border-radius: 4px; }}
            .mrdp-msg {{ display: flex; gap: 8px; align-items: flex-end; }}
            .mrdp-user {{ justify-content: flex-end; }}
            .mrdp-avatar {{ width: 28px; height: 28px; flex-shrink: 0; font-size: 20px; line-height: 28px; }}
            .mrdp-bubble {{
                padding: 10px 14px; border-radius: 16px;
                font-size: 14px; line-height: 1.5; max-width: 260px;
                word-wrap: break-word;
            }}
            .mrdp-bubble-ai {{
                background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.2);
                color: #e0e0e0; border-bottom-left-radius: 4px;
            }}
            .mrdp-bubble-user {{
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                color: #fff; border-bottom-right-radius: 4px;
            }}
            .mrdp-thinking-dots span {{
                display: inline-block;
                animation: mrdp-blink 1.4s infinite;
                font-size: 28px; line-height: 20px; letter-spacing: 3px; color: #8b5cf6;
            }}
            .mrdp-thinking-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
            .mrdp-thinking-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
            @keyframes mrdp-blink {{
                0%, 20% {{ opacity: 0.2; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.2; }}
            }}

            /* ---- Native Streamlit chat_input positioning ---- */
            /* Default: completely hidden (visibility:hidden prevents focus & scroll) */
            [data-testid="stBottom"],
            .stBottom {{
                position: fixed !important;
                bottom: 0 !important;
                right: 0 !important;
                visibility: hidden !important;
                opacity: 0 !important;
                height: 0 !important;
                overflow: hidden !important;
                pointer-events: none !important;
                z-index: -1 !important;
            }}
            [data-testid="stChatInput"] textarea,
            [data-testid="stChatInput"] input {{
                tabindex: -1;
            }}
            /* When popup is open: position at popup base */
            body.mrdp-open [data-testid="stBottom"],
            body.mrdp-open .stBottom {{
                position: fixed !important;
                bottom: 100px !important;
                right: 24px !important;
                left: auto !important;
                width: 380px !important;
                max-width: 380px !important;
                height: auto !important;
                overflow: visible !important;
                visibility: visible !important;
                opacity: 1 !important;
                pointer-events: auto !important;
                z-index: 2147483644 !important;
                background: transparent !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            /* Style the chat input to match popup */
            body.mrdp-open [data-testid="stChatInput"] {{
                background: #0d0d14 !important;
                border: 1px solid rgba(139,92,246,0.3) !important;
                border-top: 1px solid rgba(139,92,246,0.15) !important;
                border-radius: 0 0 16px 16px !important;
                padding: 10px 14px !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            }}
            body.mrdp-open [data-testid="stChatInput"] textarea,
            body.mrdp-open [data-testid="stChatInput"] input {{
                background: rgba(139,92,246,0.08) !important;
                border: 1px solid rgba(139,92,246,0.25) !important;
                border-radius: 10px !important;
                color: #f5f5f7 !important;
                caret-color: #f5f5f7 !important;
                font-size: 14px !important;
            }}
            body.mrdp-open [data-testid="stChatInput"] textarea::placeholder,
            body.mrdp-open [data-testid="stChatInput"] input::placeholder {{
                color: #666 !important;
            }}
            body.mrdp-open [data-testid="stChatInput"] button {{
                color: #8b5cf6 !important;
            }}
            body.mrdp-open [data-testid="stChatInput"] button svg {{
                fill: #8b5cf6 !important;
            }}
            /* Remove extra padding Streamlit adds for bottom bar */
            body.mrdp-open [data-testid="stBottomBlockContainer"] {{
                padding: 0 !important;
                max-width: 380px !important;
            }}
            @media (max-width: 480px) {{
                #mrdp-popup {{ width: calc(100vw - 16px); right: 8px; bottom: 145px; height: 350px; }}
                #mrdp-avatar {{ width: 56px; height: 56px; bottom: 16px; right: 16px; padding: 8px; }}
                body.mrdp-open [data-testid="stBottom"],
                body.mrdp-open .stBottom {{
                    width: calc(100vw - 16px) !important;
                    max-width: calc(100vw - 16px) !important;
                    right: 8px !important;
                    bottom: 90px !important;
                }}
            }}
        `;
        pd.head.appendChild(css);

        // JS functions in parent scope
        var js = pd.createElement('script');
        js.id = 'mrdp-js';
        js.textContent = `
            function mrdpToggle() {{
                var popup = document.getElementById('mrdp-popup');
                if (popup) {{
                    var isHidden = popup.style.display === 'none';
                    popup.style.display = isHidden ? 'flex' : 'none';
                    if (isHidden) {{
                        document.body.classList.add('mrdp-open');
                        document.body.setAttribute('data-mrdp-open', 'true');
                        var msgs = document.getElementById('mrdp-messages');
                        if (msgs) msgs.scrollTop = msgs.scrollHeight;
                        // Focus native Streamlit chat input
                        setTimeout(function() {{
                            var inp = document.querySelector('[data-testid="stChatInput"] textarea');
                            if (!inp) inp = document.querySelector('[data-testid="stChatInput"] input');
                            if (inp) inp.focus();
                        }}, 300);
                    }} else {{
                        document.body.classList.remove('mrdp-open');
                        document.body.setAttribute('data-mrdp-open', 'false');
                    }}
                }}
            }}
        `;
        pd.head.appendChild(js);

        // Set body class based on open state
        if (shouldOpen) {{
            pd.body.classList.add('mrdp-open');
            pd.body.setAttribute('data-mrdp-open', 'true');
        }} else {{
            pd.body.classList.remove('mrdp-open');
        }}

        // Widget HTML (messages only - native st.chat_input serves as input)
        var root = pd.createElement('div');
        root.id = 'mrdp-root';
        root.innerHTML = '<div id="mrdp-avatar" onclick="mrdpToggle()">'
            + {svg_escaped}
            + '<div id="mrdp-badge"></div>'
            + '</div>'
            + '<div id="mrdp-popup" style="display: ' + (shouldOpen ? 'flex' : 'none') + '">'
            + '<div id="mrdp-header">'
            + '<div id="mrdp-header-avatar">' + {header_svg_escaped} + '</div>'
            + '<div id="mrdp-header-info"><div id="mrdp-header-name">Mr.DP</div><div id="mrdp-header-status">&#9679; Online</div></div>'
            + '<button id="mrdp-close" onclick="mrdpToggle()">&#10005;</button>'
            + '</div>'
            + '<div id="mrdp-messages">' + {chat_html_escaped} + '</div>'
            + '</div>';
        pd.body.appendChild(root);

        // Scroll chat to bottom
        var msgs = pd.getElementById('mrdp-messages');
        if (msgs) msgs.scrollTop = msgs.scrollHeight;

        // Prevent hidden chat_input from stealing focus and dragging page down
        if (!shouldOpen) {{
            // Blur immediately and after delays to catch Streamlit's auto-focus
            function blurAndScroll() {{
                var inp = pd.querySelector('[data-testid="stChatInput"] textarea');
                if (inp) inp.blur();
                inp = pd.querySelector('[data-testid="stChatInput"] input');
                if (inp) inp.blur();
                // Scroll page back to top
                window.parent.scrollTo(0, 0);
                var container = pd.querySelector('[data-testid="stAppViewContainer"]');
                if (container) container.scrollTop = 0;
            }}
            blurAndScroll();
            setTimeout(blurAndScroll, 50);
            setTimeout(blurAndScroll, 150);
            setTimeout(blurAndScroll, 300);
        }}
    }})();
    </script>
    """

    components.html(inject_script, height=0, scrolling=False)

    # Native Streamlit chat input (positioned by CSS at popup location when open)
    user_input = st.chat_input("How are you feeling?", key="mr_dp_chat_input")

    if user_input:
        st.session_state.mr_dp_open = True

    return user_input
