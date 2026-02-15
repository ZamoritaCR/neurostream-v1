# CLAUDE.md - Project Instructions for AI Assistants

> **Purpose**: This file tells Claude (and other AI assistants) how to work with this project effectively.
>
> **Location**: Project root directory
>
> **Medical Audit Notice**: This project will undergo medical/clinical review. ALL design decisions must be traceable to research documentation in `/docs/brains/`. When implementing features, cite the relevant brain and section.

---

## 🎯 THE FEEL-FIRST PARADIGM (CORE PHILOSOPHY)

### This Is NOT Another Recommendation Algorithm

**Traditional Apps (Netflix, Spotify, YouTube):**
```
"Because you watched Breaking Bad → Here's Better Call Saul"
"Users who liked X also liked Y"
"Based on your viewing history..."
```
This is **behavioral/algorithmic** - it tracks what you DO, not how you FEEL.

**dopamine.watch (Feel-First):**
```
"You feel ANXIOUS and want to feel CALM → Here's content that bridges that emotional gap"
"You feel BORED and want to feel ENERGIZED → Here's your dopamine medicine"
"You feel OVERWHELMED and need to DECOMPRESS → Here's your soft landing"
```
This is **emotional/therapeutic** - it treats content as medicine for emotional states.

### Why This Matters for ADHD Brains

**The Problem (Brain 1, Section 3):**
- ADHD brains have dysregulated dopamine systems
- Decision fatigue is REAL - 45+ minutes scrolling, unable to choose
- Algorithmic recommendations create MORE overwhelm, not less
- "Because you watched..." doesn't account for emotional state RIGHT NOW

**The Solution:**
- Ask: "How do you feel NOW?" + "How do you WANT to feel?"
- Map the emotional journey needed
- Prescribe content that creates that specific emotional transition
- This is MEDIA AS MEDICINE, not media as entertainment

### The Emotional Bridge Model

```
[Current State] ──── Content Prescription ────> [Desired State]

ANXIOUS ────────── Cozy comfort show ──────────> CALM
BORED ─────────── High-energy documentary ────> ENERGIZED  
SAD ───────────── Gentle comedy ──────────────> LIGHTER
OVERWHELMED ───── Lo-fi music + nature ───────> GROUNDED
RESTLESS ──────── Action movie ───────────────> FOCUSED
NUMB ──────────── Emotional drama ────────────> CONNECTED
```

### AI Behavior Requirements

**1. LEARN FROM EVERY SESSION**
```python
# WRONG - Static responses
def get_recommendation(mood):
    return generic_list[mood]

# RIGHT - Session learning
def get_recommendation(user, current_mood, target_mood, session_context):
    # What worked for THIS user before?
    # What's their emotional pattern TODAY?
    # What time is it? (Brain 4 - time-aware)
    # How intense is their current state?
    # Build on the conversation we're having RIGHT NOW
```

The AI must remember and build upon:
- What user shared earlier in THIS session
- Emotional patterns from past sessions
- What content actually helped (feedback loop)
- Personal preferences that emerge through conversation
- Context clues (time of day, day of week, recent events mentioned)

**2. NATURAL PERSONALIZATION**
```python
# WRONG - Robotic
"Hello, User. Please select your current emotional state."

# RIGHT - Natural, warm, personal
"Hey Sarah! 💜 How are you feeling right now?"
"Johan! Good to see you. Rough day or just need something good to watch?"
"Welcome back, Alex. Last time that documentary really helped - want something similar or totally different vibe today?"
```

**3. FEEL, DON'T ANALYZE**
```python
# WRONG - Clinical
"Based on your selection of 'anxious', I recommend the following content categorized as 'calming'..."

# RIGHT - Empathetic
"Anxiety is rough. Let's find you something that feels like a warm blanket for your brain. How about..."
```

**4. THE CONVERSATION IS THE EXPERIENCE**
- Don't rush to recommendations
- Validate the feeling first
- Ask gentle follow-up questions
- Make the user feel HEARD before offering solutions
- The interaction itself should be calming, not another source of decision fatigue

### Session Learning Protocol

Every session, the AI should:

1. **Greet by name** - warmly, naturally, like a friend
2. **Remember context** - "Last time you mentioned work was stressful..."
3. **Check in on previous recommendations** - "Did that show help?"
4. **Notice patterns** - "I've noticed you often feel anxious on Sunday nights..."
5. **Adapt language** - Match the user's energy and communication style
6. **Build the relationship** - This isn't a transaction, it's ongoing support

### What Success Looks Like

