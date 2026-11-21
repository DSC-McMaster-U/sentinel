# CICD-001: Minimize `GITHUB_TOKEN` Permissions

## Why it matters

Every permission granted to `GITHUB_TOKEN` increases the impact of a compromised workflow step or action. GitHub recommends granting the token the minimum access needed; a workflow-level `write-all` or broad write scope can let untrusted or compromised code modify repository resources.

## Detection criteria

Deterministic against changed GitHub Actions workflow YAML:

- Flag `permissions: write-all` at workflow or job level.
- Flag explicit write scopes (`contents: write`, `pull-requests: write`, etc.) as a review signal, with severity based on event and job context.
- Do not flag `permissions: read-all` or explicit read-only scopes solely for being explicit.
- Treat omitted permissions as unknown: effective defaults depend on repository and organization settings, which are not present in a PR diff.

## Evidence

Cite the workflow path and line containing the broad permission declaration. Include the affected job when job-level permissions are used. The finding should explain the scope and recommend a minimal permission map.

## Severity guidance

- **High** for `write-all` or broad write scopes in a workflow handling untrusted PR content or exposing secrets.
- **Medium** for unnecessary broad write scopes when no untrusted input or secret exposure is visible.
- **Low** for narrow write scopes that appear unrelated to the job's stated purpose; manual review is appropriate.

## Examples

- Safe: [read-only pinned test workflow](../../evaluation/fixtures/safe/cicd-pinned-actions-read-only.json).
- Unsafe: [privileged PR preview workflow](../../evaluation/fixtures/risky/cicd-pull-request-target-head-checkout.json); its `write-all` scope is also a signal for this check.
- Focused unsafe case: [workflow with write-all permissions](../../evaluation/fixtures/risky/cicd-write-all-permissions.json).

## Deterministic versus agent-assisted

Parsing permission keys and detecting `write-all` are deterministic. Deciding whether an individual write scope is necessary needs workflow intent, repository settings, and sometimes deployment policy; an agent can explain the concern but should not assert excess solely from the scope name.

## Limitations and false positives

The rule cannot calculate effective permissions after organization/repository policy, event-specific restrictions, reusable workflows, or implicit defaults. For example, `pull_request` runs from forks receive a read-only `GITHUB_TOKEN` whatever the workflow requests, so a `write-all` declaration there mainly affects same-repository branches. A write permission may be required for publishing, release creation, or deployment. YAML anchors, expressions, and unusual formatting can complicate parsing. Report observed declarations and keep necessity judgments reviewable.

## Implementation recommendations

Parse changed `.github/workflows/*.{yml,yaml}` files, retain source line numbers, and inspect workflow- and job-level `permissions`. Normalize `write-all`, `read-all`, and mapping values. Do not infer effective privileges from missing declarations.

## References

- [GitHub: Automatic token authentication and permissions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)
- [GitHub: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
