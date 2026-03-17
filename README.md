# Prism - AI Portfolio Analysis (MVP)

Prism is an AI-driven fund portfolio analysis system for the Chinese market.
It is designed for research and decision support, not for real-time trading.

## What Works (MVP)

1. Wizard-based portfolio setup:
   - Portfolio name
   - Fund codes and allocations
   - Risk preference and investment horizon
2. Async analysis workflow:
   - `POST /api/portfolios/{id}/analyze` returns a `task_id`
   - Background job runs `PrismKernel`
   - Progress is pushed via WebSocket
3. Dashboard consumption:
   - View portfolio details
   - Track task status (`queued/running/completed/failed`)
   - Read latest analysis result

## Architecture

1. Frontend (TypeScript + React + Vite):
   - Wizard
   - Dashboard
   - Task progress via WebSocket
2. Backend (Python + FastAPI):
   - REST APIs for portfolios, analysis, task status
   - WebSocket endpoint for progress events
3. Core Engine (Python):
   - `PrismKernel` with LangGraph orchestration
   - Fetchers for fund and market data
   - Analysis synthesis to structured recommendations
4. Storage:
   - SQLite for MVP
   - PostgreSQL via async driver for production

## Key Endpoints

1. `POST /api/portfolios`
2. `GET /api/portfolios`
3. `GET /api/portfolios/{id}`
4. `POST /api/portfolios/{id}/analyze`
5. `GET /api/tasks/{task_id}`
6. `GET /api/portfolios/{id}/analysis`
7. `WS /ws/tasks/{task_id}`

## Local Setup

```bash
# One-command start (backend + frontend)
./start.sh

# Fast start without reinstalling dependencies
./start.sh --skip-install
 
# Override ports/host
PRISM_BACKEND_PORT=8001 PRISM_FRONTEND_PORT=5174 ./start.sh

# Or run services separately:
# Install backend dependencies
uv sync

# Initialize env
cp .env.example .env

# Run backend
uv run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
# Run frontend
cd frontend
npm install
npm run dev
```

## Quality Checks

```bash
# Backend
ruff check src
python -m compileall src

# Frontend
cd frontend
npm run lint
npm run build
```

## Notes

1. This project does not execute trades and does not connect to brokerage APIs.
2. Outputs are for research/decision support only and not investment advice.
3. Black swan monitoring and periodic snapshot service are planned for next phase.
