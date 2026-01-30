# .claude.md - Project Instructions for AI Assistants

> **Purpose**: This file tells Claude (and other AI assistants) how to work with this project effectively.
> 
> **Location**: Place this file in your project root directory as `.claude.md`

---

## 🎯 PROJECT OVERVIEW

**Project Name**: dopamine.watch  
**Description**: ADHD-friendly streaming recommendation app that helps neurodivergent users find content based on emotional state transitions  
**Repository**: https://github.com/ZamoritaCR/neurostream-v1  
**Live URL**: https://dopamine.watch

### Core Purpose
[2-3 sentence elevator pitch of what this project does and why it exists]

### Target Users
- [Primary user type]
- [Secondary user type]
- [User pain point this solves]

---

## 💻 TECH STACK

### Frontend
- **Framework**: Streamlit (Python)
- **Styling**: Custom CSS with ADHD-optimized design
- **Typography**: Lexend font (dyslexia-friendly)

### Backend
- **Database**: Supabase Pro (PostgreSQL)
- **Authentication**: Supabase Auth + Google OAuth
- **APIs**: TMDB, OpenAI, Stripe

### Hosting & Deployment
- **Main App**: Railway
- **Landing Pages**: GreenGeeks
- **Version Control**: GitHub

### Development Environment
- **OS**: macOS
- **Editor**: VS Code
- **Python Version**: 3.11+
- **Package Manager**: pip

---

## 📁 FILE STRUCTURE

```
project-root/
├── .claude.md                 # This file
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit configuration
├── static/
│   ├── mr_dp_avatar.svg      # Assets
│   └── animations/
├── landing/
│   ├── index.html            # English landing page
│   └── index_es.html         # Spanish landing page
└── README.md
```

### Key Files to Know
- `app.py` - Main application (1800+ lines, handle with care)
- `requirements.txt` - All Python dependencies
- `.streamlit/config.toml` - App configuration

---

## 🚨 CRITICAL DEVELOPMENT RULES

### Rule #1: NO REFACTORING WITHOUT PERMISSION
**Why**: Developer has ADHD and has built substantial working code over time. Breaking changes cause significant setback.

**What this means**:
- ✅ Fix specific bugs as requested
- ✅ Add new features surgically
- ✅ Preserve ALL existing functionality
- ❌ Don't "clean up" or "simplify" working code
- ❌ Don't remove features to "streamline"
- ❌ Don't refactor architecture unprompted

### Rule #2: STEP-BY-STEP APPROACH
**Why**: Developer has extreme ADHD and needs manageable chunks.

**What this means**:
- ✅ One task at a time
- ✅ Wait for confirmation before proceeding
- ✅ Break complex changes into small steps
- ❌ No overwhelming info dumps
- ❌ No "here are 5 different approaches" - pick the best one

### Rule #3: ASK, DON'T ASSUME
**What this means**:
- ✅ Ask clarifying questions if task is ambiguous
- ✅ Confirm approach before major changes
- ✅ Explain WHY you're suggesting something
- ❌ Don't make assumptions about requirements
- ❌ Don't implement features not explicitly requested

### Rule #4: PRESERVE CONTEXT
**What this means**:
- ✅ Read `DOPAMINE_WATCH_PROJECT_BRAIN.md` before starting
- ✅ Reference existing code patterns
- ✅ Maintain coding style consistency
- ❌ Don't introduce new patterns/libraries without discussion

---

## 🔧 COMMON TASKS

### Starting the Development Server
```bash
streamlit run app.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Database Migrations (Supabase)
```sql
-- Run in Supabase SQL Editor
-- Check DOPAMINE_WATCH_PROJECT_BRAIN.md for schemas
```

### Deploying to Railway
```bash
git push origin main
# Railway auto-deploys from main branch
```

### Updating Landing Pages (GreenGeeks)
```bash
# Manual SFTP upload or use VS Code SFTP extension
# Files: landing/index.html, landing/index_es.html
```

---

## 🎨 CODING STANDARDS

### Python Style
- Follow existing code patterns in `app.py`
- Use Streamlit session state for state management
- Keep functions focused and named descriptively
- Add comments for complex logic

### CSS/Styling
- Use ADHD-optimized color palette (see PROJECT_BRAIN.md)
- Maintain Lexend font family
- Keep animations smooth and subtle
- Ensure 44px minimum tap targets

### Error Handling
```python
try:
    # Operation
