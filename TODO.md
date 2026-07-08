# Backend TODO — wire up the dashboard

Right now only auth works end-to-end (`/api/auth/github`, `/api/auth/google`, `/api/users/me`, `/api/health`). Every other page (`dashboard`, `research`, `competitors`, `reports`, `healthcare`) renders hardcoded mock arrays defined inside the `page.tsx` files — no backend calls exist for them yet. Goal: replace the mocks with real endpoints.

## 1. Research pipeline
- [ ] `POST /api/research` — accepts `{ idea, industry, healthcare_mode }`, kicks off the agent pipeline (Research → Competitor → Market → Trend → SWOT → Opportunity → Risk → Report), returns a `report_id`
- [ ] `GET /api/research/{id}/stream` — `StreamingResponse`/SSE with live per-agent progress (replaces the fake `setInterval` timer in `frontend/app/dashboard/research/page.tsx`)
- [ ] One file per agent under `app/services/agents/` (e.g. `competitor_agent.py`, `swot_agent.py`), each calling `call_llm`/`stream_llm` from `app/services/fireworks_client.py`
- [ ] Agents return structured pydantic output, not raw text — validate before returning to the frontend

## 2. Reports
- [ ] `GET /api/reports` — list of the user's reports (title, industry, score, date, pages, starred)
- [ ] `GET /api/reports/{id}` — full report payload (chart data for `frontend/app/dashboard/reports/page.tsx`)
- [ ] `POST /api/reports/{id}/star`, `DELETE /api/reports/{id}`
- [ ] `GET /api/reports/{id}/download` — PDF/export

## 3. Competitors
- [ ] `GET /api/competitors` — competitor list with `marketShare`, `threat`, `trend`, `revenue` (feeds both `frontend/app/dashboard/competitors/page.tsx` and report charts)

## 4. Dashboard overview
- [ ] `GET /api/dashboard/overview` — aggregated stats for the main dashboard charts (trend, funding-by-sector, market-share pie, capability radar)

## 5. Healthcare mode
- [ ] `GET /api/healthcare/overview` — healthcare demand/regulatory/adoption trend, readiness radar, competitor watchlist

## 6. Data layer
- [ ] Add Supabase tables: `reports`, `competitors`, `research_runs` (only `users` exists today)
- [ ] Add thin DB wrappers in `app/db/` for each table, following the pattern in `app/db/users.py` — no inline queries in routers

## Notes
- Keep routers thin; put business logic in `app/services/`
- Match response shapes to what the frontend already expects (see the mock arrays in each `page.tsx` for exact field names) so the frontend changes are just swapping mock data for a `fetch` call
