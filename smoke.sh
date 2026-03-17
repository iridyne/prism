#!/usr/bin/env bash
set -Eeuo pipefail

BASE_URL="${PRISM_BASE_URL:-http://localhost:8000}"
TIMEOUT_SECS="${PRISM_SMOKE_TIMEOUT:-90}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1"
    exit 1
  fi
}

require_cmd curl
require_cmd python

echo "[1/5] health check: $BASE_URL/health"
HEALTH_RESP="$(curl -fsS "$BASE_URL/health")"
echo "health: $HEALTH_RESP"

echo "[2/5] create portfolio"
CREATE_PAYLOAD='{"name":"smoke_portfolio","positions":[{"code":"000001","allocation":0.5},{"code":"000002","allocation":0.5}],"preferences":{"risk_level":"medium","horizon_months":12}}'
CREATE_RESP="$(curl -fsS -X POST "$BASE_URL/api/portfolios" -H 'Content-Type: application/json' -d "$CREATE_PAYLOAD")"
PORTFOLIO_ID="$(CREATE_RESP="$CREATE_RESP" python - <<'PY'
import json, os
print(json.loads(os.environ["CREATE_RESP"])["id"])
PY
)"
echo "portfolio_id: $PORTFOLIO_ID"

echo "[3/5] trigger analysis"
ANALYZE_RESP="$(curl -fsS -X POST "$BASE_URL/api/portfolios/$PORTFOLIO_ID/analyze")"
TASK_ID="$(ANALYZE_RESP="$ANALYZE_RESP" python - <<'PY'
import json, os
print(json.loads(os.environ["ANALYZE_RESP"])["task_id"])
PY
)"
echo "task_id: $TASK_ID"

echo "[4/5] poll task status"
START_TS="$(date +%s)"
FINAL_STATUS=""
while true; do
  NOW_TS="$(date +%s)"
  ELAPSED=$((NOW_TS - START_TS))
  if (( ELAPSED > TIMEOUT_SECS )); then
    echo "timeout: task not finished within ${TIMEOUT_SECS}s"
    exit 1
  fi

  STATUS_RESP="$(curl -fsS "$BASE_URL/api/tasks/$TASK_ID")"
  STATUS="$(STATUS_RESP="$STATUS_RESP" python - <<'PY'
import json, os
obj = json.loads(os.environ["STATUS_RESP"])
print(obj["status"])
PY
)"
  PROGRESS="$(STATUS_RESP="$STATUS_RESP" python - <<'PY'
import json, os
obj = json.loads(os.environ["STATUS_RESP"])
print(obj["progress"])
PY
)"
  MESSAGE="$(STATUS_RESP="$STATUS_RESP" python - <<'PY'
import json, os
obj = json.loads(os.environ["STATUS_RESP"])
print(obj["message"])
PY
)"

  echo "task: $STATUS / $PROGRESS% / $MESSAGE"

  if [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]]; then
    FINAL_STATUS="$STATUS"
    break
  fi
  sleep 2
done

if [[ "$FINAL_STATUS" != "completed" ]]; then
  echo "analysis task failed"
  exit 1
fi

echo "[5/5] fetch latest analysis"
ANALYSIS_RESP="$(curl -fsS "$BASE_URL/api/portfolios/$PORTFOLIO_ID/analysis")"
ANALYSIS_SUMMARY="$(ANALYSIS_RESP="$ANALYSIS_RESP" python - <<'PY'
import json, os
obj = json.loads(os.environ["ANALYSIS_RESP"])
print(obj.get("summary", ""))
PY
)"
ANALYSIS_SCORE="$(ANALYSIS_RESP="$ANALYSIS_RESP" python - <<'PY'
import json, os
obj = json.loads(os.environ["ANALYSIS_RESP"])
print(obj.get("overall_score", ""))
PY
)"

echo "analysis_score: $ANALYSIS_SCORE"
echo "analysis_summary: $ANALYSIS_SUMMARY"
echo "SMOKE PASSED"
