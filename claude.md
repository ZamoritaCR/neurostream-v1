# CLAUDE.md - Project Instructions for AI Assistants

> **Purpose**: This file tells Claude (and other AI assistants) how to work with this project effectively.
>
> **Location**: Project root directory

---

## PROJECT OVERVIEW

**Project Name**: dopamine.watch
**Description**: ADHD-friendly streaming recommendation app that helps neurodivergent users find content based on emotional state transitions
**Repository**: https://github.com/ZamoritaCR/neurostream-v1
**Live URLs**:
- App: https://app.dopamine.watch (Railway)
- Landing EN: https://www.dopamine.watch (GreenGeeks)
- Landing ES: https://www.dopamine.watch/index_es.html
- Blog: https://dopamine.watch/blog/
- RSS Feed: https://dopamine.watch/blog/feed.xml

### Core Purpose
Media as medicine for ADHD brains. Users tell the app how they feel NOW and how they WANT to feel, and the app finds content (movies, music, podcasts, audiobooks, shorts) to bridge that emotional gap. Built on 45+ years of ADHD and neuroscience research.

### Target Users
- Primary: Adults with ADHD experiencing decision fatigue
- Secondary: Neurodivergent individuals (autism, anxiety, depression)
- Pain point: Spending 45+ minutes scrolling unable to pick what to watch

---

## TECH STACK

### Current Production (Streamlit)
- **Framework**: Streamlit (Python)
- **Styling**: Custom CSS with ADHD-optimized design
- **Hosting**: Railway (auto-deploys from GitHub main branch)
- **URL**: https://app.dopamine.watch

### Next.js Rebuild (In Development)
- **Framework**: Next.js 14 (App Router) + TypeScript
- **Styling**: Tailwind CSS + Custom Design System
- **Animations**: Framer Motion
- **Icons**: Phosphor Icons (professional, no emojis)
- **Components**: Custom UI library (Button, Card, Modal, Toast, etc.)
- **Location**: `/Users/zamorita/Desktop/Neuronav/dopamine-next/`
- **Run**: `cd dopamine-next && npm run dev` → http://localhost:3000

### Backend (Shared)
- **Database**: Supabase Pro (PostgreSQL)
- **Authentication**: Supabase Auth + Google OAuth
- **Edge Functions**: Supabase Edge Functions (Deno)
- **APIs**: TMDB, OpenAI (GPT-4), Anthropic (Claude), Stripe, Spotify

### Hosting & Deployment
- **Streamlit App**: Railway (production)
- **Next.js App**: Local development (will deploy to Vercel)
- **Landing Pages & Blog**: GreenGeeks (FTP upload)
- **Edge Functions**: Supabase
- **Version Control**: GitHub

### Analytics
- **Google Analytics 4**: G-34Q0KMXDQF
- Installed on: Landing pages, Blog, Streamlit app, Next.js app

### Payments
- **Provider**: Stripe
- **Plans**: Free (5 Mr.DP chats/day) + Premium ($4.99/month unlimited)
- **Webhooks**: Supabase Edge Function for subscription lifecycle

---

## FILE STRUCTURE

