#!/usr/bin/env python3
"""Compare Sentinel's findings on labelled fixtures with the expected findings (#6).

Each fixture in ``evaluation/fixtures/{safe,risky}/`` is a ``PullRequestInput``
JSON file. Its expected output lives in ``evaluation/expected-findings/`` under
the same base name. The harness produces actual findings for every fixture,
either by calling a review function in-process (``--runner``) or by reading
saved outputs (``--actual-dir``), matches them against the expected
``SecurityFinding`` list and reports precision, recall and false-positive rate.

Run from the repository root with the backend dependencies installed::

    python evaluation/scripts/run_evaluation.py
    python evaluation/scripts/run_evaluation.py --actual-dir path/to/outputs
    python evaluation/scripts/run_evaluation.py --check-fixtures

See ``evaluation/README.md`` for the matching rule and metric definitions.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EVALUATION_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = EVALUATION_DIR.parent
BACKEND_DIR = REPO_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.schemas import PullRequestInput, SecurityFinding
from app.schemas.review_report import ReviewReport
from pydantic import TypeAdapter, ValidationError

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from matching import compare_findings

DEFAULT_RUNNER = "app.services.review_service:build_mock_review_report"
LABELS = ("safe", "risky")
SEVERITIES = ("critical", "high", "medium", "low")
_SEVERITY_RANK = {name: rank for rank, name in enumerate(SEVERITIES)}
_HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
_FINDINGS_ADAPTER = TypeAdapter(list[SecurityFinding])

Runner = Callable[[PullRequestInput], Any]


class EvaluationError(Exception):
    """A fixture, expected-findings file or actual output is unusable."""


# --------------------------------------------------------------------------
# Loading fixtures
# --------------------------------------------------------------------------


@dataclass
class Case:
    """One labelled pull request and the findings Sentinel should report."""

    name: str
    label: str
    fixture_path: Path
    pull_request: PullRequestInput
    expected: list[SecurityFinding]
    summary: str = ""
    score_human_review: bool = True


def load_cases(evaluation_dir: Path = EVALUATION_DIR) -> list[Case]:
    """Load every fixture with its expected findings, validating both.

    Raises EvaluationError listing every problem found, so a broken dataset
    is reported in one pass rather than one file at a time.
    """
    fixtures_dir = evaluation_dir / "fixtures"
    expected_dir = evaluation_dir / "expected-findings"
    problems: list[str] = []
    cases: list[Case] = []
    seen: dict[str, Path] = {}

    for label in LABELS:
        for fixture_path in sorted((fixtures_dir / label).glob("*.json")):
            name = fixture_path.stem
            if name in seen:
                problems.append(
                    f"{fixture_path}: base name also used by {seen[name]}; "
                    "fixture names must be unique across safe/ and risky/"
                )
                continue
            seen[name] = fixture_path

            try:
                pull_request = PullRequestInput.model_validate_json(
                    fixture_path.read_text()
                )
            except ValidationError as exc:
                problems.append(f"{fixture_path}: not a valid PullRequestInput: {exc}")
                continue

            expected_path = expected_dir / f"{name}.json"
            if not expected_path.exists():
                problems.append(
                    f"{fixture_path}: missing expected findings {expected_path}"
                )
                continue

            try:
                expected_doc = json.loads(expected_path.read_text())
                expected = _FINDINGS_ADAPTER.validate_python(
                    expected_doc.get("findings")
                )
            except (json.JSONDecodeError, AttributeError, ValidationError) as exc:
                problems.append(
                    f"{expected_path}: 'findings' is not a SecurityFinding list: {exc}"
                )
                continue

            if not isinstance(expected_doc.get("score_human_review", True), bool):
                problems.append(f"{expected_path}: score_human_review must be boolean")
            try:
                compare_findings(expected, [])
            except ValueError as exc:
                problems.append(f"{expected_path}: {exc}")

            if expected_doc.get("label") != label:
                problems.append(
                    f"{expected_path}: label {expected_doc.get('label')!r} does not match "
                    f"fixture directory {label!r}"
                )
            if label == "safe" and expected:
                problems.append(
                    f"{expected_path}: safe fixtures must expect no findings"
                )
            if label == "risky" and not expected:
                problems.append(
                    f"{expected_path}: risky fixtures must expect at least one finding"
                )

            case = Case(
                name=name,
                label=label,
                fixture_path=fixture_path,
                pull_request=pull_request,
                expected=expected,
                summary=expected_doc.get("summary", ""),
                score_human_review=expected_doc.get("score_human_review", True),
            )
            problems.extend(
                f"{expected_path}: {p}" for p in check_evidence_locations(case)
            )
            cases.append(case)

    fixture_names = set(seen)
    for expected_path in sorted(expected_dir.glob("*.json")):
        if expected_path.stem not in fixture_names:
            problems.append(f"{expected_path}: no fixture with this base name")

    if not seen:
        problems.append("No fixtures found")
    if problems:
        raise EvaluationError("\n".join(problems))
    return cases


def diff_new_lines(patch: str) -> set[int]:
    """Line numbers on the new side of a unified diff (added and context lines)."""
    lines: set[int] = set()
    current: int | None = None
    for raw in patch.splitlines():
        header = _HUNK_HEADER.match(raw)
        if header:
            current = int(header.group(1))
            continue
        if current is None or raw.startswith(("-", "\\")):
            continue
        lines.add(current)
        current += 1
    return lines


def check_evidence_locations(case: Case) -> list[str]:
    """Check that expected evidence points at a changed file and at lines in its diff."""
    problems: list[str] = []
    files = {f.path: f for f in case.pull_request.files_changed}
    for finding in case.expected:
        for evidence in finding.evidence:
            changed = files.get(evidence.file_path)
            if changed is None:
                problems.append(
                    f"finding {finding.title!r}: evidence file {evidence.file_path!r} "
                    "is not in the fixture's files_changed"
                )
                continue
            if changed.patch is None:
                continue
            end = evidence.line_end or evidence.line_start
            visible = diff_new_lines(changed.patch)
            if not visible.intersection(range(evidence.line_start, end + 1)):
                problems.append(
                    f"finding {finding.title!r}: {evidence.file_path}:{evidence.line_start}"
                    f"-{end} is outside the lines shown in the fixture diff"
                )
    return problems


# --------------------------------------------------------------------------
# Producing actual findings
# --------------------------------------------------------------------------


def load_runner(spec: str) -> Runner:
    """Import ``module:function``; the function takes a PullRequestInput."""
    module_name, _, attr = spec.partition(":")
    if not module_name or not attr:
        raise EvaluationError(f"runner must look like 'module:function', got {spec!r}")
    runner = getattr(importlib.import_module(module_name), attr, None)
    if not callable(runner):
        raise EvaluationError(f"{spec!r} is not a callable")
    return runner


def findings_from_output(output: Any) -> list[SecurityFinding]:
    """Accept a ReviewReport, a {'findings': [...]} mapping or a bare finding list."""
    if isinstance(output, ReviewReport):
        if output.agents_failed or output.agents_partial:
            raise EvaluationError("Review did not complete: failed or partial agents")
        return list(output.findings)
    if isinstance(output, dict):
        if (
            output.get("agents_failed")
            or output.get("agents_partial")
            or output.get("status") in {"failure", "partial"}
        ):
            raise EvaluationError("Review did not complete: failed or partial agents")
        output = output.get("findings")
    try:
        return _FINDINGS_ADAPTER.validate_python(output)
    except ValidationError as exc:
        raise EvaluationError(
            f"output is not a list of SecurityFinding: {exc}"
        ) from exc


def actual_from_runner(runner: Runner) -> Callable[[Case], list[SecurityFinding]]:
    def produce(case: Case) -> list[SecurityFinding]:
        return findings_from_output(runner(case.pull_request.model_copy(deep=True)))

    return produce


def actual_from_dir(actual_dir: Path) -> Callable[[Case], list[SecurityFinding]]:
    def produce(case: Case) -> list[SecurityFinding]:
        path = actual_dir / f"{case.name}.json"
        if not path.exists():
            raise EvaluationError(f"no actual output at {path}")
        try:
            return findings_from_output(json.loads(path.read_text()))
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"{path} is not valid JSON: {exc}") from exc

    return produce


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------


def locations_overlap(
    expected: SecurityFinding, actual: SecurityFinding, line_tolerance: int
) -> bool:
    """True when any evidence pair shares a file and their line ranges are
    within ``line_tolerance`` lines of each other."""
    for e in expected.evidence:
        e_end = e.line_end or e.line_start
        for a in actual.evidence:
            if a.file_path != e.file_path:
                continue
            a_end = a.line_end or a.line_start
            if (
                a.line_start <= e_end + line_tolerance
                and e.line_start <= a_end + line_tolerance
            ):
                return True
    return False


@dataclass
class MatchResult:
    matched: list[tuple[SecurityFinding, SecurityFinding]] = field(default_factory=list)
    missed: list[SecurityFinding] = field(default_factory=list)
    unexpected: list[SecurityFinding] = field(default_factory=list)


def match_findings(
    expected: list[SecurityFinding],
    actual: list[SecurityFinding],
    *,
    line_tolerance: int = 2,
    matching_mode: str = "exact",
) -> MatchResult:
    """Use exact claim identity by default; location mode is exploratory only.

    Duplicates are separately detected by compare_findings, then included in
    unexpected findings so repeated reports reduce precision consistently.
    """
    if matching_mode == "exact":
        exact = compare_findings(expected, actual)
        return MatchResult(
            exact.matched, exact.missed, exact.unexpected + exact.duplicates
        )
    if matching_mode != "location":
        raise EvaluationError(f"Unknown matching mode: {matching_mode}")
    result = MatchResult()
    available = list(actual)
    for exp in sorted(expected, key=lambda f: _SEVERITY_RANK[f.severity]):
        candidates = [
            act
            for act in available
            if act.agent == exp.agent and locations_overlap(exp, act, line_tolerance)
        ]
        if not candidates:
            result.missed.append(exp)
            continue
        best = next(
            (c for c in candidates if c.severity == exp.severity), candidates[0]
        )
        available.remove(best)
        result.matched.append((exp, best))
    result.unexpected = available
    return result


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------


@dataclass
class CaseResult:
    case: Case
    expected: list[SecurityFinding]
    actual: list[SecurityFinding]
    match: MatchResult
    error: str | None = None

    @property
    def passed(self) -> bool:
        return (
            self.error is None and not self.match.missed and not self.match.unexpected
        )


def at_or_above(
    findings: list[SecurityFinding], min_severity: str
) -> list[SecurityFinding]:
    limit = _SEVERITY_RANK[min_severity]
    return [f for f in findings if _SEVERITY_RANK[f.severity] <= limit]


def evaluate_case(
    case: Case,
    produce: Callable[[Case], list[SecurityFinding]],
    *,
    line_tolerance: int = 2,
    min_severity: str = "low",
    matching_mode: str = "exact",
) -> CaseResult:
    expected = at_or_above(case.expected, min_severity)
    try:
        actual = at_or_above(produce(case), min_severity)
    # A crashing system under test is a result to report, not a harness bug.
    except Exception as exc:  # noqa: BLE001
        return CaseResult(
            case=case,
            expected=expected,
            actual=[],
            match=MatchResult(missed=list(expected)),
            error=f"{type(exc).__name__}: {exc}",
        )
    match = match_findings(
        expected, actual, line_tolerance=line_tolerance, matching_mode=matching_mode
    )
    return CaseResult(case=case, expected=expected, actual=actual, match=match)


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compute_metrics(results: list[CaseResult]) -> dict[str, Any]:
    """Aggregate finding-level and PR-level metrics. Ratios with a zero
    denominator are None (undefined), never silently 0 or 1."""
    all_results = results
    results = [r for r in all_results if r.error is None]
    tp = sum(len(r.match.matched) for r in results)
    fp = sum(len(r.match.unexpected) for r in results)
    fn = sum(len(r.match.missed) for r in results)
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    f1 = _ratio(2 * tp, 2 * tp + fp + fn)

    safe = [r for r in results if r.case.label == "safe"]
    risky = [r for r in results if r.case.label == "risky" and r.expected]
    safe_flagged = sum(1 for r in safe if r.actual)
    risky_missed = sum(1 for r in risky if r.expected and not r.match.matched)
    pairs = [pair for r in results for pair in r.match.matched]

    review_pairs = [
        pair for r in results if r.case.score_human_review for pair in r.match.matched
    ]
    return {
        "cases": len(all_results),
        "evaluated_cases": len(results),
        "safe_cases": len(safe),
        "risky_cases": len(risky),
        "errors": sum(1 for r in all_results if r.error),
        "passed": sum(1 for r in results if r.passed),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": _ratio(safe_flagged, len(safe)),
        "false_negative_rate": _ratio(risky_missed, len(risky)),
        "severity_agreement": _ratio(
            sum(1 for e, a in pairs if e.severity == a.severity), tp
        ),
        "human_review_pairs": len(review_pairs),
        "human_review_agreement": _ratio(
            sum(
                1
                for e, a in review_pairs
                if e.requires_human_review == a.requires_human_review
            ),
            len(review_pairs),
        ),
        "mean_confidence_true_positives": _mean([a.confidence for _, a in pairs]),
        "mean_confidence_false_positives": _mean(
            [f.confidence for r in results for f in r.match.unexpected]
        ),
    }


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _describe(finding: SecurityFinding) -> str:
    where = ", ".join(
        f"{e.file_path}:{e.line_start}" + (f"-{e.line_end}" if e.line_end else "")
        for e in finding.evidence
    )
    return f"[{finding.severity}] {finding.agent}: {finding.title} ({where})"


def format_report(results: list[CaseResult], metrics: dict[str, Any]) -> str:
    width = max((len(r.case.name) for r in results), default=4)
    lines = [
        f"{'case':<{width}}  label  exp  act  TP  FP  FN  result",
        "-" * (width + 38),
    ]
    for r in results:
        status = "ERROR" if r.error else ("PASS" if r.passed else "FAIL")
        lines.append(
            f"{r.case.name:<{width}}  {r.case.label:<5}  {len(r.expected):>3}  "
            f"{len(r.actual):>3}  {len(r.match.matched):>2}  {len(r.match.unexpected):>2}  "
            f"{len(r.match.missed):>2}  {status}"
        )

    details = []
    for r in results:
        if r.passed:
            continue
        details.append(f"\n{r.case.name} ({r.case.label})")
        if r.error:
            details.append(f"  error: {r.error}")
        details.extend(f"  missed:     {_describe(f)}" for f in r.match.missed)
        details.extend(f"  unexpected: {_describe(f)}" for f in r.match.unexpected)
        details.extend(
            f"  severity:   expected {e.severity}, got {a.severity} for {e.title!r}"
            for e, a in r.match.matched
            if e.severity != a.severity
        )
    if details:
        lines.append("\nDetails:")
        lines.extend(details)

    m = metrics
    rows = [
        (
            "cases",
            (
                f"{m['evaluated_cases']}/{m['cases']} evaluated ({m['safe_cases']} safe, {m['risky_cases']} risky), "
                f"{m['passed']} passed, {m['errors']} errors"
            ),
        ),
        (
            "findings",
            f"TP={m['true_positives']} FP={m['false_positives']} FN={m['false_negatives']}",
        ),
        ("precision", _fmt(m["precision"])),
        ("recall", _fmt(m["recall"])),
        ("f1", _fmt(m["f1"])),
        (
            "false-positive rate",
            f"{_fmt(m['false_positive_rate'])}  (safe PRs with any finding)",
        ),
        (
            "false-negative rate",
            f"{_fmt(m['false_negative_rate'])}  (risky PRs with no match)",
        ),
        ("severity agreement", _fmt(m["severity_agreement"])),
        ("human-review agreement", _fmt(m["human_review_agreement"])),
        (
            "mean confidence",
            (
                f"TP={_fmt(m['mean_confidence_true_positives'])} "
                f"FP={_fmt(m['mean_confidence_false_positives'])}"
            ),
        ),
    ]
    lines.append("\nMetrics:")
    lines.extend(f"  {name:<24}{value}" for name, value in rows)
    return "\n".join(lines)


def results_to_json(
    results: list[CaseResult], metrics: dict[str, Any]
) -> dict[str, Any]:
    def dump(findings: list[SecurityFinding]) -> list[dict[str, Any]]:
        return [f.model_dump(mode="json") for f in findings]

    return {
        "metrics": metrics,
        "cases": [
            {
                "name": r.case.name,
                "label": r.case.label,
                "passed": r.passed,
                "error": r.error,
                "matched": [
                    {
                        "expected": e.model_dump(mode="json"),
                        "actual": a.model_dump(mode="json"),
                    }
                    for e, a in r.match.matched
                ],
                "missed": dump(r.match.missed),
                "unexpected": dump(r.match.unexpected),
            }
            for r in results
        ],
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--runner",
        default=DEFAULT_RUNNER,
        help="module:function that takes a PullRequestInput and returns a ReviewReport "
        f"or a list of SecurityFinding (default: {DEFAULT_RUNNER})",
    )
    source.add_argument(
        "--actual-dir",
        type=Path,
        help="read actual output from <dir>/<fixture-name>.json instead of running the backend",
    )
    parser.add_argument(
        "--evaluation-dir",
        type=Path,
        default=EVALUATION_DIR,
        help="directory containing fixtures/ and expected-findings/",
    )
    parser.add_argument(
        "--matching-mode",
        choices=("exact", "location"),
        default="exact",
        help="exact claim identity (default), or exploratory location matching",
    )
    parser.add_argument(
        "--line-tolerance",
        type=int,
        default=2,
        help="lines of slack when comparing evidence locations (default: 2)",
    )
    parser.add_argument(
        "--min-severity",
        choices=SEVERITIES,
        default="low",
        help="ignore expected and actual findings below this severity (default: low)",
    )
    parser.add_argument(
        "--json-out", type=Path, help="also write the full results as JSON"
    )
    parser.add_argument(
        "--check-fixtures",
        action="store_true",
        help="only validate fixtures and expected findings, then exit",
    )
    args = parser.parse_args(argv)
    if args.line_tolerance < 0:
        parser.error("--line-tolerance must be zero or more")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        cases = load_cases(args.evaluation_dir)
    except EvaluationError as exc:
        print(f"Invalid evaluation dataset:\n{exc}", file=sys.stderr)
        return 2

    if args.check_fixtures:
        safe = sum(1 for c in cases if c.label == "safe")
        print(
            f"OK: {len(cases)} fixtures ({safe} safe, {len(cases) - safe} risky) are valid."
        )
        return 0

    try:
        produce = (
            actual_from_dir(args.actual_dir)
            if args.actual_dir
            else actual_from_runner(load_runner(args.runner))
        )
    except (EvaluationError, ImportError) as exc:
        print(f"Cannot load system under test: {exc}", file=sys.stderr)
        return 2

    results = [
        evaluate_case(
            case,
            produce,
            line_tolerance=args.line_tolerance,
            min_severity=args.min_severity,
            matching_mode=args.matching_mode,
        )
        for case in cases
    ]
    metrics = compute_metrics(results)
    print(f"Matching mode: {args.matching_mode}")
    print(format_report(results, metrics))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        payload = results_to_json(results, metrics)
        payload["configuration"] = {
            "matching_mode": args.matching_mode,
            "line_tolerance": args.line_tolerance,
            "min_severity": args.min_severity,
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"\nWrote {args.json_out}")

    # Imperfect scores are the expected state of a work-in-progress system, so
    # only harness-level problems (a crashing runner) produce a nonzero exit.
    return 1 if metrics["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