**User thinks:** "This app actually GETS me"
**User feels:** Understood, supported, less alone
**User experiences:** Relief from decision fatigue, content that actually helps
**User returns:** Because it WORKS, not because of dark patterns

### Anti-Patterns to Avoid

| ❌ DON'T | ✅ DO |
|----------|-------|
| "Based on your viewing history..." | "How are you feeling right now?" |
| Generic mood picker with no follow-up | Conversational exploration of emotional state |
| Same recommendations for everyone feeling "sad" | Personalized based on THIS user's patterns |
| Treat sessions as isolated transactions | Build cumulative understanding across sessions |
| Clinical, robotic language | Warm, human, friend-like tone |
| Rush to content delivery | Take time to understand and validate |

---

## 🧠 RESEARCH KNOWLEDGE BASE (CRITICAL - READ FIRST)

### Overview
This project is built on 425+ peer-reviewed citations across 8 research "brains." These documents are the authoritative source for ALL design decisions. For medical audit compliance, every UX choice, therapeutic technique, and gamification mechanic must trace back to this research.

### Brain Files Location
```
docs/brains/
├── 00_MASTER_INDEX.md           # Start here - overview of all brains
├── BRAIN_01_ADHD_DEEP_RESEARCH.md    # ADHD neurology, symptoms, statistics
├── BRAIN_02_PSYCHOLOGICAL_RESEARCH.md # Emotion regulation frameworks
├── BRAIN_03_ADD_RESEARCH.md          # ADHD-PI/Inattentive specifics
├── BRAIN_04_UX_ACCESSIBILITY.md      # ADHD-optimized interface design
├── BRAIN_05_GAMIFICATION_RESEARCH.md # Engagement without exploitation
├── BRAIN_06_DBT_CBT.md               # Therapeutic techniques (TIPP, STOP, etc.)
├── BRAIN_07_MONETIZATION.md          # Ethical pricing, market data
└── BRAIN_08_TECHNICAL.md             # Tech stack decisions
```

### When to Read Each Brain

| If You're Working On... | READ THIS BRAIN FIRST |
|-------------------------|----------------------|
| Any UI/UX changes | **Brain 4** (UX/Accessibility) |
| Mood selection, emotion features | **Brain 2** (Psychological) + **Brain 6** (DBT/CBT) |
| Mr.DP chatbot responses | **Brain 1** (ADHD Deep) + **Brain 6** (DBT/CBT) |
| Points, streaks, achievements | **Brain 5** (Gamification) |
| Crisis/SOS mode features | **Brain 6** (DBT/CBT) - especially TIPP, STOP skills |
| Inattentive-type user support | **Brain 3** (ADD Research) |
| Pricing, premium features | **Brain 7** (Monetization) |
| Architecture decisions | **Brain 8** (Technical) |
| Onboarding, copy, messaging | **Brain 1** (ADHD Deep) + **Brain 4** (UX) |

### Mandatory Reading Protocol

**Before ANY feature work:**
1. Check `00_MASTER_INDEX.md` for relevant brain
2. Read the full relevant section(s) in that brain
3. Note the citation/research backing your approach
4. Include citation reference in code comments

**Example:**
```python
# Touch target size: 44x44px minimum
# Research: Brain 4, Section 6 - WCAG 2.5.5, Fitts's Law
# Citation: Park & Han (2020) - 48px+ for motor difficulties
button_size = 44
```

---

## 🔬 RESEARCH-BACKED DESIGN RULES

### Typography (Brain 4, Section 5)
```css
/* MANDATORY - Research-validated for ADHD readability */
font-family: 'Lexend', sans-serif;  /* Bonnie Shaver-Troup study */
font-size: 16px;                     /* Minimum - never smaller */
line-height: 1.6;                    /* Optimal for ADHD */
letter-spacing: 0.01em;              /* Reduces crowding */
```
**Citation:** Shaver-Troup et al. - Lexend reduces visual stress, improves reading fluency

### Color Palette (Brain 4, Section 6)
```css
/* Research-validated calming colors */
--primary: #5B8FB9;      /* Calm blue - reduces anxiety */
--secondary: #7CB98F;    /* Soothing green - promotes calm */
--background: #F5F5F5;   /* Soft off-white - reduces eye strain */
--text: #333333;         /* Dark gray, NOT pure black */
--accent: #E8C07D;       /* Warm yellow - USE SPARINGLY */
--danger: #C97B7B;       /* Softened red - never harsh */
```
**Citation:** Küller et al. (2006), Stone (2006) - Blue/green calming effects
**WARNING:** Avoid red/yellow for notifications - triggers anxiety (Brain 4, Section 6)

