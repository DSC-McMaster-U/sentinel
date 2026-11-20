"""Tests for the evaluation harness in evaluation/scripts/ (#6).

Covers file loading and schema validation, metric calculations and results
output. Matching (match_findings) is tested separately by its owner, so the
metric tests here build MatchResult objects directly.

The harness lives outside the backend package, so it is loaded from its file
path. These tests run in backend CI so a broken fixture or harness change is
caught on every pull request.
"""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

from app.schemas import Evidence, SecurityFinding
from app.schemas.review_report import ReviewReport

EVALUATION_DIR = Path(__file__).resolve().parents[3] / "evaluation"
if not (EVALUATION_DIR / "scripts" / "run_evaluation.py").exists():
    # The backend Docker image copies only backend/, so there is nothing to test.
    pytest.skip("evaluation/ is not available in this checkout", allow_module_level=True)

_SPEC = importlib.util.spec_from_file_location(
    "run_evaluation", EVALUATION_DIR / "scripts" / "run_evaluation.py"
)
harness = importlib.util.module_from_spec(_SPEC)
sys.modules["run_evaluation"] = harness
_SPEC.loader.exec_module(harness)


def _finding(
    agent: str = "cicd",
    severity: str = "high",
    file_path: str = ".github/workflows/ci.yml",
    line_start: int = 10,
    confidence: float = 0.7,
    requires_human_review: bool = False,
) -> SecurityFinding:
    return SecurityFinding(
        agent=agent,
        title="Some finding",
        description="A description.",
        severity=severity,
        recommendation="A recommendation.",
        evidence=[
            Evidence(
                file_path=file_path,
                line_start=line_start,
                line_end=None,
                observation="An observation.",
            )
        ],
        confidence=confidence,
        uncertainty=[],
        requires_human_review=requires_human_review,
    )


def _case(name: str, label: str):
    cases = {c.name: c for c in harness.load_cases()}
    case = next(c for c in cases.values() if c.label == label)
    return harness.Case(
        name=name,
        label=label,
        fixture_path=case.fixture_path,
        pull_request=case.pull_request,
        expected=[],
    )


def _result(label, matched=(), missed=(), unexpected=(), error=None):
    match = harness.MatchResult(
        matched=list(matched), missed=list(missed), unexpected=list(unexpected)
    )
    return harness.CaseResult(
        case=_case(f"{label}-case", label),
        expected=[e for e, _ in matched] + list(missed),
        actual=[a for _, a in matched] + list(unexpected),
        match=match,
        error=error,
    )


# ---------------------------------------------------------------- loading and validation


def test_dataset_has_two_safe_and_one_risky_cicd_case():
    cases = harness.load_cases()

    assert sorted(c.label for c in cases) == ["risky", "safe", "safe"]
    assert all(c.name.startswith("cicd-") for c in cases)


def test_safe_cases_expect_nothing_and_risky_cases_expect_findings():
    for case in harness.load_cases():
        if case.label == "safe":
            assert case.expected == [], case.name
        else:
            assert case.expected, case.name
            assert all(f.agent == "cicd" for f in case.expected), case.name


def test_expected_evidence_points_at_lines_in_the_fixture_diff():
    for case in harness.load_cases():
        assert harness.check_evidence_locations(case) == [], case.name


def test_check_fixtures_cli_succeeds(capsys):
    assert harness.main(["--check-fixtures"]) == 0
    assert "3 fixtures (2 safe, 1 risky)" in capsys.readouterr().out


def _copy_dataset(tmp_path: Path) -> Path:
    for sub in ("fixtures/safe", "fixtures/risky", "expected-findings"):
        shutil.copytree(EVALUATION_DIR / sub, tmp_path / sub)
    return tmp_path


def _edit_expected(dataset: Path, name: str, edit) -> None:
    path = dataset / "expected-findings" / f"{name}.json"
    doc = json.loads(path.read_text())
    edit(doc)
    path.write_text(json.dumps(doc))


def test_missing_expected_file_is_reported(tmp_path):
    dataset = _copy_dataset(tmp_path)
    (dataset / "expected-findings" / "cicd-pinned-actions-read-only.json").unlink()

    with pytest.raises(harness.EvaluationError, match="missing expected findings"):
        harness.load_cases(dataset)


def test_expected_file_without_fixture_is_reported(tmp_path):
    dataset = _copy_dataset(tmp_path)
    (dataset / "fixtures" / "safe" / "cicd-pinned-actions-read-only.json").unlink()

    with pytest.raises(harness.EvaluationError, match="no fixture with this base name"):
        harness.load_cases(dataset)


def test_invalid_fixture_is_reported(tmp_path):
    dataset = _copy_dataset(tmp_path)
    path = dataset / "fixtures" / "safe" / "cicd-pinned-actions-read-only.json"
    doc = json.loads(path.read_text())
    del doc["head_sha"]
    path.write_text(json.dumps(doc))

    with pytest.raises(harness.EvaluationError, match="not a valid PullRequestInput"):
        harness.load_cases(dataset)