except Exception as e:
    st.error(f"Helpful error message: {str(e)}")
    # Log for debugging
```

### Session State Pattern
```python
# Always check before accessing
if 'key_name' not in st.session_state:
    st.session_state.key_name = default_value
```

---

## 🐛 DEBUGGING GUIDELINES

### When Code Breaks

1. **First**: Check if it's a session state initialization issue
2. **Second**: Verify API keys are set in environment
3. **Third**: Check Streamlit Cloud logs
4. **Fourth**: Test locally with `streamlit run app.py`

### Common Issues & Fixes

**Issue**: Movies not loading
- **Cause**: `media_type` missing from TMDB response
- **Fix**: Default to `"movie"` in `_clean_results()`

**Issue**: Smart quotes breaking code
- **Cause**: Copy-paste from rich text editors
- **Fix**: Replace curly quotes with straight quotes

**Issue**: Session state AttributeError
- **Cause**: Missing initialization
- **Fix**: Add key to session state initialization

---

## 🔌 API REFERENCE QUICK LINKS

### TMDB API
- **Docs**: https://developer.themoviedb.org/docs
- **Auth**: Bearer token in environment
- **Rate Limit**: 50 req/sec

### OpenAI API
- **Docs**: https://platform.openai.com/docs
- **Model**: GPT-4
- **Usage**: Mr.DP chatbot

### Supabase
- **Docs**: https://supabase.com/docs
- **Dashboard**: https://app.supabase.com
- **RLS**: Enabled on all tables

### Stripe
- **Docs**: https://stripe.com/docs/api
- **Test Mode**: Use test keys for development
- **Webhooks**: Need to configure for subscriptions

---

## 📋 FEATURE IMPLEMENTATION CHECKLIST

When adding new features:

- [ ] Read relevant sections in PROJECT_BRAIN.md
- [ ] Discuss approach with developer first
- [ ] Write minimal code to achieve goal
- [ ] Test locally before committing
- [ ] Update this file if adding new patterns
- [ ] Update PROJECT_BRAIN.md if significant
- [ ] Commit with clear message
- [ ] Verify deployment on Railway

---

## 🎯 TESTING STRATEGY

### Local Testing
```bash
# Run app
streamlit run app.py

# Test specific flows:
# 1. Sign up / Login
# 2. Mood selection → Recommendations
# 3. Mr.DP chatbot
# 4. Quick Dope Hit button
# 5. Each content tab (Movies, Music, etc.)
```

### Environment Variables Needed
```bash
OPENAI_API_KEY=sk-...
TMDB_API_KEY=eyJ...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

---

## 💬 WORKING WITH THE DEVELOPER

### Communication Style
- Developer has extreme ADHD - be concise and clear
- One task at a time, wait for go-ahead
- Use step-by-step instructions
- No overwhelming info dumps

### What Developer Values
- ✅ Surgical fixes that solve exact problem
- ✅ Clear explanations of WHY
- ✅ Preserving working code
- ✅ Quick wins over perfect solutions

### What Frustrates Developer
- ❌ Refactoring working code without permission
- ❌ Removing features to "simplify"
- ❌ Multiple options without recommendation
- ❌ Breaking existing functionality

---

## 🚀 DEPLOYMENT NOTES

### Railway Deployment
- Auto-deploys from `main` branch
- Environment variables set in Railway dashboard
- Check build logs if deployment fails
- Streamlit Cloud cache may need clearing

### GreenGeeks (Landing Pages)
- Static HTML/CSS/JS files
- Use SFTP for uploads
- Test locally first (open index.html in browser)
- Absolute URLs for all internal links

---

## 📚 ESSENTIAL READING

### Before Making Changes
1. Read this entire `.claude.md` file
2. Read `DOPAMINE_WATCH_PROJECT_BRAIN.md`
3. Ask if anything is unclear

### For Specific Features
- **ADHD Optimization**: See "ADHD OPTIMIZATION" section in PROJECT_BRAIN.md
- **API Integration**: See "API INTEGRATIONS" section in PROJECT_BRAIN.md
- **Database Schema**: See "DEPLOYMENT & INFRASTRUCTURE" section in PROJECT_BRAIN.md

