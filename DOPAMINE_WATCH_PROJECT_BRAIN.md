# DOPAMINE.WATCH - COMPLETE PROJECT REFERENCE
**Last Updated: January 30, 2026**

---

## 🎯 PROJECT OVERVIEW

**dopamine.watch** is an ADHD-friendly streaming recommendation app that helps neurodivergent users find content based on emotional state transitions. Built by Johan, who has ADHD himself, the app addresses a critical pain point: decision paralysis and sensory overload in traditional streaming platforms.

### Core Value Proposition
- **Emotion-driven filtering**: "How I feel now" → "How I want to feel"
- **Decision-free content selection**: No endless scrolling or analysis paralysis
- **ADHD-optimized interface**: Based on 45+ years of neuroscience research
- **Multi-platform aggregation**: Movies, music, podcasts, audiobooks, shorts across all streaming services

### Target Users
- Neurodivergent individuals (ADHD, ASD)
- Users with dyslexia (30-50% comorbidity with ADHD)
- Anyone experiencing decision fatigue with streaming platforms
- Users who need mood-based content curation

---

## 💻 TECH STACK

### Frontend
- **Framework**: Streamlit (Python)
- **Hosting**: Railway
- **Landing Page**: GreenGeeks (WordPress + static HTML)
- **Languages**: Bilingual (English/Spanish)

### Backend
- **Database**: Supabase Pro
- **Authentication**: Supabase Auth + Google Sign-In
- **Row Level Security**: Enabled (user isolation)

### APIs & Services
- **TMDB API**: Movie/TV metadata and streaming provider links
- **OpenAI API**: Powers "Mr.DP" AI chatbot
- **Stripe**: Payment processing and subscription management
- **Google Sign-In**: OAuth authentication

### Development Environment
- **Platform**: Mac (user switched back from PC)
- **IDE**: VS Code
- **Version Control**: GitHub (repo: ZamoritaCR/neurostream-v1)
- **AI Assistants**: Claude (web + VS Code), ChatGPT 5.2 Pro

---

## 🧠 CORE FEATURES

### 1. Mood-Based Content Discovery
**Emotion Mapping System**:
```python
# Current implementation maps emotions to TMDB genres
emotion_to_genre = {
    "happy": [35, 10751],  # Comedy, Family
    "sad": [18, 10749],    # Drama, Romance
    "anxious": [35, 16],   # Comedy, Animation
    "angry": [28, 53],     # Action, Thriller
    "bored": [12, 878],    # Adventure, Sci-Fi
    # ... full mapping in codebase
}
```

**Mood Transition Flow**:
1. User selects "How I feel now"
2. User selects "How I want to feel"
3. App filters content based on both states
4. Results show streaming availability via TMDB provider data

### 2. Mr.DP AI Chatbot
**Character**: Purple brain with antennae and sparkles, friendly ADHD-aware companion

**Core Functionality**:
- Natural language content queries
- ADHD-aware prompting (decisive, no decision paralysis)
- Validates feelings before suggesting content
- Concise responses (<3 sentences typical)
- Two processing modes:
  - Heuristic parsing for simple queries
  - OpenAI API for complex requests

**System Prompt Philosophy**:
```
- Make decisive recommendations (no "it depends" or follow-up questions)
- Validate user's emotional state first
- Keep responses brief and actionable
- Avoid overwhelming with options
- Understand neurodivergent communication patterns
```

### 3. Quick Dope Hit
**The Killer Feature**: One-click randomized content for decision paralysis

**Implementation**:
- Button in sidebar: "I don't know what I want"
- Randomly selects from emotion-appropriate content
- Bypasses all decision-making
- Designed for dopamine-seeking behavior in ADHD brains

### 4. Content Tabs
Five distinct content categories:
1. **Movies**: TMDB discover endpoint with provider links
2. **Shorts**: YouTube/TikTok-style content
3. **Music**: Streaming music recommendations
4. **Podcasts**: Podcast discovery
5. **Audiobooks**: Audiobook recommendations

### 5. Gamification System
- Streaks tracking
- Engagement rewards
- Variable reward schedules (70% more dopamine transporters in ADHD brains)
- Small, frequent rewards vs. large milestones

### 6. Search & Discovery
- Natural language search via Mr.DP
- Genre-based browsing
- Provider-specific filtering
- Fallback system: Search → Discover → Error handling