def test_invalid_expected_finding_is_reported(tmp_path):
    dataset = _copy_dataset(tmp_path)
    name = "cicd-pull-request-target-head-checkout"
    _edit_expected(dataset, name, lambda d: d["findings"][0].update(confidence=1.5))

    with pytest.raises(harness.EvaluationError, match="not a SecurityFinding list"):
        harness.load_cases(dataset)


def test_duplicate_fixture_names_are_reported(tmp_path):
    dataset = _copy_dataset(tmp_path)
    shutil.copy(
        dataset / "fixtures" / "safe" / "cicd-pinned-actions-read-only.json",
        dataset / "fixtures" / "risky" / "cicd-pinned-actions-read-only.json",
    )

    with pytest.raises(harness.EvaluationError, match="must be unique"):
        harness.load_cases(dataset)


def test_label_must_match_directory(tmp_path):
    dataset = _copy_dataset(tmp_path)
    _edit_expected(
        dataset, "cicd-pinned-actions-read-only", lambda d: d.update(label="risky")
    )

    with pytest.raises(harness.EvaluationError, match="does not match fixture directory"):
        harness.load_cases(dataset)


def test_safe_fixture_with_expected_findings_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    finding = _finding(file_path=".github/workflows/test.yml", line_start=7)
    _edit_expected(
        dataset,
        "cicd-pinned-actions-read-only",
        lambda d: d.update(findings=[finding.model_dump(mode="json")]),
    )

    with pytest.raises(harness.EvaluationError, match="safe fixtures must expect no findings"):
        harness.load_cases(dataset)


def test_risky_fixture_without_expected_findings_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    _edit_expected(
        dataset, "cicd-pull-request-target-head-checkout", lambda d: d.update(findings=[])
    )

    with pytest.raises(harness.EvaluationError, match="must expect at least one finding"):
        harness.load_cases(dataset)


def test_evidence_outside_the_diff_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    _edit_expected(
        dataset,
        "cicd-pull-request-target-head-checkout",
        lambda d: d["findings"][0]["evidence"][0].update(line_start=500),
    )

    with pytest.raises(harness.EvaluationError, match="outside the lines shown"):
        harness.load_cases(dataset)


def test_evidence_in_a_file_not_in_the_pr_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    _edit_expected(
        dataset,
        "cicd-pull-request-target-head-checkout",
        lambda d: d["findings"][0]["evidence"][0].update(file_path="other.yml"),
    )

    with pytest.raises(harness.EvaluationError, match="not in the fixture's files_changed"):
        harness.load_cases(dataset)


def test_diff_new_lines_skips_removed_lines():
    patch = "@@ -5,3 +5,3 @@\n context\n-old\n+new\n context"
    assert harness.diff_new_lines(patch) == {5, 6, 7}


def test_findings_from_output_accepts_report_mapping_and_list():
    finding = _finding()
    report = ReviewReport(
        pr_number=1,
        repo_url="https://github.com/example/repo",
        commit_sha="abc",
        generated_at="2026-11-18T00:00:00Z",
        findings=[finding],
        requires_human_review=False,
    )
    payload = finding.model_dump(mode="json")

    assert harness.findings_from_output(report) == [finding]
    assert harness.findings_from_output(report.model_dump(mode="json")) == [finding]
    assert harness.findings_from_output([payload]) == [finding]
    with pytest.raises(harness.EvaluationError):
        harness.findings_from_output({"findings": [{"title": "incomplete"}]})


# ---------------------------------------------------------------- metrics


def test_precision_recall_and_f1():
    hit = (_finding(), _finding())
    results = [
        _result("risky", matched=[hit, hit, hit], missed=[_finding()], unexpected=[_finding()]),
    ]

    m = harness.compute_metrics(results)

    assert (m["true_positives"], m["false_positives"], m["false_negatives"]) == (3, 1, 1)
    assert m["precision"] == pytest.approx(0.75)
    assert m["recall"] == pytest.approx(0.75)
    assert m["f1"] == pytest.approx(0.75)


def test_false_positive_rate_counts_safe_prs_with_any_finding():
    results = [
        _result("safe", unexpected=[_finding(), _finding()]),
        _result("safe"),
        _result("safe"),
        _result("safe"),
    ]

    m = harness.compute_metrics(results)

    # Two findings on one PR still count as one flagged safe PR.
    assert m["false_positive_rate"] == pytest.approx(0.25)
    assert m["false_positives"] == 2


def test_false_negative_rate_counts_risky_prs_with_no_match():
    results = [
        _result("risky", missed=[_finding()]),
        _result("risky", matched=[(_finding(), _finding())], missed=[_finding()]),
    ]

    m = harness.compute_metrics(results)

    # The second PR was flagged for one real issue, so it is not a missed PR.
    assert m["false_negative_rate"] == pytest.approx(0.5)


