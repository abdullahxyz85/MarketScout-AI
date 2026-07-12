# MarketScout AI

> **Autonomous multi-agent market intelligence platform** — powered by AMD Instinct GPUs via Fireworks AI, orchestrated with LangGraph.

Built for the **AMD Developer Hackathon: Act II — Unicorn Track**.

📖 **[Technical Report](https://drive.google.com/file/d/1ftUefJXMdz0EQ1CXO5BvguDeYH4HsDKj/view?usp=sharing)** — full documentation of how the system works (architecture, agent pipeline, scoring methodology, evaluation).

---

## Run It in One Command

No setup, no `.env` editing, no docker-compose. One self-contained image with everything baked in:

```bash
docker run -p 5000:5000 gam5510/marketscout-allinone:latest
```

Then open **http://localhost:5000** — the app is ready immediately (demo mode, no login required).

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
  └── nginx :5000
        ├── /api/agents/* → agent-service  (FastAPI + LangGraph)
        │                        ├── Fireworks AI (AMD Instinct GPUs)
        │                        └── Tavily Search API
        ├── /api/*         → backend       (FastAPI + Supabase)
        └── /*             → Next.js frontend
```

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 13 (App Router), TypeScript, Tailwind CSS, Radix UI, Recharts |
| Backend | FastAPI, Supabase/Postgres, Authlib (GitHub + Google OAuth), JWT cookies |
| Agent Service | FastAPI, LangGraph, 15 AI agents, Fireworks AI, Tavily |
| Infrastructure | Docker, nginx |

---

## LLM Models (all on AMD Instinct GPUs via Fireworks AI)

| Model | Use Case |
|-------|----------|
| DeepSeek V4 Flash | Fast research agents (default) |
| DeepSeek V4 Pro | Strategy, validation, reasoning |
| Qwen V3.7 Plus | SWOT synthesis |
| MiniMax M3 | Long-context report generation |
| GPT-OSS 20B | Lightweight tasks |
| GPT-OSS 120B | Heavy synthesis |

---

## Security

- 7-layer defence-in-depth (input validation, UUID injection prevention, rate limiting, JWT auth, job ownership isolation, secret scanner, prompt injection guard)
- Non-root Docker users in all three containers
- All `.env` files excluded from git

---

## License

MIT
