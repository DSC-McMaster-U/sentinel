# infrastructure/cloud-run/

Google Cloud Run service definitions and deployment notes for the backend, MCP server and (optionally) the frontend. The Sprint 1 deliverable is a written proposal, not a live deployment.

**Status:** proposal, for team review (#5). Nothing here is deployed, and no cloud account or credentials are needed to read or review it.

## Goal

Give the team a plan for running Sentinel on Google Cloud by the Sprint 6 beta, and decide the few choices that affect code written now (ports, config, secrets, how the MCP server is reached). The stack below follows the hosting section of [PROJECT.md](../../PROJECT.md).

## Proposed architecture

| Component | Runs on | Notes |
| --- | --- | --- |
| Backend (FastAPI) | Cloud Run service | Public entry point for the dashboard and webhooks. |
| MCP server | Cloud Run service | Private. Only the backend calls it, over Streamable HTTP. |
| Frontend (Next.js) | Vercel or Cloud Run | Open decision, see below. |
| Database | Cloud SQL for PostgreSQL | Not needed until after Sprint 1. `pgvector` for vector search. |
| Container images | Artifact Registry | One repository, one image per service. |
| Secrets | Secret Manager | Mounted into services as environment variables. |
| Logs | Cloud Logging | Cloud Run sends stdout and stderr automatically. |
| Artifacts and reports | Cloud Storage | Later sprints only. |

```
GitHub (webhook, API)
        |
        v
  Backend (Cloud Run, public)  --->  MCP server (Cloud Run, private)
        |                                   |
        v                                   v
  Cloud SQL (Postgres + pgvector)     GitHub API
```

## Why Cloud Run

- **Containers in, URL out.** It runs the same Docker image we build for local development, so there is no separate hosting setup to learn.
- **Scales to zero.** Cloud Run scales a service down to zero instances when idle (the default), so a project with bursty traffic does not pay for idle capacity. Check current Cloud Run pricing before the beta, since it changes. This proposal does not assume any particular free allowance.
- **Per-service identity and IAM.** Each service gets its own service account, which fits the "MCP tools are read-only by default" rule in PROJECT.md.
- **Fits the architecture.** Backend and MCP server are separate stateless HTTP services.

The tradeoff is cold starts after idle periods. For the beta, setting a minimum of one instance on the backend is an option if latency matters, at a small ongoing cost.

## Services

### Backend

- Image built from the backend source and started with `uvicorn`. The dev Dockerfile proposed in PR #19 (`infrastructure/docker/Dockerfile`) already does this, with `--host 0.0.0.0 --port 8000` written into the command.
- **Cloud Run tells the container which port to listen on through the `PORT` environment variable** (8080 by default). The container must listen on `$PORT`, so a hardcoded `8000` will not work as is. The command needs to read `PORT` (for example through a shell-form `CMD`), with 8000 as the local fallback. See "Decisions" below, because this affects how we use `BACKEND_PORT`.
- Public, so it can receive GitHub webhooks and serve the dashboard's API calls. Webhook requests are verified with `GITHUB_WEBHOOK_SECRET`, and the app must still check that signature itself.

### MCP server

- Today it runs over stdio (`mcp.run(transport="stdio")`). To run it on Cloud Run it must be served over HTTP (Streamable HTTP, as planned in PROJECT.md) and listen on `$PORT`.
- **Private.** Require authentication so only the backend's service account can call it (Cloud Run IAM "invoker" role, with the backend sending an identity token).
- Keep it stateless where possible. Cloud Run may start or stop instances at any time, so do not keep session state in memory.

### Frontend

- Next.js can run on Cloud Run as a container, or on Vercel.
- Cloud Run keeps everything in one place and one set of IAM and logging. Vercel is simpler for Next.js and has its own preview deploys per pull request.
- Whichever we pick, the frontend gets the backend URL through `NEXT_PUBLIC_API_BASE_URL`, which is public and must never hold a secret.

## Configuration and secrets

Variables are documented in [ENVIRONMENT_VARIABLES.md](../../docs/onboarding/ENVIRONMENT_VARIABLES.md).

| Kind | Examples | Where it lives in Cloud Run |
| --- | --- | --- |
| Plain config | `APP_ENV`, `LOG_LEVEL` | Environment variables on the service. |
| Secrets | `GITHUB_TOKEN`, `GITHUB_WEBHOOK_SECRET`, `LLM_API_KEY`, `DATABASE_URL` | Secret Manager, exposed to the service as environment variables. |
| Service addresses | `MCP_SERVER_URL` | Set per environment to the MCP service's Cloud Run URL. |

Rules:

- No secret in the image, in the repository or in a `NEXT_PUBLIC_` variable.
- One secret per value, with a separate copy for staging and production.
- Each service account can read only the secrets that service needs.

## Identity and access

Least privilege, one service account per service:

| Service account | Can do |
| --- | --- |
| Backend | Read its own secrets, invoke the MCP service, connect to Cloud SQL, write logs. |
| MCP server | Read its own secrets (for example a GitHub token), write logs. |
| Deployer (GitHub Actions) | Push images to Artifact Registry and deploy Cloud Run revisions. Nothing else. |

## Deployment pipeline

GitHub Actions builds and deploys. The existing CI workflow (lint and tests on pull requests) stays as the gate.

1. **On pull requests:** lint and tests only. No deployment, and no cloud credentials in this workflow.
2. **On merge to `main`:** build each image, push it to Artifact Registry tagged with the commit SHA, deploy to **staging**.
3. **Promote to production:** a manual step (a protected GitHub Environment that needs approval) so a person decides what reaches production.

Authenticate from GitHub Actions with **Workload Identity Federation**, not a long-lived service account key stored as a secret. Pin third-party actions to a full commit SHA, as the repository's workflow guidelines already require.

## Environments

| | Staging | Production |
| --- | --- | --- |
| Deployed from | every merge to `main` | manual promotion |
| Data | test data only | real data |
| Secrets | separate values | separate values |

Start with a single Google Cloud project for the beta if cost or admin overhead is a concern, and use separate Cloud Run services (and secrets) per environment. Separate projects are cleaner if the team can set them up.

## Phased rollout

| Phase | When | What |
| --- | --- | --- |
| 0 | Sprint 1 | This proposal. Local Docker only. Nothing deployed. |
| 1 | Sprint 2 to 3 | Production-style Dockerfiles for backend and MCP server (listen on `$PORT`). Decide who owns the Google Cloud project. |
| 2 | Sprint 3 | Staging deployment of backend and MCP server from GitHub Actions, with Secret Manager. |
| 3 | Sprint 4 to 5 | Cloud SQL with `pgvector` once persistence and retrieval need it. Logging and tracing. |
| 4 | Sprint 6 | Production environment, approvals, beta deployment and demo. |

## Decisions the team needs to make

1. **Who owns the Google Cloud project and billing?** Someone with an account and a budget alert. Nothing else can start until this is answered.
2. **Frontend on Cloud Run or Vercel?**
3. **Public or private backend?** Public is needed for GitHub webhooks, but the dashboard API may want its own authentication.
4. **One cloud project or two (staging and production)?**
5. **Port convention.** Cloud Run provides `PORT`. The repository's `.env.example` uses `BACKEND_PORT`. Proposal: read `PORT` first, fall back to `BACKEND_PORT`, then to 8000 for local runs, and update the environment docs when this lands.
6. **MCP transport.** Moving the MCP server from stdio to Streamable HTTP is required before it can be deployed, and it affects the MCP server's owners (#3).

## Risks

- **Unexpected cost:** set a budget alert on day one and keep minimum instances at zero outside demos.
- **Leaked secrets:** the mitigations are Secret Manager, no keys in the repository and no long-lived deploy keys.
- **A public backend that triggers expensive work:** verify webhook signatures and rate-limit before any LLM calls are live.
- **Prompt-injection through repository content:** out of scope here, but the MCP service should stay read-only and unreachable from the internet.

## Out of scope for Sprint 1

Creating a Google Cloud project, writing Terraform (a stretch goal, see `infrastructure/terraform/`), deploying anything, and production-grade Dockerfiles. Those start in later sprints, once the questions above are answered.