---

## 🏗️ ARCHITECTURE & CODE STRUCTURE

### File Structure
```
dopamine.watch/
├── app.py (main application, 1800-4461 lines depending on version)
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── static/
│   ├── mr_dp_avatar.svg
│   └── animations/
└── landing/
    ├── index.html (English landing page)
    ├── index_es.html (Spanish landing page)
    ├── privacidad.html (Spanish privacy)
    └── terminos.html (Spanish terms)
```

### Key Code Sections

**Session State Initialization**:
```python
# Must include for back-compatibility:
if 'nlp_last_prompt' not in st.session_state:
    st.session_state.nlp_last_prompt = ""
```

**Critical Bug Fix**:
```python
def _clean_results(results):
    # CRITICAL: TMDB discover endpoint doesn't include media_type
    # Must default to "movie" to prevent filtering all results
    for item in results:
        if 'media_type' not in item:
            item['media_type'] = 'movie'  # Default for discover endpoint
```

**Emotion to Genre Mapping**:
- Comprehensive mapping of human emotions to TMDB genre IDs
- Supports nuanced emotional states
- Used for both discover and search endpoints

**NLP Processing**:
- Heuristic parsing for simple queries
- OpenAI integration for complex interpretation
- Query planning system
- Fallback mechanisms

---

## ⚠️ CRITICAL DEVELOPMENT RULES

### 🚨 NEVER REFACTOR WITHOUT EXPLICIT PERMISSION
Johan has ADHD and has built a substantial codebase that works. **Preserve existing architecture at all costs**.

**Rules**:
1. **SURGICAL FIXES ONLY**: Fix the specific bug/feature requested
2. **NO SIMPLIFICATION**: Don't "clean up" or "improve" existing code
3. **PRESERVE ALL FEATURES**: Never remove functionality to "streamline"
4. **ASK BEFORE MAJOR CHANGES**: Get explicit approval for architectural changes
5. **STEP-BY-STEP**: One task at a time, wait for confirmation
6. **NO OVERWHELMING INFO DUMPS**: Break complex tasks into digestible steps

### Why This Matters
- Johan has extreme ADHD - cognitive load is a real constraint
- Refactoring broke the app before (v40.0 disaster)
- The "mother code" represents months of work and learning
- Breaking changes cause significant frustration and setback

### The Refactoring Incident (January 2026)
**What happened**: Claude created v40.0 refactor reducing code from 4,461 to 2,369 lines
**Result**: Broke core functionality - movies loading, search, Mr.DP chatbot, and more
**Lesson**: User explicitly stated "I have personal circumstances affecting focus and explicitly prefer surgical fixes over extensive refactoring"

---

## 🎨 ADHD OPTIMIZATION: RESEARCH & DESIGN PRINCIPLES

### Neuroscience Foundation
Based on 45+ years of ADHD research, dopamine.watch implements scientifically-backed accommodations:

#### 1. Dopamine System Understanding
- **70% more dopamine transporters** in ADHD brains
- Requires frequent small rewards (not large milestones)
- Quick Dope Hit feature directly addresses dopamine-seeking behavior
- Variable reward schedules keep engagement high

#### 2. Retinal Dopamine Processing
- **Impaired blue-yellow color processing** due to retinal dopamine deficiency
- Softened color palette (teal instead of bright cyan)
- Reduced pure white/black contrast (off-white/dark-gray instead)
- 20-30% desaturation across UI

#### 3. Sensory Overload Prevention
- Minimal visual clutter
- Focus Mode toggle to reduce noise
- Single-column layouts (no split attention)
- Generous whitespace
- Smooth animations only (no jarring transitions)

#### 4. Typography for Dyslexia
- **Lexend font** (scientifically designed for dyslexia)
- 30-50% ADHD comorbidity with dyslexia
- Increased letter spacing (0.05em)
- Increased line height (1.6)
- Larger base font size (16px minimum)

### Current Design Implementation

**Color Palette**:
```css
/* ADHD-Optimized Colors */
--primary: #14B8A6;        /* Teal (was bright cyan) */
--background: #1A1F2E;     /* Dark blue-gray */
--surface: #2D3748;        /* Lighter gray for cards */
--text-primary: #F7FAFC;   /* Off-white (not pure white) */
--text-secondary: #A0AEC0; /* Muted gray for secondary text */
--accent: #9D4EDD;         /* Purple for Mr.DP branding */
```

