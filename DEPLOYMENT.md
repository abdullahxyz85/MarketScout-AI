# MarketScout AI — Deployment Guide

This document covers everything a deployer needs to configure MarketScout AI for
production. Read it fully before starting.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Get Your API Keys](#2-get-your-api-keys)
3. [Environment Variables Reference](#3-environment-variables-reference)
4. [Supabase Database Setup](#4-supabase-database-setup)
5. [OAuth App Setup](#5-oauth-app-setup)
6. [Production Deployment (Docker)](#6-production-deployment-docker)
7. [TLS / HTTPS](#7-tls--https)
8. [Production Checklist](#8-production-checklist)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Docker + Docker Compose | 24+ / 2+ | For containerised deployment |
| Python | 3.11+ | For local / non-Docker deployment |
| Node.js | 20+ | For local frontend development only |
| Git | any | |

**Server requirements (minimum for production):**
- 2 vCPUs, 4 GB RAM
- 20 GB storage
- Ports 80, 443 (and 5000/8000/8001 if not behind a reverse proxy)

---

## 2. Get Your API Keys

### 2.1 Fireworks AI (required)

1. Create an account at **https://fireworks.ai**
2. Go to **API Keys** → **Create Key**
3. Copy the key (starts with `fw_`)

> All LLM inference runs on AMD Instinct GPUs via Fireworks AI. This is the
> only truly required external service.

### 2.2 Tavily Search (recommended)

1. Create an account at **https://tavily.com**
2. Go to **API Keys** → **Create Key**
3. Copy the key (starts with `tvly-`)

> Without Tavily, the system falls back to built-in mock search results.
> Mock results are useful for demos but produce lower-quality research outputs.
> Set `ALLOW_MOCK_SEARCH=false` and `TAVILY_API_KEY=<key>` in production.

### 2.3 Supabase (recommended for persistence)

1. Create a project at **https://supabase.com**
2. Go to **Settings → API**
3. Copy:
   - **Project URL** (e.g. `https://abcdef.supabase.co`)
   - **service_role** key (the long JWT — NOT the anon key)

> Without Supabase, the system runs fine but research results are not
> persisted between restarts (in-memory only).

### 2.4 GitHub OAuth App (for GitHub login)

1. Go to **https://github.com/settings/developers** → **OAuth Apps** → **New OAuth App**
2. Set:
   - **Application name**: MarketScout AI
   - **Homepage URL**: `https://yourdomain.com`
   - **Authorization callback URL**: `https://yourdomain.com/callback/github`
3. Copy **Client ID** and generate a **Client Secret**

### 2.5 Google OAuth App (for Google login)

1. Go to **https://console.cloud.google.com** → **APIs & Services** → **Credentials**
2. Create **OAuth 2.0 Client ID** (type: Web application)
3. Add **Authorized redirect URI**: `https://yourdomain.com/callback/google`
4. Copy **Client ID** and **Client Secret**

---

## 3. Environment Variables Reference

### 3.1 `agent-service/.env`

```env
# ── Required ──────────────────────────────────────────────────────────────────
FIREWORKS_API_KEY=fw_your_key_here

# ── Recommended ───────────────────────────────────────────────────────────────
TAVILY_API_KEY=tvly-your_key_here

# ── Optional: Supabase persistence ────────────────────────────────────────────
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# ── Authentication (must match backend/.env) ──────────────────────────────────
# Generate: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=your_strong_random_secret_min_32_chars

# ── Production settings ───────────────────────────────────────────────────────
AGENT_AUTH_ENABLED=true       # MUST be true in production (enforces JWT validation)
ALLOW_MOCK_SEARCH=false       # MUST be false in production (requires TAVILY_API_KEY)
```

### 3.2 `backend/.env`

```env
# ── Service URLs ──────────────────────────────────────────────────────────────
DOMAIN=https://yourdomain.com          # Public URL of the backend
FRONTEND_DOMAIN=https://yourdomain.com # Public URL of the frontend

# ── OAuth ─────────────────────────────────────────────────────────────────────
OAUTH_GITHUB_CLIENT_ID=your_github_client_id
OAUTH_GITHUB_CLIENT_SECRET=your_github_client_secret
OAUTH_GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
OAUTH_GOOGLE_CLIENT_SECRET=GOCSPX-your_google_secret

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# ── Secrets (MUST match agent-service JWT_SECRET) ─────────────────────────────
JWT_SECRET=your_strong_random_secret_min_32_chars
SESSION_SECRET=another_strong_random_secret_min_32_chars

# ── Environment ───────────────────────────────────────────────────────────────
ENVIRONMENT=production
```

### 3.3 `frontend/.env.local`

```env
# Disable demo mode in production (users must log in)
NEXT_PUBLIC_DEMO_MODE=false
```

> **Generating secrets:**
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```
> Run twice — once for `JWT_SECRET` (same value in both services), once for
> `SESSION_SECRET`.

---

## 4. Supabase Database Setup

Run the SQL setup script in your Supabase SQL editor
(**Dashboard → SQL Editor → New query**):

```bash
# The setup script is at:
cat agent-service/supabase_setup.sql
```

Paste the contents into the Supabase SQL editor and run it. This creates
the `users` and `agent_research_jobs` tables.

---

## 5. OAuth App Setup

### Callback URLs

| Provider | Development | Production |
|----------|-------------|------------|
| GitHub | `http://localhost:5000/callback/github` | `https://yourdomain.com/callback/github` |
| Google | `http://localhost:5000/callback/google` | `https://yourdomain.com/callback/google` |

Update the callback URLs in your OAuth apps before going live.

### backend/.env URLs

Update `DOMAIN` and `FRONTEND_DOMAIN` to your real production URLs. These
are used by Authlib to construct the OAuth redirect URIs.

---

## 6. Production Deployment (Docker)

```bash
# 1. Clone and enter the project
git clone https://github.com/your-org/marketscout-ai.git
cd marketscout-ai

# 2. Configure environment files (see Section 3 above)
cp agent-service/.env.example  agent-service/.env
cp backend/.env.example        backend/.env
cp frontend/.env.example       frontend/.env.local
# Edit each file with production values

# 3. Build and start (production mode: no hot-reload, restart: always)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 4. Check service health
docker compose ps
docker compose logs -f
```

### Useful commands

```bash
# View logs
docker compose logs -f agent-service
docker compose logs -f backend
docker compose logs -f frontend

# Restart a single service
docker compose restart agent-service

# Stop everything
docker compose down

# Rebuild after a code change
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build agent-service
```

---

## 7. TLS / HTTPS

The Docker Compose stack does **not** include TLS termination. For production,
place a TLS-terminating reverse proxy in front of port 5000.

### Option A — Caddy (recommended, automatic TLS)

```caddyfile
yourdomain.com {
    reverse_proxy localhost:5000
}
```

### Option B — nginx + Certbot

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Real-IP $remote_addr;

        # SSE streaming (agent progress)
        proxy_buffering off;
        proxy_read_timeout 600s;
    }
}
```

### Option C — Cloudflare (zero-config)

Point your domain at the server IP and enable Cloudflare proxy. Use
**Full (strict)** SSL mode and a Cloudflare Origin Certificate.

---

## 8. Production Checklist

Before going live, verify each item:

### Critical (security)

- [ ] `AGENT_AUTH_ENABLED=true` in `agent-service/.env`
- [ ] `JWT_SECRET` is identical in `agent-service/.env` and `backend/.env`
- [ ] `JWT_SECRET` and `SESSION_SECRET` are random 32+ char strings (not the dev defaults)
- [ ] `ALLOW_MOCK_SEARCH=false` in `agent-service/.env`
- [ ] All `.env` files are **not** committed to git (check `git status`)
- [ ] TLS is configured and HTTPS is enforced
- [ ] Docs endpoints are disabled (automatic when `AGENT_AUTH_ENABLED=true`)

### Recommended

- [ ] `TAVILY_API_KEY` is set and valid (real web search results)
- [ ] Supabase is configured (persistent research history)
- [ ] OAuth callback URLs match the production domain
- [ ] `DOMAIN` and `FRONTEND_DOMAIN` in `backend/.env` are set to production URLs
- [ ] `NEXT_PUBLIC_DEMO_MODE=false` in `frontend/.env.local`
- [ ] `ENVIRONMENT=production` in `backend/.env`
- [ ] Docker restart policy is `always` (provided by `docker-compose.prod.yml`)
- [ ] Health check endpoints are responding:
  - `curl https://yourdomain.com/api/health`
  - `curl http://localhost:8001/health`
- [ ] Supabase `supabase_setup.sql` has been run

### Performance

- [ ] Consider increasing `--workers` in `docker-compose.prod.yml` (default: 2)
- [ ] Monitor Fireworks AI usage and set spending limits on their dashboard
- [ ] Monitor Tavily API quota on their dashboard

---

## 9. Troubleshooting

### `startup failed: TAVILY_API_KEY must be set`

The agent service is in production mode (`AGENT_AUTH_ENABLED=true`) and requires a
real Tavily key. Either:
- Set `TAVILY_API_KEY` in `agent-service/.env`, **or**
- Set `ALLOW_MOCK_SEARCH=true` (not recommended for production)

### `JWT validation failed` / `401 on all requests`

The `JWT_SECRET` in `agent-service/.env` and `backend/.env` do not match. They must
be identical strings.

### `OAuth callback: state mismatch`

The `SESSION_SECRET` in `backend/.env` is incorrect or has changed between requests.
Make sure it is a stable secret (not regenerated on each restart).

### `Cannot connect to Supabase`

Check that `SUPABASE_URL` ends with `.supabase.co` and that `SUPABASE_SERVICE_KEY`
is the **service_role** key (not the `anon` key). The service role key is required
for server-side database writes.

### Frontend shows blank page / 502

Check that all three services are healthy:
```bash
docker compose ps
docker compose logs frontend
```

The frontend depends on both `backend` and `agent-service` being healthy before it
can serve requests properly.

### Research pipeline hangs / times out

The LangGraph pipeline can take 2–5 minutes for a full 15-agent run. The nginx
`proxy_read_timeout` must be set to at least 600s for SSE connections. See the
nginx config in Section 7.
