# MASTER_BRAIN.md - dopamine.* Ecosystem Documentation

> **Purpose**: Universal instructions for AI assistants across ALL dopamine.* projects
> **Location**: ~/Desktop/Neuronav/MASTER_BRAIN.md
> **Philosophy**: This file only GROWS, never shrinks
> **Last Updated**: 2026-02-14 (Platform Launch Day)

---

## CURRENT PROJECT: UNIFIED PLATFORM

**Status:** Production-ready, deploying tonight
**Repository:** TBD (will be on GitHub)
**Directory:** ~/Desktop/Neuronav/platform
**Deploy Target:** Vercel -> www.dopamine.watch

---

## PROJECT STRUCTURE

```
~/Desktop/Neuronav/
├── MASTER_BRAIN.md              # <- THIS FILE (universal brain)
├── CLAUDE.md                    # Project instructions for AI assistants
│
├── platform/                    # Main Next.js unified platform
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                 # Landing page
│   │   │   ├── layout.tsx               # Root layout (Lexend font, AuthProvider)
│   │   │   ├── globals.css              # Tailwind v4 theme + ADHD colors
│   │   │   ├── auth/page.tsx            # Authentication (sign in/up)
│   │   │   ├── watch/page.tsx           # Recommendation engine (mood -> content)
│   │   │   ├── chat/page.tsx            # Real-time messaging
│   │   │   ├── blog/
│   │   │   │   ├── page.tsx             # Blog index
│   │   │   │   └── [slug]/page.tsx      # Dynamic blog posts (SSG)
│   │   │   └── api/
│   │   │       ├── mr-dp/route.ts       # Mr.DP AI chatbot (Anthropic Claude)
│   │   │       └── recommendations/route.ts  # AI recommendations (OpenAI)
│   │   ├── components/
│   │   │   ├── app/
│   │   │   │   ├── MoodSelector.tsx     # 8-mood emotion picker
│   │   │   │   └── MrDPChat.tsx         # Floating chat widget
│   │   │   ├── chat/
│   │   │   │   ├── chat-view.tsx        # Main 3-column chat layout
│   │   │   │   ├── server-sidebar.tsx   # Server list
│   │   │   │   ├── channel-sidebar.tsx  # Channel list + header
│   │   │   │   ├── message-list.tsx     # Virtualized message rendering
│   │   │   │   ├── message-input.tsx    # Compose + send
│   │   │   │   ├── member-list.tsx      # Online members
│   │   │   │   ├── presence-selector.tsx # ADHD presence states
│   │   │   │   ├── quick-switcher.tsx   # Cmd+K switcher
│   │   │   │   └── shortcuts-modal.tsx  # Keyboard shortcuts help
│   │   │   └── shared/
│   │   │       └── AuthProvider.tsx     # React Context auth wrapper
│   │   ├── hooks/
│   │   │   └── use-keyboard-shortcuts.ts
│   │   ├── lib/
│   │   │   ├── supabase/
│   │   │   │   ├── client.ts            # Browser-side Supabase client
│   │   │   │   ├── server.ts            # Server-side (async cookies, getAll/setAll)
│   │   │   │   └── helpers.ts           # ensureUserInDefaultServer()
│   │   │   ├── tmdb/
│   │   │   │   └── client.ts            # TMDB API wrapper (search, discover, posters)
│   │   │   └── ai/
│   │   │       └── recommendations.ts   # Type definitions
│   │   ├── stores/
│   │   │   ├── chat-store.ts            # Zustand: messages, realtime subscriptions
│   │   │   ├── presence-store.ts        # Zustand: ADHD presence states
│   │   │   └── server-store.ts          # Zustand: servers, channels, members
│   │   └── types/
│   │       └── database.ts              # TypeScript interfaces
│   ├── src/content/posts/               # Future markdown blog posts
│   ├── .env.local                       # All API keys (gitignored)
│   ├── package.json                     # Next.js 16.1.6, React 19.2.3
│   └── postcss.config.mjs              # Tailwind v4 via @tailwindcss/postcss
│
├── docs/
│   └── brains/                  # Research knowledge base (425+ citations)
│       ├── 00_MASTER_INDEX.md
│       ├── BRAIN_01_ADHD_DEEP_RESEARCH.md
│       ├── BRAIN_02_PSYCHOLOGICAL_RESEARCH.md
│       ├── BRAIN_03_ADD_RESEARCH.md
│       ├── BRAIN_04_UX_ACCESSIBILITY.md
│       ├── BRAIN_05_GAMIFICATION_RESEARCH.md
│       ├── BRAIN_06_DBT_CBT.md
│       ├── BRAIN_07_MONETIZATION.md
│       └── BRAIN_08_TECHNICAL.md
│
├── dopamine-next/               # Previous Next.js rebuild (reference only)
├── reference/                   # Archive of old projects
│   ├── dopamine-streamlit/      # Original Streamlit app
│   └── focus-chat/              # Original standalone chat
│
├── app.py                       # Original Streamlit app (~10,000 lines)
├── index.html                   # English landing page (GreenGeeks)
├── index_es.html                # Spanish landing page
└── blog/                        # Existing blog content
```