**Typography**:
```css
/* Lexend font for dyslexia support */
font-family: 'Lexend', -apple-system, BlinkMacSystemFont, sans-serif;
letter-spacing: 0.05em;
line-height: 1.6;
```

**UI Principles**:
- Main area: Content ONLY (no controls)
- Sidebar: ALL controls and filters
- Cards: High contrast, clear boundaries
- CTAs: Large tap targets (44px minimum)
- Icons: Simple, recognizable, consistent

### Focus Mode
Toggle to reduce visual noise:
- Hides decorative elements
- Disables animations
- Increases contrast
- Simplifies layout
- Reduces color saturation further

---

## 🔧 CURRENT TECHNICAL ISSUES & SOLUTIONS

### Known Bugs & Fixes

#### 1. Movies Not Loading (FIXED)
**Problem**: `_clean_results()` filtered all movies out
**Cause**: TMDB discover endpoint doesn't include `media_type` field
**Solution**:
```python
def _clean_results(results):
    for item in results:
        if 'media_type' not in item:
            item['media_type'] = 'movie'  # Default for discover
    return [item for item in results if item.get('media_type') == 'movie']
```

#### 2. Session State Error (FIXED)
**Problem**: `AttributeError: st.session_state.nlp_last_prompt`
**Cause**: Missing initialization for existing users
**Solution**:
```python
# Add to initialization section
if 'nlp_last_prompt' not in st.session_state:
    st.session_state.nlp_last_prompt = ""
```

#### 3. Landing Page Issues (FIXED - January 2026)
**Problems**:
- Broken language switching on Spanish site
- Non-functional login buttons
- Dead internal links on both English/Spanish pages
- Corrupted JavaScript (truncated mid-line)

