# backend/app/agents/

Security agents. Each subpackage takes normalized input from the workflow state and returns findings that match `app/schemas/`.

| Subpackage | Responsibility |
| --- | --- |
| `dependency/` | Manifest and lockfile changes, install scripts, suspicious versions |
| `cicd/` | GitHub Actions permissions, unpinned actions, unsafe triggers, secret exposure |
| `release/` | Build and packaging config, source maps, artifacts (later sprint) |
| `synthesis/` | Combine findings, remove duplicates, assign severity and confidence |

**Primary owners:** Neel + Alex (#1) build the Sprint 1 placeholder agent nodes and the synthesis node. Jin + Behzad (#2) define the checks these agents will implement, so coordinate with them.

> **TODO (Sprint 1, Jin + Behzad, #2: "Research and Define Initial Dependency and CI/CD Security Checks"):** document at least three dependency and three CI/CD checks in `docs/security-checks/` before implementing them.
