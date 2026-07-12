# All-in-one image

Bundles frontend + backend + agent-service + nginx into a single container
(`Dockerfile.allinone` at the repo root) so it runs with one `docker run` —
built for handing a working demo to judges/reviewers without them needing to
stand up `docker-compose.yml` and three separate `.env` files.

Not for production — that's `docker-compose.prod.yml`.

## Rebuilding

Secrets are passed as `--build-arg` at build time (never hardcoded in the
Dockerfile) and pulled from the existing `backend/.env` / `agent-service/.env`
files, which are gitignored:

```bash
docker build -f Dockerfile.allinone \
  --build-arg SUPABASE_URL="$(grep ^SUPABASE_URL= backend/.env | cut -d= -f2-)" \
  --build-arg SUPABASE_SERVICE_KEY="$(grep ^SUPABASE_SERVICE_KEY= backend/.env | cut -d= -f2-)" \
  --build-arg OAUTH_GOOGLE_CLIENT_ID="$(grep ^OAUTH_GOOGLE_CLIENT_ID= backend/.env | cut -d= -f2-)" \
  --build-arg OAUTH_GOOGLE_CLIENT_SECRET="$(grep ^OAUTH_GOOGLE_CLIENT_SECRET= backend/.env | cut -d= -f2-)" \
  --build-arg OAUTH_GITHUB_CLIENT_ID="$(grep ^OAUTH_GITHUB_CLIENT_ID= backend/.env | cut -d= -f2-)" \
  --build-arg OAUTH_GITHUB_CLIENT_SECRET="$(grep ^OAUTH_GITHUB_CLIENT_SECRET= backend/.env | cut -d= -f2-)" \
  --build-arg JWT_SECRET="$(grep ^JWT_SECRET= backend/.env | cut -d= -f2-)" \
  --build-arg SESSION_SECRET="$(grep ^SESSION_SECRET= backend/.env | cut -d= -f2-)" \
  --build-arg FIREWORKS_API_KEY="$(grep ^FIREWORKS_API_KEY= agent-service/.env | cut -d= -f2-)" \
  --build-arg TAVILY_API_KEY="$(grep ^TAVILY_API_KEY= agent-service/.env | cut -d= -f2-)" \
  -t gam5510/marketscout-allinone:latest .

docker push gam5510/marketscout-allinone:latest
```

## Running (what judges do)

```bash
docker run -p 5000:5000 gam5510/marketscout-allinone:latest
```

Open http://localhost:5000 — `NEXT_PUBLIC_DEMO_MODE=true` is baked into the
frontend build, so the login screen is bypassed and research runs work
immediately (agent-service auth is disabled by default, `AGENT_AUTH_ENABLED=false`).

**Security note:** this image bakes real Supabase/OAuth/JWT/Fireworks/Tavily
keys as plain environment variables (visible via `docker inspect` /
`docker history`). It is a throwaway hackathon demo package, not a template
for production deploys. Rotate all of these keys once the review period ends.
