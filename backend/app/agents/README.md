# backend/app/agents/

Security agents. Each subpackage takes normalized input from the workflow state and returns findings that match `app/schemas/`.

| Subpackage | Responsibility |
| --- | --- |
| `dependency/` | Manifest and lockfile changes, install scripts, suspicious versions |
| `cicd/` | GitHub Actions permissions, unpinned actions, unsafe triggers, secret exposure |
| `release/` | Build and packaging config, source maps, artifacts (later sprint) |
| `synthesis/` | Combine findings, remove duplicates, assign severity and confidence |

**Primary owners:** Rohit + Ronn. The mock agent nodes for Sprint 1 are wired in by Sarthak + Alex, so coordinate interfaces with them.

> **TODO (Sprint 1, Rohit + Ronn: "Research and Define Initial Dependency and CI/CD Security Checks"):** document at least three dependency and three CI/CD checks in `docs/security-checks/` before implementing them.