---

## TECH STACK (PLATFORM)

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 16.1.6 |
| Language | TypeScript | 5.x |
| UI Library | React | 19.2.3 |
| Styling | Tailwind CSS | v4 (@theme inline) |
| Font | Lexend (via next/font/google) | - |
| State | Zustand | 5.0.11 |
| Database | Supabase (PostgreSQL) | - |
| Auth | Supabase Auth (@supabase/ssr) | 0.8+ |
| Realtime | Supabase Realtime | - |
| AI (Mr.DP) | Anthropic Claude Sonnet 4 | claude-sonnet-4-20250514 |
| AI (Recs) | OpenAI GPT-4o-mini | gpt-4o-mini |
| Content API | TMDB | v3 |
| Virtual Lists | @tanstack/react-virtual | - |
| Icons | Lucide React | - |
| Utilities | clsx, tailwind-merge, date-fns, cmdk | - |

---

## CREDENTIALS (PRODUCTION)

### Supabase (Unified Database)

```
Project: dopamine.watch (wkfewpynskakgbetscsa)
URL: https://wkfewpynskakgbetscsa.supabase.co
Dashboard: https://supabase.com/dashboard/project/wkfewpynskakgbetscsa

Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrZmV3cHluc2tha2diZXRzY3NhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5MDcwMTAsImV4cCI6MjA4MzQ4MzAxMH0.DXnSsvabfwfNZIJaP0UR39YQe_3CHW-RjL2o1vDsunQ

Service Role Key: [STORED IN .env.local - NEVER COMMIT]
```

**Database:** Unified for entire ecosystem
- dopamine.watch tables
- chat tables (servers, channels, messages)
- Shared profiles table
- Single sign-on across all apps

### Anthropic (Mr.DP Chatbot)

```
API Key: [STORED IN .env.local]
Model: claude-sonnet-4-20250514
Usage: Mr.DP personality, emotional support
Max tokens: 150 (keeps responses ADHD-friendly short)
Temperature: 0.8
```

### TMDB (Content Discovery)

```
API Key: [STORED IN .env.local as NEXT_PUBLIC_TMDB_API_KEY]
Usage: Movie/TV show search, posters, mood-based discovery
```

### OpenAI (Recommendations)

```
API Key: [STORED IN .env.local]
Model: gpt-4o-mini
Usage: AI-powered content recommendations (mood -> titles)
```

### Daily.co (Voice Rooms - Not Active)

```
Status: Requires payment method - currently placeholder
Workaround: "Voice channels coming soon" placeholder in chat-view.tsx
```

### GitHub

```
Username: ZamoritaCR
Repos: TBD (will create tonight)
```

### Vercel (Deployment)

```
Project: TBD
Domain: www.dopamine.watch
```

---

## WHAT WORKS (AS OF 2026-02-14)

**Landing Page (/):**
- Hero with gradient logo
- Feature grid (content discovery, chat, meal planning, smart home)
- Footer with Blog, About, GitHub links
- Lexend font, ADHD-optimized dark theme
- Responsive design

**Authentication (/auth):**
- Email/password signup
- Email/password login
- Supabase Auth integration via @supabase/ssr
- Protected routes (redirect to /auth if not logged in)
- Sign out functionality

**Content Discovery (/watch):**
- 3-step mood flow: current mood -> target mood -> results
- 8 mood options (anxious, happy, sad, bored, energized, tired, stressed, calm)
- AI recommendations via OpenAI GPT-4o-mini (server-side API route)
- TMDB integration for poster images and metadata
- Fallback to mood-based TMDB discovery if AI sparse
- Emotional bridge concept (feel-first, not algorithm-first)

