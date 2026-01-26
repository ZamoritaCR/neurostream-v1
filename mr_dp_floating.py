"""
Mr.DP Floating Chat Widget
Floating version with chat in top-right corner
"""

import streamlit as st
import streamlit.components.v1 as components


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

    # Build chat history HTML
    chat_html = ""
    if chat_history:
        for msg in chat_history[-8:]:  # Show last 8 messages
            if msg["role"] == "user":
                chat_html += f'<div class="mr-dp-message mr-dp-message-user">{msg["content"]}</div>'
            else:
                chat_html += f'<div class="mr-dp-message mr-dp-message-assistant">{msg["content"]}</div>'
    else:
        chat_html = '<div class="mr-dp-message mr-dp-message-assistant">👋 Hey! Tell me how you\'re feeling and I\'ll find the perfect content for you!</div>'

    # Floating widget HTML with embedded chat
    chat_display = "flex" if is_open else "none"

    widget_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}

            .mr-dp-floating-avatar {{
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
            }}

            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-8px); }}
            }}

            .mr-dp-floating-avatar:hover {{
                transform: scale(1.1);
                box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
            }}

            .mr-dp-chat-popup {{
                position: fixed;
                top: 160px;
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
            }}

            .mr-dp-chat-header {{
                padding: 20px 20px 12px 20px;
                border-bottom: 1px solid rgba(139, 92, 246, 0.2);
            }}

            .mr-dp-chat-title {{
                color: #f5f5f7;
                font-size: 1.2rem;
                font-weight: bold;
                margin-bottom: 4px;
            }}

            .mr-dp-status {{
                color: #10b981;
                font-size: 0.85rem;
            }}

            .mr-dp-chat-messages {{
                flex: 1;
                overflow-y: auto;
                padding: 16px 20px;
                max-height: 300px;
            }}

            .mr-dp-message {{
                margin: 8px 0;
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 0.9rem;
                line-height: 1.6;
                word-wrap: break-word;
            }}

            .mr-dp-message-user {{
                background: linear-gradient(135deg, #8b5cf6, #06b6d4);
                color: #ffffff;
                margin-left: 40px;
                text-align: right;
            }}

            .mr-dp-message-assistant {{
                background: rgba(139, 92, 246, 0.15);
                border: 1px solid rgba(139, 92, 246, 0.25);
                color: #f5f5f7;
                margin-right: 40px;
            }}

            .mr-dp-chat-input-area {{
                padding: 16px 20px;
                border-top: 1px solid rgba(139, 92, 246, 0.2);
            }}

            .mr-dp-input-form {{
                display: flex;
                gap: 8px;
            }}

            .mr-dp-input {{
                flex: 1;
                background: rgba(139, 92, 246, 0.1);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 12px;
                padding: 10px 14px;
                color: #f5f5f7;
                font-size: 0.9rem;
                outline: none;
            }}

            .mr-dp-input:focus {{
                border-color: #8b5cf6;
                background: rgba(139, 92, 246, 0.15);
            }}

            .mr-dp-send-btn {{
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

            .mr-dp-send-btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.5);
            }}

            .mr-dp-close-btn {{
                position: absolute;
                top: 16px;
                right: 16px;
                background: rgba(139, 92, 246, 0.2);
                border: none;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                color: #f5f5f7;
                font-size: 1.2rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }}

            .mr-dp-close-btn:hover {{
                background: rgba(139, 92, 246, 0.4);
                transform: scale(1.1);
            }}
        </style>
    </head>
    <body>
        <div class="mr-dp-floating-avatar" onclick="toggleChat()" title="Chat with Mr.DP">
            🧠
        </div>

        <div class="mr-dp-chat-popup" id="chatPopup">
            <button class="mr-dp-close-btn" onclick="toggleChat()">×</button>

            <div class="mr-dp-chat-header">
                <div class="mr-dp-chat-title">🧠 Mr.DP Chat</div>
                <div class="mr-dp-status">● Online - Your Dopamine Buddy</div>
            </div>

            <div class="mr-dp-chat-messages" id="chatMessages">
                {chat_html}
            </div>

            <div class="mr-dp-chat-input-area">
                <form class="mr-dp-input-form" onsubmit="sendMessage(event)">
                    <input type="text"
                           class="mr-dp-input"
                           id="messageInput"
                           placeholder="How are you feeling?"
                           autocomplete="off"
                           required>
                    <button type="submit" class="mr-dp-send-btn">Send 🚀</button>
                </form>
            </div>
        </div>

        <script>
            function toggleChat() {{
                // Update URL to trigger Streamlit rerun
                const url = new URL(window.top.location.href);
                url.searchParams.set('mr_dp_toggle', Date.now().toString());
                window.top.location.href = url.toString();
            }}

            function sendMessage(event) {{
                event.preventDefault();
                const input = document.getElementById('messageInput');
                const message = input.value.trim();

                if (message) {{
                    // Update URL with message to trigger Streamlit rerun
                    const url = new URL(window.top.location.href);
                    url.searchParams.set('mr_dp_msg', encodeURIComponent(message));
                    url.searchParams.set('mr_dp_ts', Date.now().toString());
                    window.top.location.href = url.toString();
                }}
            }}

            // Auto-scroll to bottom of chat
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {{
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }}
        </script>
    </body>
    </html>
    """

    # Render the widget
    components.html(widget_html, height=1, scrolling=False)

    # Check for toggle or message in query params
    try:
        # Check for toggle
        if "mr_dp_toggle" in st.query_params:
            st.session_state.mr_dp_open = not is_open
            # Clear the param
            params = dict(st.query_params)
            params.pop("mr_dp_toggle", None)
            st.query_params.clear()
            st.query_params.update(params)
            st.rerun()

        # Check for message
        if "mr_dp_msg" in st.query_params:
            import urllib.parse
            message = urllib.parse.unquote(st.query_params["mr_dp_msg"])
            # Clear the params
            params = dict(st.query_params)
            params.pop("mr_dp_msg", None)
            params.pop("mr_dp_ts", None)
            st.query_params.clear()
            st.query_params.update(params)
            return message
    except Exception:
        pass

    return None
