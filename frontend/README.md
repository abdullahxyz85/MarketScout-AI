# MarketScout AI Frontend

MarketScout AI is a Next.js frontend for an autonomous market-intelligence product that turns a startup idea into structured research insights.

## Run Locally

### 1. Prerequisites

- Node.js 18.18+ (Node 20 LTS recommended)
- npm 9+

### 2. Install dependencies

```bash
npm install
```

### 3. Start development server

```bash
npm run dev
```

Open http://localhost:3000.

### 4. Production verification (recommended)

```bash
npm run build
npm run start
```

## Deploy On Vercel

### Option A: Vercel dashboard (recommended)

1. Push this project to a GitHub repository.
2. In Vercel, click **Add New Project** and import the repo.
3. Keep defaults (Vercel auto-detects Next.js):
   - Framework: Next.js
   - Build Command: `next build`
   - Output Directory: `.next` (auto)
4. Click **Deploy**.

### Option B: Vercel CLI

```bash
npm i -g vercel
vercel
```

For production deployment:

```bash
vercel --prod
```

## Notes

- This frontend currently builds successfully as static pages.
- If you later connect backend APIs, add required environment variables in Vercel Project Settings > Environment Variables.
- `metadataBase` is set in app metadata for production URL resolution.
- `vercel.json` is included to keep deployment settings explicit and Vercel-first.

## Scripts

- `npm run dev` - Run local development server
- `npm run build` - Create production build
- `npm run start` - Start production server
- `npm run lint` - Run Next.js lint
- `npm run typecheck` - Run TypeScript checks