**Real-Time Chat (/chat):**
- Server/channel structure (Discord-like)
- Real-time messaging via Supabase Realtime
- ADHD presence states (Hyperfocus, High Energy, Low Bandwidth, Task Mode)
- Channel switching
- Message history with optimistic updates
- Virtualized message rendering (@tanstack/react-virtual)
- Keyboard shortcuts (Cmd+K switcher, Cmd+/ help)

**Mr.DP Chatbot (floating on /watch and /chat):**
- Floating purple gradient button (bottom-right)
- Conversational AI powered by Claude Sonnet 4
- Empathetic, ADHD-friendly personality
- Context awareness (current mood, target mood, activity)
- 12 expression states with emoji avatars
- Brief responses (2-3 sentences max)
- Never uses guilt or shame

**Blog (/blog):**
- Blog index page with post cards
- Dynamic post routes with SSG (generateStaticParams)
- 2 launch posts: "Introducing dopamine.watch" + "Why Privacy Matters"
- Tag system
- Responsive layout
- Markdown-style content rendering

---

## KNOWN ISSUES

**Voice Rooms:**
- Daily.co requires payment method on file
- Currently shows "Voice channels coming soon" placeholder
- Options: Add payment, remove feature, or switch provider

**Auto-Join Server:**
- New users don't auto-join default server
- Workaround: Manual SQL or update trigger in Supabase

**Email Confirmation:**
- Disabled for MVP speed
- Should enable before public launch

**Blog Content Rendering:**
- Simple line-by-line parser (not full markdown)
- Works for current content structure
- Could upgrade to MDX or remark/rehype later

---

## ARCHITECTURE DECISIONS

### Why One Supabase Project?

**Decision:** Use single Supabase project (wkfewpynskakgbetscsa) for entire ecosystem

**Reasoning:**
- Single sign-on across all apps
- Shared user profiles
- Integrated data for cross-platform features
- Stay in free tier (2 projects max)
- One database to manage

**Trade-offs:**
- All apps share same database (coupling)
- RLS policies more complex
- But: Benefits outweigh costs for MVP

### Why Next.js 16?

**Decision:** Migrate from Streamlit (Python) to Next.js (TypeScript)

**Reasoning:**
- Better performance (SSR, SSG, caching)
- Easier deployment (Vercel)
- Modern tech stack with TypeScript
- Real-time features via Supabase Realtime
- Better mobile experience
- Unified codebase for web/mobile

**Key Adaptations (from older templates):**
- Tailwind v4: Uses `@theme inline` in CSS, NOT tailwind.config.ts
- Next.js 15+: `cookies()` must be `await`ed in server components
- Next.js 15+: `params` in dynamic routes is a Promise, must be `await`ed
- @supabase/ssr: Uses `getAll/setAll` cookie pattern, NOT deprecated get/set/remove
- React 19: No issues with current codebase

### Why Anthropic for Mr.DP?

**Decision:** Use Claude Sonnet 4 instead of GPT-4 for chatbot

**Reasoning:**
- Better at following "brief response" instructions
- More natural empathetic tone
- Stronger adherence to personality constraints
- Cost-effective for short responses
- Alignment with Anthropic values

### Why OpenAI for Recommendations?

**Decision:** Use GPT-4o-mini for content recommendation generation

**Reasoning:**
- Good at structured JSON output
- Fast response time for recommendation lists
- Cost-effective for batch title generation
- Separate from Mr.DP to avoid mixing concerns

---

## DESIGN SYSTEM

### Colors (ADHD-Optimized, Tailwind v4)

```css
/* Defined in globals.css via @theme inline */
--color-primary: #667EEA;        /* Calming purple */
--color-primary-hover: #5A67D8;
--color-secondary: #7CB98F;      /* Soothing green */
--color-secondary-hover: #6BA580;
--color-accent: #4ecdc4;         /* Gentle teal */
--color-background: #0f0f1a;    /* Dark, not pure black */
--color-foreground: #e0e0ec;    /* Soft white */
--color-surface: #1a1a2e;
--color-surface-hover: #222240;
--color-border: #2a2a45;
--color-muted: #7a7a95;
```

