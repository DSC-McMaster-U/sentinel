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

## Initial CI/CD checks (#2)

- [CICD-001: Minimize `GITHUB_TOKEN` permissions](CICD-001-minimum-token-permissions.md)
- [CICD-002: Pin external actions to immutable refs](CICD-002-pin-actions-to-immutable-refs.md)
- [CICD-003: Keep untrusted PR code out of privileged workflows](CICD-003-untrusted-pr-code-in-privileged-workflows.md)

The representative safe and risky PR fixtures are linked from each check. These checks target changed GitHub Actions workflow YAML. They do not establish repository-wide effective permissions, action provenance, or complete data flow through custom actions and reusable workflows.

**Primary owners:** Jin + Behzad (#2)

> **Dependency follow-up:** Jin's DEP-001–003 specifications are being delivered in [PR #25](https://github.com/DSC-McMaster-U/sentinel/pull/25); combine them with the CI/CD checks above to complete #2.
