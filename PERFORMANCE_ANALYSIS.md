# Performance Analysis Report

## Executive Summary

This document identifies performance anti-patterns, N+1 queries, unnecessary re-renders, and inefficient algorithms in the Dopamine.watch codebase.

**Critical Issues Found:**
- 6 N+1 query patterns causing excessive database/API calls
- 2 major uncached external API calls
- 3 inefficient O(n*m) algorithms in the heuristic fallback
- 50+ `st.rerun()` calls causing full page re-renders
- Unbounded memory growth in chat history

---

## 1. N+1 Query Patterns

### 1.1 Database N+1: `add_dopamine_points_db()` (app.py:195-205)

**Issue:** Two database round-trips when one would suffice.

```python
def add_dopamine_points_db(user_id: str, amount: int, reason: str = ""):
    profile = get_user_profile(user_id)  # DB Query #1
    if profile:
        new_points = profile.get("dopamine_points", 0) + amount
        update_user_profile(user_id, {"dopamine_points": new_points})  # DB Query #2
```

**Fix:** Use Supabase's atomic increment or a single RPC call:
```python
supabase.rpc('increment_points', {'user_id': user_id, 'amount': amount})
```

### 1.2 Database N+1: `update_streak_db()` (app.py:207-236)

**Issue:** Fetches full profile, then updates - 2 queries per streak check.

```python
def update_streak_db(user_id: str):
    profile = get_user_profile(user_id)  # DB Query #1
    # ... calculations ...
    update_user_profile(user_id, {...})  # DB Query #2
```

### 1.3 Duplicate Profile Fetches: `render_stats_bar()` (app.py:2631-2658)

**Issue:** Calls both `get_dopamine_points()` and `get_streak()`, each fetching the full profile.

```python
def render_stats_bar():
    level_name, level_num, next_level = get_level()  # Fetches profile
    points = get_dopamine_points()  # Fetches profile AGAIN
    streak = get_streak()  # Fetches profile AGAIN (3rd time!)
```

**Impact:** 3 database queries instead of 1.

**Fix:** Fetch profile once and pass it to helper functions:
```python
def render_stats_bar():
    profile = get_user_profile_cached(st.session_state.db_user_id)
    points = profile.get("dopamine_points", 0)
    streak = profile.get("streak_days", 0)
```

### 1.4 API N+1: Movie Provider Queries (app.py:2669-2683)

**Issue:** Each movie card triggers a separate API call for streaming providers.

```python
def render_movie_card(item, show_providers=True):
    if show_providers:
        providers = get_movie_providers(tmdb_id, media_type)  # API call per card!
```

**Impact:** Rendering 24 movies = 24 API calls (even with caching, cold cache causes waterfall).

**Fix:** Batch fetch providers for all visible movies before rendering:
```python
# Prefetch all providers
provider_map = batch_get_movie_providers([m["id"] for m in movies[:24]])
# Then render with cached data
for movie in movies:
    providers = provider_map.get(movie["id"], [])
```

### 1.5 API N+1: Trailer Fetching Without Cache (app.py:759-787)

**Issue:** `get_movie_trailer()` has NO CACHING and is called for hero movies.

```python
def get_movie_trailer(tmdb_id, media_type="movie"):
    # NO @st.cache_data decorator!
    r = requests.get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/videos", ...)
```

**Impact:** Every page load with a hero section makes an uncached TMDB API call.

**Fix:** Add caching decorator:
```python
@st.cache_data(ttl=86400)  # 24-hour cache like providers
def get_movie_trailer(tmdb_id, media_type="movie"):
```

---

## 2. Uncached External API Calls

### 2.1 OpenAI GPT Calls: `ask_mr_dp()` (app.py:971-1029)

**Issue:** Every chat message triggers an OpenAI API call with no caching.

```python
def ask_mr_dp(user_prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": MR_DP_SYSTEM_PROMPT},
                  {"role": "user", "content": user_prompt}],
        temperature=0.7,  # Non-deterministic output
    )
```

**Impact:**
- Cost: ~$0.00015 per call
- Latency: 1-3 seconds per request
- No deduplication for similar queries

**Mitigation Options:**
1. Cache responses for exact query matches (limited benefit due to temperature)
2. Implement semantic caching with embeddings
3. Use cheaper model for simple queries (mood detection)
4. Add request debouncing (prevent rapid submissions)

### 2.2 Trailer API Calls (already covered in 1.5)

---

## 3. Inefficient Algorithms

### 3.1 Artist Detection Loop: O(n*m) (app.py:1062-1070)

**Issue:** Linear scan through 60+ artists for EVERY heuristic fallback call.

```python
popular_artists = [
    "drake", "taylor swift", "kendrick", ... # 60+ artists
]

for artist in popular_artists:  # O(60)
    if artist in t:  # O(len(t)) substring search
        media_type = "artist"
        break
```

**Complexity:** O(60 * len(user_input)) per call

**Fix:** Use a set for O(1) exact matches, or use regex compilation:
```python
ARTIST_PATTERN = re.compile(r'\b(' + '|'.join(map(re.escape, popular_artists)) + r')\b', re.I)
match = ARTIST_PATTERN.search(user_input)
```

### 3.2 Keyword Matching Loops (app.py:1130-1318)

**Issue:** Multiple nested loops with `any(k in t for k in keywords)` pattern.

```python
# Line 1256-1261
for feeling, data in feeling_responses.items():
    if any(k in t for k in data["keywords"]):  # O(keywords * len(t))
        current = feeling
        break

# Line 1308-1318
for keyword, data in desire_responses.items():  # O(30+ entries)
    if keyword in t:  # O(len(t))
        ...
```