```
project-root/
├── CLAUDE.md                    # This file - AI assistant instructions
├── app.py                       # Main Streamlit app (~10,000 lines)
├── requirements.txt             # Python dependencies
│
├── # Core Feature Modules
├── mr_dp_intelligence.py        # Mr.DP AI chatbot logic, gamification
├── mr_dp_floating.py            # Floating chat widget UI
├── mood_utils.py                # Mood logging and history
├── behavior_tracking.py         # User engagement tracking
├── watch_queue.py               # Save for later functionality
├── sos_calm_mode.py             # Crisis/calm mode features
├── time_aware_picks.py          # Time-of-day recommendations
├── focus_timer.py               # Pomodoro-style focus sessions
│
├── # Phase 3 Enhanced Features (dopamine_2027 integration)
├── gamification_enhanced.py     # Points, streaks, leaderboards, 30 achievements
├── user_learning.py             # Pattern detection, personalization
├── wellness_enhanced.py         # Breathing exercises, grounding, affirmations
├── search_aggregator.py         # Multi-platform search (TMDB, Spotify, YouTube)
├── social_features.py           # Watch parties, messaging, friends
│
├── # Monetization
├── subscription_utils.py        # Usage limits, premium checks
├── stripe_utils.py              # Pricing page, checkout URLs
├── analytics_utils.py           # User analytics
├── email_utils.py               # Welcome/milestone emails
│
├── # Landing Pages (deployed to GreenGeeks)
├── index.html                   # English landing page (with GA)
├── index_es.html                # Spanish landing page (with GA)
├── privacy.html                 # Privacy policy
├── terms.html                   # Terms of service
│
├── # Blog (deployed to GreenGeeks /blog/)
├── blog/
│   ├── index.html               # Blog home page
│   ├── feed.xml                 # RSS feed
│   ├── sitemap.xml              # Blog sitemap
│   ├── assets/
│   │   └── css/
│   │       └── blog.css         # Blog styles
│   ├── posts/
│   │   ├── adhd-decision-paralysis-science.html
│   │   ├── netflix-algorithm-not-built-for-adhd.html
│   │   └── shows-that-help-anxiety.html
│   └── categories/
│       ├── adhd.html
│       ├── streaming.html
│       └── psychology.html
│
├── # Content Bot (AI-powered content automation)
├── content-bot/
│   ├── .env                     # API keys (gitignored)
│   ├── .env.example             # Template for .env
│   ├── tools.py                 # 12 callable tools for Claude agent
│   ├── agent.py                 # Claude-powered conversational agent
│   ├── chat.py                  # Terminal chat interface
│   ├── social_media.py          # Social media posting (Twitter, LinkedIn, Facebook)
│   ├── analytics_dashboard.py   # Analytics tracking
│   ├── ab_testing.py            # A/B testing for headlines
│   ├── generate_rss.py          # RSS feed generator
│   ├── seo_audit.py             # SEO analysis tool
│   ├── monitor.py               # Site health monitoring
│   ├── LAUNCH_CHECKLIST.md      # Launch checklist
│   ├── templates/
│   │   └── newsletter_template.html
│   └── dashboard/
│       ├── api.py               # Flask API server (port 5001)
│       ├── index.html           # Dashboard UI
│       ├── web_chat.html        # Web chat interface
│       └── start.sh             # Server start script
│
├── # Supabase
├── supabase/
│   └── functions/
│       ├── mr-dp-chat/          # AI chat Edge Function
│       │   └── index.ts
│       └── stripe-webhook/      # Stripe webhook handler
│           └── index.ts
│
├── # Streamlit Config
├── .streamlit/
│   ├── config.toml              # Streamlit settings
│   └── secrets.toml             # API keys (gitignored)
│
└── static/                      # PWA assets, icons

# Next.js Rebuild (dopamine-next/)
dopamine-next/
├── package.json                 # Dependencies (Next.js 14, Tailwind, Framer Motion)
├── tailwind.config.ts           # Design system tokens
├── .env.local                   # Environment variables
├── src/
│   ├── app/
│   │   ├── page.tsx             # Landing page (hero, features, CTA)
│   │   ├── layout.tsx           # Root layout (GA, PWA meta)
│   │   ├── providers.tsx        # Auth + Toast providers
│   │   ├── globals.css          # Design system CSS
│   │   ├── login/page.tsx       # Auth (Google + email)
│   │   ├── auth/callback/route.ts # OAuth callback
│   │   └── (app)/               # App route group
│   │       ├── layout.tsx       # App layout with navigation
│   │       ├── home/page.tsx    # Dashboard with quick actions
│   │       ├── discover/page.tsx # Mood selector flow
│   │       ├── recommendations/ # Content grid with filters
│   │       ├── quick-hit/       # Instant recommendation
│   │       ├── chat/page.tsx    # Mr.DP chat (iMessage style)
│   │       └── profile/page.tsx # Stats, achievements, settings
│   ├── components/
│   │   ├── ui/                  # Button, Card, Input, Modal, Toast, Skeleton
│   │   ├── layout/Navigation.tsx # Mobile bottom tabs + desktop header
│   │   └── features/MoodSelector.tsx # Swipeable cards (mobile) + grid
│   ├── lib/
│   │   ├── utils.ts             # Helper functions, haptic feedback
│   │   ├── moods.ts             # 12 mood definitions
│   │   ├── supabase.ts          # Database functions
│   │   ├── auth-context.tsx     # Auth provider
│   │   └── tmdb.ts              # TMDB API client
│   └── types/index.ts           # TypeScript definitions
```

### Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | ~10,000 | Main application - handle with extreme care |
| `mr_dp_intelligence.py` | ~800 | Mr.DP AI, gamification, behavioral tracking |
| `mr_dp_floating.py` | ~400 | Chat widget UI with SVG sanitization |
| `gamification_enhanced.py` | ~500 | Points, streaks, 30 achievements |
| `index.html` | ~2,400 | English landing with auth modals + GA |
| `content-bot/agent.py` | ~200 | Claude-powered content agent |
| `content-bot/tools.py` | ~400 | 12 tools for content automation |

---

## CONTENT BOT SYSTEM

### Overview
AI-powered content automation system with Claude conversational agent for managing blog, social media, and SEO.

### Starting the Content Bot
```bash
cd /Users/zamorita/Desktop/Neuronav/content-bot/dashboard
python3 api.py
# Server runs on http://127.0.0.1:5001
```

### Interfaces
- **Dashboard**: http://127.0.0.1:5001/ - Visual dashboard
- **Web Chat**: http://127.0.0.1:5001/chat - ChatGPT-style interface
- **Terminal Chat**: `python3 chat.py` - CLI interface

### Available Tools (12 total)
1. `generate_blog_post` - Create SEO-optimized blog posts
2. `get_analytics` - View traffic and engagement stats
3. `check_site_health` - Monitor site status
4. `list_posts` - List all blog posts
5. `get_scheduler_status` - Check scheduled posts
6. `control_scheduler` - Start/stop scheduler
7. `generate_rss_feed` - Regenerate RSS feed
8. `run_seo_audit` - SEO analysis
9. `get_activity_log` - Recent activity
10. `get_system_status` - API connection status
11. `create_landing_pages` - Generate landing pages
12. `generate_topic_ideas` - AI topic suggestions

### Content Bot Environment Variables
Located in `content-bot/.env`:
```bash
# Required
OPENAI_API_KEY=sk-proj-...           # For content generation
ANTHROPIC_API_KEY=sk-ant-api03-...   # For Claude agent
FTP_HOST=ftp.pcmodderscr.com
FTP_USER=MrRobotto2@dopamine.watch
FTP_PASSWORD=ElroboT0b@!l@
FTP_PATH=/blog

# Optional - Social Media
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
LINKEDIN_TOKEN=
FACEBOOK_PAGE_TOKEN=

# Optional - Analytics
GA4_MEASUREMENT_ID=G-34Q0KMXDQF
```

---

## BLOG SYSTEM

### Structure
- **Home**: https://dopamine.watch/blog/
- **RSS**: https://dopamine.watch/blog/feed.xml
- **Categories**: ADHD, Streaming, Psychology

### Current Posts
1. "Why ADHD Makes Choosing Content Impossible (The Science)" - ADHD category
2. "The Netflix Algorithm Wasn't Built for Your Brain" - Streaming category
3. "10 Shows That Actually Help With Anxiety (Research-Backed)" - Psychology category

### Adding New Posts
1. Create HTML file in `blog/posts/`
2. Add Google Analytics snippet to `<head>`
3. Add post card to `blog/index.html`
4. Add post card to relevant category page
5. Update `blog/feed.xml` with new item
6. Upload all changed files via FTP

### Blog CSS Variables
```css
--primary: #8B7FD8;        /* Purple accent */
--primary-dark: #6B5FB8;
--text: #1a1a2e;
--text-light: #64748b;
--bg: #fafafa;
--card-bg: white;
```

---

## GOOGLE ANALYTICS

### Measurement ID
`G-34Q0KMXDQF`

### Installed On
- Landing pages (index.html, index_es.html)
- All blog pages (index, posts, categories)
- Streamlit app (app.py via inject_google_analytics())

