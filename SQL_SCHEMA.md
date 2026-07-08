# MarketScout AI — Supabase SQL schema

Run these statements in the Supabase SQL editor (in order) to create the tables required
by `TODO.md` item 6. Only the `users` table exists today — everything below is new.

## Extension (for `gen_random_uuid()`)

```sql
create extension if not exists pgcrypto;
```

## `reports`

Stores the final assembled output of a research run: scores, chart data (trend, funding
by sector, market-share pie, SWOT, healthcare block, etc.) and metadata used by
`frontend/app/dashboard/reports/page.tsx` and the main dashboard.

```sql
create table if not exists reports (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    research_run_id uuid,
    title text not null,
    description text,
    industry text,
    healthcare_mode boolean not null default false,
    score numeric not null default 0,
    opportunity_score numeric not null default 0,
    risk_level text,
    pages integer not null default 1,
    starred boolean not null default false,
    chart_data jsonb not null default '{}'::jsonb,
    created_at double precision not null default extract(epoch from now())
);

create index if not exists reports_user_id_idx on reports(user_id);
create index if not exists reports_created_at_idx on reports(created_at desc);
```

## `research_runs`

Tracks a single async agent-pipeline execution (research → competitor → market → trend →
SWOT → opportunity → risk → report). `GET /api/research/{id}/stream` polls this row for
live progress; on completion it points at the `reports` row it produced.

```sql
create table if not exists research_runs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    idea text not null,
    industry text,
    healthcare_mode boolean not null default false,
    status text not null default 'pending', -- pending | running | completed | failed
    current_agent text,
    progress integer not null default 0,
    report_id uuid references reports(id) on delete set null,
    error text,
    created_at double precision not null default extract(epoch from now()),
    updated_at double precision not null default extract(epoch from now())
);

create index if not exists research_runs_user_id_idx on research_runs(user_id);
```

## `competitors`

Competitor rows produced by the Competitor Agent for a given report; also queried
directly by `GET /api/competitors` for the competitor-landscape page.

```sql
create table if not exists competitors (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    report_id uuid references reports(id) on delete cascade,
    name text not null,
    segment text,
    market_share numeric,
    threat text, -- low | medium | high
    trend text,  -- up | down | stable
    revenue text,
    created_at double precision not null default extract(epoch from now())
);

create index if not exists competitors_user_id_idx on competitors(user_id);
create index if not exists competitors_report_id_idx on competitors(report_id);
```

## Notes

- `created_at`/`updated_at` are stored as epoch-seconds `double precision` to match the
  existing `users.created_at` convention used in `app/schemas/users.py`.
- All access goes through the Supabase **service key** from the FastAPI backend
  (`app/db/supabase_client.py`), so table-level RLS policies are optional; add them if you
  ever expose these tables to the Supabase anon/public key.
- `research_runs.report_id` is nullable and only set once the pipeline finishes
  successfully; `reports.research_run_id` is stored as plain `uuid` (no FK) to avoid a
  circular foreign key between the two tables.
