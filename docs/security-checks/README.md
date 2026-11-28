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

## Release checks

The Release agent currently returns placeholder output. These specifications use Dockerfile changes already routed to it. They require read-only access to the patch and, when a hunk omits stage definitions or instruction boundaries, the Dockerfile text at the PR head. A diff line mapper and a Dockerfile instruction tokenizer should preserve physical line spans across continuations. REL-002 also needs shell tokenization for command and pipeline boundaries. No registry queries, builds or external downloads are needed.

Only report complete instructions touched by added lines. Skip deleted instructions and ambiguous or truncated input. The existing .dockerignore route carries no instructions for these rules. Extending coverage to Containerfile, Dockerfile variants or release workflows would require reviewing their routing and syntax first.

- [REL-001 · Mutable base image](REL-001-mutable-base-image.md)
- [REL-002 · Remote script piped to a shell](REL-002-remote-script-pipeline.md)
- [REL-003 · Remote artifact without a checksum](REL-003-remote-add-integrity.md)
