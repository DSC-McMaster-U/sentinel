# Environment Variables

Sentinel reads its local configuration from environment variables. The full list lives in the root [`.env.example`](../../.env.example). This page explains what each one is for and whether you need it.

## Short version

**You don't need a `.env` file to run the backend tests or the mock review API in Sprint 1.** Nothing in the unit tests reads one.

The only variable any code reads today is `GITHUB_TOKEN`, and it is optional. Everything else in `.env.example` is reserved for later sprints.

## Setup

```bash
cp .env.example .env              # macOS / Linux
Copy-Item .env.example .env       # Windows PowerShell
```

- **Never commit `.env`.** It is gitignored. See [SECURITY.md](../../SECURITY.md).
- Every value in `.env.example` is a placeholder. Never put a real secret in `.env.example`.
- Never put a secret in a variable that starts with `NEXT_PUBLIC_`. Next.js sends those to the browser.

## Reference

"Read by code" means a line of code on `main` reads the variable. Status is current as of the date this page was written, so check the code if it matters.

| Variable | Example value | Used by | Needed in Sprint 1? | Read by code? |
| --- | --- | --- | --- | --- |
| `APP_ENV` | `development` | Backend | No | No |
| `LOG_LEVEL` | `INFO` | Backend | No | No |
| `BACKEND_HOST` | `127.0.0.1` | Backend | No | No |
| `BACKEND_PORT` | `8000` | Backend | No | No |
| `MCP_SERVER_URL` | `http://localhost:8001/mcp` | Backend (MCP client) | No | No |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Frontend | No | No |
| `DATABASE_URL` | `postgresql://sentinel:change-me@localhost:5432/sentinel` | Backend | No | No |
| `GITHUB_TOKEN` | *(empty)* | MCP server | Optional | Yes (`mcp-server`) |
| `GITHUB_WEBHOOK_SECRET` | *(empty)* | Backend | No | No |
| `LLM_API_KEY` | *(empty)* | Agents | No | No |

## What each variable does

### Application

- **`APP_ENV`**: meant to tell the app whether it is running locally or deployed. Not read yet.
- **`LOG_LEVEL`**: how much the backend logs. When logging is added, use a standard Python level: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. Not read yet.

### Backend (FastAPI)

- **`BACKEND_HOST`**, **`BACKEND_PORT`**: where the backend listens. The backend does not read these yet. When you start it by hand it uses uvicorn's defaults, `127.0.0.1` and port `8000` (the dev Dockerfile in `infrastructure/docker/` passes `--host 0.0.0.0` and uses `${PORT:-8000}` as the port instead):

  ```bash
  cd backend
  python -m uvicorn app.main:app --reload
  ```

  To use a different port for now, pass it to uvicorn (`--port 8010`).

### MCP server

- **`MCP_SERVER_URL`**: the address a client would use to reach the MCP server over HTTP. In Sprint 1 the MCP server runs over **stdio** (`mcp.run(transport="stdio")`), so there is no URL to connect to and nothing reads this variable. It will matter only if the server is later served over HTTP, for example as its own Cloud Run service.

### Frontend (Next.js)

- **`NEXT_PUBLIC_API_BASE_URL`**: the backend address the browser calls. It must match wherever the backend is running. The frontend app has not been initialized yet.

### Database

- **`DATABASE_URL`**: connection string for PostgreSQL. Postgres is not used in Sprint 1. The password in the example (`change-me`) is a placeholder. Use your own for a real database and never commit it.

### GitHub

- **`GITHUB_TOKEN`**: optional token the MCP server sends with its GitHub API calls.
  - **Without it**, public repositories still work, but GitHub applies its lower unauthenticated rate limit.
  - **With it**, you get a higher rate limit and can read private repositories you have access to.
  - Use a fine-grained personal access token with **read-only** access and only the repositories you need. Do not reuse a token that can write.
  - The MCP tests mock GitHub, so they pass without a token.
- **`GITHUB_WEBHOOK_SECRET`**: shared secret used to verify that incoming webhook requests really come from GitHub. Needed when live PR intake starts (Sprint 2). Not used in Sprint 1.

### LLM provider

- **`LLM_API_KEY`**: key for the model provider. Sprint 1 agents are mocked, so you do not need one. Keep it out of logs, test fixtures and commits.

## Adding or renaming a variable

Variable names in `.env.example` are proposals, and the workstream that owns the code may change them. When you add, rename or remove one:

1. Update `.env.example` in the same pull request.
2. Update the table in this file.
3. Use an obviously fake placeholder value. Never a real secret.
4. If the code reads it, read it in one place (for example `backend/app/core/`) instead of scattering `os.environ` calls.

Questions about conventions go to the #5 owners (Saqib + Ronn).
