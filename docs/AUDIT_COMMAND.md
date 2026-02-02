# AUTONOMOUS END-TO-END AUDIT COMMAND

You are conducting a comprehensive audit of dopamine.watch against its research foundation.

## PHASE 0: THE NEURODIVERGENT ENGINE (READ THIS FIRST - THIS IS THE CORE)

```
cat docs/brains/NEURODIVERGENT_ENGINE.md
```

This is the PHILOSOPHY that drives everything. Understand:
- Feel-First paradigm (emotional search, not algorithmic)
- Session Learning (AI gets smarter every interaction)
- Natural Personalization (greet by name, remember context)
- Validate Before Solve (acknowledge feelings first)
- Progress Without Shame (no guilt, no resets)
- Reduce Cognitive Load (single focus, calm design)
- Therapeutic Integration (DBT/CBT woven in)

**EVERY feature must be evaluated against these principles.**

## PHASE 1: RESEARCH INGESTION

Read ALL files in this exact order:

1. `cat docs/brains/00_MASTER_INDEX.md` - Get overview
2. `cat docs/brains/BRAIN_01_ADHD_DEEP_RESEARCH.md` - ADHD neurology
3. `cat docs/brains/BRAIN_02_PSYCHOLOGICAL_RESEARCH.md` - Emotion regulation
4. `cat docs/brains/BRAIN_03_ADD_RESEARCH.md` - Inattentive type
5. `cat docs/brains/BRAIN_04_UX_ACCESSIBILITY.md` - Design rules
6. `cat docs/brains/BRAIN_05_GAMIFICATION_RESEARCH.md` - Engagement ethics
7. `cat docs/brains/BRAIN_06_DBT_CBT.md` - Therapeutic techniques
8. `cat docs/brains/BRAIN_07_MONETIZATION.md` - Pricing ethics
9. `cat docs/brains/BRAIN_08_TECHNICAL.md` - Tech decisions

Take notes on key requirements from each brain.

## PHASE 2: CODEBASE ANALYSIS

Examine these critical files:

1. `app.py` - Main application (focus on mood selection, recommendations, UI)
2. `mr_dp_intelligence.py` - AI chatbot (check: warmth, personalization, session learning)
3. `mr_dp_floating.py` - Chat UI
4. `gamification_enhanced.py` - Points/streaks (check: no guilt, grace periods)
5. `sos_calm_mode.py` - Crisis features (check: TIPP, STOP skills present)
6. `mood_utils.py` - Mood handling
7. `wellness_enhanced.py` - Breathing/grounding exercises
8. `index.html` - Landing page copy (check: no pressure language)

## PHASE 3: NEURODIVERGENT ENGINE COMPLIANCE CHECK

This is the MOST IMPORTANT phase. Every feature must pass these checks:

### 🎯 FEEL-FIRST PARADIGM
- [ ] Does the app ask "How do you FEEL right now?"
- [ ] Does the app ask "How do you WANT to feel?"
- [ ] Are recommendations based on EMOTIONAL TRANSITION, not viewing history?
- [ ] Is content treated as "medicine" for emotional states?
- [ ] Does it say "You feel X, want Y → here's the bridge" NOT "Because you watched X..."?
- [ ] Is the emotional journey honored throughout the experience?

### 🧠 SESSION LEARNING (AI GETS SMARTER)
- [ ] Does Mr.DP greet user BY NAME naturally? ("Hey Sarah!" not "Hello, User")
- [ ] Does the AI remember what user shared EARLIER in this session?
- [ ] Does it reference PREVIOUS sessions? ("Last time you mentioned...")
- [ ] Does it notice PATTERNS? ("I've noticed Sunday nights are tough for you...")
- [ ] Does it check in on previous recommendations? ("Did that show help?")
- [ ] Does it adapt its LANGUAGE to match user's energy/style?
- [ ] Does the AI feel like a FRIEND, not a bot?

### 💜 VALIDATE BEFORE SOLVE
- [ ] When user shares an emotion, does AI acknowledge it FIRST?
- [ ] Does it say "That's rough" BEFORE "Here's what to do"?
- [ ] Does it offer CHOICE rather than immediately prescribing? ("Want to talk about it or just find something calming?")
- [ ] Does the interaction itself feel SUPPORTIVE, not transactional?

### 🏆 PROGRESS WITHOUT SHAME
- [ ] Streaks have grace periods (3+ days)?
- [ ] NO reset to zero ever?
- [ ] Points reward ATTEMPTING, not just success?
- [ ] Language celebrates return, not punishes absence?
- [ ] "You came back! That's what matters" not "You broke your streak"?
- [ ] All competitive elements are OPTIONAL?
- [ ] Compare to YOUR past self, not others?

### 🧘 COGNITIVE LOAD REDUCTION
- [ ] Single focus per screen?
- [ ] Clear, obvious primary action?
- [ ] No overwhelming lists of options?
- [ ] "Here's THE one for you" not "Here are 47 choices"?
- [ ] White space respected?
- [ ] Lexend font used?
- [ ] Calming colors (blues/greens)?

### 🏥 THERAPEUTIC INTEGRATION
- [ ] TIPP technique available (not buried in settings)?
- [ ] STOP skill accessible?
- [ ] Grounding exercises present?
- [ ] Crisis resources ALWAYS visible (not behind paywall)?
- [ ] Therapeutic features woven into core experience (not separate "wellness" tab)?