def test_undefined_ratios_are_none_not_zero():
    m = harness.compute_metrics([_result("safe")])

    assert m["precision"] is None
    assert m["recall"] is None
    assert m["f1"] is None
    assert m["false_negative_rate"] is None
    assert m["severity_agreement"] is None
    assert m["false_positive_rate"] == 0.0


def test_severity_and_human_review_agreement():
    pairs = [
        (_finding(severity="high"), _finding(severity="high", requires_human_review=True)),
        (_finding(severity="high"), _finding(severity="low")),
    ]

    m = harness.compute_metrics([_result("risky", matched=pairs)])

    assert m["severity_agreement"] == pytest.approx(0.5)
    assert m["human_review_agreement"] == pytest.approx(0.5)


def test_mean_confidence_is_split_by_true_and_false_positives():
    results = [
        _result(
            "risky",
            matched=[(_finding(), _finding(confidence=0.9))],
            unexpected=[_finding(confidence=0.3)],
        )
    ]

    m = harness.compute_metrics(results)

    assert m["mean_confidence_true_positives"] == pytest.approx(0.9)
    assert m["mean_confidence_false_positives"] == pytest.approx(0.3)


def test_passed_and_error_counts():
    results = [
        _result("safe"),
        _result("safe", unexpected=[_finding()]),
        _result("risky", missed=[_finding()], error="RuntimeError: boom"),
    ]

    m = harness.compute_metrics(results)

    assert m["passed"] == 1
    assert m["errors"] == 1


def test_min_severity_filters_both_sides():
    findings = [_finding(severity="low"), _finding(severity="critical")]
    assert [f.severity for f in harness.at_or_above(findings, "high")] == ["critical"]


def test_crashing_runner_is_reported_as_an_error_with_missed_findings():
    case = next(c for c in harness.load_cases() if c.label == "risky")

    def broken(_case):
        raise RuntimeError("agent exploded")

    result = harness.evaluate_case(case, broken)

    assert result.error == "RuntimeError: agent exploded"
    assert result.match.missed == case.expected
    assert harness.compute_metrics([result])["errors"] == 1


# ---------------------------------------------------------------- results output


def test_text_report_lists_cases_details_and_metrics():
    results = [
        _result("safe", unexpected=[_finding(file_path="a.yml", line_start=3)]),
        _result("risky", matched=[(_finding(), _finding())]),
    ]

    text = harness.format_report(results, harness.compute_metrics(results))

    assert "safe-case" in text and "FAIL" in text and "PASS" in text
    assert "unexpected: [high] cicd: Some finding (a.yml:3)" in text
    assert "precision" in text and "false-positive rate" in text


def test_text_report_shows_undefined_metrics_as_na():
    results = [_result("safe")]

    text = harness.format_report(results, harness.compute_metrics(results))

    assert "precision               n/a" in text


def test_json_output_has_metrics_and_per_case_detail():
    results = [_result("risky", matched=[(_finding(), _finding())], missed=[_finding()])]

    doc = harness.results_to_json(results, harness.compute_metrics(results))

    json.dumps(doc)  # serializable
    case = doc["cases"][0]
    assert case["passed"] is False
    assert len(case["matched"]) == 1 and len(case["missed"]) == 1
    assert doc["metrics"]["recall"] == pytest.approx(0.5)


# ---------------------------------------------------------------- CLI


def test_cli_runs_the_mock_backend_and_writes_json(tmp_path, capsys):
    out = tmp_path / "results.json"

    assert harness.main(["--json-out", str(out)]) == 0

    results = json.loads(out.read_text())
    assert results["metrics"]["cases"] == 3
    assert {c["name"] for c in results["cases"]} == {c.name for c in harness.load_cases()}
    assert "precision" in capsys.readouterr().out


def test_cli_reads_actual_outputs_from_a_directory(tmp_path):
    out = tmp_path / "results.json"

    code = harness.main(
        ["--actual-dir", str(EVALUATION_DIR / "expected-findings"), "--json-out", str(out)]
    )

    assert code == 0
    metrics = json.loads(out.read_text())["metrics"]
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["false_positive_rate"] == 0.0


def test_cli_missing_actual_output_is_an_error(tmp_path):
    assert harness.main(["--actual-dir", str(tmp_path)]) == 1


def test_cli_rejects_a_bad_runner_spec():
    assert harness.main(["--runner", "not-a-spec"]) == 2


def test_cli_reports_an_invalid_dataset(tmp_path, capsys):
    dataset = _copy_dataset(tmp_path)
    (dataset / "expected-findings" / "cicd-pinned-actions-read-only.json").unlink()

    assert harness.main(["--evaluation-dir", str(dataset)]) == 2
    assert "Invalid evaluation dataset" in capsys.readouterr().err
