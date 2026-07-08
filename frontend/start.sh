#!/bin/sh
set -e

npm run dev -- -p 3000 &

nginx -g "daemon off;"