### ⚠️ ANTI-PATTERNS (MUST NOT EXIST)
Search codebase for these - ANY match is a CRITICAL FAILURE:
- [ ] "Based on your viewing history" - FAIL
- [ ] "Users who liked X also liked" - FAIL
- [ ] "You broke your streak" - FAIL
- [ ] "Don't miss out" - FAIL
- [ ] "You haven't visited in a while" - FAIL
- [ ] "Don't let Mr.DP down" - FAIL
- [ ] Countdown timers creating urgency - FAIL
- [ ] Streak resets to zero - FAIL
- [ ] Forced daily requirements - FAIL
- [ ] Social comparison leaderboards (not optional) - FAIL

## PHASE 4: UX AUDIT (Brain 4)

### Typography
- [ ] Lexend font used?
- [ ] 16px minimum font size?
- [ ] 1.6 line-height?
- [ ] No walls of text?

### Colors
- [ ] Blues/greens for calming elements?
- [ ] No harsh reds in notifications?
- [ ] Soft, not stark contrasts?
- [ ] Dark mode available?

### Touch/Click Targets
- [ ] 44px minimum touch targets?
- [ ] Adequate spacing between clickables?

### Cognitive Load
- [ ] Single focus per screen?
- [ ] Clear visual hierarchy?
- [ ] Reduce motion option?
- [ ] No auto-playing animations?

## PHASE 5: GAMIFICATION AUDIT (Brain 5)

### Positive Patterns
- [ ] Points reward ATTEMPTING, not just success?
- [ ] Streaks have grace periods (3+ days)?
- [ ] Lifetime stats never reset?
- [ ] Achievements celebrate progress, not perfection?

### Dark Patterns (MUST NOT EXIST)
- [ ] NO streak reset to zero
- [ ] NO guilt messaging ("You broke your streak!")
- [ ] NO forced daily requirements
- [ ] NO social comparison leaderboards
- [ ] NO countdown timers creating pressure
- [ ] NO "You let Mr.DP down" messaging

## PHASE 6: THERAPEUTIC FEATURES AUDIT (Brain 6)

### Crisis Mode
- [ ] TIPP technique available? (Temperature, Intense exercise, Paced breathing, Progressive relaxation)
- [ ] STOP skill available? (Stop, Take step back, Observe, Proceed mindfully)
- [ ] Grounding exercises present?
- [ ] Crisis resources always visible (hotlines, etc.)?

### Emotional Regulation
- [ ] Breathing exercises follow research guidelines?
- [ ] Self-soothe options (5 senses)?
- [ ] Validation before solution?

## PHASE 7: MESSAGING/COPY AUDIT

### Language Check (scan all user-facing strings)
- [ ] NO guilt language
- [ ] NO pressure/urgency language
- [ ] NO "Don't miss out!"
- [ ] NO "You haven't visited in a while"
- [ ] Warm, supportive tone throughout
- [ ] ADHD-friendly (short, scannable, actionable)

## PHASE 8: GENERATE AUDIT REPORT

Create file: `AUDIT_REPORT.md` with:

```markdown
# dopamine.watch Research Compliance Audit
## Generated: [DATE]
## Audited Against: The Neurodivergent Engine™ + 8 Research Brains (425+ citations)

### Executive Summary
[Overall alignment score: X/10]
[Neurodivergent Engine compliance: X/10] ← THIS IS THE KEY METRIC
[Critical issues found: X]
[Minor improvements suggested: X]

---

### 🚀 NEURODIVERGENT ENGINE COMPLIANCE (Most Important Section)

#### Feel-First Paradigm: [PASS/PARTIAL/FAIL]
[Findings with specific code references]

#### Session Learning: [PASS/PARTIAL/FAIL]
[Does AI greet by name? Remember context? Learn patterns?]

#### Validate Before Solve: [PASS/PARTIAL/FAIL]
[Does it acknowledge emotions before solutions?]

#### Progress Without Shame: [PASS/PARTIAL/FAIL]
[Any guilt language? Resets? Fear tactics?]

#### Cognitive Load Reduction: [PASS/PARTIAL/FAIL]
[Single focus? Calm design? Clear actions?]

#### Therapeutic Integration: [PASS/PARTIAL/FAIL]
[TIPP/STOP available? Crisis resources visible?]

#### Anti-Pattern Check: [PASS/FAIL]
[List any violations found - these are CRITICAL]

---

### 🎨 UX/Accessibility Compliance (Brain 4)
[Checklist results with citations]

### 🎮 Gamification Ethics (Brain 5)
[Checklist results with citations]

### 🏥 Therapeutic Features (Brain 6)
[Checklist results with citations]

### ✍️ Messaging/Copy Review
[Findings - search for guilt/pressure language]

---

### ✅ What We're Doing RIGHT
[Celebrate wins! This matters for morale]

### 🔧 Small Fixes (Safe to Apply)
[List with brain/section citations]
[Include specific file:line references]
[Prioritized by impact]

### ⚠️ Larger Considerations (Discuss First)
[Bigger changes needing conversation]

### 🚨 CRITICAL ISSUES (Must Fix)
[Anything that violates Neurodivergent Engine principles]
[Any anti-patterns found]

---

### 📋 Medical Audit Readiness
[Assessment of documentation trail]
[Can every feature be traced to research?]
[Are citations present in code comments?]
```

## PHASE 9: TEST RECOMMENDATIONS

For each content type, verify the recommendation logic:
1. Create test scenario: User feels ANXIOUS, wants CALM
2. Trace through code: Is this emotional journey honored?
3. Check: Is it algorithmic ("you watched...") or emotional ("you feel...")?

## EXECUTION

Run this audit autonomously. Read all brains first, then systematically check each file. Generate the complete AUDIT_REPORT.md. Be thorough - this is for medical review.

When complete, output:
1. The full AUDIT_REPORT.md content
2. Summary of most critical findings
3. Recommended priority order for fixes
