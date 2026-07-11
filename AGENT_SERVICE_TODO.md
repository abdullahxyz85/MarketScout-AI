# MarketScout AI — Integration TODO for Frontend & Backend Teams

> This document describes every task needed to connect the multi-agent service
> to the existing frontend and backend so the product reaches final demo quality.
> The agent-service itself is complete and tested. These are integration tasks only.

---

## Context: what the agent-service provides

- **Base URL (dev)** : `http://localhost:8001` (rewritten to `/api/agents/` by Next.js)
- **Base URL (prod)** : `/api/agents/` (nginx proxies to `agent-service:8001`)
- All endpoints are documented at `http://localhost:8001/docs`

### Available endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/research/start` | Start a research job → returns `{ job_id }` |
| GET | `/research/{job_id}/stream` | SSE stream of progress events |
| GET | `/research/{job_id}/result` | Full JSON result when complete |
| GET | `/research/{job_id}/report/pdf` | Download PDF report (binary) |
| POST | `/research/{job_id}/scenario` | Run a what-if scenario simulation |
| GET | `/research/history/{user_id}` | List past research jobs for a user |
| GET | `/health` | Health check |

### Result JSON shape (key fields)

```json
{
  "innovation_score": { "innovation_score": 75, "grade": "B", "scores": { "novelty": 65, ... } },
  "opportunities":    { "opportunity_score": 78, "market_gaps": [...], "target_segments": [...] },
  "risks":            { "risk_score": 72, "overall_risk_level": "high", "risks": [...] },
  "competitors":      { "competitors": [{ "name": "...", "market_share": "15%", "threat_level": "high" }] },
  "research_gaps":    { "novelty_score": 65, "unexplored_opportunities": [...] },
  "swot":             { "strengths": [...], "weaknesses": [...], "opportunities": [...], "threats": [...] },
  "funding":          { "funding_activity_score": 70, "recent_rounds": [...] },
  "scientific":       { "research_maturity_score": 60, "key_papers": [...] },
  "patents":          { "patent_density_score": 15, "white_spaces": [...] },
  "trends":           { "top_trends": [...], "emerging_technologies": [...] },
  "strategy":         { "gtm_strategy": "...", "pricing_model": "...", "innovation_hypotheses": [...] },
  "validation":       { "challenged_assumptions": [...], "validation_experiments": [...] },
  "report":           { "executive_summary": "...", "recommendations": [...] },
  "knowledge_graph":  { "nodes": [...], "links": [...] }
}
```

---

## FRONTEND TASKS

### F-1 — Dashboard overview page (`app/dashboard/page.tsx`) 🔴 HIGH

**Current state**: uses 100% hardcoded mock data (fake company names, fake scores).  
**Goal**: replace mock data with real data from the last research run.

**How**:
1. Import `loadLastResearch` from `@/lib/research-store`
2. In a `useEffect`, call `loadLastResearch()` — returns `{ jobId, result }` or `null`
3. Replace `trendData` / `barData` / `pieData` / `radarData` / `competitors` arrays with real values:

```ts
// At top of component
import { loadLastResearch } from '@/lib/research-store';

const [liveData, setLiveData] = useState<any>(null);

useEffect(() => {
  const stored = loadLastResearch();
  if (stored?.result) setLiveData(stored.result);
}, []);

// Then use liveData?.competitors?.competitors for the PieChart
// liveData?.innovation_score?.innovation_score for the score card
// liveData?.opportunities?.opportunity_score for opportunity card
// liveData?.risks?.risk_score for risk card
// liveData?.funding?.funding_activity_score for funding card
```

4. If `liveData` is null, keep showing the existing mock data as placeholder.

---

### F-2 — Competitors page (`app/dashboard/competitors/page.tsx`) 🟡 MEDIUM

**Current state**: hardcoded 4 fake competitors.  
**Goal**: show real competitors from last research.

**How**:
```ts
import { loadLastResearch } from '@/lib/research-store';

// In component
const stored = loadLastResearch();
const competitors = stored?.result?.competitors?.competitors ?? MOCK_COMPETITORS;
// competitors[i] has: { name, description, market_share, threat_level, strengths, weaknesses }
```

Map over `competitors` to build the cards instead of the static array.

---

### F-3 — Reports/History page (`app/dashboard/reports/page.tsx`) 🟡 MEDIUM

**Current state**: hardcoded fake report list.  
**Goal**: show real past research jobs from the API.

**How**:
```ts
// Fetch history when user is logged in
const userId = 'current-user-id'; // get from your auth context / cookie
const res = await fetch(`/api/agents/research/history/${userId}`);
const history = await res.json(); // array of { job_id, idea, industry, created_at, innovation_score }

// Each item has a PDF download button:
// href={`/api/agents/research/${item.job_id}/report/pdf`}
```

---

### F-4 — Knowledge Graph visualization 🔴 HIGH (Unicorn Track feature)

