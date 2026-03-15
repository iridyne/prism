# Prism - Fund Portfolio Optimization Framework

Multi-agent system for optimizing fund holdings in the Chinese market.

## Features

- Multi-source data aggregation (funds, markets, news, sentiment)
- Multi-Agent System (MAS) with Chain-of-Thought reasoning
- Portfolio analysis and rebalancing recommendations
- Event-driven monitoring for black swan events

## Architecture

- **Data Layer**: Fetchers, preprocessing, storage
- **MAS Layer**: Specialized agents with debate-based consensus
- **Analysis Layer**: Portfolio optimization and recommendations
- **Monitoring Layer**: Event detection and alerts
- **API Layer**: REST API and WebSocket

## Setup

```bash
# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
```

## Development

```bash
# Run tests
pytest

# Start API server
python -m src.api.main
```
