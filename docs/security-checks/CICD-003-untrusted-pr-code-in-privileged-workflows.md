# CICD-003: Keep Untrusted PR Code Out of Privileged Workflows

## Why it matters

`pull_request_target` and `workflow_run` workflows can run with base-repository privileges, including secrets and a write-capable token. Checking out or executing untrusted pull-request code in that context can let an attacker steal credentials or modify the repository (the “pwn request” pattern).

Real-world example: in December 2024 attackers opened pull requests with crafted branch names that injected shell commands into a `pull_request_target` workflow in the `ultralytics/ultralytics` repository, running attacker-controlled code with base-repository privileges. This led to compromised PyPI releases (8.3.41 and 8.3.42) that shipped a cryptominer.

## Detection criteria

Deterministic risk signals in changed workflow YAML:

- Flag `pull_request_target` or `workflow_run` workflows that check out a PR head, fork ref, PR-controlled artifact, or other untrusted content.
- Raise severity when a subsequent step executes scripts/build/install commands from that content, or when secrets or write permissions are exposed to those steps.
- Treat `pull_request_target` alone as a review signal, not proof of vulnerability; labeling/commenting-only workflows can use it safely.
- Flag direct interpolation of attacker-controlled GitHub context values into `run:` scripts as a related injection signal, with context-specific evidence.

## Evidence

Cite separate lines for the privileged trigger, untrusted checkout/artifact use, and execution or secret/permission exposure. Explain which code is untrusted and how it reaches a privileged step.

## Severity guidance

- **Critical** when untrusted PR code executes in a privileged workflow with secrets or write-capable token access.
- **High** when untrusted code executes in a privileged workflow, even without an obvious secret reference.
- **Medium** for a privileged trigger plus checkout of PR content where execution cannot be established from the changed lines.
- No finding for a privileged trigger that only performs safe metadata operations without consuming untrusted code.

## Examples

- Safe: [read-only `pull_request` test workflow](../../evaluation/fixtures/safe/cicd-pinned-actions-read-only.json).
- Safe (close pair): [`pull_request_target` labeler that never checks out PR code](../../evaluation/fixtures/safe/cicd-pull-request-target-labeler.json).
- Unsafe: [PR head checkout and execution under `pull_request_target`](../../evaluation/fixtures/risky/cicd-pull-request-target-head-checkout.json).

## Deterministic versus agent-assisted

Trigger, checkout ref expressions, `run` commands, permissions, and explicit secret references can be parsed deterministically. Determining whether a custom action, artifact, cache, generated file, or called script contains attacker-controlled material can require data-flow analysis and agent-assisted review. Keep uncertain cases at a lower severity and request human review.

## Limitations and false positives

Static diff inspection may miss checkout behavior hidden in reusable workflows or custom actions, shell indirection, downloaded scripts, artifacts, and cache poisoning. `workflow_run` is not inherently unsafe. A workflow may need privileged metadata access; the security boundary is crossing untrusted data into privileged execution. Secret names and token permissions do not prove a value is reachable by a particular step.

## Implementation recommendations

Parse event triggers, checkout refs, commands, and per-job permissions; correlate steps within each job and report each evidence location. Treat expressions and YAML constructs conservatively. Recommend using `pull_request` for untrusted builds or splitting privileged metadata work from untrusted code execution.

## References

- [GitHub: Securely using `pull_request_target`](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
- [GitHub: Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