### Touch Targets (Brain 4, Section 6)
- **Minimum:** 44x44px (WCAG 2.5.5)
- **Recommended:** 48x48px for motor difficulties
- **Spacing:** 8px minimum between targets
**Citation:** Park & Han (2020) - ADHD motor coordination challenges

### Gamification Rules (Brain 5, Section 3-7)

**DO:**
- ✅ Points for ATTEMPTING, not just success
- ✅ Streaks with grace periods (3 day buffer)
- ✅ Cumulative lifetime stats that never reset
- ✅ Optional visibility for all competitive elements
- ✅ Celebrate attempts: "You showed up - that's what matters"

**DON'T:**
- ❌ NO streak resets to zero (triggers shame spiral)
- ❌ NO guilt-based messaging ("You broke your streak!")
- ❌ NO forced daily requirements
- ❌ NO social comparison leaderboards (RSD trigger)
- ❌ NO punishment mechanics

**Citation:** Volkow et al. (2009) dopamine reward pathway, Plichta & Scheres (2014) ventral-striatal responsiveness

### Crisis Mode Design (Brain 6, Section 2)

**TIPP Technique (immediate physiological regulation):**
- **T**emperature - Cold water on face
- **I**ntense exercise - Channel stored energy
- **P**aced breathing - 5 seconds in, 7 seconds out
- **P**rogressive relaxation - Tense and release

**STOP Skill (impulse prevention):**
- **S**top - Don't react
- **T**ake a step back - Remove from situation
- **O**bserve - Notice surroundings and feelings
- **P**roceed mindfully - Think before acting

**Citation:** Linehan (2015) DBT Skills Training Manual

### Notification Rules (Brain 4, Section 10)
- User-controlled frequency
- Non-guilt language only
- Never use countdown timers
- Actionable, not anxiety-inducing
- Respect "Do Not Disturb"

---

## 🏥 MEDICAL AUDIT COMPLIANCE

### Documentation Requirements

Every feature must have:
1. **Research justification** - Which brain/section supports this?
2. **Citation trail** - What study/paper backs this approach?
3. **ADHD-specific consideration** - How does this help neurodivergent users?
4. **Harm prevention** - What could go wrong? How do we prevent it?

### Code Comment Format
```python
def show_streak_with_grace(user_streak, grace_period=3):
    """
    Display streak with grace period to prevent shame spirals.
    
    Research Basis:
    - Brain 5, Section 4: "The Streak Problem - ADHD-Specific"
    - Citation: Duolingo study - easier streaks = higher retention
    - ADHD Consideration: All-or-nothing thinking makes streak breaks devastating
    - Harm Prevention: Grace period prevents shame spiral and app abandonment
    """
    # Implementation...
```

### Prohibited Patterns (Brain 5, Section 7)

These are **dark patterns** that exploit ADHD vulnerabilities and MUST NOT be implemented:

| Pattern | Why It's Harmful | Brain Reference |
|---------|------------------|-----------------|
| Temporal manipulation | Forced daily login creates anxiety | Brain 5, Section 7 |
| Guilt messaging | "You let Mr.DP down" - triggers RSD | Brain 5, Section 4 |
| Streak reset to zero | Devastating for ADHD motivation | Brain 5, Section 4 |
| Countdown timers | Creates panic, not motivation | Brain 5, Section 7 |
| Social comparison | RSD trigger, shame spiral | Brain 1, Section 5 |
| Pay-to-recover | Exploits emotional vulnerability | Brain 7, Section 4 |

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

**User Profile Research:** Brain 1 (ADHD Deep), Brain 3 (ADD/Inattentive)

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

**Tech Decisions Research:** Brain 8 (Technical Implementation)

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

### Rule #3: RESEARCH-BACKED CHANGES ONLY
**Why**: Medical audit compliance requires evidence trail.

- ✅ Cite brain/section for any UX change
- ✅ Explain ADHD-specific benefit
- ✅ Note harm prevention considerations
- ❌ No "I think this looks better" changes
- ❌ No following generic UX trends that conflict with research

### Rule #4: ASK, DON'T ASSUME
- ✅ Ask clarifying questions if task is ambiguous
- ✅ Confirm approach before major changes
- ❌ Don't make assumptions about requirements

---

## RESEARCH-BACKED AUDIT PROCESS

### Before Modifying Any Feature

1. **Identify relevant brain(s):**
   ```
   Read docs/brains/00_MASTER_INDEX.md
   → Identify which brain(s) cover this feature area
   ```

