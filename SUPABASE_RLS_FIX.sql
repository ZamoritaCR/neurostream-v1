-- ============================================
-- DOPAMINE.WATCH - COMPLETE RLS SECURITY FIX
-- Run this ENTIRE script in Supabase SQL Editor
-- ============================================

-- ============================================
-- 1. ENABLE RLS ON ALL TABLES
-- ============================================
ALTER TABLE IF EXISTS public.watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.mood_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_behavior ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.watch_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.focus_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.daily_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_inventory ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 2. PROFILES TABLE POLICIES
-- (profiles uses 'id' as user_id since it matches auth.users.id)
-- ============================================
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;

CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ============================================
-- 3. WATCHLIST TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own watchlist" ON watchlist;
DROP POLICY IF EXISTS "Users can insert to own watchlist" ON watchlist;
DROP POLICY IF EXISTS "Users can update own watchlist" ON watchlist;
DROP POLICY IF EXISTS "Users can delete from own watchlist" ON watchlist;

CREATE POLICY "Users can view own watchlist"
    ON watchlist FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert to own watchlist"
    ON watchlist FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own watchlist"
    ON watchlist FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete from own watchlist"
    ON watchlist FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- 4. MOOD HISTORY POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own mood history" ON mood_history;
DROP POLICY IF EXISTS "Users can insert own mood history" ON mood_history;

CREATE POLICY "Users can view own mood history"
    ON mood_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own mood history"
    ON mood_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 5. USER BEHAVIOR POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own behavior" ON user_behavior;
DROP POLICY IF EXISTS "Users can insert own behavior" ON user_behavior;

CREATE POLICY "Users can view own behavior"
    ON user_behavior FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own behavior"
    ON user_behavior FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 6. WATCH QUEUE POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own queue" ON watch_queue;
DROP POLICY IF EXISTS "Users can insert to own queue" ON watch_queue;
DROP POLICY IF EXISTS "Users can update own queue" ON watch_queue;
DROP POLICY IF EXISTS "Users can delete from own queue" ON watch_queue;

CREATE POLICY "Users can view own queue"
    ON watch_queue FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert to own queue"
    ON watch_queue FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own queue"
    ON watch_queue FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete from own queue"
    ON watch_queue FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================
-- 7. FOCUS SESSIONS POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own focus sessions" ON focus_sessions;
DROP POLICY IF EXISTS "Users can insert own focus sessions" ON focus_sessions;

CREATE POLICY "Users can view own focus sessions"
    ON focus_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own focus sessions"
    ON focus_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 8. SUBSCRIPTIONS POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own subscription" ON subscriptions;

CREATE POLICY "Users can view own subscription"
    ON subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Note: Only backend (service role) can modify subscriptions

-- ============================================
-- 9. DAILY USAGE POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own usage" ON daily_usage;
DROP POLICY IF EXISTS "Users can insert own usage" ON daily_usage;
DROP POLICY IF EXISTS "Users can update own usage" ON daily_usage;

CREATE POLICY "Users can view own usage"
    ON daily_usage FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own usage"
    ON daily_usage FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own usage"
    ON daily_usage FOR UPDATE
    USING (auth.uid() = user_id);

-- ============================================
-- 10. REFERRALS POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own referrals" ON referrals;
DROP POLICY IF EXISTS "Users can view referrals they made" ON referrals;
DROP POLICY IF EXISTS "Users can insert referrals" ON referrals;

CREATE POLICY "Users can view own referrals"
    ON referrals FOR SELECT
    USING (auth.uid() = referred_id);

CREATE POLICY "Users can view referrals they made"
    ON referrals FOR SELECT
    USING (auth.uid() = referrer_id);

CREATE POLICY "Users can insert referrals"
    ON referrals FOR INSERT
    WITH CHECK (auth.uid() = referred_id);

-- ============================================
-- 11. USER CHALLENGES POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own challenge progress" ON user_challenges;
DROP POLICY IF EXISTS "Users can insert own challenge progress" ON user_challenges;
DROP POLICY IF EXISTS "Users can update own challenge progress" ON user_challenges;

CREATE POLICY "Users can view own challenge progress"
    ON user_challenges FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own challenge progress"
    ON user_challenges FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own challenge progress"
    ON user_challenges FOR UPDATE
    USING (auth.uid() = user_id);

-- ============================================
-- 12. USER INVENTORY POLICIES
-- ============================================
DROP POLICY IF EXISTS "Users can view own inventory" ON user_inventory;
DROP POLICY IF EXISTS "Users can insert to own inventory" ON user_inventory;

CREATE POLICY "Users can view own inventory"
    ON user_inventory FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert to own inventory"
    ON user_inventory FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- VERIFICATION QUERY
-- Run this to verify all tables have RLS enabled
-- ============================================
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- All should show rowsecurity = true