**Impact:** Each heuristic call performs hundreds of substring operations.

**Fix:** Compile keywords into a single regex or use a trie-based matcher:
```python
# Pre-compile at module load
FEELING_PATTERNS = {
    feeling: re.compile(r'\b(' + '|'.join(map(re.escape, data["keywords"])) + r')\b', re.I)
    for feeling, data in feeling_responses.items()
}

# At runtime - O(1) per pattern
for feeling, pattern in FEELING_PATTERNS.items():
    if pattern.search(t):
        current = feeling
        break
```

### 3.3 Deep Link Fuzzy Matching (app.py:749-757)

**Issue:** Linear search with substring matching for every provider link.

```python
def get_movie_deep_link(provider_name, title):
    if provider in MOVIE_SERVICES:
        return MOVIE_SERVICES[provider].format(title=safe_title)
    for key, template in MOVIE_SERVICES.items():  # O(n) fallback
        if key.lower() in provider.lower() or provider.lower() in key.lower():
            return template.format(title=safe_title)
```

---

## 4. Excessive Re-renders

### 4.1 `st.rerun()` Overuse (50+ instances)

**Locations:** Lines 2836, 2840, 2980, 2985, 3034, 3037, 3043, 3046, 3053, 3061, 3066, 3070, 3097, 3117, 3120, 3127, 3130, 3138, 3143, 3147, 3176, 3179, 3185, 3237, 3280, 3296, 3307, 3368, 3390, 3397, 3492, 3498, 3525, 3531, 3567, 3573, 3612, 3618, 3686, 3692, 3708, 3718, 3724, 3764, 3884, 3972, 4041

**Issue:** Each `st.rerun()` causes:
- Full Python script re-execution
- All session state recalculations
- Potential API re-fetches (if cache expired)
- Complete DOM rebuild

**High-Impact Examples:**
```python
# Line 3764 - After loading more movies
st.session_state.movies_feed.extend(more)
add_dopamine_points(5, "Exploring!")
st.rerun()  # Full page rebuild just to show more movies

# Line 3884 - Changing shorts mood
st.session_state.desired_feeling = feeling
st.rerun()  # Could use fragment rerender
```

**Fix Options:**
1. Use Streamlit fragments (`@st.fragment`) for partial reruns
2. Batch state changes before single rerun
3. Use `st.experimental_rerun()` judiciously
4. Consider component-based architecture for dynamic sections

---

## 5. Memory Issues

### 5.1 Unbounded Chat History Growth (app.py:4008-4018)

**Issue:** Chat history grows indefinitely in session state.

```python
st.session_state.mr_dp_chat_history.append({
    "role": "user",
    "content": prompt
})
# ... later ...
st.session_state.mr_dp_chat_history.append({
    "role": "assistant",
    "content": dp_response.get("message", "")
})
```

**Impact:** Long sessions accumulate memory; no message limit.

**Fix:** Implement rolling window:
```python
MAX_CHAT_HISTORY = 20
st.session_state.mr_dp_chat_history = st.session_state.mr_dp_chat_history[-MAX_CHAT_HISTORY:]
```

### 5.2 Large Static Dictionaries

**Issue:** Mood mapping dicts are large and loaded for every session.

- `FEELING_TO_MUSIC`: ~50 lines
- `FEELING_TO_PODCASTS`: ~30 lines
- `FEELING_TO_AUDIOBOOKS`: ~30 lines
- `FEELING_TO_SHORTS`: ~25 lines

**Total:** ~700 lines of static data in memory per session

**Recommendation:** This is acceptable for a Streamlit app since these are module-level constants shared across requests. However, consider lazy loading if adding more content.

---

## 6. Missing Optimizations

### 6.1 No Request Deduplication

**Issue:** Rapid button clicks can trigger duplicate API calls.

**Fix:** Add debouncing or request coalescing:
```python
last_search_time = st.session_state.get("last_search_time", 0)
if time.time() - last_search_time < 1.0:  # 1 second debounce
    return st.session_state.get("last_search_results", [])
```

### 6.2 No Batch Provider Fetching

**TMDB API supports batch requests but code makes individual calls.**

### 6.3 Missing Connection Pooling

**Issue:** Each request creates new HTTP connection.

**Fix:** Use `requests.Session()` for connection reuse:
```python
# At module level
tmdb_session = requests.Session()

# In functions
r = tmdb_session.get(url, params=params)
```

---

## Summary of Fixes by Priority

### Critical (Immediate Impact)
1. Add `@st.cache_data(ttl=86400)` to `get_movie_trailer()`
2. Consolidate profile fetches in `render_stats_bar()`
3. Use atomic database operations for point/streak updates

### High (Significant Improvement)
4. Batch movie provider queries before rendering
5. Pre-compile regex patterns for heuristic matching
6. Limit chat history size

### Medium (Quality of Life)
7. Add request debouncing
8. Use `requests.Session()` for connection pooling
9. Consider Streamlit fragments for partial reruns

### Low (Future Consideration)
10. Implement semantic caching for GPT responses
11. Move static data to external config if it grows significantly
12. Consider server-side state management for heavy users

---

## Metrics to Monitor

1. **API Call Count:** Track TMDB/OpenAI calls per session
2. **Database Query Count:** Monitor Supabase operations
3. **Page Load Time:** Measure time from rerun to render complete
4. **Memory Usage:** Track session state size over time
5. **Cache Hit Rate:** Monitor `@st.cache_data` effectiveness
