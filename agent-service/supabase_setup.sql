-- Run this script in your Supabase project:
-- Dashboard → SQL Editor → New query → paste → Run

CREATE TABLE IF NOT EXISTS agent_research_jobs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id           TEXT NOT NULL UNIQUE,
    user_id          TEXT,
    idea             TEXT NOT NULL,
    industry         TEXT,
    innovation_score NUMERIC,
    result           JSONB,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast user history queries
CREATE INDEX IF NOT EXISTS idx_research_jobs_user_id
    ON agent_research_jobs (user_id);

-- Index for fast lookups by job_id (already covered by UNIQUE, but explicit)
CREATE INDEX IF NOT EXISTS idx_research_jobs_job_id
    ON agent_research_jobs (job_id);

-- Index for sorting by date
CREATE INDEX IF NOT EXISTS idx_research_jobs_created_at
    ON agent_research_jobs (created_at DESC);

-- Optional: enable Row Level Security (recommended for production)
-- ALTER TABLE agent_research_jobs ENABLE ROW LEVEL SECURITY;
