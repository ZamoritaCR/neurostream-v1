"""
Dopamine.watch 2027 - Landing Page
Modern, engaging landing page with hero section, features, and social proof.
Inspired by Linear, Vercel, and Arc Browser landing pages.
"""

import streamlit as st
from core.session import show_modal


def render_landing_page():
    """Render the complete landing page."""

    # Inject landing page specific styles
    st.markdown(get_landing_styles(), unsafe_allow_html=True)

    # Hero Section
    render_hero()

    # Features Section (Bento Grid)
    render_features_bento()

    # Social Proof
    render_social_proof()

    # Mr.DP Introduction
    render_mr_dp_section()

    # CTA Section
    render_cta_section()

    # Footer
    render_footer()


def render_hero():
    """Render the hero section with gradient background."""

    hero_html = """
    <div class="landing-hero">
        <div class="hero-gradient-bg"></div>
        <div class="hero-content">
            <div class="hero-badge animate-fade-in">
                <span class="badge-icon">🧠</span>
                <span>Built for ADHD brains</span>
            </div>

            <h1 class="hero-title animate-slide-up">
                Your AI-Powered<br>
                <span class="gradient-text">Dopamine Curator</span>
            </h1>

            <p class="hero-subtitle animate-slide-up stagger-1">
                Stop doom-scrolling. Start enjoying.<br>
                Mr.DP finds the perfect content for your mood in seconds.
            </p>

            <div class="hero-cta animate-slide-up stagger-2">
                <button class="btn btn-primary btn-xl" onclick="window.dispatchEvent(new CustomEvent('open-signup'))">
                    Start Free
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                </button>
                <button class="btn btn-outline btn-xl" onclick="window.dispatchEvent(new CustomEvent('open-demo'))">
                    Watch Demo
                </button>
            </div>

            <div class="hero-stats animate-fade-in stagger-3">
                <div class="stat">
                    <span class="stat-value">50K+</span>
                    <span class="stat-label">Happy Users</span>
                </div>
                <div class="stat-divider"></div>
                <div class="stat">
                    <span class="stat-value">4.9</span>
                    <span class="stat-label">App Rating</span>
                </div>
                <div class="stat-divider"></div>
                <div class="stat">
                    <span class="stat-value">2M+</span>
                    <span class="stat-label">Recommendations</span>
                </div>
            </div>
        </div>

        <div class="hero-visual animate-scale-in stagger-2">
            <div class="app-preview">
                <div class="preview-header">
                    <div class="preview-dots">
                        <span></span><span></span><span></span>
                    </div>
                    <span class="preview-title">dopamine.watch</span>
                </div>
                <div class="preview-content">
                    <div class="preview-mr-dp">
                        <div class="mr-dp-avatar animate-float">🧠</div>
                        <div class="mr-dp-bubble">
                            Hey! Feeling stressed? I found 3 calming shows perfect for unwinding...
                        </div>
                    </div>
                    <div class="preview-cards">
                        <div class="preview-card"></div>
                        <div class="preview-card"></div>
                        <div class="preview-card"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)

    # Handle button clicks via Streamlit
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Get Started Free", key="hero_cta", type="primary", use_container_width=True):
            show_modal("signup")


def render_features_bento():
    """Render features in a modern bento grid layout."""

    bento_html = """
    <section class="features-section">
        <div class="section-header">
            <h2 class="section-title">Everything you need.<br><span class="gradient-text">Nothing you don't.</span></h2>
            <p class="section-subtitle">Designed specifically for ADHD brains - no clutter, no overwhelm, just content you'll actually enjoy.</p>
        </div>

        <div class="bento-grid">
            <!-- Large Feature: Mr.DP -->
            <div class="bento-card bento-large">
                <div class="bento-icon">🤖</div>
                <h3>Meet Mr.DP</h3>
                <p>Your AI companion who actually understands ADHD. Tell him how you feel, and he'll find exactly what you need - no endless scrolling required.</p>
                <div class="bento-visual mr-dp-demo">
                    <div class="chat-bubble user">I'm stressed and can't focus</div>
                    <div class="chat-bubble ai">I hear you! Let me find something calming. How about a nature documentary? They're proven to reduce cortisol.</div>
                </div>
            </div>

            <!-- Mood-Based -->
            <div class="bento-card">
                <div class="bento-icon">🎭</div>
                <h3>Mood-Based Discovery</h3>
                <p>Select how you feel now and how you want to feel. We handle the rest.</p>
            </div>

            <!-- Quick Picks -->
            <div class="bento-card">
                <div class="bento-icon">⚡</div>
                <h3>Quick Dope Hit</h3>
                <p>Can't decide? One tap and Mr.DP picks something perfect for you.</p>
            </div>

            <!-- Time Estimates -->
            <div class="bento-card">
                <div class="bento-icon">⏱️</div>
                <h3>Time-Aware</h3>
                <p>Every suggestion shows duration. No more starting a 3-hour movie when you have 30 minutes.</p>
            </div>

            <!-- Social -->
            <div class="bento-card">
                <div class="bento-icon">👥</div>
                <h3>Watch Together</h3>
                <p>Synchronized watch parties with friends. Chat while you watch, react together.</p>
            </div>

            <!-- Save for Later -->
            <div class="bento-card bento-wide">
                <div class="bento-icon">💾</div>
                <h3>Your Dopamine Queue</h3>
                <p>Save anything for later. Mr.DP remembers what you liked and learns your preferences.</p>
                <div class="queue-preview">
                    <div class="queue-item"></div>
                    <div class="queue-item"></div>
                    <div class="queue-item"></div>
                    <div class="queue-item"></div>
                </div>
            </div>
        </div>
    </section>
    """
    st.markdown(bento_html, unsafe_allow_html=True)


def render_social_proof():
    """Render testimonials and social proof."""

    proof_html = """
    <section class="social-proof-section">
        <div class="section-header">
            <h2 class="section-title">Loved by ADHD brains<br><span class="gradient-text">everywhere</span></h2>
        </div>

        <div class="testimonials-grid">
            <div class="testimonial-card">
                <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
                <p class="testimonial-text">"Finally an app that gets it. No more spending 45 minutes deciding what to watch and then giving up."</p>
                <div class="testimonial-author">
                    <div class="author-avatar">S</div>
                    <div class="author-info">
                        <span class="author-name">Sarah M.</span>
                        <span class="author-tag">ADHD + Anxiety</span>
                    </div>
                </div>
            </div>

            <div class="testimonial-card">
                <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
                <p class="testimonial-text">"Mr.DP is like having a friend who knows exactly what I need. The mood-based recommendations are spot on."</p>
                <div class="testimonial-author">
                    <div class="author-avatar">J</div>
                    <div class="author-info">
                        <span class="author-name">James K.</span>
                        <span class="author-tag">Adult ADHD</span>
                    </div>
                </div>
            </div>

            <div class="testimonial-card">
                <div class="testimonial-stars">⭐⭐⭐⭐⭐</div>
                <p class="testimonial-text">"The Quick Dope Hit button is genius. Takes away the decision paralysis completely."</p>
                <div class="testimonial-author">
                    <div class="author-avatar">M</div>
                    <div class="author-info">
                        <span class="author-name">Maria L.</span>
                        <span class="author-tag">Combined Type</span>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """
    st.markdown(proof_html, unsafe_allow_html=True)


def render_mr_dp_section():
    """Render the Mr.DP introduction section."""

    mr_dp_html = """
    <section class="mr-dp-section">
        <div class="mr-dp-container">
            <div class="mr-dp-visual">
                <div class="mr-dp-avatar-large animate-float">
                    <div class="avatar-glow"></div>
                    🧠
                </div>
                <div class="mr-dp-expressions">
                    <span>😊</span>
                    <span>🤔</span>
                    <span>🎉</span>
                    <span>😴</span>
                </div>
            </div>

            <div class="mr-dp-info">
                <h2>Say hello to <span class="gradient-text">Mr.DP</span></h2>
                <p class="mr-dp-description">
                    Mr.DP (Mr. Dopamine) is your personal AI curator. He understands that ADHD brains work differently - and that's okay!
                </p>
                <ul class="mr-dp-features">
                    <li>
                        <span class="feature-icon">💬</span>
                        <span>Tell him how you feel in plain language</span>
                    </li>
                    <li>
                        <span class="feature-icon">🧠</span>
                        <span>He learns your preferences over time</span>
                    </li>
                    <li>
                        <span class="feature-icon">🎯</span>
                        <span>Max 3 suggestions - no decision paralysis</span>
                    </li>
                    <li>
                        <span class="feature-icon">💚</span>
                        <span>Never judges, always supportive</span>
                    </li>
                </ul>
            </div>
        </div>
    </section>
    """
    st.markdown(mr_dp_html, unsafe_allow_html=True)


def render_cta_section():
    """Render the final call-to-action section."""

    cta_html = """
    <section class="cta-section">
        <div class="cta-container">
            <h2>Ready for your next<br><span class="gradient-text">dopamine hit?</span></h2>
            <p>Join thousands of ADHD brains who've found their perfect content curator.</p>
            <div class="cta-buttons">
                <button class="btn btn-primary btn-xl" onclick="window.dispatchEvent(new CustomEvent('open-signup'))">
                    Start Free Today
                </button>
            </div>
            <p class="cta-note">No credit card required • Free plan available forever</p>
        </div>
    </section>
    """
    st.markdown(cta_html, unsafe_allow_html=True)

    # Streamlit button fallback
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Free Today", key="cta_final", type="primary", use_container_width=True):
            show_modal("signup")


def render_footer():
    """Render the footer."""

    footer_html = """
    <footer class="landing-footer">
        <div class="footer-content">
            <div class="footer-brand">
                <span class="footer-logo">🧠 dopamine.watch</span>
                <p>Built with love for ADHD brains.</p>
            </div>
            <div class="footer-links">
                <div class="footer-column">
                    <h4>Product</h4>
                    <a href="#">Features</a>
                    <a href="#">Pricing</a>
                    <a href="#">Mr.DP</a>
                </div>
                <div class="footer-column">
                    <h4>Company</h4>
                    <a href="#">About</a>
                    <a href="#">Blog</a>
                    <a href="#">Careers</a>
                </div>
                <div class="footer-column">
                    <h4>Legal</h4>
                    <a href="#">Privacy</a>
                    <a href="#">Terms</a>
                </div>
            </div>
        </div>
        <div class="footer-bottom">
            <p>© 2027 dopamine.watch. All rights reserved.</p>
        </div>
    </footer>
    """
    st.markdown(footer_html, unsafe_allow_html=True)


def get_landing_styles():
    """Get landing page specific CSS."""

    return """
    <style>
    /* Hide Streamlit elements on landing */
    .landing-hero ~ div [data-testid="stButton"] {
        display: none;
    }

    /* ═══ HERO SECTION ═══ */
    .landing-hero {
        min-height: 100vh;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4rem;
        padding: 4rem;
        position: relative;
        overflow: hidden;
    }

    .hero-gradient-bg {
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse at 20% 20%, rgba(139, 127, 216, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(94, 186, 175, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(245, 197, 99, 0.05) 0%, transparent 70%);
        z-index: 0;
    }

    .hero-content {
        position: relative;
        z-index: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(139, 127, 216, 0.1);
        border: 1px solid rgba(139, 127, 216, 0.2);
        border-radius: 100px;
        font-size: 0.875rem;
        font-weight: 500;
        color: #8B7FD8;
        width: fit-content;
        margin-bottom: 1.5rem;
    }

    .badge-icon {
        font-size: 1rem;
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: 1.5rem;
        color: #1C1917;
    }

    .gradient-text {
        background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: #57534E;
        line-height: 1.6;
        margin-bottom: 2rem;
        max-width: 500px;
    }

    .hero-cta {
        display: flex;
        gap: 1rem;
        margin-bottom: 3rem;
    }

    .hero-stats {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .stat {
        text-align: center;
    }

    .stat-value {
        display: block;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1C1917;
    }

    .stat-label {
        font-size: 0.875rem;
        color: #78716C;
    }

    .stat-divider {
        width: 1px;
        height: 40px;
        background: #E7E5E2;
    }

    /* Hero Visual */
    .hero-visual {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .app-preview {
        background: #FFFFFF;
        border-radius: 1.5rem;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        width: 100%;
        max-width: 450px;
    }

    .preview-header {
        background: #F5F5F3;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .preview-dots {
        display: flex;
        gap: 0.5rem;
    }

    .preview-dots span {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #E7E5E2;
    }

    .preview-dots span:first-child { background: #EF4444; }
    .preview-dots span:nth-child(2) { background: #F59E0B; }
    .preview-dots span:nth-child(3) { background: #10B981; }

    .preview-title {
        font-size: 0.875rem;
        color: #78716C;
    }

    .preview-content {
        padding: 1.5rem;
    }

    .preview-mr-dp {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .mr-dp-avatar {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }

    .mr-dp-bubble {
        background: rgba(139, 127, 216, 0.1);
        border-radius: 1rem;
        padding: 1rem;
        font-size: 0.875rem;
        color: #44403C;
        line-height: 1.5;
    }

    .preview-cards {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
    }

    .preview-card {
        aspect-ratio: 2/3;
        background: linear-gradient(135deg, #E7E5E2, #D6D3D0);
        border-radius: 0.75rem;
    }

    /* ═══ FEATURES BENTO ═══ */
    .features-section {
        padding: 6rem 4rem;
        background: #F5F5F3;
    }

    .section-header {
        text-align: center;
        margin-bottom: 4rem;
    }

    .section-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 1rem;
    }

    .section-subtitle {
        font-size: 1.125rem;
        color: #57534E;
        max-width: 600px;
        margin: 0 auto;
    }

    .bento-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .bento-card {
        background: #FFFFFF;
        border-radius: 1.5rem;
        padding: 2rem;
        transition: all 0.3s ease;
    }

    .bento-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }

    .bento-large {
        grid-column: span 2;
        grid-row: span 2;
    }

    .bento-wide {
        grid-column: span 2;
    }

    .bento-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    .bento-card h3 {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .bento-card p {
        color: #57534E;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* ═══ SOCIAL PROOF ═══ */
    .social-proof-section {
        padding: 6rem 4rem;
    }

    .testimonials-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .testimonial-card {
        background: #FFFFFF;
        border: 1px solid #E7E5E2;
        border-radius: 1.5rem;
        padding: 2rem;
    }

    .testimonial-stars {
        margin-bottom: 1rem;
    }

    .testimonial-text {
        font-size: 1rem;
        line-height: 1.7;
        color: #44403C;
        margin-bottom: 1.5rem;
    }

    .testimonial-author {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .author-avatar {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
    }

    .author-name {
        display: block;
        font-weight: 600;
    }

    .author-tag {
        font-size: 0.875rem;
        color: #78716C;
    }

    /* ═══ MR.DP SECTION ═══ */
    .mr-dp-section {
        padding: 6rem 4rem;
        background: linear-gradient(135deg, rgba(139, 127, 216, 0.05), rgba(94, 186, 175, 0.05));
    }

    .mr-dp-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4rem;
        max-width: 1200px;
        margin: 0 auto;
        align-items: center;
    }

    .mr-dp-avatar-large {
        width: 200px;
        height: 200px;
        background: linear-gradient(135deg, #8B7FD8, #5EBAAF);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 5rem;
        margin: 0 auto;
        position: relative;
        box-shadow: 0 20px 60px rgba(139, 127, 216, 0.4);
    }

    .avatar-glow {
        position: absolute;
        inset: -20px;
        background: radial-gradient(circle, rgba(139, 127, 216, 0.3), transparent 70%);
        border-radius: 50%;
        z-index: -1;
    }

    .mr-dp-expressions {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 2rem;
        font-size: 2rem;
    }

    .mr-dp-info h2 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    .mr-dp-description {
        font-size: 1.125rem;
        color: #57534E;
        margin-bottom: 2rem;
        line-height: 1.7;
    }

    .mr-dp-features {
        list-style: none;
    }

    .mr-dp-features li {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        font-size: 1rem;
    }

    .feature-icon {
        font-size: 1.25rem;
    }

    /* ═══ CTA SECTION ═══ */
    .cta-section {
        padding: 6rem 4rem;
        text-align: center;
    }

    .cta-container h2 {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .cta-container p {
        font-size: 1.125rem;
        color: #57534E;
        margin-bottom: 2rem;
    }

    .cta-note {
        font-size: 0.875rem;
        color: #78716C;
        margin-top: 1rem;
    }

    /* ═══ FOOTER ═══ */
    .landing-footer {
        background: #1C1917;
        color: #A8A29D;
        padding: 4rem;
    }

    .footer-content {
        display: flex;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
        padding-bottom: 3rem;
        border-bottom: 1px solid #292524;
    }

    .footer-logo {
        font-size: 1.25rem;
        font-weight: 700;
        color: #FAFAFA;
    }

    .footer-brand p {
        margin-top: 0.5rem;
    }

    .footer-links {
        display: flex;
        gap: 4rem;
    }

    .footer-column h4 {
        color: #FAFAFA;
        margin-bottom: 1rem;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .footer-column a {
        display: block;
        color: #A8A29D;
        text-decoration: none;
        margin-bottom: 0.5rem;
        transition: color 0.2s;
    }

    .footer-column a:hover {
        color: #FAFAFA;
    }

    .footer-bottom {
        max-width: 1200px;
        margin: 0 auto;
        padding-top: 2rem;
        text-align: center;
        font-size: 0.875rem;
    }

    /* ═══ RESPONSIVE ═══ */
    @media (max-width: 1024px) {
        .landing-hero {
            grid-template-columns: 1fr;
            padding: 2rem;
        }

        .hero-title {
            font-size: 2.5rem;
        }

        .hero-visual {
            order: -1;
        }

        .bento-grid {
            grid-template-columns: 1fr;
        }

        .bento-large, .bento-wide {
            grid-column: span 1;
            grid-row: span 1;
        }

        .testimonials-grid {
            grid-template-columns: 1fr;
        }

        .mr-dp-container {
            grid-template-columns: 1fr;
            text-align: center;
        }

        .footer-content {
            flex-direction: column;
            gap: 2rem;
        }

        .footer-links {
            flex-wrap: wrap;
            gap: 2rem;
        }
    }
    </style>
    """