### Code Snippet
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-34Q0KMXDQF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-34Q0KMXDQF');
</script>
```

### Streamlit Integration
GA is injected via `inject_google_analytics()` function right after `st.set_page_config()` in app.py.

---

## CRITICAL DEVELOPMENT RULES

### Rule #1: NO REFACTORING WITHOUT PERMISSION
**Why**: Developer has ADHD. Breaking changes cause significant setback.

- ✅ Fix specific bugs as requested
- ✅ Add new features surgically
- ✅ Preserve ALL existing functionality
- ❌ Don't "clean up" or "simplify" working code
- ❌ Don't remove features to "streamline"
- ❌ Don't refactor architecture unprompted

### Rule #2: STEP-BY-STEP APPROACH
**Why**: Developer has extreme ADHD and needs manageable chunks.

- ✅ One task at a time
- ✅ Wait for confirmation before proceeding
- ✅ Break complex changes into small steps
- ❌ No overwhelming info dumps
- ❌ No "here are 5 different approaches" - pick the best one

### Rule #3: ASK, DON'T ASSUME
- ✅ Ask clarifying questions if task is ambiguous
- ✅ Confirm approach before major changes
- ❌ Don't make assumptions about requirements

### Rule #4: PRESERVE CONTEXT
- ✅ Read this file before starting
- ✅ Reference existing code patterns
- ✅ Maintain coding style consistency

---

## COMMON TASKS

### Starting Streamlit App (Production)
```bash
cd /Users/zamorita/Desktop/Neuronav
streamlit run app.py
```

### Starting Next.js App (Development)
```bash
cd /Users/zamorita/Desktop/Neuronav/dopamine-next
npm run dev
# Opens at http://localhost:3000
```

### Building Next.js for Production
```bash
cd /Users/zamorita/Desktop/Neuronav/dopamine-next
npm run build
```

### Starting Content Bot
```bash
cd /Users/zamorita/Desktop/Neuronav/content-bot/dashboard
python3 api.py
# Open http://127.0.0.1:5001/chat
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Deploying to Railway
```bash
git add <files>
git commit -m "Description"
git push origin main
# Railway auto-deploys from main branch
```

### Uploading to GreenGeeks (FTP)
```bash
# Landing pages
curl -T index.html ftp://ftp.pcmodderscr.com/MrRoboto/index.html \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@"

curl -T index_es.html ftp://ftp.pcmodderscr.com/MrRoboto/index_es.html \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@"

# Blog files
curl -T blog/index.html ftp://ftp.pcmodderscr.com/MrRoboto/blog/index.html \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@" --ftp-create-dirs

curl -T blog/feed.xml ftp://ftp.pcmodderscr.com/MrRoboto/blog/feed.xml \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@"

# Blog posts
curl -T blog/posts/POST_NAME.html ftp://ftp.pcmodderscr.com/MrRoboto/blog/posts/POST_NAME.html \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@" --ftp-create-dirs

# Blog categories
curl -T blog/categories/CATEGORY.html ftp://ftp.pcmodderscr.com/MrRoboto/blog/categories/CATEGORY.html \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@" --ftp-create-dirs

# Blog CSS
curl -T blog/assets/css/blog.css ftp://ftp.pcmodderscr.com/MrRoboto/blog/assets/css/blog.css \
  --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@" --ftp-create-dirs
```

### Deploying Supabase Edge Functions
```bash
npx supabase login
npx supabase link --project-ref wkfewpynskakgbetscsa
npx supabase functions deploy stripe-webhook --no-verify-jwt
npx supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_xxx
```

---

## ENVIRONMENT VARIABLES

### Railway / .streamlit/secrets.toml
```toml
[supabase]
url = "https://wkfewpynskakgbetscsa.supabase.co"
anon_key = "eyJhbGci..."

[openai]
api_key = "sk-proj-..."

[tmdb]
api_key = "cdec2af78254e8aea1983848ebdb7b58"

[stripe]
publishable_key = "pk_live_..."
secret_key = "sk_live_..."
payment_link_monthly = "https://buy.stripe.com/..."
customer_portal = "https://billing.stripe.com/..."
webhook_secret = "whsec_..."

[spotify]
client_id = "..."
client_secret = "..."
```

### Content Bot / content-bot/.env
```bash
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
FTP_HOST=ftp.pcmodderscr.com
FTP_USER=MrRobotto2@dopamine.watch
FTP_PASSWORD=ElroboT0b@!l@
FTP_PATH=/blog
GA4_MEASUREMENT_ID=G-34Q0KMXDQF
```

### Next.js / dopamine-next/.env.local
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://wkfewpynskakgbetscsa.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...

# TMDB
NEXT_PUBLIC_TMDB_API_KEY=cdec2af78254e8aea1983848ebdb7b58

# Google Analytics
NEXT_PUBLIC_GA_ID=G-34Q0KMXDQF

