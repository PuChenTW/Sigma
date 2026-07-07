#!/bin/sh
set -eu

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
API_PORT="${E2E_API_PORT:-18080}"
WEB_PORT="${E2E_WEB_PORT:-13000}"
API_URL="http://127.0.0.1:$API_PORT"

cd "$ROOT_DIR"
rm -f .local/e2e-studio-api.json

STUDIO_API_DATA_FILE=.local/e2e-studio-api.json uv run uvicorn studio_api.main:app --app-dir src --host 127.0.0.1 --port "$API_PORT" &
API_PID="$!"

cleanup() {
  kill "$API_PID" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

for _ in $(seq 1 120); do
  if ! kill -0 "$API_PID" >/dev/null 2>&1; then
    echo "API server exited before becoming ready." >&2
    wait "$API_PID"
    exit 1
  fi
  if curl -fsS "$API_URL/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

curl -fsS "$API_URL/health" >/dev/null

cd "$ROOT_DIR/frontend"
NEXT_PUBLIC_API_BASE_URL="$API_URL" npx next dev --hostname 127.0.0.1 --port "$WEB_PORT"
