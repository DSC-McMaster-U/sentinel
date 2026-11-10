# Getting Started

This guide gets you from zero to your first pull request. For the full rules (commit format, review expectations, linking issues), see [CONTRIBUTING.md](../../CONTRIBUTING.md).

## 1. Prerequisites

- [Git](https://git-scm.com/downloads) and a GitHub account with access to the repository
- Python 3 for backend, MCP and retrieval work (the exact version will be pinned by the DevOps workstream)
- Node.js LTS for frontend work, once the frontend app is initialized
- Docker, once the local Docker setup lands

## 2. Clone the Repository

```bash
git clone https://github.com/DSC-McMaster-U/sentinel.git
cd sentinel
```

Copy the example environment file. **Never commit `.env`.**

```bash
cp .env.example .env              # macOS / Linux
Copy-Item .env.example .env       # Windows PowerShell
```

> **TODO (Neel + Parmeet):** add dependency install and run instructions once `requirements.txt` / `pyproject.toml` and Docker are set up.

## 3. Find Your Directory

Find your group in [REPOSITORY_STRUCTURE.md](../architecture/REPOSITORY_STRUCTURE.md), then read the `README.md` in your directory. It explains what belongs there and lists your Sprint 1 TODOs.

| Group | Start here |
| --- | --- |
| Sarthak + Alex | `backend/app/workflows/` |
| Rohit + Ronn | `backend/app/agents/`, `docs/security-checks/` |
| Megh + Behzad | `backend/app/api/`, `backend/app/schemas/`, `mcp-server/` |
| Yug + Toheeb | `backend/app/retrieval/` |
| Neel + Parmeet | `infrastructure/`, `.github/workflows/` |
| Saqib + Nana | `frontend/`, `evaluation/` |

## 4. Create a Feature Branch

Pick or claim your GitHub issue first, then branch from an up-to-date `main`:

```bash
git checkout main
git pull origin main
git checkout -b feat/12-mock-review-endpoint
```

Branch format: `<type>/<issue-number>-short-description`, where type is one of `feat`, `fix`, `docs`, `chore`, `refactor`, `test` or `ci`.

## 5. Commit and Push

```bash
git add <files>
git commit -m "feat: add mock review endpoint (#12)"
git push -u origin feat/12-mock-review-endpoint
```

Commit often and keep each commit focused. Don't commit secrets, `.env` files or generated folders (`node_modules/`, `.venv/`).

## 6. Open a Pull Request

1. On GitHub, open a pull request from your branch into `main`. Open it as a **Draft** if it's still a work in progress.
2. Fill in the PR template and include `Closes #<issue-number>`.
3. Self-review the diff, make sure tests pass, then mark it **Ready for review**.
4. Address every review comment. After approval, the PR is squash-merged and the branch is deleted.

`main` is protected, so all changes go through pull requests.

## Getting Help

Ask in the team Discord, or comment on your issue. If you're stuck for more than a day, say so early. That's what the team is for.
