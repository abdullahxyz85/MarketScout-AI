# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN mkdir -p public

# NEXT_PUBLIC_* vars are inlined at build time, so they must arrive as
# build args (not just runtime env) — pass them via `docker build --build-arg`
# or docker-compose's `build.args`.
ARG NEXT_PUBLIC_DEMO_MODE=false
ARG NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_DEMO_MODE=${NEXT_PUBLIC_DEMO_MODE}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM node:20-alpine AS runner

RUN apk add --no-cache nginx

WORKDIR /app

# Copy built assets from builder
COPY --from=builder /app/.next      ./.next
COPY --from=builder /app/public     ./public
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/next.config.js ./

COPY nginx.conf /etc/nginx/http.d/default.conf
COPY start.sh   /start.sh
RUN chmod +x /start.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD wget -qO- http://localhost:5000/ | head -c 50 || exit 1

CMD ["/start.sh"]