**Principles:**
- No harsh reds (use #C97B7B if needed)
- Softened, calming palette
- High contrast for readability
- Research: Brain 4, Section 6 - Blue/green calming effects

### Typography

```css
font-family: 'Lexend', sans-serif;  /* via next/font/google */
font-size: 16px minimum;
line-height: 1.6;
letter-spacing: 0.01em;
```

**Why Lexend:** Bonnie Shaver-Troup study - reduces visual stress, improves reading fluency
**Research:** Brain 4, Section 5

### Accessibility

- 44x44px minimum touch targets (Brain 4, Section 6)
- `prefers-reduced-motion` support in globals.css
- Keyboard navigation (Cmd+K, Cmd+/)
- Clear focus indicators
- ARIA labels on interactive elements

---

## CRITICAL DEVELOPMENT RULES

### Rule #1: NO REFACTORING WITHOUT PERMISSION
- Developer has extreme ADHD
- Breaking changes cause major setbacks
- Fix bugs surgically, don't rewrite

### Rule #2: STEP-BY-STEP APPROACH
- One task at a time
- Wait for confirmation before proceeding
- Break complex changes into digestible chunks

### Rule #3: VERIFY, DON'T HALLUCINATE
- Check files exist before editing
- Test code with `npm run build`
- Read actual content before modifying
- When uncertain, ask

### Rule #4: EMPATHY-FIRST COMMUNICATION
- Warm, natural tone (not robotic)
- Validate feelings before offering solutions
- Build relationships across sessions

### Rule #5: HARM PREVENTION
- No guilt-inducing features
- No shame mechanics
- No addictive dark patterns
- Celebrate attempts, not just success
- Research: Brain 5, Section 7 (prohibited patterns)

---

## DEPLOYMENT ARCHITECTURE

### Current State (2026-02-14 Evening)

```
Railway -------- app.dopamine.watch ---- Streamlit (Python) BACKUP
GreenGeeks ----- www.dopamine.watch ---- Static landing pages (EN/ES)
Vercel --------- [PENDING] ------------- Next.js Platform (NEW)
Supabase ------- Backend --------------- Shared Database
```

### Post-Launch State (Goal)

```
Vercel --------- www.dopamine.watch ---- Main hub + all apps
                 ├── / ──────────────── Landing page
                 ├── /watch ─────────── Recommendations
                 ├── /chat ──────────── Real-time messaging
                 ├── /blog ──────────── Content/updates
                 └── /auth ──────────── Authentication

Supabase ------- wkfewpynskakgbetscsa -- Unified database

Railway -------- app.dopamine.watch ---- [SUNSET in 2-4 weeks]
GreenGeeks ----- [REDIRECT to Vercel] -- [SUNSET after DNS switch]
```

---

## CHANGELOG

### 2026-02-14 - Platform Launch Day

**Session Duration:** 6+ hours
**Developer:** Johan
**AI Assistants:** Claude Opus 4.6 (Claude Code CLI)

**Built:**
- Next.js 16.1.6 platform from scratch
- Landing page with ecosystem overview
- Authentication (Supabase + @supabase/ssr)
- Content recommendation engine (TMDB + OpenAI)
- Real-time chat (Supabase Realtime + Zustand)
- Mr.DP chatbot (Anthropic Claude Sonnet 4)
- Blog with 2 launch posts (SSG)
- ADHD-optimized design system (Tailwind v4)

**Migrated:**
- Chat system from standalone app (reference/focus-chat)
- Core recommendation logic from Streamlit

**Key Adaptations:**
- Tailwind v3 templates -> v4 @theme inline format
- @supabase/auth-helpers-nextjs -> @supabase/ssr (getAll/setAll)
- Synchronous cookies() -> async await (Next.js 15+)
- Client-side OpenAI import -> server-side API route (security)
- params as object -> params as Promise (Next.js 15+)
- VoiceRoom/Daily.co -> placeholder (payment required)

**Statistics:**
- Files created: 31 TypeScript/TSX files
- Components: 15+
- API routes: 2 (mr-dp, recommendations)
- Blog posts: 2
- Build: Zero TypeScript errors across all phases

**Phases Completed:**
- Phase 1A: Initialize Next.js project + dependencies
- Phase 1B: Landing page + Tailwind v4 design system
- Phase 1C: Supabase Auth + protected routes
- Phase 1D: Chat migration from focus-chat reference
- Phase 1E: TMDB + AI recommendation engine
- Phase 1F: Mr.DP chatbot with Anthropic Claude
- Phase 1G: Blog structure + 2 launch posts
- Phase 1H: This documentation (MASTER_BRAIN.md)

**Next Steps:**
- [ ] Deploy to Vercel (Phase 1I)
- [ ] Configure DNS (www.dopamine.watch)
- [ ] Test in production
- [ ] Enable email confirmation
- [ ] Monitor for errors

---

## NEXT SESSION PRIORITIES

### Immediate (Tonight)
1. Deploy to Vercel
2. Configure DNS
3. Smoke test production
4. Fix any deployment issues

### Short-Term (This Week)
1. Enable email confirmation
2. Add more blog posts
3. Fix auto-server-join trigger
4. Decide on voice rooms (fix or remove)
5. Add user profile pages
6. Implement points/streak display

### Medium-Term (Next 2 Weeks)
1. Migrate remaining Streamlit features
2. Add watch queue (save for later)
3. Implement full gamification (Brain 5)
4. Add SOS/calm mode (Brain 6)
5. Build analytics dashboard
6. Stripe integration (Brain 7)

### Long-Term (Month 1-2)
1. Mobile app (The Cockpit)
2. food.dopamine.watch (meal planning)
3. home.dopamine.watch (smart home)
4. Full feature parity with Streamlit
5. Sunset Railway deployment
6. Sunset GreenGeeks landing pages

---

## HOW TO USE THIS FILE

### At START of Session (Claude CLI or Web)

```bash
cd ~/Desktop/Neuronav
head -100 MASTER_BRAIN.md
```

Then:
- Review current status
- Check next priorities
- Verify credentials if needed

### At END of Session (Update Changelog)

Add to CHANGELOG section:
```
### [DATE] - [SESSION TITLE]
**Duration:** X hours
**Changes:**
- Change 1
- Change 2
**Next:**
- [ ] Todo 1
- [ ] Todo 2
```

### Running the Platform

```bash
cd ~/Desktop/Neuronav/platform
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Production build (verify zero errors)
```

---

## RESEARCH FOUNDATION

### Knowledge Base Location
```
~/Desktop/Neuronav/docs/brains/
```

### Quick Reference

| Working On... | Read This Brain |
|---------------|----------------|
| Any UI/UX changes | Brain 4 (UX/Accessibility) |
| Mood selection, emotions | Brain 2 (Psychological) + Brain 6 (DBT/CBT) |
| Mr.DP chatbot | Brain 1 (ADHD Deep) + Brain 6 (DBT/CBT) |
| Points, streaks | Brain 5 (Gamification) |
| Crisis/SOS mode | Brain 6 (DBT/CBT) - TIPP, STOP skills |
| Inattentive-type support | Brain 3 (ADD Research) |
| Pricing, premium | Brain 7 (Monetization) |
| Architecture | Brain 8 (Technical) |

### The Feel-First Paradigm

```
[Current State] ---- Content Prescription ----> [Desired State]

ANXIOUS ----------- Cozy comfort show ----------> CALM
BORED ------------- High-energy documentary ----> ENERGIZED
SAD --------------- Gentle comedy --------------> LIGHTER
OVERWHELMED ------- Lo-fi music + nature -------> GROUNDED
RESTLESS ---------- Action movie ---------------> FOCUSED
NUMB -------------- Emotional drama ------------> CONNECTED
```

This is MEDIA AS MEDICINE, not media as entertainment.

---

## TROUBLESHOOTING

### App Won't Start

```bash
cd ~/Desktop/Neuronav/platform
rm -rf .next
rm -rf node_modules
npm install
npm run dev
```

### Database Connection Issues

```bash
# Check .env.local has Supabase keys
grep SUPABASE platform/.env.local

# Test connection
curl https://wkfewpynskakgbetscsa.supabase.co
```

### Mr.DP Not Responding

```bash
# Check Anthropic key exists
grep ANTHROPIC platform/.env.local

# Test API route
curl http://localhost:3000/api/mr-dp \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hi"}]}'
```

### Build Errors

```bash
cd ~/Desktop/Neuronav/platform
npm run build 2>&1 | head -50
# Fix any TypeScript errors shown
```

### Chat Not Real-Time

- Check Supabase Realtime is enabled in dashboard
- Verify RLS policies allow SELECT/INSERT
- Check browser console for WebSocket errors

---

## TIPS FOR FUTURE SESSIONS

**ADHD-Friendly Workflow:**
1. One task at a time
2. Short, focused sessions
3. Celebrate progress
4. Take breaks
5. Done > perfect

**Working with Claude CLI:**
1. Always start by reading this file
2. Verify current state with `npm run build`
3. Work in phases (1A, 1B, etc.)
4. Test after each phase
5. Update this file at session end

**Working with Web Claude:**
1. Reference this file for context
2. Ask for verification commands
3. Paste outputs for review
4. Get phase-by-phase prompts

---

**Last Updated:** 2026-02-14
**Maintained By:** Johan (with Claude assistance)
**Version:** 1.0 (Platform Launch)
**Status:** PRODUCTION-READY