**Current state**: graph is built by the agent-service but displayed nowhere in the UI.  
**Goal**: add an interactive graph visualization in the research results page.

**How**:
1. Install the library:
   ```bash
   npm install react-force-graph-2d
   ```
2. After a research completes (in `app/dashboard/research/page.tsx`), fetch:
   ```ts
   const res = await fetch(`/api/agents/research/${jobId}/result`);
   const data = await res.json();
   const graphData = data.knowledge_graph; // { nodes: [...], links: [...] }
   ```
3. Add a new section in the results view:
   ```tsx
   import dynamic from 'next/dynamic';
   const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

   // Node colors by type
   const NODE_COLORS: Record<string, string> = {
     idea: '#6366f1', competitor: '#ef4444', paper: '#10b981',
     patent: '#f59e0b', funding: '#06b6d4', trend: '#a855f7',
     opportunity: '#84cc16',
   };

   <div style={{ height: 500, background: '#0f0f1a', borderRadius: 12 }}>
     <ForceGraph2D
       graphData={graphData}
       nodeLabel="label"
       nodeColor={n => NODE_COLORS[n.type] ?? '#94a3b8'}
       nodeRelSize={6}
       linkColor={() => '#334155'}
       backgroundColor="#0f0f1a"
     />
   </div>
   ```

---

### F-5 — Scenario Simulation UI 🟡 MEDIUM

**Current state**: the API endpoint exists but there is no UI to trigger it.  
**Goal**: add a "What-if Scenario" section at the bottom of the research results page.

**How** — add a form with these 6 fields after the results are shown:

```tsx
// State
const [scenario, setScenario] = useState({
  pricing_strategy: 'subscription',
  target_market: '',
  geography: '',
  technology_choice: '',
  team_size: '',
  funding_amount: '',
});
const [scenarioResult, setScenarioResult] = useState(null);

// Submit
const runScenario = async () => {
  const res = await fetch(`/api/agents/research/${jobId}/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario }),
  });
  setScenarioResult(await res.json());
};
```

Display `scenarioResult.overall_recommendation` and `scenarioResult.key_action_items` as a card below the form.

---

### F-6 — Pass `user_id` when starting research 🟡 MEDIUM

**Current state**: `POST /research/start` is called without a `user_id`.  
**Goal**: send the authenticated user's ID so research history is saved per user.

**How** (in `app/dashboard/research/page.tsx`):
```ts
// Get current user first
const userRes = await fetch('/api/users/me');
const user = await userRes.json();

// Then start research with user_id
const body = {
  idea,
  industry,
  healthcare_mode: healthcareMode,
  user_id: user?.id ?? 'anonymous',
};
```

---

## BACKEND TASKS

### B-1 — No backend changes required for agent-service integration

The agent-service is a completely independent microservice. It has its own FastAPI app, its own Supabase client, and its own authentication-free endpoints. The backend does NOT need to be modified to make the multi-agent features work.

---

### B-2 — Optional: expose user ID to frontend for history (already done)

The endpoint `GET /api/users/me` already returns the current user including their `id`. Frontend task F-6 above reads this to pass `user_id` to the agent-service. No backend change needed.

---

### B-3 — ⚠️ REQUIRED: Create Supabase table for research memory

**Without this step, all research results are lost on server restart and the history page returns nothing.**

The SQL script is already written and ready at `agent-service/supabase_setup.sql`.

**Steps:**
1. Open your Supabase project → **SQL Editor** → **New query**
2. Copy-paste the content of `agent-service/supabase_setup.sql`
3. Click **Run**

That's it — no code change needed. The `memory_service.py` detects the table automatically if `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are set in `agent-service/.env`.

The script creates:
```sql
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
-- + 3 indexes (user_id, job_id, created_at)
```

---

## Infrastructure reminder

- **Dev**: `next.config.js` already rewrites `/api/agents/*` → `http://localhost:8001/*`
- **Prod (Docker)**: `nginx.conf` already proxies `/api/agents/` → `agent-service:8001` with SSE support
- **Start all services**: `docker compose up --build -d`
  - Frontend: http://localhost:5000
  - Backend API: http://localhost:8000/api/docs
  - Agent Service API: http://localhost:8001/docs

---

## Priority order

| # | Task | Owner | Impact |
|---|------|-------|--------|
| 1 | **B-3 Create Supabase table** (`supabase_setup.sql`) | Backend/Infra | 🔴 **REQUIRED** — history + memory broken without it |
| 2 | F-4 Knowledge Graph visualization | Frontend | 🔴 Demo WOW factor |
| 3 | F-1 Dashboard with real data | Frontend | 🔴 Judge credibility |
| 4 | F-6 Pass user_id on research start | Frontend | 🟡 History works |
| 5 | F-3 Reports page with real history | Frontend | 🟡 Full feature |
| 6 | F-2 Competitors page real data | Frontend | 🟡 Consistency |
| 7 | F-5 Scenario simulation UI | Frontend | 🟡 Unicorn Track |
