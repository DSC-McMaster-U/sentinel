"""Run from backend/: python -m pytest tests/unit/test_evaluation_matching.py -q."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if not (ROOT / "evaluation/scripts/matching.py").exists():
    pytest.skip("evaluation/ is not available", allow_module_level=True)
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "evaluation" / "scripts"))

from matching import compare_findings

from app.schemas import Evidence, PullRequestInput, SecurityFinding


def finding(**changes):
    payload = {
        "agent": "dependency",
        "title": "Install script executes remote code",
        "description": "An install hook downloads and executes a script.",
        "severity": "high",
        "recommendation": "Remove the remote execution hook.",
        "evidence": [
            Evidence(
                file_path="package.json",
                line_start=5,
                line_end=5,
                observation="Remote script is piped into sh.",
            )
        ],
        "confidence": 0.9,
        "uncertainty": [],
        "requires_human_review": True,
    }
    payload.update(changes)
    return SecurityFinding(**payload)


def test_match_keeps_expected_actual_pair_and_inputs():
    expected, actual = finding(), finding(confidence=0.5, severity="medium")
    before = actual.model_dump()
    result = compare_findings([expected], [actual])
    assert result.matched == [(expected, actual)]
    assert result.passed
    assert actual.model_dump() == before


def test_missed_and_unexpected():
    expected, actual = finding(), finding(title="Another issue")
    result = compare_findings([expected], [actual])
    assert result.missed == [expected]
    assert result.unexpected == [actual]
    assert not result.matched and not result.passed


def test_duplicate_match_fails_without_extra_false_positive():
    f = finding()
    result = compare_findings([f], [f, f, f])
    assert len(result.matched) == 1
    assert result.duplicates == [f, f]
    assert not result.unexpected and not result.passed


def test_duplicate_unexpected_counts_once():
    f = finding()
    result = compare_findings([], [f, f])
    assert result.unexpected == [f]
    assert result.duplicates == [f]


def test_duplicate_expected_is_annotation_error():
    f = finding()
    with pytest.raises(ValueError, match="duplicate"):
        compare_findings([f, f], [])


@pytest.mark.parametrize(
    "changes",
    [
        {"agent": "cicd"},
        {"title": "install script executes remote code"},
        {
            "evidence": [
                Evidence(
                    file_path="other.json", line_start=5, line_end=5, observation="x"
                )
            ]
        },
        {
            "evidence": [
                Evidence(
                    file_path="package.json", line_start=6, line_end=6, observation="x"
                )
            ]
        },
        {
            "evidence": [
                Evidence(
                    file_path="package.json",
                    line_start=5,
                    line_end=None,
                    observation="x",
                )
            ]
        },
    ],
)
def test_identity_difference_is_not_a_match(changes):
    result = compare_findings([finding()], [finding(**changes)])
    assert len(result.missed) == len(result.unexpected) == 1


def test_evidence_order_and_prose_do_not_change_identity():
    a = Evidence(file_path="a", line_start=1, observation="a")
    b = Evidence(file_path="b", line_start=2, observation="b")
    result = compare_findings(
        [finding(evidence=[a, b])],
        [finding(evidence=[b, a], description="Different wording")],
    )
    assert result.passed


def test_empty_and_missing_output_lists():
    assert compare_findings([], []).passed
    assert len(compare_findings([finding()], []).missed) == 1


def test_distinct_locations_match_one_to_one_despite_output_order():
    a = finding()
    b = finding(evidence=[Evidence(file_path="b", line_start=1, observation="x")])
    result = compare_findings([a, b], [b, a])
    assert result.matched == [(b, b), (a, a)] and result.passed


def test_dependency_fixtures_validate_and_evidence_points_to_added_lines():
    fixtures = [
        ROOT / "evaluation/fixtures" / name
        for name in (
            "safe/dep-safe-local-install-script.json",
            "risky/dep-risky-remote-install-script.json",
            "risky/dep-risky-http-tarball.json",
        )
    ]
    for path in fixtures:
        pr = PullRequestInput.model_validate_json(path.read_text(encoding="utf-8"))
        expected_path = ROOT / "evaluation" / "expected-findings" / path.name
        expected = [
            SecurityFinding.model_validate(f)
            for f in json.loads(expected_path.read_text(encoding="utf-8"))["findings"]
        ]
        assert bool(expected) == (path.parent.name == "risky")
        assert compare_findings(expected, expected).passed  # wiring, not agent accuracy
        files = {f.path: f for f in pr.files_changed}
        for f in expected:
            assert f.agent == "dependency"
            for e in f.evidence:
                changed = files[e.file_path]
                # These fixtures use complete file-creation diffs from line 1.
                added = [
                    line[1:]
                    for line in changed.patch.splitlines()
                    if line.startswith("+") and not line.startswith("+++")
                ]
                assert changed.additions == len(added)
                assert 1 <= e.line_start <= (e.line_end or e.line_start) <= len(added)
                assert e.observation in "\n".join(
                    added[e.line_start - 1 : e.line_end or e.line_start]
                )
