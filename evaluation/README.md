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

That is 8 pull requests (5 safe, 3 risky) with 5 expected findings across
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

For each fixture, the harness pairs each expected finding with **at most
one** actual finding when both of these hold:

1. **Same `agent`**.
2. **Overlapping evidence:** some evidence item in each points at the same
   `file_path`, with line ranges within `--line-tolerance` lines of each
   other (default 2).

Titles, descriptions and wording are **not** compared, because agents phrase
the same claim differently. When several actual findings qualify, one with
the same severity is preferred. Expected findings are matched from most to
least severe, so the most important claims get their best candidate first.

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
| **F1** | 2 · P · R / (P + R) | One number balancing both, for tracking over time |
| **False-positive rate** | safe PRs with ≥ 1 finding / safe PRs | How often does Sentinel bother reviewers on a clean PR? |
| **False-negative rate** | risky PRs where no expected finding was matched / risky PRs | How often does a risky PR go completely unflagged? |
| **Severity agreement** | matched pairs with equal severity / TP | Are real issues rated at the right severity? |
| **Human-review agreement** | matched pairs with equal `requires_human_review` / TP | Does the agent ask for review when it should? |
| **Mean confidence (TP vs FP)** | average `confidence` of matched vs unexpected findings | Is confidence informative? TP confidence should be clearly higher than FP confidence. |

Notes:

- A ratio with a zero denominator is reported as `n/a`, never as 0 or 1.
  For example, precision is undefined when Sentinel reports nothing.
- **The false-positive rate is measured per PR, not per finding.** There's
  no countable set of "true negative findings", so a per-finding FPR is
  undefined. Per PR, it matches what reviewers experience: a clean PR that
  gets flagged.
- The per-finding miss rate is 1 − recall, so it isn't reported separately.
- With 8 cases (5 safe, 3 risky), one case moves the false-positive rate
  by 20 points and the false-negative rate by 33. Treat the
  numbers as a regression signal, not a benchmark, until the dataset grows
  (PROJECT.md plans that for Sprint 5).

### Current baseline

The default runner is the mock review from #3
(`app.services.review_service:build_mock_review_report`). It flags any
change to the root `package.json` at line 1 and nothing else:

```text
case                                     label  exp  act  TP  FP  FN  result
cicd-pinned-actions-read-only            safe     0    0   0   0   0  PASS
cicd-third-party-action-sha-bump         safe     0    0   0   0   0  PASS
dep-lodash-patch-bump                    safe     0    1   0   1   0  FAIL
docs-readme-typo                         safe     0    0   0   0   0  PASS
release-dockerfile-digest-bump           safe     0    0   0   0   0  PASS
cicd-pull-request-target-head-checkout   risky    2    0   0   0   2  FAIL
dep-new-package-install-script           risky    1    1   0   1   1  FAIL
release-dockerfile-latest-and-curl-bash  risky    2    0   0   0   2  FAIL

precision 0.00 · recall 0.00 · false-positive rate 0.20 · false-negative rate 1.00
```

This is the expected result for a mock. It shows the harness catching both
failure modes: a false positive on a safe dependency bump, and a finding on
the right file at the wrong place (line 1 instead of the new dependency on
line 13), which counts as one FP plus one FN.

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

- Matching is greedy, not an optimal assignment. That is fine at this size.
  Revisit it if fixtures start having many overlapping findings.
- Evidence must point at the right file and lines. A correct claim with
  evidence somewhere else counts as FP + FN. This is deliberate, because
  Sentinel's findings must be grounded, but `--line-tolerance` can be raised
  for exploratory runs.
- Expected findings describe today's checks. When #2 finalizes check IDs and
  severity guidance, the expected severities here should be aligned with it.
