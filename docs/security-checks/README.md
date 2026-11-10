# docs/security-checks/

One Markdown file per security check, named by ID (e.g. `DEP-001-install-scripts.md`, `CICD-001-unpinned-actions.md`).

Each check should document:

- **ID and title**
- **Why it matters**: the risk, with a real-world example if possible
- **Detection criteria**: exactly what the check looks for
- **Evidence**: what a finding must cite (file, line, package, version)
- **Severity guidance**
- **Safe and unsafe examples**, linked to `evaluation/fixtures/`
- **False-positive limitations**

**Primary owners:** Jin + Behzad (#2)

> **TODO (Sprint 1, Jin + Behzad, #2: "Research and Define Initial Dependency and CI/CD Security Checks"):** at least three dependency checks and three CI/CD checks.
