# CICD-002: Pin External Actions to Immutable Refs

## Why it matters

An action referenced by a movable tag can change after review, allowing different code to run without a workflow change. Pinning to a full commit SHA makes the selected revision immutable. A SHA alone does not prove that the revision is safe or belongs to the expected upstream repository.

Real-world example: in March 2025 an attacker repointed the version tags of `tj-actions/changed-files` (CVE-2025-30066) to a malicious commit that dumped CI secrets into workflow logs. Every workflow referencing the action by tag ran the new code without any change on their side. Workflows pinned to a full SHA of an earlier commit were not affected.

## Detection criteria

Deterministic against changed workflow YAML:

- For each external `uses: OWNER/REPOSITORY@REF`, flag refs that are not exactly 40 hexadecimal characters.
- Apply the same rule to reusable workflows referenced as `OWNER/REPOSITORY/PATH/FILE@REF`.
- Exclude local actions (`./...`) and Docker actions (`docker://...`) from this rule; they need different validation.
- Do not classify a SHA as trusted or verify the hash points to the named upstream repository.

## Evidence

Cite the workflow path and line containing the `uses` reference. Include the action/workflow identifier and observed ref; recommend verifying the upstream revision and pinning its full commit SHA.

## Severity guidance

- **Medium** for a third-party action or reusable workflow pinned only to a tag or branch.
- **High** when an unpinned action receives secrets, write-capable tokens, or runs in a privileged workflow.
- A short SHA is also mutable/incomplete for this rule and should be flagged.

## Examples

- Safe: [third-party action SHA update](../../evaluation/fixtures/safe/cicd-third-party-action-sha-bump.json).
- Safe: [read-only workflow with SHA-pinned actions](../../evaluation/fixtures/safe/cicd-pinned-actions-read-only.json).
- Unsafe: [tag-pinned third-party action](../../evaluation/fixtures/risky/cicd-unpinned-third-party-action.json).

## Deterministic versus agent-assisted

Reference parsing and SHA-shape validation are deterministic. Verifying a SHA's upstream origin, assessing maintainer trust, and reviewing action source or release provenance require external context and are candidates for agent-assisted investigation or a separately permissioned advisory service.

## Limitations and false positives

This check covers workflow `uses` references only; it does not validate composite-action dependencies, container tags, downloaded scripts, or action source. A repository or organization may already enforce full-SHA pinning for actions through its GitHub Actions "allowed actions" policy (reusable workflows are not covered); that setting is not visible in a PR diff, and current fixtures model workflow-file checks only. Some organizations intentionally allow tags under enforced allowlists. SHA pinning does not prevent malicious code at the pinned revision.

## Implementation recommendations

Inspect added/modified workflow lines, parse `uses` values, and accept only a full 40-character hexadecimal commit SHA as pinned. Keep origin verification out of this deterministic finding unless a trusted mapping is supplied.

## References

- [GitHub: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub: Managing GitHub Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
