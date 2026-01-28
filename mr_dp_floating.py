"""
Mr.DP Floating Chat Widget
Injects widget into parent Streamlit page via JavaScript
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
    Render floating Mr.DP chatbot that stays on screen while scrolling.
    Injects widget into parent Streamlit page DOM via JavaScript.
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

    # Build chat history HTML
    chat_html = ""
    if chat_history:
        for msg in chat_history[-8:]:
            role_class = "user" if msg["role"] == "user" else "assistant"
            content = msg["content"].replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace('"', "&quot;")
            if msg["role"] == "assistant":
                chat_html += f'<div class="chat-message {role_class}"><div class="avatar">{get_mr_dp_svg("happy")}</div><div class="message-content">{content}</div></div>'
            else:
                chat_html += f'<div class="chat-message {role_class}"><div class="message-content">{content}</div><div class="avatar">&#128522;</div></div>'
    else:
        chat_html = f'<div class="chat-message assistant"><div class="avatar">{get_mr_dp_svg("happy")}</div><div class="message-content">&#128075; Hey! Tell me how you\'re feeling and I\'ll find the perfect content for you!</div></div>'

    chat_display = "flex" if is_open else "none"

    # Escape for JavaScript string embedding
    svg_escaped = json.dumps(mr_dp_svg)
    chat_html_escaped = json.dumps(chat_html)

    # JavaScript that injects the widget into the parent Streamlit page
    inject_script = f"""
    <script>
    (function() {{
        var parentDoc = window.parent.document;

        // Remove existing widget if present (prevents duplicates on rerun)
        var existing = parentDoc.getElementById('mr-dp-widget-container');
        if (existing) existing.remove();
        var existingStyle = parentDoc.getElementById('mr-dp-widget-style');
        if (existingStyle) existingStyle.remove();

        // Inject CSS into parent
        var style = parentDoc.createElement('style');
        style.id = 'mr-dp-widget-style';
        style.textContent = `
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
                animation: mr-dp-bounce 3s ease-in-out infinite;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 8px;
            }}
            @keyframes mr-dp-bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-8px); }}
            }}
            .mr-dp-floating-avatar:hover {{
                transform: scale(1.1);
                box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
            }}
            .mr-dp-chat-popup {{
                position: fixed;
                top: 180px;
                right: 24px;
                width: 360px;
                max-height: 500px;
                background: rgba(13, 13, 20, 0.98);
                border: 1px solid rgba(139, 92, 246, 0.4);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(20px);
                z-index: 999998;
                display: {chat_display};
                flex-direction: column;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            .mr-dp-chat-popup .chat-header {{
                padding: 20px 20px 12px 20px;
                border-bottom: 1px solid rgba(139, 92, 246, 0.2);
                position: relative;
            }}
            .mr-dp-chat-popup .chat-title {{
                color: #f5f5f7;
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 4px;
            }}
            .mr-dp-chat-popup .chat-status {{
                color: #10b981;
                font-size: 0.85rem;
            }}
            .mr-dp-chat-popup .close-btn {{
                position: absolute;
                top: 16px;
                right: 16px;
                background: rgba(139, 92, 246, 0.2);
                border: none;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                color: #f5f5f7;
                font-size: 1.4rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                line-height: 1;
            }}
            .mr-dp-chat-popup .close-btn:hover {{
                background: rgba(139, 92, 246, 0.4);
                transform: scale(1.1);
            }}
            .mr-dp-chat-popup .chat-messages {{
                flex: 1;
                overflow-y: auto;
                padding: 16px 20px;
                max-height: 300px;
            }}
            .mr-dp-chat-popup .chat-message {{
                display: flex;
                gap: 8px;
                margin: 12px 0;
                align-items: flex-start;
            }}
            .mr-dp-chat-popup .chat-message.user {{
                flex-direction: row-reverse;
            }}
            .mr-dp-chat-popup .avatar {{
                width: 32px;
                height: 32px;
                flex-shrink: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
            }}
            .mr-dp-chat-popup .avatar svg {{
                width: 100%;
                height: 100%;
            }}
            .mr-dp-chat-popup .message-content {{
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 0.9rem;
                line-height: 1.6;
                word-wrap: break-word;
                max-width: 260px;
            }}
            .mr-dp-chat-popup .chat-message.user .message-content {{
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                color: #ffffff;
            }}
            .mr-dp-chat-popup .chat-message.assistant .message-content {{
                background: rgba(139, 92, 246, 0.15);
                border: 1px solid rgba(139, 92, 246, 0.25);
                color: #f5f5f7;
            }}
            .mr-dp-chat-popup .chat-input-area {{
                padding: 16px 20px;
                border-top: 1px solid rgba(139, 92, 246, 0.2);
            }}
            .mr-dp-chat-popup .input-form {{
                display: flex;
                gap: 8px;
            }}
            .mr-dp-chat-popup .message-input {{
                flex: 1;
                background: rgba(139, 92, 246, 0.1);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 12px;
                padding: 10px 14px;
                color: #f5f5f7;
                font-size: 0.9rem;
                outline: none;
            }}
            .mr-dp-chat-popup .message-input:focus {{
                border-color: #8b5cf6;
                background: rgba(139, 92, 246, 0.15);
            }}
            .mr-dp-chat-popup .send-btn {{
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                color: white;
                font-size: 0.9rem;
                cursor: pointer;
                transition: all 0.3s ease;
                white-space: nowrap;
            }}
            .mr-dp-chat-popup .send-btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.5);
            }}
        `;
        parentDoc.head.appendChild(style);

        // Create widget container
        var container = parentDoc.createElement('div');
        container.id = 'mr-dp-widget-container';

        // Avatar
        var avatar = parentDoc.createElement('div');
        avatar.className = 'mr-dp-floating-avatar';
        avatar.title = 'Chat with Mr.DP';
        avatar.innerHTML = {svg_escaped};
        avatar.onclick = function() {{
            var parentWin = parentDoc.defaultView || window.top;
            var url = new URL(parentWin.location.href);
            url.searchParams.set('mr_dp_toggle', Date.now().toString());
            parentWin.location.href = url.toString();
        }};
        container.appendChild(avatar);

        // Chat popup
        var popup = parentDoc.createElement('div');
        popup.className = 'mr-dp-chat-popup';
        popup.id = 'mr-dp-chat-popup';
        popup.innerHTML = '<div class="chat-header">'
            + '<button class="close-btn" id="mr-dp-close-btn">\\u00d7</button>'
            + '<div class="chat-title">\\ud83e\\udde0 Mr.DP Chat</div>'
            + '<div class="chat-status">\\u25cf Online - Your Dopamine Buddy</div>'
            + '</div>'
            + '<div class="chat-messages" id="mr-dp-chat-messages">'
            + {chat_html_escaped}
            + '</div>'
            + '<div class="chat-input-area">'
            + '<form class="input-form" id="mr-dp-form">'
            + '<input type="text" class="message-input" id="mr-dp-input" placeholder="How are you feeling?" autocomplete="off" required>'
            + '<button type="submit" class="send-btn">Send \\ud83d\\ude80</button>'
            + '</form>'
            + '</div>';
        container.appendChild(popup);

        parentDoc.body.appendChild(container);

        // Attach event listeners
        var parentWin = parentDoc.defaultView || window.top;

        parentDoc.getElementById('mr-dp-close-btn').onclick = function() {{
            var url = new URL(parentWin.location.href);
            url.searchParams.set('mr_dp_toggle', Date.now().toString());
            parentWin.location.href = url.toString();
        }};

        parentDoc.getElementById('mr-dp-form').onsubmit = function(e) {{
            e.preventDefault();
            var input = parentDoc.getElementById('mr-dp-input');
            var message = input.value.trim();
            if (message) {{
                var url = new URL(parentWin.location.href);
                url.searchParams.set('mr_dp_msg', encodeURIComponent(message));
                url.searchParams.set('mr_dp_ts', Date.now().toString());
                parentWin.location.href = url.toString();
            }}
        }};

        // Auto-scroll chat to bottom
        var chatMessages = parentDoc.getElementById('mr-dp-chat-messages');
        if (chatMessages) {{
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
    }})();
    </script>
    """

    components.html(inject_script, height=1, scrolling=False)

    # Check for toggle in query params
    if "mr_dp_toggle" in st.query_params:
        st.session_state.mr_dp_open = not is_open
        st.query_params.pop("mr_dp_toggle", None)
        st.rerun()

    # Check for message in query params
    if "mr_dp_msg" in st.query_params:
        import urllib.parse
        message = urllib.parse.unquote(st.query_params["mr_dp_msg"])
        st.query_params.pop("mr_dp_msg", None)
        st.query_params.pop("mr_dp_ts", None)
        return message

    return None
