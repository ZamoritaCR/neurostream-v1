"""
Mr.DP Floating Chat Widget
A truly floating chatbot that stays on screen while scrolling
Uses the neuron character from index.html
"""

import streamlit as st
import streamlit.components.v1 as components
import json


def render_floating_mr_dp():
    """
    Render floating Mr.DP chatbot that stays on screen while scrolling.
    Only shows when user is logged in.
    Returns user message if sent, None otherwise.
    """

    # Only show if user is logged in
    if not st.session_state.get("user"):
        return None

    # Get chat history and state
    chat_history = st.session_state.get("mr_dp_chat_history", [])
    is_open = st.session_state.get("mr_dp_open", False)

    # Convert chat history to JSON for JavaScript
    chat_json = json.dumps(chat_history)
    popup_class = "mr-dp-popup open" if is_open else "mr-dp-popup"
    expression = 'happy' if is_open else 'sleeping'

    # Complete floating widget HTML/CSS/JS
    widget_html = f'''
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: transparent;
    overflow: visible;
}}

/* Floating container - position fixed so it floats */
.mr-dp-container {{
    position: fixed;
    top: 80px;
    right: 24px;
    z-index: 999999;
    pointer-events: none;
}}

.mr-dp-container * {{
    pointer-events: auto;
}}

/* Avatar button */
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
    animation: mrDpBounce 4s ease-in-out infinite;
    position: relative;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.mr-dp-avatar:hover {{
    transform: scale(1.05);
    box-shadow: 0 12px 40px rgba(139, 92, 246, 0.6);
    animation: none;
}}

.mr-dp-avatar svg {{
    width: 48px !important;
    height: 48px !important;
}}

@keyframes mrDpBounce {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-6px); }}
}}

/* Chat popup */
.mr-dp-popup {{
    position: absolute;
    top: 80px;
    right: 0;
    width: 360px;
    max-height: 500px;
    background: rgba(13, 13, 20, 0.98);
    border: 1px solid rgba(139, 92, 246, 0.4);
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
    overflow: hidden;
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

.mr-dp-header-img svg {{
    width: 40px;
    height: 40px;
}}

.mr-dp-header-name {{
    font-weight: 700;
    font-size: 1rem;
    background: linear-gradient(135deg, #a78bfa, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

.mr-dp-header-status {{
    font-size: 0.75rem;
    color: #10b981;
}}

/* Messages */
.mr-dp-messages {{
    padding: 16px;
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-height: 320px;
}}

.mr-dp-empty {{
    text-align: center;
    padding: 30px 20px;
    color: rgba(255, 255, 255, 0.5);
    line-height: 1.5;
}}

.mr-dp-empty-icon {{
    font-size: 2.5rem;
    margin-bottom: 12px;
}}

.mr-dp-msg {{
    padding: 12px 16px;
    border-radius: 18px;
    font-size: 0.9rem;
    line-height: 1.5;
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
    color: white;
    margin-right: auto;
    border-bottom-left-radius: 6px;
}}

/* Input area */
.mr-dp-input-area {{
    padding: 12px 16px;
    background: rgba(139, 92, 246, 0.1);
    border-top: 1px solid rgba(139, 92, 246, 0.2);
    display: flex;
    gap: 8px;
}}

.mr-dp-input {{
    flex: 1;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: white;
    font-size: 0.9rem;
    outline: none;
    font-family: inherit;
}}

.mr-dp-input:focus {{
    border-color: #8b5cf6;
    background: rgba(255, 255, 255, 0.08);
}}

.mr-dp-input::placeholder {{
    color: rgba(255, 255, 255, 0.3);
}}

.mr-dp-send {{
    padding: 10px 16px;
    background: linear-gradient(135deg, #8b5cf6, #06b6d4);
    border: none;
    border-radius: 12px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
    font-size: 0.9rem;
}}

.mr-dp-send:hover {{
    transform: translateY(-2px);
}}

.mr-dp-send:active {{
    transform: translateY(0);
}}
</style>
</head>
<body>

<div class="mr-dp-container">
    <!-- Chat popup -->
    <div class="{popup_class}" id="mrDpPopup">
        <div class="mr-dp-header">
            <div class="mr-dp-header-img" id="mrDpHeaderImg"></div>
            <div>
                <div class="mr-dp-header-name">Mr.DP</div>
                <div class="mr-dp-header-status">● Online - Your Dopamine Buddy</div>
            </div>
        </div>
        <div class="mr-dp-messages" id="mrDpMessages">
            <div class="mr-dp-empty">
                <div class="mr-dp-empty-icon">🧠</div>
                <div>Hey! I'm Mr.DP. Tell me how you're feeling and I'll find the perfect content for you!</div>
            </div>
        </div>
        <div class="mr-dp-input-area">
            <input type="text" class="mr-dp-input" id="mrDpInput" placeholder="How are you feeling?" />
            <button class="mr-dp-send" id="mrDpSend">Send</button>
        </div>
    </div>

    <!-- Avatar button -->
    <div class="mr-dp-avatar" id="mrDpAvatar" title="Chat with Mr.DP"></div>
</div>

<script>
// Chat history from Streamlit
let chatHistory = {chat_json};
let isOpen = {str(is_open).lower()};

// Dynamic neuron SVG generation (from index.html)
function getMrDpSvg(expression) {{
    const expressions = {{
        happy: {{ leftEye: '◠', rightEye: '◠', mouth: 'smile', blush: true }},
        thinking: {{ leftEye: '•', rightEye: '•', mouth: 'hmm', blush: false }},
        excited: {{ leftEye: '★', rightEye: '★', mouth: 'big_smile', blush: true }},
        empathetic: {{ leftEye: '◠', rightEye: '◠', mouth: 'soft_smile', blush: true }},
        curious: {{ leftEye: '◉', rightEye: '◉', mouth: 'o', blush: false }},
        wink: {{ leftEye: '◠', rightEye: '−', mouth: 'smile', blush: true }},
        sleeping: {{ leftEye: '−', rightEye: '−', mouth: 'sleeping', blush: false }}
    }};

    const expr = expressions[expression] || expressions.happy;

    const mouths = {{
        smile: '<path d="M24 38 Q32 46 40 38" stroke="#ff6b9d" stroke-width="3" fill="none" stroke-linecap="round"/>',
        big_smile: '<path d="M22 36 Q32 48 42 36" stroke="#ff6b9d" stroke-width="3" fill="none" stroke-linecap="round"/><path d="M26 40 Q32 44 38 40" fill="#ff6b9d"/>',
        soft_smile: '<path d="M26 38 Q32 43 38 38" stroke="#ff6b9d" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
        hmm: '<path d="M26 40 L38 38" stroke="#ff6b9d" stroke-width="2.5" fill="none" stroke-linecap="round"/>',
        o: '<circle cx="32" cy="40" r="4" fill="#ff6b9d"/>',
        sleeping: '<path d="M26 42 Q32 40 38 42" stroke="#ff6b9d" stroke-width="2" fill="none" stroke-linecap="round"/>'
    }};

    const blush = expr.blush ? '<circle cx="18" cy="36" r="5" fill="#ff6b9d" opacity="0.3"/><circle cx="46" cy="36" r="5" fill="#ff6b9d" opacity="0.3"/>' : '';

    return `<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="ng-${{Math.random()}}" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#a78bfa"/>
<stop offset="50%" style="stop-color:#8b5cf6"/>
<stop offset="100%" style="stop-color:#7c3aed"/>
</linearGradient>
<linearGradient id="ag-${{Math.random()}}" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" style="stop-color:#8b5cf6"/>
<stop offset="100%" style="stop-color:#06b6d4"/>
</linearGradient>
</defs>
<g>
<path d="M32 12 Q28 4 20 2" stroke="url(#ag-0)" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="20" cy="2" r="3" fill="#06b6d4"/>
<path d="M32 12 Q36 4 44 2" stroke="url(#ag-0)" stroke-width="3" fill="none" stroke-linecap="round"/>
<circle cx="44" cy="2" r="3" fill="#06b6d4"/>
<path d="M32 12 Q32 6 32 0" stroke="url(#ag-0)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="32" cy="0" r="2.5" fill="#10b981"/>
<path d="M12 28 Q4 24 0 20" stroke="url(#ag-0)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="0" cy="20" r="2.5" fill="#f59e0b"/>
<path d="M52 28 Q60 24 64 20" stroke="url(#ag-0)" stroke-width="2.5" fill="none" stroke-linecap="round"/>
<circle cx="64" cy="20" r="2.5" fill="#f59e0b"/>
</g>
<path d="M32 52 Q32 58 28 62" stroke="url(#ag-0)" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="28" cy="62" r="3" fill="#10b981"/>
<ellipse cx="32" cy="32" rx="22" ry="20" fill="url(#ng-0)"/>
<ellipse cx="26" cy="24" rx="8" ry="5" fill="white" opacity="0.3"/>
<text x="22" y="32" font-size="10" fill="white" text-anchor="middle" font-family="Arial">${{expr.leftEye}}</text>
<text x="42" y="32" font-size="10" fill="white" text-anchor="middle" font-family="Arial">${{expr.rightEye}}</text>
<path d="M18 24 Q22 22 26 24" stroke="white" stroke-width="1.5" fill="none" opacity="0.8"/>
<path d="M38 24 Q42 22 46 24" stroke="white" stroke-width="1.5" fill="none" opacity="0.8"/>
${{mouths[expr.mouth]}}
${{blush}}
<text x="54" y="14" font-size="8" fill="#ffd700" opacity="0.8">✦</text>
<text x="8" y="18" font-size="6" fill="#ffd700" opacity="0.6">✦</text>
</svg>`;
}}

// Initialize Mr.DP neuron character
function initMrDp() {{
    const avatar = document.getElementById('mrDpAvatar');
    const headerImg = document.getElementById('mrDpHeaderImg');

    // Set initial expression based on open state
    const initialExpression = isOpen ? 'happy' : 'sleeping';
    const svg = getMrDpSvg(initialExpression);

    avatar.innerHTML = svg;
    headerImg.innerHTML = svg;

    // Render chat history
    renderChatHistory();
}}

// Render chat history
function renderChatHistory() {{
    const messagesDiv = document.getElementById('mrDpMessages');

    if (chatHistory.length === 0) {{
        messagesDiv.innerHTML = `
            <div class="mr-dp-empty">
                <div class="mr-dp-empty-icon">🧠</div>
                <div>Hey! I'm Mr.DP. Tell me how you're feeling and I'll find the perfect content for you!</div>
            </div>
        `;
    }} else {{
        let html = '';
        chatHistory.forEach(msg => {{
            const className = msg.role === 'user' ? 'mr-dp-msg user' : 'mr-dp-msg assistant';
            const content = msg.content.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            html += `<div class="${{className}}">${{content}}</div>`;
        }});
        messagesDiv.innerHTML = html;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }}
}}

// Toggle chat popup
function toggleMrDp() {{
    const popup = document.getElementById('mrDpPopup');
    const avatar = document.getElementById('mrDpAvatar');
    const headerImg = document.getElementById('mrDpHeaderImg');
    const currentlyOpen = popup.classList.contains('open');

    if (!currentlyOpen) {{
        // Wake up Mr.DP and open chat
        const happySvg = getMrDpSvg('happy');
        avatar.innerHTML = happySvg;
        headerImg.innerHTML = happySvg;

        popup.classList.add('open');
        setTimeout(() => {{
            document.getElementById('mrDpInput').focus();
        }}, 100);
        const msgs = document.getElementById('mrDpMessages');
        msgs.scrollTop = msgs.scrollHeight;

        // Notify Streamlit
        updateStreamlitState('open');
    }} else {{
        // Put Mr.DP to sleep and close chat
        const sleepingSvg = getMrDpSvg('sleeping');
        avatar.innerHTML = sleepingSvg;

        popup.classList.remove('open');

        // Notify Streamlit
        updateStreamlitState('close');
    }}
}}

// Send message
function sendMessage() {{
    const input = document.getElementById('mrDpInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message immediately
    chatHistory.push({{ role: 'user', content: message }});
    renderChatHistory();

    // Change expression to thinking
    const avatar = document.getElementById('mrDpAvatar');
    const headerImg = document.getElementById('mrDpHeaderImg');
    const thinkingSvg = getMrDpSvg('thinking');
    avatar.innerHTML = thinkingSvg;
    headerImg.innerHTML = thinkingSvg;

    // Clear input
    input.value = '';

    // Notify Streamlit of message
    updateStreamlitState('send', message);
}}

// Update Streamlit state via URL query params
function updateStreamlitState(action, message = '') {{
    // Use URL hash to communicate with Streamlit
    const data = {{ action, message, timestamp: Date.now() }};
    window.location.hash = 'mr_dp:' + btoa(JSON.stringify(data));

    // Clear hash after a moment
    setTimeout(() => {{
        window.location.hash = '';
    }}, 100);
}}

// Event listeners
document.getElementById('mrDpAvatar').addEventListener('click', toggleMrDp);
document.getElementById('mrDpSend').addEventListener('click', sendMessage);
document.getElementById('mrDpInput').addEventListener('keypress', (e) => {{
    if (e.key === 'Enter') {{
        e.preventDefault();
        sendMessage();
    }}
}});

// Initialize on load
initMrDp();
</script>
</body>
</html>
'''

    # Inject directly into page using st.markdown (avoids iframe issues)
    st.markdown(widget_html, unsafe_allow_html=True)

    # Add invisible button handler for toggling (CSS will position it over the avatar)
    toggle_col1, toggle_col2 = st.columns([10, 1])
    with toggle_col2:
        if st.button("🧠", key="mr_dp_toggle_btn", help="Chat with Mr.DP"):
            st.session_state.mr_dp_open = not st.session_state.mr_dp_open
            st.rerun()

    # Show chat input in sidebar when open
    if is_open:
        with st.sidebar:
            st.markdown("### 💬 Mr.DP Chat")
            with st.form(key="mr_dp_chat_form"):
                user_input = st.text_input("How are you feeling?", key="mr_dp_input_field")
                submitted = st.form_submit_button("Send")
                if submitted and user_input:
                    return user_input

    return None