---

## 🔄 WORKFLOW EXAMPLES

### Example 1: Fixing a Bug
```
Developer: "The login button isn't working on the Spanish landing page"

Claude:
1. ✅ Read .claude.md and PROJECT_BRAIN.md
2. ✅ Ask: "What error message do you see?" (if not provided)
3. ✅ Locate issue in index_es.html
4. ✅ Propose minimal fix
5. ✅ Show before/after code
6. ✅ Wait for approval
7. ✅ Implement fix
```

### Example 2: Adding a Feature
```
Developer: "Add a 'Save for Later' button to each movie card"

Claude:
1. ✅ Read existing movie card implementation
2. ✅ Ask: "Should this save to Supabase or session state?"
3. ✅ Propose approach with code example
4. ✅ Wait for approval
5. ✅ Implement in stages (UI → functionality → storage)
6. ✅ Test each stage before proceeding
```

### Example 3: What NOT to Do
```
Developer: "The app is slow, can you optimize it?"

Claude:
❌ "I'll refactor the entire app.py to be more efficient"
✅ "Let me profile the app to find the bottleneck first. Can you tell me which specific actions feel slow?"
```

---

## 🎓 LEARNING RESOURCES

### Streamlit
- Official Docs: https://docs.streamlit.io
- Session State Guide: https://docs.streamlit.io/library/api-reference/session-state

### ADHD-Friendly Design
- See research citations in PROJECT_BRAIN.md
- Lexend Font: https://fonts.google.com/specimen/Lexend

### Project-Specific
- TMDB API Wrapper: `tmdbv3api` library docs
- Supabase Python Client: https://supabase.com/docs/reference/python

---

## ⚠️ RED FLAGS - STOP AND ASK

**Stop and confirm with developer if you're about to**:
- Delete any existing code (except obvious bugs)
- Change the structure of session state
- Modify the database schema
- Add new dependencies to requirements.txt
- Change how APIs are called
- Refactor more than 20 lines of code
- Remove or rename any functions
- Change the UI layout significantly

---

## 📝 COMMIT MESSAGE FORMAT

```
[Component] Brief description

- Specific change 1
- Specific change 2

Fixes: #issue-number (if applicable)
```

**Examples**:
```
[Landing] Fix Spanish login modal

- Corrected button event listener
- Updated Google Sign-In integration
```

```
[Chatbot] Add ADHD-aware response system

- Updated Mr.DP system prompt
- Reduced response length to 3 sentences max
```

---

## 🎯 SUCCESS CRITERIA

**You're doing it right when**:
- ✅ Developer says "yes, exactly"
- ✅ Code works first time
- ✅ Existing features still work
- ✅ Changes are minimal and focused
- ✅ Developer understands what you did

**You're doing it wrong when**:
- ❌ Developer says "that broke everything"
- ❌ You removed working features
- ❌ You refactored without permission
- ❌ Developer is confused by your changes
- ❌ You introduced new bugs

---

## 🆘 WHEN STUCK

### Ask These Questions
1. "What specifically should change?"
2. "Should I preserve [existing functionality]?"
3. "Do you want me to [specific approach]?"
4. "Can you show me the error message?"

### Never Say
- ❌ "I'll refactor this for you"
- ❌ "Let me simplify this"
- ❌ "Here are 5 different approaches"
- ❌ "I don't have enough context" (read PROJECT_BRAIN.md)

---

## 📞 GETTING HELP

### For Claude Issues
- Developer's memory contains project history
- Reference past conversations if needed
- Use `conversation_search` for specific topics

### For Technical Issues
- Check Streamlit documentation
- Verify environment variables
- Test API endpoints directly
- Check Railway logs

---

**FINAL REMINDER**: 

🚨 **READ `DOPAMINE_WATCH_PROJECT_BRAIN.md` BEFORE EVERY SESSION** 🚨

This file contains the complete project context, history, and technical specifications. Without it, you're flying blind.

---

**Last Updated**: January 30, 2026  
**Maintained By**: Johan (with Claude assistance)  
**Version**: 1.0

