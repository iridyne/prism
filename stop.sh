#!/usr/bin/env bash
set -Eeuo pipefail

PIDS=()

while IFS= read -r line; do
  PIDS+=("$line")
done < <(pgrep -f "uvicorn src.api.main:app" || true)

while IFS= read -r line; do
  PIDS+=("$line")
done < <(pgrep -f "vite.*--host" || true)

if [[ ${#PIDS[@]} -eq 0 ]]; then
  echo "No Prism backend/frontend process found."
  exit 0
fi

echo "Stopping processes: ${PIDS[*]}"
kill "${PIDS[@]}" 2>/dev/null || true
sleep 1

LEFT=()
for pid in "${PIDS[@]}"; do
  if kill -0 "$pid" 2>/dev/null; then
    LEFT+=("$pid")
  fi
done

if [[ ${#LEFT[@]} -gt 0 ]]; then
  echo "Force killing remaining processes: ${LEFT[*]}"
  kill -9 "${LEFT[@]}" 2>/dev/null || true
fi

echo "Prism services stopped."
