# .github/workflows/

GitHub Actions workflows (`*.yml`) for linting, tests and, later, Docker builds and deployment.

Sentinel's own CI should pass Sentinel's checks:

- Set least-privilege `permissions:` (e.g. `contents: read`) on every workflow.
- Pin third-party actions to a full commit SHA.
- Avoid `pull_request_target` with untrusted code, and never expose secrets to fork PRs.

**Primary owners:** Neel + Parmeet

> **TODO (Sprint 1, Neel + Parmeet: "Configure Local Development Environment, Docker, and GitHub Actions CI"):** automated lint and test workflow. Once it exists, mark it as a required status check on `main`.
