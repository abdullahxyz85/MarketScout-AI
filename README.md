# MarketScout AI

> **Autonomous multi-agent market intelligence platform** — powered by AMD Instinct GPUs via Fireworks AI, orchestrated with LangGraph.

Built for the **AMD Developer Hackathon: Act II — Unicorn Track**.

[![CI](https://github.com/your-org/marketscout-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/marketscout-ai/actions/workflows/ci.yml)
[![Docker Build](https://github.com/your-org/marketscout-ai/actions/workflows/docker.yml/badge.svg)](https://github.com/your-org/marketscout-ai/actions/workflows/docker.yml)

📖 **[Technical Report](#)** — full documentation of how the system works (architecture, agent pipeline, scoring methodology, evaluation).

---

## For Judges — Run It in One Command

No setup, no `.env` editing, no docker-compose. One self-contained image with everything baked in:

```bash
docker run -p 5000:5000 gam5510/marketscout-allinone:latest
```

Then open **http://localhost:5000** — the app is ready immediately (demo mode, no login required).

> This all-in-one image bundles the frontend, backend, and agent-service together for convenience. For the real multi-service architecture used in production, see [Architecture](#architecture) and `docker-compose.yml` below.

---

## What it does

You describe a startup idea. MarketScout AI deploys **15 specialised AI agents** in a stateful LangGraph pipeline to research every dimension of the market:

| Step | Agent | Output |
|------|-------|--------|
| 0 | Idea Guard | Validates legality, ethics, feasibility |
| 1 | Research Agent | Market overview, TAM, pain points |
| 2 | Competitor Agent | Competitor profiles, saturation score |
| 3 | Scientific Agent | Literature review, research maturity |
| 4 | Patent Agent | IP landscape, freedom-to-operate |
| 5 | Funding Agent | VC activity, funding rounds |
| 6 | Trend Agent | Market trends, adoption signals |
| 7 | Research Gap Agent | Novelty score, white spaces |
| 8 | SWOT Agent | Full SWOT matrix |
| 9 | Opportunity Agent | Scored opportunity list |
| 10 | Risk Agent | Risk registry with mitigations |
| 11 | Innovation Scoring | Composite score 0–100 with grade |
| 12 | Validation Agent | Go/no-go verdict |
| 13 | Strategy Agent | Go-to-market plan |
| 14 | Report Generator | Full narrative report |

On completion the platform generates on-demand:
- 📄 **PDF report** — formatted market intelligence document
- 🎤 **Pitch deck** — 10-slide investor deck
- 💼 **Business plan** — full investor-ready business plan
- 🔭 **Scenario simulation** — what-if analysis without re-running the pipeline
- ↔️ **Idea comparison** — deterministic side-by-side comparison of two research jobs
- 🧭 **Knowledge graph** — interactive evidence network (vis.js)

All LLM inference runs on **AMD Instinct MI300X GPUs** via [Fireworks AI](https://fireworks.ai).

---

## Architecture

```
browser
  │
  └── nginx :5000 (inside frontend container)
        ├── /api/agents/* → agent-service :8001  (FastAPI + LangGraph)
        │                        ├── Fireworks AI (AMD Instinct GPUs)
        │                        └── Tavily Search API
        ├── /api/*         → backend :8000       (FastAPI + Supabase)
        └── /*             → Next.js :3000
```

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 13 (App Router), TypeScript, Tailwind CSS, Radix UI, Recharts |
| Backend | FastAPI, Supabase/Postgres, Authlib (GitHub + Google OAuth), JWT cookies |
| Agent Service | FastAPI, LangGraph, 15 AI agents, Fireworks AI, Tavily |
| Infrastructure | Docker Compose, nginx |

---

## Quick Start (Docker)

**Prerequisites:** Docker Desktop, Git

```bash
# 1. Clone
git clone https://github.com/your-org/marketscout-ai.git
cd marketscout-ai

# 2. Configure environment
cp agent-service/.env.example  agent-service/.env
cp backend/.env.example        backend/.env
cp frontend/.env.example       frontend/.env.local

# 3. Set your API keys (minimum required: FIREWORKS_API_KEY)
#    See DEPLOYMENT.md for the full configuration guide.
notepad agent-service/.env    # Windows
# nano agent-service/.env     # Linux / macOS

# 4. Start
docker compose up --build
```

| URL | Service |
|-----|---------|
| http://localhost:5000 | App (frontend + reverse proxy) |
| http://localhost:8000/api/docs | Backend API docs |
| http://localhost:8001/docs | Agent Service API docs |

> **Minimum config for a working demo:** set `FIREWORKS_API_KEY` in `agent-service/.env`. OAuth, Supabase, and Tavily are all optional — the platform runs with mock search and anonymous dev mode when they are not configured.

---

## Running Without Docker (Development)

**Prerequisites:** Python 3.11+, Node.js 20+

```bash
# Backend (terminal 1)
cd backend
python -m venv .venv
source .venv/bin/activate        # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Agent Service (terminal 2)
cd agent-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Frontend (terminal 3)
cd frontend
npm install
npm run dev          # runs on http://localhost:3000
                     # rewrites /api/* to backend and /api/agents/* to agent-service
```

---

## Testing

```bash
# Agent service (unit + integration tests)
cd agent-service
python -m pytest tests/ -v

# Security wiring audit
python audit_security.py

# Frontend type-check
cd frontend
npm run typecheck
```

---

## Project Structure

```
marketscout-ai/
├── agent-service/          # Multi-agent research pipeline (FastAPI + LangGraph)
│   ├── agents/             # 15 individual agent modules
│   ├── orchestrator/       # LangGraph StateGraph pipeline
│   ├── services/           # Quality layer, LLM client, utilities
│   ├── schemas/            # Pydantic models + ResearchState
│   ├── tests/              # pytest test suite
│   ├── main.py             # FastAPI entry point
│   ├── router.py           # API routes
│   ├── audit_security.py   # Automated security wiring audit
│   ├── requirements.txt
│   └── .env.example
├── backend/                # Auth + user management (FastAPI + Supabase)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/        # OAuth (GitHub, Google), users
│   │   ├── db/             # Supabase wrappers
│   │   └── dependencies/   # JWT auth dependency
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # Next.js 13 App Router
│   ├── app/                # Pages and layouts
│   ├── components/         # React components
│   ├── lib/                # API clients, stores
│   ├── nginx.conf          # Internal reverse proxy config
│   ├── package.json
│   └── .env.example
├── report/                 # LaTeX academic report (AMD Hackathon submission)
├── docker-compose.yml      # Development stack
├── docker-compose.prod.yml # Production overrides
└── DEPLOYMENT.md           # Production deployment guide
```

---

## LLM Models (all on AMD Instinct GPUs via Fireworks AI)

| Model | Enum | Use Case |
|-------|------|----------|
| DeepSeek V4 Flash | `DEEPSEEK_V4_FLASH` | Fast research agents (default) |
| DeepSeek V4 Pro | `DEEPSEEK_V4_PRO` | Strategy, validation, reasoning |
| Qwen V3.7 Plus | `QWEN_V37_PLUS` | SWOT synthesis |
| MiniMax M3 | `MINIMAX_M3` | Long-context report generation |
| GPT-OSS 20B | `GPT_OSS_20B` | Lightweight tasks |
| GPT-OSS 120B | `GPT_OSS_120B` | Heavy synthesis |

---

## Environment Variables

Copy the `.env.example` files and fill in your credentials:

```bash
cp agent-service/.env.example  agent-service/.env
cp backend/.env.example        backend/.env
cp frontend/.env.example       frontend/.env.local
```

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the complete configuration reference, production settings, and how to obtain each API key.

---

## CI / CD

| Workflow | Trigger | Checks |
|----------|---------|--------|
| `ci.yml` | Push / PR to `main`, `develop` | Agent-service tests, security audit, backend import check, frontend TypeScript |
| `docker.yml` | Push / PR to `main` | Builds all three Docker images |

---

## Security

- 7-layer defence-in-depth (input validation, UUID injection prevention, rate limiting, JWT auth, job ownership isolation, secret scanner, prompt injection guard)
- Non-root Docker users in all three containers
- All `.env` files excluded from git
- Automated security audit via `audit_security.py`

---

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step production deployment instructions.

---

## License

MIT


## Getting started

```bash
 docker compose up --build -d
```

- App: http://localhost:5000 (frontend + `/api/*` proxied to backend)
- Backend directly: http://localhost:8000
- API docs: http://localhost:5000/api/docs

Backend env vars live in `backend/.env` (Supabase keys, OAuth client id/secret, `JWT_SECRET`, `SESSION_SECRET`, `FireworksAPIKey`, `DOMAIN`, `FRONTEND_DOMAIN`). Both containers mount source with hot-reload.

## For frontend devs

- Code lives in `frontend/app` (App Router pages) and `frontend/components`.
- Call the backend via relative paths (`/api/...`) — nginx proxies same-origin, so cookies just work, no CORS setup needed.
- Auth: `GET /api/users/me` returns the current user (401 if not logged in). Login links are plain `<a href="/api/auth/github/login">` / `/api/auth/google/login"` (full navigation, not fetch — OAuth needs a real redirect). After GitHub/Google redirects back to `/callback/github` or `/callback/google`, that page calls the backend to exchange the code and set the session cookie, then routes to `/dashboard`. See `app/callback/github/page.tsx` for the pattern.
- Logout: `POST /api/auth/logout` clears the cookie.
- Dashboard UI (`app/dashboard/**`) currently uses mock data for charts — wire it up to real endpoints as they land.

## For backend devs

- Entry point: `backend/app/main.py` — mounts routers and `SessionMiddleware` (needed for OAuth state).
- Routers live in `backend/app/routers/`; OAuth providers are split under `routers/auth/` (`github.py`, `google.py`) and share the `/api/auth` prefix.
- DB access goes through `backend/app/db/` (thin Supabase wrappers, no ORM). Add new queries there, not inline in routers.
- Auth model: on OAuth callback we upsert a user in Supabase by `github_id`/`google_id`, falling back to matching by `email` so the same person can link both GitHub and Google to one account (see `db/users.py`). A signed JWT is set as an httponly `access_token` cookie (`dependencies/auth.py`); `routers/users.py::get_current_user` reads it back.
- Settings are centralized in `app/config.py` (pydantic `Settings`, loaded from `.env`). Add new env vars there.

## Creating AI agents

Agents are just async functions that call an LLM through `app/services/fireworks_client.py`:

```python
from app.services.fireworks_client import call_llm, stream_llm
from app.schemas.LLMmodels import LLMModels

# one-shot
result = await call_llm(
    prompt="Analyze the competitive landscape for...",
    system_prompt="You are a market research analyst.",
    model=LLMModels.GPT_OSS_120B,
)

# streamed (for SSE/StreamingResponse endpoints)
async for chunk in stream_llm(prompt="...", model=LLMModels.DeepSeek_V4_Flash):
    ...
```
## LLM Models 

- `GPT_OSS_20B`
- `GPT_OSS_120B`
- `DeepSeek_V4_Flash` 
- `DeepSeek_V4_Pro` 
- `Qwen_V37_PLUS` 
- `MINIMAX_M3` 

Guidelines for new agents:

- Pick a model from `LLMModels` (`schemas/LLMmodels.py`) based on cost/quality tradeoff — small models (`GPT_OSS_20B`, `Qwen_V37_PLUS`) for cheap/fast steps, larger ones (`GPT_OSS_120B`, `DeepSeek_V4_Pro`, `MINIMAX_M3`) for synthesis/reasoning steps.
- Keep each agent to one responsibility (research, competitor scan, SWOT, risk scan, etc.) and compose them in a pipeline/orchestrator rather than writing one giant prompt.
- Return structured data (pydantic models) from agents where the frontend needs to render it, not raw text — parse/validate the LLM output before returning it from the endpoint.
- Long-running agents should stream progress via `StreamingResponse` (see `stream_llm` + the `/api/llm-stream-test` example in `main.py`) so the UI can show live status instead of a blocking spinner.
- Put new agent modules under `app/services/` (e.g. `services/agents/competitor_agent.py`), one file per agent.
