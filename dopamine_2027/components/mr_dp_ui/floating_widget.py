"""
Dopamine.watch 2027 - Floating Mr.DP Widget
The always-visible floating Mr.DP avatar and chat popup.
"""

import streamlit as st
import streamlit.components.v1 as components
import json

from core.session import get_state, get_user


def render_floating_mr_dp():
    """Render the floating Mr.DP widget."""

    # Only show for logged-in users
    if not get_user():
        return

    is_open = get_state("mr_dp_open", False)
    is_thinking = get_state("mr_dp_thinking", False)
    expression = get_state("mr_dp_expression", "happy")
    anim_state = get_state("mr_dp_animation_state", "idle")

    # Get chat history for display
    chat_history = get_state("mr_dp_chat_history", [])

    # Build chat HTML
    chat_html = ""
    if chat_history:
        for msg in chat_history[-8:]:
            content = msg.get("content", "").replace("<", "&lt;").replace(">", "&gt;")
            if msg["role"] == "assistant":
                chat_html += f'<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">🧠</div><div class="mrdp-bubble mrdp-bubble-ai">{content}</div></div>'
            else:
                chat_html += f'<div class="mrdp-msg mrdp-user"><div class="mrdp-bubble mrdp-bubble-user">{content}</div></div>'
    else:
        chat_html = '''
        <div class="mrdp-msg mrdp-assistant">
            <div class="mrdp-avatar">🧠</div>
            <div class="mrdp-bubble mrdp-bubble-ai">Hey! I'm Mr.DP - your dopamine curator. Tell me how you're feeling!</div>
        </div>
        '''

    if is_thinking:
        chat_html += '<div class="mrdp-msg mrdp-assistant"><div class="mrdp-avatar">🧠</div><div class="mrdp-bubble mrdp-bubble-ai"><span class="mrdp-dots"><span>.</span><span>.</span><span>.</span></span></div></div>'

    # Inject the widget
    widget_html = f"""
    <script>
    (function() {{
        var pd = window.parent.document;

        // Remove old widget
        var old = pd.getElementById('mrdp-widget');
        if (old) old.remove();

        // CSS
        var style = pd.createElement('style');
        style.id = 'mrdp-style';
        style.textContent = `
            #mrdp-widget {{
                position: fixed;
                bottom: 24px;
                right: 24px;
                z-index: 2147483647;
                font-family: 'Inter', sans-serif;
            }}

            #mrdp-avatar {{
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5rem;
                cursor: pointer;
                box-shadow: 0 10px 40px rgba(139,92,246,0.5);
                animation: mrdp-float 3s ease-in-out infinite;
                transition: transform 0.3s ease;
            }}

            #mrdp-avatar:hover {{
                transform: scale(1.1);
            }}

            @keyframes mrdp-float {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-8px); }}
            }}

            #mrdp-popup {{
                position: absolute;
                bottom: 100px;
                right: 0;
                width: 380px;
                height: 480px;
                background: #0d0d14;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
                display: none;
                flex-direction: column;
                overflow: hidden;
                border: 1px solid rgba(139,92,246,0.3);
            }}

            #mrdp-popup.open {{
                display: flex;
            }}

            #mrdp-header {{
                padding: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
                border-bottom: 1px solid rgba(139,92,246,0.2);
            }}

            #mrdp-header-avatar {{
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            #mrdp-header-info {{
                flex: 1;
            }}

            #mrdp-header-name {{
                color: #f5f5f7;
                font-weight: 600;
            }}

            #mrdp-header-status {{
                color: #10b981;
                font-size: 12px;
            }}

            #mrdp-close {{
                background: none;
                border: none;
                color: #888;
                cursor: pointer;
                font-size: 20px;
            }}

            #mrdp-messages {{
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}

            .mrdp-msg {{
                display: flex;
                gap: 8px;
                align-items: flex-end;
            }}

            .mrdp-user {{
                justify-content: flex-end;
            }}

            .mrdp-avatar {{
                width: 28px;
                height: 28px;
                font-size: 18px;
            }}

            .mrdp-bubble {{
                padding: 10px 14px;
                border-radius: 16px;
                font-size: 14px;
                max-width: 240px;
                line-height: 1.5;
            }}

            .mrdp-bubble-ai {{
                background: rgba(139,92,246,0.15);
                color: #e0e0e0;
            }}

            .mrdp-bubble-user {{
                background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
                color: white;
            }}

            .mrdp-dots span {{
                animation: mrdp-blink 1.4s infinite;
            }}
            .mrdp-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
            .mrdp-dots span:nth-child(3) {{ animation-delay: 0.4s; }}

            @keyframes mrdp-blink {{
                0%, 20% {{ opacity: 0.2; }}
                50% {{ opacity: 1; }}
                100% {{ opacity: 0.2; }}
            }}

            #mrdp-input-area {{
                padding: 12px;
                border-top: 1px solid rgba(139,92,246,0.2);
                display: flex;
                gap: 8px;
            }}

            #mrdp-input {{
                flex: 1;
                background: rgba(139,92,246,0.1);
                border: 1px solid rgba(139,92,246,0.3);
                border-radius: 10px;
                padding: 10px 14px;
                color: #f5f5f7;
                font-size: 14px;
                outline: none;
            }}

            #mrdp-send {{
                background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
                border: none;
                border-radius: 10px;
                color: white;
                padding: 10px 16px;
                cursor: pointer;
            }}
        `;
        pd.head.appendChild(style);

        // Widget HTML
        var widget = pd.createElement('div');
        widget.id = 'mrdp-widget';
        widget.innerHTML = `
            <div id="mrdp-avatar" onclick="document.getElementById('mrdp-popup').classList.toggle('open')">🧠</div>
            <div id="mrdp-popup" class="{{'open' if is_open else ''}}">
                <div id="mrdp-header">
                    <div id="mrdp-header-avatar">🧠</div>
                    <div id="mrdp-header-info">
                        <div id="mrdp-header-name">Mr.DP</div>
                        <div id="mrdp-header-status">● Ready to help</div>
                    </div>
                    <button id="mrdp-close" onclick="document.getElementById('mrdp-popup').classList.remove('open')">×</button>
                </div>
                <div id="mrdp-messages">{chat_html}</div>
                <div id="mrdp-input-area">
                    <input type="text" id="mrdp-input" placeholder="Tell me how you're feeling...">
                    <button id="mrdp-send">Send</button>
                </div>
            </div>
        `;
        pd.body.appendChild(widget);

        // Scroll messages
        var msgs = pd.getElementById('mrdp-messages');
        if (msgs) msgs.scrollTop = msgs.scrollHeight;
    }})();
    </script>
    """

    components.html(widget_html, height=0, scrolling=False)