**Solutions**:
- Complete rewrite of index.html with proper JavaScript
- Created full Spanish translation (index_es.html)
- Converted all links to absolute URLs (https://dopamine.watch/...)
- Added Download App section with PWA instructions
- Fixed authentication modals and Google Sign-In integration

#### 4. Floating Mr.DP Avatar (ONGOING)
**Problem**: HTML element error (specific details needed from user)
**Status**: Cannot debug without error messages
**Next Steps**: User needs to provide error output

#### 5. Smart Quotes Bug (FIXED)
**Problem**: Syntax errors from curly quotes in code
**Cause**: Copy-paste from rich text editors
**Solution**:
```python
# Replace smart quotes with straight quotes
code = code.replace('"', '"').replace('"', '"')
code = code.replace("'", "'").replace("'", "'")
```

---

## 💰 MARKETING & MONETIZATION

### Business Model

**Free Tier**:
- 5 mood-based recommendations per day
- 10 Mr.DP AI chat messages per day
- 3 Quick Dope Hits per day
- Full access to all content types

**Premium Tier** (Stripe):
- Unlimited everything
- Advanced features (TBD)
- Priority support
- Early access to new features

### Supabase Usage Tracking
```sql
-- Implementation needed via Claude VS Code commands
CREATE TABLE user_usage (
    user_id UUID REFERENCES auth.users,
    date DATE,
    recommendations_count INT DEFAULT 0,
    chat_messages_count INT DEFAULT 0,
    quick_hits_count INT DEFAULT 0,
    subscription_tier TEXT DEFAULT 'free'
);
```

### Marketing Strategy

#### SEO Optimization (Implemented)
**Meta Tags**:
```html
<!-- Primary Keywords -->
<meta name="keywords" content="ADHD streaming guide, neurodivergent what to watch, decision fatigue solution, mood-based streaming, dopamine streaming app">

<!-- Schema.org for AI Search Engines -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Dopamine.Watch",
  "applicationCategory": "EntertainmentApplication",
  "audience": {
    "@type": "Audience",
    "audienceType": "People with ADHD and neurodivergent conditions"
  }
}
</script>
```

**FAQ Section**:
- Targets "ADHD what to watch" searches
- Addresses common neurodivergent streaming struggles
- Optimized for featured snippets

#### Content Marketing Automation (In Development)
**Goal**: Zero human intervention content pipeline

**Platforms**:
1. TikTok (primary viral platform)
2. Instagram Reels
3. Facebook
4. YouTube Shorts

**Tools Available**:
- Sora API access (OpenAI - not yet public)
- Gemini API (Google)
- GPT Enterprise API (OpenAI)

**Current Status**:
- TikTok automation failed (rate limiting)
- Pivoted to Instagram Reels
- Created MoviePy-based video generation
- Need reliable posting automation

**Prototype Code**:
```python
# Video generation with text overlays
# Gemini for content creation
# MoviePy for compilation
# Platform-specific posting SDKs
```

#### iConvert Promoter (WordPress Plugin)
**Popup Campaigns** (5 designed for ADHD users):
1. Exit-intent email capture
2. Premium upsell after 3rd recommendation
3. Quick Dope Hit promotion
4. Mr.DP feature highlight
5. Subscription CTA

**Status**: Paused due to WordPress editor loading issue

### Marketing Positioning
**Unique Selling Points**:
- ONLY streaming app designed for ADHD brains
- Science-backed design (45+ years research)
- Addresses decision paralysis specifically
- Mood transition filtering (unique feature)
- ADHD-aware AI assistant

**Target Demographic**:
- 6.4M adults with ADHD in US
- 20% of Gen Z reports ADHD symptoms
- Growing awareness and diagnosis rates
- Underserved market with high willingness to pay

---

## 🚀 DEPLOYMENT & INFRASTRUCTURE

### Production Environment

**Main App**:
- **Host**: Railway
- **Domain**: dopamine.watch
- **Framework**: Streamlit
- **Database**: Supabase Pro (PostgreSQL)
- **CDN**: Cloudflare (assumed)

**Landing Pages**:
- **Host**: GreenGeeks (WordPress)
- **Files**: Static HTML/CSS/JS
- **Languages**: English (index.html), Spanish (index_es.html)
- **Legal Pages**: privacidad.html, terminos.html

### Deployment Workflow

**Current Process**:
1. Edit code in VS Code (Mac)
2. Push to GitHub (ZamoritaCR/neurostream-v1)
3. Railway auto-deploys from main branch
4. Landing pages: Manual SFTP upload to GreenGeeks

**Proposed Improvement**:
- VS Code SFTP extension for automated GreenGeeks deployment
- Git hooks for landing page sync
- Streamlit Cloud cache clearing automation

### Environment Variables
```
OPENAI_API_KEY=sk-...
TMDB_API_KEY=eyJ...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
```

### Database Schema (Supabase)

**Tables Needed**:
```sql
-- Users (managed by Supabase Auth)
-- auth.users (built-in)

-- User Preferences
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES auth.users,
    favorite_genres INT[],
    streaming_services TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage Tracking
CREATE TABLE user_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users,
    date DATE DEFAULT CURRENT_DATE,
    recommendations_count INT DEFAULT 0,
    chat_messages_count INT DEFAULT 0,
    quick_hits_count INT DEFAULT 0,
    UNIQUE(user_id, date)
);

-- Subscription Status
CREATE TABLE subscriptions (
    user_id UUID PRIMARY KEY REFERENCES auth.users,
    stripe_customer_id TEXT,
    subscription_tier TEXT DEFAULT 'free',
    stripe_subscription_id TEXT,
    subscription_status TEXT,
    current_period_end TIMESTAMPTZ
);

-- Chat History
CREATE TABLE chat_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users,
    message TEXT,
    response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Row Level Security**:
```sql
-- Enable RLS on all tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only see their own data
CREATE POLICY user_preferences_policy ON user_preferences
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY user_usage_policy ON user_usage
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY subscriptions_policy ON subscriptions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY chat_history_policy ON chat_history
    FOR ALL USING (auth.uid() = user_id);
```

---

## 🔌 API INTEGRATIONS

### TMDB (The Movie Database)

**Authentication**: Bearer Token (JWT)
```
Authorization: Bearer eyJ...
```

**Key Endpoints Used**:

1. **Discover Movies**:
```
GET /discover/movie
Parameters:
  - with_genres: Comma-separated genre IDs
  - with_watch_providers: Provider IDs
  - watch_region: US (default)
  - sort_by: popularity.desc
```

2. **Search**:
```
GET /search/multi
Parameters:
  - query: Search term
  - include_adult: false
```

3. **Provider Details**:
```
GET /movie/{movie_id}/watch/providers
```

**Genre ID Mapping**:
```python
TMDB_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}
```

**Known Issues**:
- Discover endpoint doesn't include `media_type` (always default to "movie")
- Rate limits: 50 requests per second
- Results may include unavailable content (filter client-side)

### OpenAI API

**Model**: GPT-4 (or latest available)
**Use Case**: Mr.DP chatbot natural language processing

**System Prompt**:
```python
system_prompt = """You are Mr.DP, a friendly AI assistant for dopamine.watch.
You help neurodivergent users find content based on their emotional state.

CRITICAL RULES:
1. Be decisive - no "it depends" or asking clarifying questions
2. Validate their feelings first, then recommend
3. Keep responses under 3 sentences
4. Avoid decision paralysis triggers
5. Understand ADHD communication patterns

Example:
User: "I'm feeling overwhelmed"
You: "That sounds really tough. Let me find you something calming and familiar. How about a cozy sitcom rewatch?"
"""
```

**Implementation**:
```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ],
    max_tokens=150,
    temperature=0.7
)
```

### Supabase

**Authentication**:
```python
from supabase import create_client

supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_ANON_KEY")
)

# Sign up
supabase.auth.sign_up({
    "email": email,
    "password": password
})

# Sign in
supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

# Get current user
user = supabase.auth.get_user()
```

**Database Operations**:
```python
# Insert usage
supabase.table('user_usage').insert({
    'user_id': user.id,
    'recommendations_count': 1
}).execute()

# Query with RLS (automatic filtering)
data = supabase.table('user_preferences').select('*').execute()
```

### Stripe

**Checkout Session**:
```python
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

session = stripe.checkout.Session.create(
    customer_email=user_email,
    mode='subscription',
    line_items=[{
        'price': 'price_xxxxxxxxxxxxx',  # Price ID from Stripe
        'quantity': 1,
    }],
    success_url='https://dopamine.watch/success',
    cancel_url='https://dopamine.watch/pricing',
)
```

**Webhook Handling**:
```python
# Listen for subscription events
# subscription.created
# subscription.updated
# subscription.deleted
# invoice.paid
# invoice.payment_failed
```

---

## 🔮 FUTURE FEATURES & ROADMAP

### Immediate Priorities (Next 2 Weeks)

1. **Stripe Integration**
   - Checkout flow
   - Webhook handlers
   - Subscription management UI
   - Usage limit enforcement

2. **Free Tier Limits**
   - Daily counters (recommendations, chats, quick hits)
   - Warning messages at 80% usage
   - Upsell prompts at limit

3. **Email Automation**
   - Welcome series
   - Usage notifications
   - Subscription confirmations
   - Engagement campaigns

4. **Content Marketing Pipeline**
   - Automated video generation
   - Instagram Reels posting
   - TikTok alternative strategy
   - YouTube Shorts integration

### Short-Term (1-2 Months)

1. **Enhanced Personalization**
   - Watch history tracking
   - Improved recommendations based on past picks
   - Favorite streaming services

2. **Social Features**
   - Share recommendations
   - Friend lists
   - Watch together scheduling

3. **Advanced Filters**
   - Runtime preferences
   - Release year ranges
   - Certification/rating filters
   - Multiple streaming services

4. **Mr.DP Enhancements**
   - Voice interface
   - Proactive suggestions
   - Mood check-ins
   - Learning from user interactions

### Long-Term Vision (3-6 Months)

1. **Mobile Apps**
   - iOS native app
   - Android native app
   - Progressive Web App improvements

2. **Integrations**
   - Direct streaming links (deep linking)
   - Calendar integrations
   - Smart home integration (lights, routines)

3. **Community Features**
   - User reviews (ADHD-friendly format)
   - Lists and collections
   - Trending among neurodivergent users

4. **Analytics Dashboard**
   - Mood tracking over time
   - Content consumption patterns
   - Personalized insights

5. **Expansion**
   - More content types (books, games, events)
   - International markets
   - Additional languages

---

## 🎯 KEY SUCCESS METRICS

### User Engagement
- Daily active users (DAU)
- Recommendations per user per day
- Mr.DP chat sessions per user
- Quick Dope Hit usage rate
- Session duration

### Conversion Metrics
- Free → Premium conversion rate (target: 2-5%)
- Landing page → Signup (target: 15%)
- Trial → Paid (target: 40%)
- Churn rate (target: <5% monthly)

### Content Discovery
- Successful recommendation rate (user clicked through)
- Mood transition success (user found desired emotional state)
- Streaming service coverage
- Time to decision (target: <30 seconds)

### Technical Performance
- Page load time (target: <2 seconds)
- API response times
- Error rates
- Uptime (target: 99.9%)

---

## 🚨 CRITICAL REMINDERS FOR CLAUDE VS CODE

### When Working on This Project:

1. **ALWAYS READ THIS FILE FIRST** before making any code changes
2. **ASK BEFORE REFACTORING** - Johan needs control over architectural changes
3. **ONE CHANGE AT A TIME** - Wait for confirmation before proceeding
4. **PRESERVE EXISTING FEATURES** - Never remove functionality without explicit permission
5. **ADHD-AWARE COMMUNICATION** - Break complex explanations into steps
6. **TEST ASSUMPTIONS** - If unsure, ask Johan rather than assuming
7. **DOCUMENT CHANGES** - Keep clear commit messages
8. **RESPECT THE WORKFLOW** - Johan works with multiple AI assistants (you and ChatGPT)

### Johan's Working Style:
- Has extreme ADHD - cognitive load matters
- Prefers step-by-step guidance
- Values surgical fixes over sweeping changes
- Works on Mac (switched back from PC)
- Uses VS Code as primary editor
- GitHub repo: ZamoritaCR/neurostream-v1

### Common Pitfalls to Avoid:
- ❌ Suggesting "let's refactor this for clarity"
- ❌ Removing features to "simplify"
- ❌ Overwhelming with multiple options
- ❌ Making assumptions about what Johan wants
- ❌ Trying to "improve" working code unprompted

### Best Practices:
- ✅ Ask "what specifically should I fix?"
- ✅ Propose minimal changes to solve the exact problem
- ✅ Show before/after for any modification
- ✅ Explain WHY a change is needed
- ✅ Respect the existing architecture

---

## 📚 ADDITIONAL RESOURCES

### Research Papers Referenced
- "Retinal Dopamine Deficiency in ADHD" (Various, 2015-2024)
- "Typography for Dyslexia: The Lexend Font Family" (Google Fonts, 2021)
- "Variable Reward Schedules in ADHD Management" (Behavioral Psychology, 2020)
- "Sensory Processing in Neurodivergent Populations" (Multiple sources)

### Design Inspiration
- Notion (clean, minimal)
- Headspace (calming, friendly)
- Duolingo (gamification, rewards)
- Spotify (music discovery)

### Competitive Analysis
**No direct competitors** - dopamine.watch is unique in:
- Emotion-based filtering
- ADHD-specific optimization
- Decision paralysis solution
- Neuroscience-backed design

**Adjacent competitors**:
- JustWatch (aggregator, no emotion focus)
- Letterboxd (social, not ADHD-optimized)
- Reelgood (tracking, not mood-based)

---

## 🎨 BRAND ASSETS

### Mr.DP Character
- **Shape**: Round purple brain
- **Features**: Two antennae with sparkle effects
- **Expression**: Friendly, encouraging
- **Animations**: Gentle bounce, subtle glow
- **File**: `static/mr_dp_avatar.svg`

### Color Palette
```
Primary (Teal): #14B8A6
Secondary (Purple): #9D4EDD
Background: #1A1F2E
Surface: #2D3748
Text Primary: #F7FAFC
Text Secondary: #A0AEC0
Success: #10B981
Warning: #F59E0B
Error: #EF4444
```

### Typography
- **Primary**: Lexend (all weights)
- **Monospace**: JetBrains Mono (code blocks)
- **Base Size**: 16px
- **Scale**: 1.25 (major third)

---

## 📞 SUPPORT & FEEDBACK

### User Feedback Channels
- In-app feedback button
- Email: support@dopamine.watch
- Twitter: @dopaminewatch
- Discord community (planned)

### Common User Questions
1. "How does mood-based filtering work?"
2. "Which streaming services do you support?"
3. "Is my data private?"
4. "How do I cancel my subscription?"
5. "Can I suggest features?"

### Feature Requests (from users)
- Watchlist / Save for later
- Cross-platform sync
- Parental controls
- Group watching
- Offline mode

---

**END OF DOCUMENT**

*This file serves as the complete reference for dopamine.watch development. Update it whenever significant changes occur to architecture, features, or strategy.*

**Last Updated: January 30, 2026**
**Maintained by: Johan (with Claude assistance)**
**Version: 1.0**
