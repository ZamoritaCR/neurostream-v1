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
- Landing: https://www.dopamine.watch (GreenGeeks)
- Landing ES: https://www.dopamine.watch/index_es.html

### Core Purpose
Media as medicine for ADHD brains. Users tell the app how they feel NOW and how they WANT to feel, and the app finds content (movies, music, podcasts, audiobooks, shorts) to bridge that emotional gap. Built on 45+ years of ADHD and neuroscience research.

### Target Users
- Primary: Adults with ADHD experiencing decision fatigue
- Secondary: Neurodivergent individuals (autism, anxiety, depression)
- Pain point: Spending 45+ minutes scrolling unable to pick what to watch

---

## TECH STACK

### Frontend
- **Framework**: Streamlit (Python)
- **Styling**: Custom CSS with ADHD-optimized design (softer colors, larger touch targets)
- **Typography**: Inter font family
- **PWA**: Progressive Web App with service worker

### Backend
- **Database**: Supabase Pro (PostgreSQL)
- **Authentication**: Supabase Auth + Google OAuth
- **Edge Functions**: Supabase Edge Functions (Deno)
- **APIs**: TMDB, OpenAI (GPT-4), Stripe, Spotify

### Hosting & Deployment
- **Main App**: Railway (auto-deploys from GitHub main branch)
- **Landing Pages**: GreenGeeks (FTP upload)
- **Edge Functions**: Supabase
- **Version Control**: GitHub

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
├── index.html                   # English landing page
├── index_es.html                # Spanish landing page
├── privacy.html                 # Privacy policy
├── terms.html                   # Terms of service
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
```

### Key Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | ~10,000 | Main application - handle with extreme care |
| `mr_dp_intelligence.py` | ~800 | Mr.DP AI, gamification, behavioral tracking |
| `mr_dp_floating.py` | ~400 | Chat widget UI with SVG sanitization |
| `gamification_enhanced.py` | ~500 | Points, streaks, 30 achievements |
| `index.html` | ~2,400 | English landing with auth modals |

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

### Starting Development Server
```bash
cd /Users/zamorita/Desktop/Neuronav
streamlit run app.py
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

### Uploading Landing Pages to GreenGeeks
```bash
# Via curl/FTP
curl -T index.html ftp://ftp.pcmodderscr.com/MrRoboto/index.html \
  --user "MrRobotto@dopamine.watch:PASSWORD"

curl -T index_es.html ftp://ftp.pcmodderscr.com/MrRoboto/index_es.html \
  --user "MrRobotto@dopamine.watch:PASSWORD"
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
[tmdb]
api_key = "eyJ..."

[openai]
api_key = "sk-..."

[supabase]
url = "https://wkfewpynskakgbetscsa.supabase.co"
anon_key = "eyJ..."
service_role_key = "eyJ..."

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

### Supabase Edge Function Secrets
```bash
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
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

---

## DEPLOYMENT CHECKLIST

### Before Deploying
- [ ] Test locally with `streamlit run app.py`
- [ ] Check for console errors
- [ ] Verify all API keys are set
- [ ] Test critical flows (login, recommendations, Mr.DP)

### After Deploying
- [ ] Verify Railway deployment succeeded
- [ ] Test production app at app.dopamine.watch
- [ ] Check Railway logs for errors
- [ ] If landing pages changed, upload to GreenGeeks

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
| Run locally | `streamlit run app.py` |
| Deploy app | `git push origin main` |
| Upload landing | `curl -T index.html ftp://...` |
| Deploy function | `npx supabase functions deploy NAME` |
| View logs | Railway dashboard → Deployments |

| URL | Purpose |
|-----|---------|
| https://app.dopamine.watch | Main app |
| https://www.dopamine.watch | Landing page |
| https://app.supabase.com | Database dashboard |
| https://dashboard.stripe.com | Payments |
| https://railway.app | App hosting |

---

**Last Updated**: January 31, 2026
**Maintained By**: Johan (with Claude assistance)
**Version**: 2.0 (Phase 3 Complete)
