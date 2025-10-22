#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api-gateway"
WEB_DIR="$ROOT_DIR/apps/web-frontend"

export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000/v1}"

echo "==> Using NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL"

# --- API ---
echo "==> Bootstrapping API env"
python3 -V
if [ ! -d "$API_DIR/.venv" ]; then
  python3 -m venv "$API_DIR/.venv"
fi
# shellcheck disable=SC1091
source "$API_DIR/.venv/bin/activate"
pip install -U pip >/dev/null
pushd "$API_DIR" >/dev/null
pip install -e . >/dev/null
echo "==> Starting API on :8000"
( uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload ) &
API_PID=$!
popd >/dev/null

# --- Web ---
echo "==> Bootstrapping Web deps"
pushd "$WEB_DIR" >/dev/null
if command -v pnpm >/dev/null 2>&1; then
  pnpm install
  echo "==> Starting Web (pnpm) on :3000"
  ( NEXT_PUBLIC_API_BASE_URL="$NEXT_PUBLIC_API_BASE_URL" pnpm dev ) &
  WEB_PID=$!
else
  npm install
  echo "==> Starting Web (npm) on :3000"
  ( NEXT_PUBLIC_API_BASE_URL="$NEXT_PUBLIC_API_BASE_URL" npm run dev ) &
  WEB_PID=$!
fi
popd >/dev/null

cleanup() {
  echo ""
  echo "==> Shutting down..."
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "---------------------------------------------"
echo "API   : http://localhost:8000 (docs at /v1/docs)"
echo "Web   : http://localhost:3000"
echo "Proxy : Web -> $NEXT_PUBLIC_API_BASE_URL"
echo "Press Ctrl+C to stop."
echo "---------------------------------------------"

# wait on background jobs
wait