# OpenAI (for Mr.DP)
OPENAI_API_KEY=sk-proj-...
```

### Supabase Edge Function Secrets
```bash
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
```

---

## FTP CREDENTIALS (GreenGeeks)

```
Host: ftp.pcmodderscr.com
User: MrRobotto2@dopamine.watch
Password: ElroboT0b@!l@
Path: /MrRoboto/
```

**Directory Structure on Server:**
```
/MrRoboto/
├── index.html          # Landing EN
├── index_es.html       # Landing ES
├── privacy.html
├── terms.html
├── favicon.ico
└── blog/
    ├── index.html
    ├── feed.xml
    ├── sitemap.xml
    ├── assets/css/blog.css
    ├── posts/
    │   ├── adhd-decision-paralysis-science.html
    │   ├── netflix-algorithm-not-built-for-adhd.html
    │   └── shows-that-help-anxiety.html
    └── categories/
        ├── adhd.html
        ├── streaming.html
        └── psychology.html
```

---

## DATABASE SCHEMA (Supabase)

### Core Tables
```sql
-- profiles (user data)
id UUID PRIMARY KEY
email TEXT
name TEXT
is_premium BOOLEAN DEFAULT false
premium_since TIMESTAMP
stripe_customer_id TEXT
subscription_id TEXT
mr_dp_uses INTEGER DEFAULT 0
last_mr_dp_reset DATE
created_at TIMESTAMP

-- mood_logs
id UUID PRIMARY KEY
user_id UUID REFERENCES profiles(id)
current_mood TEXT
target_mood TEXT
created_at TIMESTAMP

-- watch_queue
id UUID PRIMARY KEY
user_id UUID REFERENCES profiles(id)
content_id TEXT
content_type TEXT
title TEXT
added_at TIMESTAMP

-- user_achievements
id UUID PRIMARY KEY
user_id UUID REFERENCES profiles(id)
achievement_id TEXT
unlocked_at TIMESTAMP

-- user_points
id UUID PRIMARY KEY
user_id UUID REFERENCES profiles(id)
total_points INTEGER DEFAULT 0
level INTEGER DEFAULT 1
streak_days INTEGER DEFAULT 0
last_active DATE
```

---

## STRIPE INTEGRATION

### Payment Flow
1. User clicks "Go Premium" → opens premium modal
2. Modal shows Stripe Payment Link with `client_reference_id={user_id}`
3. User completes checkout on Stripe
4. Stripe redirects to `app.dopamine.watch?upgraded=true`
5. App detects `?upgraded=true` and updates session state
6. Webhook updates database for persistent premium status

### Webhook Events Handled
- `checkout.session.completed` → Set is_premium=true
- `customer.subscription.updated` → Update status based on subscription.status
- `customer.subscription.deleted` → Set is_premium=false

### Testing
- Use Stripe test mode keys for development
- Test card: 4242 4242 4242 4242, any future date, any CVC

---

## MR.DP CHATBOT

### Overview
Mr.DP is the AI assistant mascot - a friendly neuron character with expressions.

### Key Functions
- `chat_with_mr_dp()` - Main conversation handler
- `get_contextual_greeting()` - Time-aware greetings
- `detect_decision_fatigue()` - ADHD intervention triggers
- `sanitize_chat_content()` - Removes SVG leakage from responses

### Usage Limits
- Free: 5 chats per day (resets at midnight)
- Premium: Unlimited

### Expressions
happy, thinking, excited, listening, sad, love, surprised, wink, confused, cool, focused, sleeping

---

## CURRENT FEATURES

### Phase 1: Core
- Mood-based recommendations (12 moods)
- Quick Dope Hit (instant recommendation)
- Content tabs: Movies, Music, Podcasts, Audiobooks, Shorts
- Watch queue (save for later)
- SOS Calm Mode

### Phase 2: Engagement
- Mr.DP AI chatbot
- Gamification (XP, levels, achievements)
- Focus timer with break reminders
- Time-aware suggestions

### Phase 3: Growth (dopamine_2027)
- Enhanced gamification (30 achievements, leaderboards, streaks)
- User learning/personalization
- Wellness features (breathing, grounding, affirmations)
- Search aggregator (multi-platform)
- Social features (watch parties, messaging, friends)

### Phase 4: Content & SEO
- Blog with 3 categories (ADHD, Streaming, Psychology)
- RSS feed for syndication
- Content bot for automated publishing
- Google Analytics tracking
- SEO-optimized posts

### Monetization
- Free tier with limits
- Premium ($4.99/month) via Stripe
- Referral system

---

## DEBUGGING GUIDELINES

### Common Issues

**Issue**: Movies not loading
- Check TMDB API key in secrets
- Verify `media_type` handling in `_clean_results()`

**Issue**: Mr.DP chat shows SVG content
- `sanitize_chat_content()` in mr_dp_floating.py handles this
- Check for new SVG patterns leaking

**Issue**: Premium not persisting after checkout
- Verify webhook is deployed and receiving events
- Check Supabase profiles table for `is_premium` column
- Ensure `client_reference_id` is being passed to Stripe

**Issue**: Session state errors
- Always check `if 'key' not in st.session_state` before access
- Initialize all keys in the session state initialization block

**Issue**: Content bot can't generate posts
- Check OpenAI API key in content-bot/.env
- Verify OPENAI_API_KEY is not empty
- Restart API server after adding key

**Issue**: Blog pages not updating
- FTP upload may have failed - check curl output
- Verify file exists on server
- Clear browser cache

**Issue**: Google Analytics not tracking
- Check GA4 measurement ID is correct (G-34Q0KMXDQF)
- Verify script is in `<head>` section
- Check browser console for blocked scripts

---

## DEPLOYMENT CHECKLIST

### Before Deploying App
- [ ] Test locally with `streamlit run app.py`
- [ ] Check for console errors
- [ ] Verify all API keys are set
- [ ] Test critical flows (login, recommendations, Mr.DP)

### After Deploying App
- [ ] Verify Railway deployment succeeded
- [ ] Test production app at app.dopamine.watch
- [ ] Check Railway logs for errors

### Deploying Landing/Blog to GreenGeeks
- [ ] Upload changed HTML files via FTP
- [ ] Verify Google Analytics is in each file
- [ ] Test pages load correctly
- [ ] Check mobile responsiveness
- [ ] Verify RSS feed validates (feed.xml)

---

## RED FLAGS - STOP AND ASK

Stop and confirm with developer if you're about to:
- Delete any existing code
- Change session state structure
- Modify database schema
- Add new dependencies
- Refactor more than 20 lines
- Remove or rename functions
- Change UI layout significantly
- Modify FTP credentials
- Change API keys

---

## COMMIT MESSAGE FORMAT

```
Brief description of change

