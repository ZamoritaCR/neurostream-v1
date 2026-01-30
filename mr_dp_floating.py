"""
Mr.DP Floating Chat Widget
Professional floating chat popup with native HTML input.
Uses JavaScript for UI and bridges to Streamlit via hidden form.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import re


def sanitize_chat_content(content: str) -> str:
    """Remove any SVG tags or SVG-related content that might have leaked into chat messages."""
    if not content:
        return content

    # Remove SVG tags and their content
    content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Remove partial SVG elements that might appear
    content = re.sub(r'<(circle|rect|path|ellipse|polygon|line|polyline|g|defs|linearGradient|radialGradient|filter|animate|text|tspan)[^>]*/?>', '', content, flags=re.IGNORECASE)

    # Remove SVG closing tags
    content = re.sub(r'</(svg|circle|rect|path|ellipse|polygon|line|polyline|g|defs|linearGradient|radialGradient|filter|animate|text|tspan)>', '', content, flags=re.IGNORECASE)

    # Remove dpGradient references and other SVG ID patterns
    content = re.sub(r'(dpGradient|dpGlow|ng-|ag-)_?\w*', '', content, flags=re.IGNORECASE)

    # Remove any remaining SVG attributes
    content = re.sub(r'fill="url\([^)]*\)"', '', content)
    content = re.sub(r'(stroke|fill|opacity|transform|viewBox|xmlns)[^"]*="[^"]*"', '', content)

    # Clean up multiple spaces and newlines
    content = re.sub(r'\s+', ' ', content).strip()

    return content


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
    Uses JavaScript for UI with native HTML input in the popup.
    Bridges to Streamlit via hidden form for message submission.
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
            # Sanitize content to remove any SVG that might have leaked in
            raw_content = sanitize_chat_content(msg.get("content", ""))
            content = raw_content.replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;").replace("\n", "<br>")
            if msg["role"] == "assistant":
                chat_html += f'<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai">{content}</div></div>'
            else:
                chat_html += f'<div class="mrdp-msg mrdp-user"><div class="mrdp-bubble mrdp-bubble-user">{content}</div></div>'
    else:
        # First-time onboarding message - explain what Mr.DP can do
        chat_html = '''<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai">&#128075; Hey there! I'm <b>Mr.DP</b> - your personal dopamine curator!</div></div>
<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai">Here's what I can do for you:<br><br>&#127916; <b>Find movies & shows</b> that match your mood<br>&#127926; <b>Create playlists</b> for any vibe<br>&#127897; <b>Suggest podcasts</b> to keep you engaged<br>&#128218; <b>Recommend audiobooks</b> for focus or relaxation<br>&#9889; <b>Curate a movie marathon</b> for your night in</div></div>
<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">&#129504;</div><div class="mrdp-bubble mrdp-bubble-ai">Try saying something like:<br>&#8226; "I need something funny"<br>&#8226; "Play some chill music"<br>&#8226; "I'm feeling stressed"<br>&#8226; "Plan a movie marathon for tonight"</div></div>'''

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

        // Check if first time user (no previous interactions)
        var isFirstTime = !localStorage.getItem('mrdp_interacted');

        // CSS
        var css = pd.createElement('style');
        css.id = 'mrdp-css';
        css.textContent = `
            #mrdp-root * {{ box-sizing: border-box; }}
            #mrdp-avatar {{
                position: fixed; bottom: 24px; right: 24px;
                width: 100px; height: 100px; border-radius: 50%;
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                box-shadow: 0 8px 32px rgba(139,92,246,0.6), 0 0 60px rgba(139,92,246,0.3);
                cursor: pointer; z-index: 2147483647;
                animation: mrdp-bounce 2s ease-in-out infinite, mrdp-glow 3s ease-in-out infinite;
                display: flex; align-items: center; justify-content: center;
                padding: 12px; transition: transform 0.3s;
                border: 3px solid rgba(139,92,246,0.5);
            }}
            #mrdp-avatar:hover {{ transform: scale(1.15); }}
            @keyframes mrdp-bounce {{
                0%, 100% {{ transform: translateY(0); }}
                25% {{ transform: translateY(-8px); }}
                50% {{ transform: translateY(0); }}
                75% {{ transform: translateY(-4px); }}
            }}
            @keyframes mrdp-glow {{
                0%, 100% {{ box-shadow: 0 8px 32px rgba(139,92,246,0.6), 0 0 60px rgba(139,92,246,0.3); }}
                50% {{ box-shadow: 0 12px 48px rgba(139,92,246,0.8), 0 0 80px rgba(139,92,246,0.5); }}
            }}
            #mrdp-badge {{
                position: absolute; top: -2px; right: -2px;
                width: 22px; height: 22px; border-radius: 50%;
                background: #10b981; border: 3px solid #1a1a2e;
                animation: mrdp-badge-pulse 1.5s ease-in-out infinite;
            }}
            @keyframes mrdp-badge-pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.2); }}
            }}
            /* Click me tooltip for first-time users */
            #mrdp-tooltip {{
                position: fixed; bottom: 135px; right: 24px;
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                color: white; padding: 12px 18px; border-radius: 12px;
                font-weight: 600; font-size: 14px; z-index: 2147483646;
                box-shadow: 0 8px 32px rgba(139,92,246,0.4);
                animation: mrdp-tooltip-bounce 1.5s ease-in-out infinite;
                white-space: nowrap;
            }}
            #mrdp-tooltip::after {{
                content: ''; position: absolute; bottom: -8px; right: 40px;
                border-left: 8px solid transparent; border-right: 8px solid transparent;
                border-top: 8px solid #06b6d4;
            }}
            @keyframes mrdp-tooltip-bounce {{
                0%, 100% {{ transform: translateY(0); opacity: 1; }}
                50% {{ transform: translateY(-5px); opacity: 0.9; }}
            }}
            .mrdp-tooltip-hidden {{ display: none !important; }}
            #mrdp-popup {{
                position: fixed; bottom: 140px; right: 24px;
                width: 400px; height: 500px;
                background: #0d0d14; border: 1px solid rgba(139,92,246,0.3);
                border-radius: 16px; z-index: 2147483645;
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
            /* Input area at bottom of popup */
            #mrdp-input-area {{
                padding: 12px 14px;
                border-top: 1px solid rgba(139,92,246,0.2);
                display: flex; gap: 8px; align-items: center;
            }}
            #mrdp-input {{
                flex: 1;
                background: rgba(139,92,246,0.08);
                border: 1px solid rgba(139,92,246,0.25);
                border-radius: 10px;
                color: #f5f5f7;
                font-size: 14px;
                padding: 10px 14px;
                outline: none;
                font-family: inherit;
            }}
            #mrdp-input::placeholder {{ color: #666; }}
            #mrdp-input:focus {{ border-color: rgba(139,92,246,0.5); }}
            #mrdp-send {{
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: 500;
                padding: 10px 16px;
                cursor: pointer;
                transition: opacity 0.2s;
            }}
            #mrdp-send:hover {{ opacity: 0.9; }}
            /* Hide Streamlit's form off-screen but keep it interactable */
            [data-testid="stForm"] {{
                position: fixed !important;
                left: -9999px !important;
                top: 0 !important;
                opacity: 0 !important;
            }}
            @media (max-width: 480px) {{
                #mrdp-popup {{ width: calc(100vw - 16px); right: 8px; bottom: 130px; height: 420px; }}
                #mrdp-avatar {{ width: 80px; height: 80px; bottom: 16px; right: 16px; padding: 10px; }}
                #mrdp-tooltip {{ bottom: 110px; right: 16px; font-size: 12px; padding: 10px 14px; }}
            }}
        `;
        pd.head.appendChild(css);

        // JS functions in parent scope
        var js = pd.createElement('script');
        js.id = 'mrdp-js';
        js.textContent = `
            function mrdpToggle() {{
                var popup = document.getElementById('mrdp-popup');
                var tooltip = document.getElementById('mrdp-tooltip');

                // Hide tooltip on first click and mark as interacted
                if (tooltip) {{
                    tooltip.classList.add('mrdp-tooltip-hidden');
                    localStorage.setItem('mrdp_interacted', 'true');
                }}

                if (popup) {{
                    var isHidden = popup.style.display === 'none';
                    popup.style.display = isHidden ? 'flex' : 'none';
                    if (isHidden) {{
                        document.body.classList.add('mrdp-open');
                        document.body.setAttribute('data-mrdp-open', 'true');
                        var msgs = document.getElementById('mrdp-messages');
                        if (msgs) msgs.scrollTop = msgs.scrollHeight;
                        // Focus native input
                        setTimeout(function() {{
                            var inp = document.getElementById('mrdp-input');
                            if (inp) inp.focus();
                        }}, 100);
                    }} else {{
                        document.body.classList.remove('mrdp-open');
                        document.body.setAttribute('data-mrdp-open', 'false');
                    }}
                }}
            }}
            function mrdpSend() {{
                var inp = document.getElementById('mrdp-input');
                if (!inp || !inp.value.trim()) return;
                var msg = inp.value.trim();
                inp.value = '';

                // Find the Streamlit hidden form input and submit
                var formEl = document.querySelector('[data-testid="stForm"]');
                if (!formEl) {{
                    console.log('MrDP: Form not found');
                    return;
                }}
                var stInput = formEl.querySelector('input');
                var stBtn = formEl.querySelector('button');
                console.log('MrDP: Found input:', !!stInput, 'button:', !!stBtn);
                if (stInput && stBtn) {{
                    // Set value using native setter to trigger React
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(stInput, msg);
                    stInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    stInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    console.log('MrDP: Set value to:', msg);
                    // Small delay then submit
                    setTimeout(function() {{
                        console.log('MrDP: Clicking submit');
                        stBtn.click();
                    }}, 100);
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

        // Widget HTML with native input
        var root = pd.createElement('div');
        root.id = 'mrdp-root';

        // Tooltip for first-time users
        var tooltipHtml = isFirstTime
            ? '<div id="mrdp-tooltip">&#128075; Hey! Click me to get started!</div>'
            : '';

        root.innerHTML = tooltipHtml
            + '<div id="mrdp-avatar" onclick="mrdpToggle()">'
            + {svg_escaped}
            + '<div id="mrdp-badge"></div>'
            + '</div>'
            + '<div id="mrdp-popup" style="display: ' + (shouldOpen ? 'flex' : 'none') + '">'
            + '<div id="mrdp-header">'
            + '<div id="mrdp-header-avatar">' + {header_svg_escaped} + '</div>'
            + '<div id="mrdp-header-info"><div id="mrdp-header-name">Mr.DP - Your Dopamine Curator</div><div id="mrdp-header-status">&#9679; Ready to help!</div></div>'
            + '<button id="mrdp-close" onclick="mrdpToggle()">&#10005;</button>'
            + '</div>'
            + '<div id="mrdp-messages">' + {chat_html_escaped} + '</div>'
            + '<div id="mrdp-input-area">'
            + '<input type="text" id="mrdp-input" placeholder="Tell me what you\\'re in the mood for..." onkeydown="if(event.key===\\'Enter\\')mrdpSend()">'
            + '<button id="mrdp-send" onclick="mrdpSend()">Send</button>'
            + '</div>'
            + '</div>';
        pd.body.appendChild(root);

        // Scroll chat messages to bottom
        var msgs = pd.getElementById('mrdp-messages');
        if (msgs) msgs.scrollTop = msgs.scrollHeight;
    }})();
    </script>
    """

    components.html(inject_script, height=0, scrolling=False)

    # Hidden Streamlit form - used as bridge for message submission
    with st.container():
        with st.form("mr_dp_form", clear_on_submit=True, border=False):
            user_input = st.text_input(
                "Message",
                placeholder="How are you feeling?",
                key="mr_dp_text_input",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Send", use_container_width=True)

            if submitted and user_input:
                st.session_state.mr_dp_open = True
                return user_input

    return None
