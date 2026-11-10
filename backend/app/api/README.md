# backend/app/api/

The HTTP layer. `routes/` holds FastAPI routers, one module per resource (e.g. `health.py`, `reviews.py`, `findings.py`, and later `github_webhook.py`).

Keep routes thin. Validate input with `app/schemas/`, then delegate to `app/services/` or `app/workflows/`. Do not put business logic here.

**Primary owners:** Megh + Behzad

> **TODO (Sprint 1, Megh + Behzad: "Set Up FastAPI Backend and Initial MCP Tool Integration"):** health endpoint and mock review endpoint.
