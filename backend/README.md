# backend/

The Sentinel backend: a Python FastAPI service that accepts pull request data, runs the LangGraph review workflow, and returns structured security findings.

| Path | What goes here | Primary owners |
| --- | --- | --- |
| `app/api/routes/` | FastAPI routers (HTTP layer only) | Megh + Behzad |
| `app/schemas/` | Shared Pydantic models and contracts | Megh + Behzad (contracts with Sarthak) |
| `app/github/` | GitHub webhook and API integration | Megh + Behzad |
| `app/workflows/` | LangGraph state, routing and graphs | Sarthak + Alex |
| `app/agents/` | Security agents and checks | Rohit + Ronn |
| `app/retrieval/` | Repository context ingestion and search | Yug + Toheeb |
| `app/services/` | Business logic between API and workflows | Megh + Behzad |
| `app/core/` | Config, logging and shared errors | Megh + Behzad (env config with Neel + Parmeet) |
| `tests/unit/`, `tests/integration/` | Tests | Everyone; integration coordinated by Sarthak + Behzad |

## Imports

Run Python commands from inside `backend/` so the `app` package is importable:

```python
from app.schemas import ...
```

> **TODO (Sprint 1, Megh + Behzad: "Set Up FastAPI Backend and Initial MCP Tool Integration"):** create the FastAPI application entry point (e.g. `app/main.py`) with health and mock review endpoints.
>
> **TODO (Sprint 1, Neel + Parmeet: "Configure Local Development Environment, Docker, and GitHub Actions CI"):** add dependency management (`requirements.txt` or `pyproject.toml`) and run instructions here.
