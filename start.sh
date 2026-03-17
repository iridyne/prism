#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"

PYTHON_VERSION="${PRISM_PYTHON_VERSION:-3.12}"
BACKEND_HOST="${PRISM_BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${PRISM_BACKEND_PORT:-8000}"
FRONTEND_HOST="${PRISM_FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${PRISM_FRONTEND_PORT:-5173}"
SKIP_INSTALL=0

print_help() {
  cat <<'EOF'
Usage: ./start.sh [--skip-install]

Options:
  --skip-install   Skip dependency installation and only start services
  -h, --help       Show this help message

Environment variables:
  PRISM_PYTHON_VERSION   Python version for uv sync (default: 3.12)
  PRISM_BACKEND_HOST     Backend host (default: 0.0.0.0)
  PRISM_BACKEND_PORT     Backend port (default: 8000)
  PRISM_FRONTEND_HOST    Frontend host (default: 0.0.0.0)
  PRISM_FRONTEND_PORT    Frontend port (default: 5173)
EOF
}

for arg in "$@"; do
  case "$arg" in
    --skip-install)
      SKIP_INSTALL=1
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg"
      print_help
      exit 1
      ;;
  esac
done

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1"
    exit 1
  fi
}

wait_for_url() {
  local url="$1"
  local name="$2"

  if ! command -v curl >/dev/null 2>&1; then
    echo "curl not found; skip readiness check for $name"
    return 0
  fi

  for _ in $(seq 1 30); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$name is ready: $url"
      return 0
    fi
    sleep 1
  done

  echo "Warning: $name readiness check timed out: $url"
  return 0
}

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo "Stopping Prism services..."

  if [[ -n "$BACKEND_PID" ]]; then
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
  fi

  if [[ -n "$FRONTEND_PID" ]]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
    wait "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

require_cmd uv
require_cmd npm

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo "Creating .env from .env.example"
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

if [[ "$SKIP_INSTALL" -eq 0 ]]; then
  echo "Installing backend dependencies with uv (Python $PYTHON_VERSION)..."
  (
    cd "$ROOT_DIR"
    uv sync --python "$PYTHON_VERSION"
  )

  echo "Installing frontend dependencies..."
  (
    cd "$FRONTEND_DIR"
    npm install
  )
else
  echo "Skipping dependency installation"
fi

echo "Starting backend..."
(
  cd "$ROOT_DIR"
  uv run uvicorn src.api.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT" --reload
) &
BACKEND_PID=$!

echo "Starting frontend..."
(
  cd "$FRONTEND_DIR"
  npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

wait_for_url "http://127.0.0.1:${BACKEND_PORT}/health" "Backend"
wait_for_url "http://127.0.0.1:${FRONTEND_PORT}" "Frontend"

echo
echo "Prism is running"
echo "Backend:  http://localhost:${BACKEND_PORT}"
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo "API docs: http://localhost:${BACKEND_PORT}/docs"
echo
echo "Press Ctrl+C to stop all services"

wait
