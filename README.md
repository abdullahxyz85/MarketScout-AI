# MarketScout AI

Autonomous AI market intelligence platform. Users describe a startup idea and a pipeline of AI agents researches the market, competitors, and opportunities.

## Stack

- **Frontend**: Next.js 13 (App Router), TypeScript, Tailwind, Radix UI, Recharts, Framer Motion
- **Backend**: FastAPI, Supabase (Postgres), Authlib (GitHub/Google OAuth), JWT cookie sessions
- **AI**: Fireworks AI (OpenAI-compatible API) — GPT-OSS, DeepSeek, Qwen, MiniMax models
- **Infra**: Docker Compose. The frontend container runs Next.js + an internal nginx reverse proxy on port `5000`, forwarding `/api/*` to the backend and everything else to Next.js.

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
