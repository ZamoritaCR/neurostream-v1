-- ============================================
-- DOPAMINE.WATCH PHASE 1 & 2 DATABASE TABLES
-- Run this SQL in Supabase SQL Editor
-- Safe to re-run (drops policies first)
-- ============================================

-- ============================================
-- 1. MOOD HISTORY TABLE
-- Tracks user mood selections over time
-- ============================================
CREATE TABLE IF NOT EXISTS mood_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    current_feeling TEXT NOT NULL,
    desired_feeling TEXT NOT NULL,
    source TEXT DEFAULT 'manual', -- 'manual', 'mr_dp', 'quick_hit'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user queries
CREATE INDEX IF NOT EXISTS idx_mood_history_user_id ON mood_history(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_history_created_at ON mood_history(created_at DESC);

-- RLS Policy (drop first to avoid conflicts)
ALTER TABLE mood_history ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own mood history" ON mood_history;
DROP POLICY IF EXISTS "Users can insert own mood history" ON mood_history;

CREATE POLICY "Users can view own mood history"
    ON mood_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own mood history"
    ON mood_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 2. USER BEHAVIOR TABLE
-- Tracks all user actions for analytics
-- ============================================
CREATE TABLE IF NOT EXISTS user_behavior (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    action_type TEXT NOT NULL, -- 'view', 'click', 'save', 'watch', 'search', 'mr_dp_chat', 'quick_hit', 'sos_calm_mode'
    content_id TEXT,
    content_type TEXT, -- 'movie', 'tv', 'podcast', 'music', 'audiobook'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_behavior_user_id ON user_behavior(user_id);
CREATE INDEX IF NOT EXISTS idx_user_behavior_action_type ON user_behavior(action_type);
CREATE INDEX IF NOT EXISTS idx_user_behavior_created_at ON user_behavior(created_at DESC);

-- RLS Policy
ALTER TABLE user_behavior ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own behavior"
    ON user_behavior FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own behavior"
    ON user_behavior FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 3. WATCH QUEUE TABLE
-- User's saved content queue (Watch Later)
-- ============================================
CREATE TABLE IF NOT EXISTS watch_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    content_id TEXT NOT NULL,
    content_type TEXT NOT NULL, -- 'movie', 'tv', 'podcast', 'music', 'audiobook'
    title TEXT NOT NULL,
    poster_path TEXT,
    mood_when_saved JSONB DEFAULT '{}', -- {current_feeling, desired_feeling}
    status TEXT DEFAULT 'queued', -- 'queued', 'watching', 'watched'
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    watched_at TIMESTAMPTZ,
    UNIQUE(user_id, content_id, content_type)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_watch_queue_user_id ON watch_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_watch_queue_status ON watch_queue(status);
CREATE INDEX IF NOT EXISTS idx_watch_queue_added_at ON watch_queue(added_at DESC);

-- RLS Policy
ALTER TABLE watch_queue ENABLE ROW LEVEL SECURITY;

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
-- 4. FOCUS SESSIONS TABLE
-- Tracks completed focus/watch sessions
-- ============================================
CREATE TABLE IF NOT EXISTS focus_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    duration_minutes DECIMAL(10,1) NOT NULL,
    content_watched JSONB DEFAULT '[]', -- Array of content IDs watched
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_focus_sessions_user_id ON focus_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_completed_at ON focus_sessions(completed_at DESC);

-- RLS Policy
ALTER TABLE focus_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own focus sessions"
    ON focus_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own focus sessions"
    ON focus_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ============================================
-- 5. SUBSCRIPTIONS TABLE (from Master Command)
-- Premium subscription tracking
-- ============================================
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    stripe_customer_id TEXT,
    plan_type TEXT DEFAULT 'free', -- 'free', 'premium'
    status TEXT DEFAULT 'inactive', -- 'active', 'inactive', 'cancelled', 'past_due'
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);

-- RLS Policy
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own subscription"
    ON subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Only backend can modify subscriptions (via service role)
-- No INSERT/UPDATE/DELETE policies for regular users

-- ============================================
-- 6. DAILY USAGE TABLE (from Master Command)
-- Track free tier usage limits
-- ============================================
CREATE TABLE IF NOT EXISTS daily_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    recommendations_count INT DEFAULT 0,
    mr_dp_chats_count INT DEFAULT 0,
    quick_dope_hits_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_daily_usage_user_date ON daily_usage(user_id, date);

-- RLS Policy
ALTER TABLE daily_usage ENABLE ROW LEVEL SECURITY;

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
-- VERIFICATION QUERIES
-- Run these to confirm tables were created
-- ============================================
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================
-- INSERT INTO mood_history (user_id, current_feeling, desired_feeling, source)
-- VALUES ('your-user-id-here', 'Anxious', 'Calm', 'manual');

-- ============================================
-- CLEANUP (Only if needed to reset)
-- ============================================
-- DROP TABLE IF EXISTS mood_history CASCADE;
-- DROP TABLE IF EXISTS user_behavior CASCADE;
-- DROP TABLE IF EXISTS watch_queue CASCADE;
-- DROP TABLE IF EXISTS focus_sessions CASCADE;
-- DROP TABLE IF EXISTS subscriptions CASCADE;
-- DROP TABLE IF EXISTS daily_usage CASCADE;
