"""Tests for the evaluation fixtures and harness in evaluation/ (#6).

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

from app.schemas import Evidence, FindingSubject, SecurityFinding
from app.schemas.review_report import ReviewReport

EVALUATION_DIR = Path(__file__).resolve().parents[3] / "evaluation"
if not (EVALUATION_DIR / "scripts" / "run_evaluation.py").exists():
    # The backend Docker image copies only backend/, so there is nothing to test.
    pytest.skip(
        "evaluation/ is not available in this checkout", allow_module_level=True
    )

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
    line_end: int | None = None,
    title: str = "Some finding",
) -> SecurityFinding:
    return SecurityFinding(
        agent=agent,
        check_id="test.evaluation",
        subject=FindingSubject(file_path=file_path, key="test-subject"),
        title=title,
        description="A description.",
        severity=severity,
        recommendation="A recommendation.",
        evidence=[
            Evidence(
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                observation="An observation.",
            )
        ],
        confidence=0.7,
        uncertainty=[],
        requires_human_review=False,
    )


def location_match(expected, actual, **kwargs):
    return harness.match_findings(expected, actual, matching_mode="location", **kwargs)


# ---------------------------------------------------------------- dataset


def test_dataset_is_valid_and_has_at_least_six_labelled_cases():
    cases = harness.load_cases()

    assert len(cases) >= 6
    labels = {case.label for case in cases}
    assert labels == {"safe", "risky"}


def test_safe_cases_expect_nothing_and_risky_cases_expect_findings():
    for case in harness.load_cases():
        if case.label == "safe":
            assert case.expected == [], case.name
        else:
            assert case.expected, case.name


def test_expected_evidence_points_at_lines_in_the_fixture_diff():
    for case in harness.load_cases():
        assert harness.check_evidence_locations(case) == [], case.name


def test_expected_findings_are_valid_agent_output_for_their_agent():
    # Each expected finding must be something a real agent could return.
    for case in harness.load_cases():
        for finding in case.expected:
            assert finding.agent in {"dependency", "cicd", "release"}, case.name


def test_check_fixtures_cli_succeeds(capsys):
    assert harness.main(["--check-fixtures"]) == 0
    assert "fixtures" in capsys.readouterr().out


def _copy_dataset(tmp_path: Path) -> Path:
    for sub in ("fixtures/safe", "fixtures/risky", "expected-findings"):
        shutil.copytree(EVALUATION_DIR / sub, tmp_path / sub)
    return tmp_path


def test_missing_expected_file_is_reported(tmp_path):
    dataset = _copy_dataset(tmp_path)
    (dataset / "expected-findings" / "docs-readme-typo.json").unlink()

    with pytest.raises(harness.EvaluationError, match="missing expected findings"):
        harness.load_cases(dataset)


def test_safe_fixture_with_expected_findings_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    path = dataset / "expected-findings" / "docs-readme-typo.json"
    doc = json.loads(path.read_text())
    doc["findings"] = [
        _finding(file_path="README.md", line_start=20).model_dump(mode="json")
    ]
    path.write_text(json.dumps(doc))

    with pytest.raises(
        harness.EvaluationError, match="safe fixtures must expect no findings"
    ):
        harness.load_cases(dataset)


def test_evidence_outside_the_diff_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    path = dataset / "expected-findings" / "cicd-pull-request-target-head-checkout.json"
    doc = json.loads(path.read_text())
    doc["findings"][0]["evidence"][0]["line_start"] = 500
    path.write_text(json.dumps(doc))

    with pytest.raises(harness.EvaluationError, match="outside the lines shown"):
        harness.load_cases(dataset)


def test_diff_new_lines_skips_removed_lines():
    patch = "@@ -5,3 +5,3 @@\n context\n-old\n+new\n context"
    assert harness.diff_new_lines(patch) == {5, 6, 7}


# ---------------------------------------------------------------- matching


def test_matches_same_agent_with_overlapping_evidence():
    result = location_match([_finding(line_start=10)], [_finding(line_start=11)])

    assert len(result.matched) == 1
    assert result.missed == []
    assert result.unexpected == []


def test_does_not_match_a_different_agent():
    result = location_match([_finding(agent="cicd")], [_finding(agent="release")])

    assert result.matched == []
    assert len(result.missed) == 1
    assert len(result.unexpected) == 1


def test_does_not_match_a_different_file():
    result = location_match(
        [_finding(file_path="a.yml")], [_finding(file_path="b.yml")]
    )

    assert result.matched == []


def test_line_tolerance_controls_matching():
    expected = [_finding(line_start=10)]
    actual = [_finding(line_start=14)]

    assert location_match(expected, actual, line_tolerance=2).matched == []
    assert len(location_match(expected, actual, line_tolerance=4).matched) == 1


def test_line_ranges_overlap():
    expected = [_finding(line_start=10, line_end=20)]
    actual = [_finding(line_start=18)]

    assert len(location_match(expected, actual, line_tolerance=0).matched) == 1


def test_titles_are_not_compared():
    result = location_match(
        [_finding(title="A")], [_finding(title="Different wording")]
    )

    assert len(result.matched) == 1


def test_each_actual_finding_matches_at_most_one_expected():
    expected = [_finding(line_start=10), _finding(line_start=11)]
    actual = [_finding(line_start=10)]

    result = location_match(expected, actual)

    assert len(result.matched) == 1
    assert len(result.missed) == 1


def test_duplicate_actual_findings_count_as_false_positives():
    result = location_match([_finding()], [_finding(), _finding()])

    assert len(result.matched) == 1
    assert len(result.unexpected) == 1


def test_prefers_candidate_with_the_same_severity():
    expected = [_finding(severity="critical")]
    actual = [_finding(severity="low"), _finding(severity="critical")]

    result = location_match(expected, actual)

    assert result.matched[0][1].severity == "critical"
    assert result.unexpected[0].severity == "low"


# ---------------------------------------------------------------- metrics


def _produce_from(mapping):
    return lambda case: mapping.get(case.name, [])


def test_expected_findings_score_perfectly():
    cases = harness.load_cases()
    produce = _produce_from({case.name: case.expected for case in cases})

    metrics = harness.compute_metrics(
        [harness.evaluate_case(c, produce) for c in cases]
    )

    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["false_positive_rate"] == 0.0
    assert metrics["false_negative_rate"] == 0.0
    assert metrics["severity_agreement"] == 1.0
    assert metrics["passed"] == metrics["cases"]


def test_reporting_nothing_has_zero_recall_and_undefined_precision():
    cases = harness.load_cases()

    metrics = harness.compute_metrics(
        [harness.evaluate_case(c, _produce_from({})) for c in cases]
    )

    assert metrics["recall"] == 0.0
    assert metrics["precision"] is None
    assert metrics["false_positive_rate"] == 0.0
    assert metrics["false_negative_rate"] == 1.0


def test_flagging_a_safe_pr_raises_false_positive_rate():
    cases = harness.load_cases()
    safe = [c for c in cases if c.label == "safe"]
    produce = _produce_from({safe[0].name: [_finding()]})

    metrics = harness.compute_metrics(
        [harness.evaluate_case(c, produce) for c in cases]
    )

    assert metrics["false_positives"] == 1
    assert metrics["false_positive_rate"] == pytest.approx(1 / len(safe))


def test_min_severity_ignores_lower_findings_on_both_sides():
    cases = harness.load_cases()
    produce = _produce_from({case.name: case.expected for case in cases})

    results = [harness.evaluate_case(c, produce, min_severity="high") for c in cases]

    for result in results:
        assert all(
            f.severity in {"critical", "high"} for f in result.expected + result.actual
        )
    assert harness.compute_metrics(results)["recall"] == 1.0


def test_crashing_runner_is_reported_as_an_error_with_missed_findings():
    case = next(c for c in harness.load_cases() if c.label == "risky")

    def broken(_case):
        raise RuntimeError("agent exploded")

    result = harness.evaluate_case(case, broken)

    assert result.error == "RuntimeError: agent exploded"
    assert result.match.missed == case.expected
    assert harness.compute_metrics([result])["errors"] == 1


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


# ---------------------------------------------------------------- CLI


def test_cli_runs_the_mock_backend_and_writes_json(tmp_path, capsys):
    out = tmp_path / "results.json"

    assert harness.main(["--json-out", str(out)]) == 0

    results = json.loads(out.read_text())
    assert results["metrics"]["cases"] == len(harness.load_cases())
    # The mock review flags any package.json change, so it trips the safe
    # lodash bump and misses the real install-script finding.
    lodash = next(c for c in results["cases"] if c["name"] == "dep-lodash-patch-bump")
    assert lodash["passed"] is False
    assert len(lodash["unexpected"]) == 1
    assert "precision" in capsys.readouterr().out


def test_cli_reads_actual_outputs_from_a_directory(tmp_path):
    out = tmp_path / "results.json"

    code = harness.main(
        [
            "--actual-dir",
            str(EVALUATION_DIR / "expected-findings"),
            "--json-out",
            str(out),
        ]
    )

    assert code == 0
    assert json.loads(out.read_text())["metrics"]["recall"] == 1.0


def test_cli_missing_actual_output_is_an_error(tmp_path):
    assert harness.main(["--actual-dir", str(tmp_path)]) == 1


def test_cli_rejects_a_bad_runner_spec():
    assert harness.main(["--runner", "not-a-spec"]) == 2


def test_default_match_rejects_different_claim_at_same_location():
    result = harness.match_findings(
        [_finding(title="Remote code")], [_finding(title="Other issue")]
    )
    assert not result.matched
    assert len(result.missed) == len(result.unexpected) == 1


def test_exact_duplicate_output_counts_as_false_positive():
    result = harness.match_findings([_finding()], [_finding(), _finding()])
    assert len(result.matched) == len(result.unexpected) == 1


def test_failed_safe_run_is_excluded_from_rates():
    case = next(c for c in harness.load_cases() if c.label == "safe")

    def broken(_case):
        raise RuntimeError("failed")

    metrics = harness.compute_metrics([harness.evaluate_case(case, broken)])
    assert metrics["errors"] == 1
    assert metrics["evaluated_cases"] == 0
    assert metrics["false_positive_rate"] is None


def test_zero_true_positives_with_errors_in_detection_has_zero_f1():
    case = next(c for c in harness.load_cases() if c.label == "risky")
    metrics = harness.compute_metrics(
        [harness.evaluate_case(case, lambda _: [_finding(agent="wrong")])]
    )
    assert metrics["precision"] == metrics["recall"] == metrics["f1"] == 0


def test_placeholder_review_flags_are_not_scored():
    case = next(c for c in harness.load_cases() if c.name == "dep-risky-http-tarball")
    metrics = harness.compute_metrics(
        [harness.evaluate_case(case, lambda _: case.expected)]
    )
    assert metrics["recall"] == 1
    assert metrics["human_review_pairs"] == 0
    assert metrics["human_review_agreement"] is None


@pytest.mark.parametrize("field", ["agents_failed", "agents_partial"])
def test_incomplete_report_is_not_successful_empty_output(field):
    with pytest.raises(harness.EvaluationError, match="did not complete"):
        harness.findings_from_output({"findings": [], field: ["dependency"]})


def test_empty_dataset_is_rejected(tmp_path):
    with pytest.raises(harness.EvaluationError, match="No fixtures"):
        harness.load_cases(tmp_path)


def test_duplicate_expected_identity_is_rejected(tmp_path):
    dataset = _copy_dataset(tmp_path)
    path = dataset / "expected-findings/dep-risky-http-tarball.json"
    doc = json.loads(path.read_text())
    doc["findings"] *= 2
    path.write_text(json.dumps(doc))
    with pytest.raises(harness.EvaluationError, match="duplicate identity"):
        harness.load_cases(dataset)
