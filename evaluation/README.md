# evaluation/

Datasets and scripts that measure how well Sentinel detects real risks without flagging safe changes.

| Path | What goes here |
| --- | --- |
| `fixtures/safe/` | Sample pull requests that should **not** be flagged |
| `fixtures/risky/` | Sample pull requests containing known issues |
| `expected-findings/` | Labelled expected output for each fixture (same base name) |
| `scripts/` | Evaluation harness that compares Sentinel output with expected findings |

**Primary owners:** Sarthak + Rohit (#6). Jin + Behzad (#2) contribute safe and unsafe fixtures for each documented security check.

**Never use real secrets in fixtures.** Use obviously fake values such as `ghp_FAKE_TOKEN_FOR_TESTING`.

## Quick start

From the repository root, with the backend dependencies installed (see
[GETTING_STARTED.md](../docs/onboarding/GETTING_STARTED.md)):

```bash
# Check every fixture and expected-findings file is valid
python evaluation/scripts/run_evaluation.py --check-fixtures

# Run the current backend review against every fixture and print metrics
python evaluation/scripts/run_evaluation.py

# Score saved outputs instead, e.g. from an LLM run: <dir>/<fixture-name>.json
python evaluation/scripts/run_evaluation.py --actual-dir path/to/outputs

# Also save the full per-case results
python evaluation/scripts/run_evaluation.py --json-out evaluation-results.json
```

The harness tests run in backend CI (`backend/tests/unit/test_evaluation_harness.py`).

## Dataset

| Fixture | Label | Expected findings |
| --- | --- | --- |
| `safe/dep-lodash-patch-bump` | safe | none: exact-pinned patch bump with a matching lockfile |
| `safe/cicd-pinned-actions-read-only` | safe | none: SHA-pinned actions, `contents: read`, no persisted credentials |
| `safe/docs-readme-typo` | safe | none: docs-only change, no agent should run |
| `safe/release-dockerfile-digest-bump` | safe | none: base image stays pinned by digest |
| `safe/cicd-third-party-action-sha-bump` | safe | none: a third-party action that receives a secret moves to a newer release and stays pinned to a full SHA |
| `risky/cicd-pull-request-target-head-checkout` | risky | **critical** (cicd): `pull_request_target` runs PR code with secrets; **medium** (cicd): `permissions: write-all` |
| `risky/dep-new-package-install-script` | risky | **high** (dependency): new dependency with `hasInstallScript: true` |
| `risky/release-dockerfile-latest-and-curl-bash` | risky | **high** (release): `curl \| bash` during build; **medium** (release): `FROM node:latest` replaces a digest pin |
| `safe/dep-safe-local-install-script` | safe | none: supplied local install script only prints a message |
| `risky/dep-risky-remote-install-script` | risky | **high** (dependency): install hook downloads and executes remote code |
| `risky/dep-risky-http-tarball` | risky | **medium** (dependency): manifest downloads a tarball over HTTP |

That is 11 pull requests (6 safe, 5 risky) with 7 expected findings across
all three agents. The CI/CD set is 2 safe + 1 risky. The safe cases are deliberately close to the risky ones
(the same files and agents), so a check that only looks at file names
produces false positives.

### Fixture format

A fixture is a `PullRequestInput` JSON file
([CONTRACTS.md](../docs/architecture/CONTRACTS.md#pullrequestinput)) with
unified diffs in each file's `patch`. It can be POSTed to `/reviews` as-is.
Fixtures are synthetic: the repository `sentinel-fixtures/demo-app`, the
packages and the URLs ending in `.invalid` don't exist.

### Expected-findings format

`expected-findings/<fixture-name>.json` holds the label and the findings
Sentinel should report, as `SecurityFinding` objects:

```json
{
  "fixture": "risky/cicd-pull-request-target-head-checkout.json",
  "label": "risky",
  "summary": "One sentence on why this PR is safe or risky.",
  "findings": [
    {
      "agent": "cicd",
      "title": "Workflow grants write-all token permissions",
      "description": "...",
      "severity": "medium",
      "recommendation": "...",
      "evidence": [
        {
          "file_path": ".github/workflows/preview.yml",
          "line_start": 7,
          "line_end": null,
          "observation": "Top-level permissions set to write-all."
        }
      ],
      "confidence": 0.9,
      "uncertainty": ["Did not check repository-level default token permissions."],
      "requires_human_review": false
    }
  ]
}
```

Line numbers are on the **new** side of the diff (the head commit), which is
where reviewers and GitHub links point.

`--check-fixtures` (and CI) enforces these rules:

- Every fixture is a valid `PullRequestInput` with a matching expected file,
  and every expected file has a fixture.
- Fixture base names are unique across `safe/` and `risky/`.
- `label` matches the fixture's directory. Safe fixtures expect `[]`, and
  risky fixtures expect at least one finding.
- Every expected finding is a valid `SecurityFinding`, and its evidence
  points at a file in the fixture and at a line visible in that file's diff.

### Adding a fixture

1. Add `fixtures/<safe|risky>/<name>.json`. Prefix the name with the area
   (`dep-`, `cicd-`, `release-`) or the check ID (`DEP-001-...`).
2. Add `expected-findings/<name>.json` in the format above.
3. Run `python evaluation/scripts/run_evaluation.py --check-fixtures`.
4. Link the fixture from the check's document in `docs/security-checks/`.

Prefer **pairs**: a risky change and the closest safe change that the check
must not flag. Pairs are what measure false positives.

## How actual findings are matched

The default `--matching-mode exact` uses Sarthak's
`scripts/matching.py:compare_findings(expected, actual)`. It matches exact agent,
title and the **set** of evidence `(file_path, line_start, line_end)` locations,
the same identity used by `combine_findings`. Evidence order and repeated
locations do not matter; case, whitespace and line ranges do. Duplicate expected
identities are rejected as annotation errors. Inputs are not mutated.

The helper returns `matched` (expected/actual pairs), `missed`, `unexpected`,
`duplicates` and `passed`. The runner includes duplicate actual occurrences in
`unexpected` for scoring: every extra reported finding is an FP. This deliberately
adapts the ZIP's separate duplicate accounting to the combined runner's policy.

Exact matching is a deterministic regression baseline, **not semantic LLM
accuracy**. Paraphrases can produce FP + FN. Severity, confidence, observations,
uncertainty, recommendation and review flags are not part of detection identity.

Rohit's original matcher remains available with `--matching-mode location`.
It requires the same agent and overlapping evidence in the same file, with
`--line-tolerance` (default 2); it prefers equal severity and ignores titles.
This mode is exploratory: an unrelated claim at the same location can match.
Do not compare scores across modes. Console output and JSON configuration
identify the mode. Agree check IDs with #2/#7 before interpreting flexible
matching as claim accuracy.

After matching:

- a matched pair is a **true positive (TP)**
- an expected finding with no match is a **false negative (FN)**
- an actual finding left over is a **false positive (FP)**. This includes
  duplicates of a finding that was already matched, and findings on safe
  fixtures.

`--min-severity medium` (for example) drops lower-severity findings from
**both** sides before matching, to measure the system at a reporting
threshold.

## Metrics

| Metric | Definition | Question it answers |
| --- | --- | --- |
| **Precision** | TP / (TP + FP) | When Sentinel reports something, how often is it real? |
| **Recall** | TP / (TP + FN) | Of the real issues, how many does Sentinel find? |
| **F1** | 2TP / (2TP + FP + FN) | One number balancing both, for tracking over time |
| **False-positive rate** | successfully evaluated safe PRs with ≥ 1 finding / successfully evaluated safe PRs | How often does Sentinel bother reviewers on a clean PR? |
| **False-negative rate** | successfully evaluated risky PRs with no match / evaluated risky PRs with expected findings at the selected threshold | How often does a risky PR go completely unflagged? |
| **Severity agreement** | matched pairs with equal severity / TP | Are real issues rated at the right severity? |
| **Human-review agreement** | labelled matched pairs with equal `requires_human_review` / labelled matched pairs | Does the agent ask for review when it should? |
| **Mean confidence (TP vs FP)** | average `confidence` of matched vs unexpected findings | Is confidence informative? TP confidence should be clearly higher than FP confidence. |

Notes:

- A ratio with a zero denominator is reported as `n/a`, never as 0 or 1.
  For example, precision is undefined when Sentinel reports nothing.
- **The false-positive rate is measured per PR, not per finding.** There's
  no countable set of "true negative findings", so a per-finding FPR is
  undefined. Per PR, it matches what reviewers experience: a clean PR that
  gets flagged.
- The per-finding miss rate is 1 − recall, so it isn't reported separately.
- Errors, including failed/partial reports, are excluded from detection metrics.
  Always show `evaluated_cases / cases` and `errors`; an entirely failed run has
  undefined rates, not a clean score. Risky cases with no expected findings above
  `--min-severity` are excluded from the PR-level miss-rate denominator.
- `score_human_review: false` on an expected-file envelope excludes that case
  from human-review agreement. Sarthak's three fixtures use this because their
  expected flags are placeholders; no shared schema fields are changed.
- With all 11 cases evaluated, one safe case changes FPR by about 16.7 points;
  one risky case changes PR-level miss rate by 20 points. This is a small
  regression dataset, not a reliable accuracy estimate.

### Current baseline

The default runner is the mock review from #3
(`app.services.review_service:build_mock_review_report`). It flags any
change to the root `package.json` at line 1 and nothing else:

Against the current mock, the combined exact-mode baseline is TP=0, FP=5,
FN=7, precision=0, recall=0, F1=0, FPR=2/6 and PR-level miss rate=5/5.
This measures mock behavior, not security-agent accuracy. Replaying expected
files against themselves is only a wiring check.

## Plugging in the real workflow

`--runner module:function` takes any function that accepts a
`PullRequestInput` and returns a `ReviewReport` (or a list of
`SecurityFinding`). When #9 connects the API to the LangGraph workflow,
point the runner at the new review service function. If that function
keeps the current name, no flag is needed.

For nondeterministic (LLM) agents, save each run's output with one file per
fixture and score it with `--actual-dir`. Run several times and report the
spread rather than a single number.

The exit code is `0` when every case ran, `1` if the system under test
raised an exception or an actual-output file is missing, and `2` if the
dataset or runner can't be loaded. Low scores don't fail the run, because
they are the expected state of a system in development. Threshold gates can
be added once the agents are real.

## Limitations

- Exploratory location matching is greedy and can confuse nearby claims.
  Exact matching remains the default.
- Evidence must point at the right file and lines. A correct claim with
  evidence somewhere else counts as FP + FN. This is deliberate, because
  Sentinel's findings must be grounded, but `--line-tolerance` can be raised
  for exploratory location-mode runs.
- Expected findings describe today's checks. When #2 finalizes check IDs and
  severity guidance, the expected severities here should be aligned with it.


## Combined contribution and tests

Sarthak contributes the overview SVG, coverage-state specification, three
dependency fixtures, exact matching helper and matching regression tests.
Rohit contributes the expanded review interface, runner, validation, metrics,
frontend types/components and the original eight fixtures. See
[dependency criteria](fixtures/dependency-examples.md); #2 owners still need
to approve the proposed criteria and severity labels.

Both test modules live under `backend/tests/unit/`, so existing backend CI
runs them. From `backend/`, run `python -m pytest` and `ruff check .`.
From the repository root, run `ruff check evaluation/scripts` and
`python evaluation/scripts/run_evaluation.py --check-fixtures`.
