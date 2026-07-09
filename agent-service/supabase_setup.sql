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

-- ─────────────────────────────────────────────────────────────────
-- Agent Events table — structured per-agent activity log
-- Populated by services/agent_logger.py (fire-and-forget, async)
-- ─────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS agent_events (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id       TEXT NOT NULL,
    agent_name   TEXT NOT NULL,
    event_type   TEXT NOT NULL,       -- 'start' | 'complete' | 'error' | 'pipeline_complete'
    duration_s   NUMERIC,             -- wall-clock seconds the agent ran
    scores       JSONB DEFAULT '{}',  -- numeric scores extracted from agent output
    output_keys  JSONB DEFAULT '[]',  -- top-level keys present in result dict
    error_msg    TEXT,                -- set when event_type = 'error'
    timestamp    TIMESTAMPTZ DEFAULT NOW()
);

-- Fast queries: all events for a given job
CREATE INDEX IF NOT EXISTS idx_agent_events_job_id
    ON agent_events (job_id);

-- Fast queries: all events for a given agent name (performance analysis)
CREATE INDEX IF NOT EXISTS idx_agent_events_agent_name
    ON agent_events (agent_name);

-- Fast queries: filter by event type (e.g. all errors)
CREATE INDEX IF NOT EXISTS idx_agent_events_event_type
    ON agent_events (event_type);

-- Fast queries: recent events sorted by time
CREATE INDEX IF NOT EXISTS idx_agent_events_timestamp
    ON agent_events (timestamp DESC);

-- ─────────────────────────────────────────────────────────────────
-- Useful analytics queries (read-only examples)
-- ─────────────────────────────────────────────────────────────────

-- Average duration per agent (last 7 days):
-- SELECT agent_name, ROUND(AVG(duration_s)::numeric, 2) AS avg_s, COUNT(*) AS runs
-- FROM agent_events
-- WHERE event_type = 'complete' AND timestamp > NOW() - INTERVAL '7 days'
-- GROUP BY agent_name ORDER BY avg_s DESC;

-- All errors in the last 24 hours:
-- SELECT timestamp, job_id, agent_name, error_msg
-- FROM agent_events
-- WHERE event_type = 'error' AND timestamp > NOW() - INTERVAL '24 hours'
-- ORDER BY timestamp DESC;

-- Innovation score trend over time:
-- SELECT timestamp, job_id, (scores->>'innovation_score')::numeric AS score
-- FROM agent_events
-- WHERE agent_name = 'PIPELINE' AND event_type = 'pipeline_complete'
-- ORDER BY timestamp DESC LIMIT 50;
