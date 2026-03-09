# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Status

This project is in early setup (Phase 1 of the roadmap). The architecture and database schema are planned but no application code has been written yet. See `roadmap.md` for the phased implementation plan and `docs/architecture.md` for the system design.

## Tech Stack

- **Language**: Python 3.14 (managed via pyenv, see `.python-version`)
- **API**: FastAPI + Uvicorn
- **Database**: PostgreSQL via SQLAlchemy + psycopg + Alembic migrations
- **Queue**: Redis + RQ (Redis Queue)
- **LLM**: OpenAI (or compatible provider)
- **Testing**: pytest

## Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv/bin/activate.fish for fish shell

# Install dependencies (once pyproject.toml/requirements are added)
pip install -e ".[dev]"
```

## Planned Commands

Once implemented, the expected development commands are:

```bash
# Run API server
uvicorn app.main:app --reload

# Run background worker
rq worker

# Run tests
pytest

# Run a single test
pytest tests/path/to/test_file.py::test_name

# Run database migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"
```

## Architecture

Event-driven system with separated concerns:

1. **API Layer** (`app/`) — FastAPI app handling incident ingestion (`POST /incidents`) and retrieval (`GET /incidents/{id}`, `GET /incidents`). On incident creation, stores to DB and enqueues an RQ job.

2. **Database Layer** — Three core tables:
   - `incidents`: id, service_name, alert_type, status, created_at
   - `incident_logs`: id, incident_id, message, timestamp
   - `analysis_results`: id, incident_id, summary, suspected_service, confidence, recommendations

3. **Worker Service** — Consumes RQ jobs, fetches incident data from DB, calls the analysis engine, stores results back to DB.

4. **Analysis Engine** (`services/analyzer.py`) — LLM-based service with functions `summarize_logs()`, `detect_root_cause()`, `generate_recommendations()`.

The key design principle: ingestion is synchronous and fast; heavy LLM analysis runs asynchronously via the queue.

## Infrastructure

Services run via Docker Compose: `api`, `postgres`, `redis`, `worker`. These are not yet defined — add them as Phase 1 is completed.