2. **Read the research:**
   ```
   Read the full relevant section in the brain file
   → Note specific citations and recommendations
   ```

3. **Check current implementation:**
   ```
   Does current code align with research?
   → If yes: Document alignment
   → If no: Flag for surgical fix
   ```

4. **Propose change with citation:**
   ```
   "Change X to Y because Brain N, Section M says Z"
   "Citation: [Author] (Year) - [Finding]"
   ```

### Audit Report Format

When asked to audit a feature against research:

```markdown
## Feature: [Feature Name]

### Current Implementation
- [How it works now]

### Research Requirements (Brain X, Section Y)
- [What the research says]
- Citation: [Source]

### Alignment Status
✅ Aligned: [What's correct]
⚠️ Minor gap: [Small tweaks needed]
❌ Misaligned: [Needs attention]

### Recommended Changes
1. [Change with citation]
2. [Change with citation]

### Harm Prevention Check
- [Potential issues and mitigations]
```

---

## FILE STRUCTURE

```
project-root/
├── CLAUDE.md                    # This file - AI assistant instructions
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
├── app.py                       # Main Streamlit app (~10,000 lines)
├── requirements.txt             # Python dependencies
│
├── # Core Feature Modules
├── mr_dp_intelligence.py        # Mr.DP AI chatbot logic, gamification
├── mr_dp_floating.py            # Floating chat widget UI
├── mood_utils.py                # Mood logging and history
├── behavior_tracking.py         # User engagement tracking
├── watch_queue.py               # Save for later functionality
├── sos_calm_mode.py             # Crisis/calm mode features (Brain 6!)
├── time_aware_picks.py          # Time-of-day recommendations
├── focus_timer.py               # Pomodoro-style focus sessions
│
├── # Phase 3 Enhanced Features
├── gamification_enhanced.py     # Points, streaks, leaderboards, 30 achievements
├── user_learning.py             # Pattern detection, personalization
├── wellness_enhanced.py         # Breathing exercises, grounding, affirmations
├── search_aggregator.py         # Multi-platform search
├── social_features.py           # Watch parties, messaging, friends
│
├── # Monetization
├── subscription_utils.py        # Usage limits, premium checks
├── stripe_utils.py              # Pricing page, checkout URLs
├── analytics_utils.py           # User analytics
├── email_utils.py               # Welcome/milestone emails
│
├── # Landing Pages & Blog
├── index.html                   # English landing page
├── index_es.html                # Spanish landing page
└── blog/                        # Blog content
```

---

## MR.DP CHATBOT

### Overview
Mr.DP is the AI assistant mascot - a friendly neuron character with expressions.

### Research Basis
- **Brain 1:** ADHD emotional dysregulation (Mr.DP must be calming, not triggering)
- **Brain 6:** DBT/CBT techniques (Mr.DP can guide TIPP, STOP skills in crisis)
- **Brain 5:** Gamification (Mr.DP gives points for engagement, never guilt)

### Key Personality Rules
- ✅ Warm, supportive, never judgmental
- ✅ Validates feelings before offering solutions
- ✅ Uses ADHD-friendly language (short, clear, actionable)
- ✅ Can guide crisis techniques (TIPP, STOP) when user is distressed
- ❌ Never uses guilt ("You haven't visited in a while...")
- ❌ Never overwhelming with options
- ❌ Never dismissive of struggles

### Expressions
happy, thinking, excited, listening, sad, love, surprised, wink, confused, cool, focused, sleeping

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
- **Implement anything that conflicts with brain research**
- **Add any gamification that could trigger shame/guilt**
- **Modify crisis/wellness features without reading Brain 6**

---

## QUICK REFERENCE

| Action | Command |
|--------|---------|
| Run Streamlit locally | `streamlit run app.py` |
| Run Next.js locally | `cd dopamine-next && npm run dev` |
| Read research before work | `cat docs/brains/00_MASTER_INDEX.md` |
| Check specific brain | `cat docs/brains/BRAIN_0X_NAME.md` |
| Deploy Streamlit | `git push origin main` |
| View logs | Railway dashboard → Deployments |

---

## COMMIT MESSAGE FORMAT

```
Brief description of change

- Specific change 1
- Specific change 2

Research: Brain X, Section Y - [Relevant finding]

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**Last Updated**: February 2, 2026
**Maintained By**: Johan (with Claude assistance)
**Research Base**: 8 brains, 5,117 lines, 425+ citations
**Version**: 5.0 (Research-Integrated for Medical Audit)
