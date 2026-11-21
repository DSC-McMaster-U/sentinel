# Dependency examples — Sarthak, issue #6

Three synthetic `PullRequestInput` files: one safe and two risky. Labels are encoded
by directory and filename; matching expected files wrap a `SecurityFinding` list in the runner envelope
(`fixture`, `label`, `summary`, `score_human_review`, `findings`).
Repository URLs and SHAs are fictional. Do not install or execute fixture content.

These are proposed fixture criteria, not approved #2 check IDs. Main currently
contains only the security-check specification scaffold. Jin and Behzad should
review the criteria/severity before these become a benchmark for real agents.

| Fixture | Label / expected | Reason and scope |
| --- | --- | --- |
| `dep-safe-local-install-script` | Safe / `[]` | Local `postinstall` runs a supplied script that only prints a message. An install hook alone is insufficient to trigger the remote-code criterion. No dependencies are declared. |
| `dep-risky-remote-install-script` | Risky / one high finding | `package.json:5` downloads a remote script and pipes it into `sh` during installation. Criterion: added install lifecycle command directly downloads and executes remote code. This does not assert the remote script is malicious. |
| `dep-risky-http-tarball` | Risky / one medium finding | `package.json:5` uses an HTTP dependency tarball. Criterion: added manifest dependency URL starts with `http://`. No independent integrity metadata is provided. This is a transport risk, not a claim of a known vulnerable package. |

All diffs create complete files, with valid unified-diff headers. Evidence line 5
is the new file's line 5, not the fifth line of the diff. `example.invalid` is a
placeholder; evaluation requires no network, registry lookup, or real secrets.

Expected confidence `1.0`, uncertainty `[]`, and review flag `false` are annotation
placeholders following the proposed team convention. They are excluded from
matching; `score_human_review: false` also excludes these cases from review-flag
agreement. They must not be used as a calibration dataset or production review policy.
Severity and recommendations are proposed labels, also outside identity matching.
The safe label means no issue under these narrow criteria, not general safety.