- Specific change 1
- Specific change 2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

---

## QUICK REFERENCE

| Action | Command |
|--------|---------|
| Run Streamlit locally | `streamlit run app.py` |
| Run Next.js locally | `cd dopamine-next && npm run dev` |
| Build Next.js | `cd dopamine-next && npm run build` |
| Run content bot | `cd content-bot/dashboard && python3 api.py` |
| Deploy Streamlit | `git push origin main` |
| Upload landing | `curl -T index.html ftp://ftp.pcmodderscr.com/MrRoboto/index.html --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@"` |
| Upload blog post | `curl -T blog/posts/FILE.html ftp://ftp.pcmodderscr.com/MrRoboto/blog/posts/FILE.html --user "MrRobotto2@dopamine.watch:ElroboT0b@!l@" --ftp-create-dirs` |
| Deploy function | `npx supabase functions deploy NAME` |
| View logs | Railway dashboard → Deployments |

| URL | Purpose |
|-----|---------|
| https://app.dopamine.watch | Production app (Streamlit) |
| http://localhost:3000 | Next.js dev server |
| https://www.dopamine.watch | Landing page |
| https://dopamine.watch/blog/ | Blog |
| https://dopamine.watch/blog/feed.xml | RSS Feed |
| http://127.0.0.1:5001/chat | Content bot chat (local) |
| https://app.supabase.com | Database dashboard |
| https://dashboard.stripe.com | Payments |
| https://analytics.google.com | Google Analytics |
| https://railway.app | App hosting |

---

## API KEYS REFERENCE

| Service | Location | Purpose |
|---------|----------|---------|
| OpenAI | .streamlit/secrets.toml, content-bot/.env | GPT-4 for Mr.DP and content generation |
| Anthropic | content-bot/.env | Claude for content bot agent |
| TMDB | .streamlit/secrets.toml | Movie/TV data |
| Supabase | .streamlit/secrets.toml | Database and auth |
| Stripe | .streamlit/secrets.toml | Payments |
| Spotify | .streamlit/secrets.toml | Music recommendations |
| Google Analytics | Hardcoded in HTML/app.py | Traffic analytics |

---

**Last Updated**: January 31, 2026
**Maintained By**: Johan (with Claude assistance)
**Version**: 4.0 (Phase 5: Next.js Rebuild)
