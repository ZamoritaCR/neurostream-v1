-- ================================================================
-- MR.DP INTELLIGENCE SYSTEM - SUPABASE TABLES
-- ================================================================
-- Run this SQL in your Supabase SQL editor to create the
-- necessary tables for Mr.DP's intelligence features:
-- 1. Behavioral Learning
-- 2. Gamification/Evolution
-- 3. Conversation History
-- ================================================================

-- ----------------------------------------------------------------
-- 1. MR.DP BEHAVIOR LOGS
-- Tracks user browsing behavior for pattern detection
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mr_dp_behavior_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    session_date DATE NOT NULL,
    scroll_events INT DEFAULT 0,
    recommendations_seen INT DEFAULT 0,
    recommendations_clicked INT DEFAULT 0,
    click_through_rate DECIMAL(5,4) DEFAULT 0,
    quick_hit_uses INT DEFAULT 0,
    session_duration_minutes DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for efficient user + date queries
CREATE INDEX IF NOT EXISTS idx_behavior_user_date
    ON mr_dp_behavior_logs(user_id, session_date);

-- Index for analytics queries
CREATE INDEX IF NOT EXISTS idx_behavior_created
    ON mr_dp_behavior_logs(created_at DESC);

-- ----------------------------------------------------------------
-- 2. MR.DP GAMIFICATION PROGRESS
-- Stores evolution, XP, achievements, and accessories
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mr_dp_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
    xp INT DEFAULT 0,
    evolution VARCHAR(50) DEFAULT 'baby',
    achievements JSONB DEFAULT '[]',
    accessory VARCHAR(50) DEFAULT 'none',
    game_data JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for user lookups
CREATE INDEX IF NOT EXISTS idx_progress_user
    ON mr_dp_progress(user_id);

-- ----------------------------------------------------------------
-- 3. MR.DP CONVERSATION HISTORY (Optional)
-- Stores chat history for conversation memory
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mr_dp_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    expression VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fetching recent conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user
    ON mr_dp_conversations(user_id, created_at DESC);

-- ================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ================================================================

-- Enable RLS on all tables
ALTER TABLE mr_dp_behavior_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mr_dp_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE mr_dp_conversations ENABLE ROW LEVEL SECURITY;

-- ----------------------------------------------------------------
-- Behavior Logs Policies
-- ----------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own behavior logs" ON mr_dp_behavior_logs;
DROP POLICY IF EXISTS "Users can insert own behavior logs" ON mr_dp_behavior_logs;

CREATE POLICY "Users can view own behavior logs"
    ON mr_dp_behavior_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own behavior logs"
    ON mr_dp_behavior_logs FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ----------------------------------------------------------------
-- Progress Policies
-- ----------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own progress" ON mr_dp_progress;
DROP POLICY IF EXISTS "Users can upsert own progress" ON mr_dp_progress;

CREATE POLICY "Users can view own progress"
    ON mr_dp_progress FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can upsert own progress"
    ON mr_dp_progress FOR ALL
    USING (auth.uid() = user_id);

-- ----------------------------------------------------------------
-- Conversations Policies
-- ----------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view own conversations" ON mr_dp_conversations;
DROP POLICY IF EXISTS "Users can insert own conversations" ON mr_dp_conversations;

CREATE POLICY "Users can view own conversations"
    ON mr_dp_conversations FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations"
    ON mr_dp_conversations FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- ================================================================
-- OPTIONAL: TRIGGER FOR AUTO-UPDATING updated_at
-- ================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_mr_dp_progress_updated_at ON mr_dp_progress;
CREATE TRIGGER update_mr_dp_progress_updated_at
    BEFORE UPDATE ON mr_dp_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- SUCCESS MESSAGE
-- ================================================================
DO $$
BEGIN
    RAISE NOTICE 'Mr.DP Intelligence tables created successfully!';
    RAISE NOTICE 'Tables: mr_dp_behavior_logs, mr_dp_progress, mr_dp_conversations';
END $$;
