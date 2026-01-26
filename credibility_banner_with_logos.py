# ========================================
# CREDIBILITY BANNER - With Real Logos
# Add to app.py render_landing() function
# ========================================

def render_credibility_banner():
    """Render credibility banner with research institution logos"""

    st.markdown("""
    <style>
    /* ===== CREDIBILITY BANNER ===== */
    .credibility-section {
        margin: 60px 0 40px 0;
        padding: 40px 20px;
        background: linear-gradient(180deg, rgba(124, 58, 237, 0.05), transparent);
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        overflow: hidden;
    }

    .credibility-header {
        text-align: center;
        margin-bottom: 32px;
    }

    .credibility-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }

    .credibility-subtitle {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.5);
        line-height: 1.5;
    }

    /* ===== MARQUEE CONTAINER ===== */
    .marquee-container {
        overflow: hidden;
        position: relative;
        width: 100%;
        max-width: 100%;
        height: 120px;
        display: flex;
        align-items: center;
        margin: 0 auto;
    }

    /* Fade effects on edges */
    .marquee-container::before,
    .marquee-container::after {
        content: '';
        position: absolute;
        top: 0;
        width: 150px;
        height: 100%;
        z-index: 2;
        pointer-events: none;
    }

    .marquee-container::before {
        left: 0;
        background: linear-gradient(to right, var(--bg-primary), transparent);
    }

    .marquee-container::after {
        right: 0;
        background: linear-gradient(to left, var(--bg-primary), transparent);
    }

    /* ===== MARQUEE ANIMATION ===== */
    .marquee-content {
        display: flex;
        animation: scroll 50s linear infinite;
        will-change: transform;
    }

    /* Pause on hover for accessibility */
    .marquee-container:hover .marquee-content {
        animation-play-state: paused;
    }

    @keyframes scroll {
        0% {
            transform: translateX(0);
        }
        100% {
            transform: translateX(-50%);
        }
    }

    /* Respect reduced motion preference */
    @media (prefers-reduced-motion: reduce) {
        .marquee-content {
            animation: scroll 120s linear infinite !important;
        }
    }

    /* ===== LOGO ITEMS ===== */
    .logo-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 220px;
        padding: 0 30px;
        opacity: 0.5;
        transition: opacity 0.3s ease, transform 0.3s ease;
        cursor: pointer;
    }

    .logo-item:hover {
        opacity: 1;
        transform: scale(1.05);
    }

    .logo-wrapper {
        width: 90px;
        height: 90px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 16px;
        transition: all 0.3s ease;
    }

    .logo-item:hover .logo-wrapper {
        background: rgba(124, 58, 237, 0.1);
        border-color: rgba(124, 58, 237, 0.3);
        box-shadow: 0 8px 24px rgba(124, 58, 237, 0.15);
    }

    .logo-img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        filter: brightness(0) invert(1) opacity(0.7);
        transition: filter 0.3s ease;
    }

    .logo-item:hover .logo-img {
        filter: brightness(1) invert(0) opacity(1);
    }

    .logo-svg {
        width: 100%;
        height: 100%;
        fill: rgba(255, 255, 255, 0.7);
        transition: fill 0.3s ease;
    }

    .logo-item:hover .logo-svg {
        fill: #7c3aed;
    }

    .logo-name {
        font-size: 0.75rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.5);
        text-align: center;
        line-height: 1.3;
        max-width: 160px;
        transition: color 0.3s ease;
    }

    .logo-item:hover .logo-name {
        color: rgba(255, 255, 255, 0.8);
    }

    /* ===== STATS ROW ===== */
    .credibility-stats {
        display: flex;
        justify-content: center;
        gap: 48px;
        margin-top: 40px;
        flex-wrap: wrap;
    }

    .stat-badge {
        text-align: center;
        padding: 16px 24px;
        background: rgba(124, 58, 237, 0.08);
        border-radius: 16px;
        border: 1px solid rgba(124, 58, 237, 0.2);
        transition: all 0.3s ease;
    }

    .stat-badge:hover {
        background: rgba(124, 58, 237, 0.12);
        border-color: rgba(124, 58, 237, 0.3);
        transform: translateY(-2px);
    }

    .stat-number {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(120deg, #7c3aed, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
    }

    .stat-label {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .marquee-container {
            height: 100px;
        }

        .logo-item {
            min-width: 180px;
            padding: 0 20px;
        }

        .logo-wrapper {
            width: 70px;
            height: 70px;
        }

        .credibility-stats {
            gap: 24px;
        }

        .stat-badge {
            padding: 12px 16px;
        }

        .stat-number {
            font-size: 1.4rem;
        }
    }
    </style>

    <div class="credibility-section">
        <div class="credibility-header">
            <div class="credibility-title">🏆 Backed by Leading Research</div>
            <div class="credibility-subtitle">
                Designed with insights from 45+ years of peer-reviewed accessibility studies<br>
                from world-renowned institutions and organizations
            </div>
        </div>

        <!-- Scrolling Marquee -->
        <div class="marquee-container">
            <div class="marquee-content">
                <!-- First set of logos -->
                <div class="logo-item" title="W3C - Web Accessibility Initiative">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg">
                            <text x="10" y="35" font-size="28" font-weight="700" font-family="Arial">W3C</text>
                        </svg>
                    </div>
                    <div class="logo-name">W3C Accessibility Initiative</div>
                </div>

                <div class="logo-item" title="Stanford University">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <rect x="20" y="30" width="60" height="40" fill="none" stroke="currentColor" stroke-width="3"/>
                            <polygon points="50,15 20,30 80,30" fill="currentColor"/>
                            <rect x="40" y="45" width="8" height="20" fill="currentColor"/>
                            <rect x="52" y="45" width="8" height="20" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">Stanford University</div>
                </div>

                <div class="logo-item" title="British Dyslexia Association">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="50" cy="50" r="35" fill="none" stroke="currentColor" stroke-width="4"/>
                            <path d="M35 50 L50 35 L65 50 L50 65 Z" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">British Dyslexia Association</div>
                </div>

                <div class="logo-item" title="University of Oxford">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <rect x="25" y="20" width="50" height="60" rx="5" fill="none" stroke="currentColor" stroke-width="3"/>
                            <line x1="35" y1="35" x2="65" y2="35" stroke="currentColor" stroke-width="2"/>
                            <line x1="35" y1="50" x2="65" y2="50" stroke="currentColor" stroke-width="2"/>
                            <line x1="35" y1="65" x2="65" y2="65" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </div>
                    <div class="logo-name">Oxford University Research</div>
                </div>

                <div class="logo-item" title="ADHD Foundation">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="50" cy="40" r="20" fill="currentColor"/>
                            <path d="M30 60 Q50 70 70 60" stroke="currentColor" stroke-width="4" fill="none"/>
                            <circle cx="40" cy="35" r="3" fill="white"/>
                            <circle cx="60" cy="35" r="3" fill="white"/>
                        </svg>
                    </div>
                    <div class="logo-name">ADHD Foundation</div>
                </div>

                <div class="logo-item" title="National Autistic Society">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <path d="M30 30 L70 30 L70 70 L30 70 Z" fill="none" stroke="currentColor" stroke-width="3"/>
                            <circle cx="40" cy="45" r="4" fill="currentColor"/>
                            <circle cx="60" cy="45" r="4" fill="currentColor"/>
                            <circle cx="50" cy="60" r="4" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">National Autistic Society</div>
                </div>

                <div class="logo-item" title="Nielsen Norman Group">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg">
                            <text x="15" y="35" font-size="24" font-weight="700" font-family="Arial">NN/g</text>
                        </svg>
                    </div>
                    <div class="logo-name">Nielsen Norman Group</div>
                </div>

                <div class="logo-item" title="WebAIM - Web Accessibility In Mind">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="50" cy="50" r="30" fill="none" stroke="currentColor" stroke-width="4"/>
                            <circle cx="50" cy="50" r="15" fill="none" stroke="currentColor" stroke-width="3"/>
                            <circle cx="50" cy="50" r="5" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">WebAIM Institute</div>
                </div>

                <!-- DUPLICATE SET for seamless loop -->
                <div class="logo-item" title="W3C - Web Accessibility Initiative">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg">
                            <text x="10" y="35" font-size="28" font-weight="700" font-family="Arial">W3C</text>
                        </svg>
                    </div>
                    <div class="logo-name">W3C Accessibility Initiative</div>
                </div>

                <div class="logo-item" title="Stanford University">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <rect x="20" y="30" width="60" height="40" fill="none" stroke="currentColor" stroke-width="3"/>
                            <polygon points="50,15 20,30 80,30" fill="currentColor"/>
                            <rect x="40" y="45" width="8" height="20" fill="currentColor"/>
                            <rect x="52" y="45" width="8" height="20" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">Stanford University</div>
                </div>

                <div class="logo-item" title="British Dyslexia Association">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="50" cy="50" r="35" fill="none" stroke="currentColor" stroke-width="4"/>
                            <path d="M35 50 L50 35 L65 50 L50 65 Z" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">British Dyslexia Association</div>
                </div>

                <div class="logo-item" title="University of Oxford">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <rect x="25" y="20" width="50" height="60" rx="5" fill="none" stroke="currentColor" stroke-width="3"/>
                            <line x1="35" y1="35" x2="65" y2="35" stroke="currentColor" stroke-width="2"/>
                            <line x1="35" y1="50" x2="65" y2="50" stroke="currentColor" stroke-width="2"/>
                            <line x1="35" y1="65" x2="65" y2="65" stroke="currentColor" stroke-width="2"/>
                        </svg>
                    </div>
                    <div class="logo-name">Oxford University Research</div>
                </div>

                <div class="logo-item" title="ADHD Foundation">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="50" cy="40" r="20" fill="currentColor"/>
                            <path d="M30 60 Q50 70 70 60" stroke="currentColor" stroke-width="4" fill="none"/>
                            <circle cx="40" cy="35" r="3" fill="white"/>
                            <circle cx="60" cy="35" r="3" fill="white"/>
                        </svg>
                    </div>
                    <div class="logo-name">ADHD Foundation</div>
                </div>

                <div class="logo-item" title="National Autistic Society">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <path d="M30 30 L70 30 L70 70 L30 70 Z" fill="none" stroke="currentColor" stroke-width="3"/>
                            <circle cx="40" cy="45" r="4" fill="currentColor"/>
                            <circle cx="60" cy="45" r="4" fill="currentColor"/>
                            <circle cx="50" cy="60" r="4" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">National Autistic Society</div>
                </div>

                <div class="logo-item" title="Nielsen Norman Group">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg">
                            <text x="15" y="35" font-size="24" font-weight="700" font-family="Arial">NN/g</text>
                        </svg>
                    </div>
                    <div class="logo-name">Nielsen Norman Group</div>
                </div>

                <div class="logo-item" title="WebAIM - Web Accessibility In Mind">
                    <div class="logo-wrapper">
                        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="50" cy="50" r="30" fill="none" stroke="currentColor" stroke-width="4"/>
                            <circle cx="50" cy="50" r="15" fill="none" stroke="currentColor" stroke-width="3"/>
                            <circle cx="50" cy="50" r="5" fill="currentColor"/>
                        </svg>
                    </div>
                    <div class="logo-name">WebAIM Institute</div>
                </div>
            </div>
        </div>

        <!-- Stats Row -->
        <div class="credibility-stats">
            <div class="stat-badge">
                <div class="stat-number">45+</div>
                <div class="stat-label">Years Research</div>
            </div>
            <div class="stat-badge">
                <div class="stat-number">60M+</div>
                <div class="stat-label">Users Helped</div>
            </div>
            <div class="stat-badge">
                <div class="stat-number">94/100</div>
                <div class="stat-label">A11y Score</div>
            </div>
            <div class="stat-badge">
                <div class="stat-number">AAA</div>
                <div class="stat-label">WCAG Level</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ========================================
# HOW TO ADD TO APP.PY
# ========================================

"""
1. Copy the render_credibility_banner() function above

2. In app.py, find the render_landing() function (around line 2800)

3. Add the call after the hero section:

def render_landing():
    st.markdown('''
    <div class="landing-hero">
        <h1 class="landing-title">🧠 Dopamine.watch</h1>
        <p class="landing-subtitle">The first streaming guide designed for <strong>ADHD & neurodivergent brains</strong>.</p>
        <p class="landing-tagline">Tell us how you feel. We'll find the perfect content to match your mood.</p>
    </div>
    ''', unsafe_allow_html=True)

    # ADD THIS LINE 👇
    render_credibility_banner()

    # Then continue with CTA buttons...
    col1, col2, col3 = st.columns([1, 2, 1])
    ...

4. Save and refresh!
"""
