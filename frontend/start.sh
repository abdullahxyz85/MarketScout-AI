#!/bin/sh
set -e

# Start Next.js in production mode on port 3000 (nginx proxies from 5000)
npm run start -- -p 3000 &

# Start nginx as the primary process (keeps container alive)
nginx -g "daemon off;"
