"""Example payloads and validation boundaries for shared agent schemas."""

import pytest
from pydantic import ValidationError

from app.schemas import AgentInput, AgentOutput, ChangedFile, Evidence, SecurityFinding


@pytest.fixture
def finding_payload():
    return {
        "agent": "cicd",
        "title": "Untrusted input in a shell command",
        "description": "A workflow interpolates the PR title into a shell command.",
        "severity": "critical",
        "risks": "An attacker could execute commands in the CI runner.",
        "evidence": [
            {
                "file_path": ".github/workflows/build.yml",
                "line_start": 12,
                "line_end": 14,
                "observation": "The run step references github.event.pull_request.title.",
            }
        ],
        "confidence": 0.8,
        "uncertainty": ["Runner permissions have not been verified."],
        "requires_human_review": True,
    }


@pytest.fixture
def input_payload():
    return {
        "pr_number": 42,
        "commit_sha": "abc123",
        "repo_url": "https://github.com/example/repo",
        "changed_files": [
            {
                "file_path": ".github/workflows/build.yml",
                "patch": '@@ -12 +12 @@\n- run: echo safe\n+ run: echo "${{ github.event.pull_request.title }}"',
            }
        ],
    }


def test_agent_input_example_round_trip(input_payload):
    context = AgentInput.model_validate(input_payload)
    assert isinstance(context.changed_files[0], ChangedFile)
    assert context.changed_files[0].patch == input_payload["changed_files"][0]["patch"]
    assert AgentInput.model_validate_json(context.model_dump_json()) == context


def test_agent_output_example_round_trip(finding_payload):
    output = AgentOutput(
        agent_name="cicd", findings=[finding_payload], status="success"
    )
    assert isinstance(output.findings[0], SecurityFinding)
    assert isinstance(output.findings[0].evidence[0], Evidence)
    assert output.model_dump(mode="json")["findings"][0]["severity"] == "critical"
    assert AgentOutput.model_validate_json(output.model_dump_json()) == output


@pytest.mark.parametrize("status", ["success", "failure", "partial"])
def test_agent_output_statuses(status):
    output = AgentOutput(
        agent_name="cicd",
        findings=[],
        status=status,
        error_message=None if status == "success" else "Context retrieval failed.",
    )
    assert output.findings == []
    assert output.status == status


@pytest.mark.parametrize("field", ["agent", "title", "description", "risks"])
def test_finding_rejects_empty_required_strings(finding_payload, field):
    finding_payload[field] = ""
    with pytest.raises(ValidationError) as exc:
        SecurityFinding.model_validate(finding_payload)
    assert exc.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize(
    ("field", "value"),
    [("pr_number", 0), ("pr_number", -1), ("commit_sha", ""),
     ("changed_files", []), ("changed_files", ["build.yml"])],
)
def test_agent_input_rejects_invalid_fields(input_payload, field, value):
    input_payload[field] = value
    with pytest.raises(ValidationError) as exc:
        AgentInput.model_validate(input_payload)
    assert exc.value.errors()[0]["loc"][0] == field


def test_changed_file_rejects_empty_path(input_payload):
    input_payload["changed_files"][0]["file_path"] = ""
    with pytest.raises(ValidationError) as exc:
        AgentInput.model_validate(input_payload)
    assert exc.value.errors()[0]["loc"] == ("changed_files", 0, "file_path")


@pytest.mark.parametrize("confidence", [0.0, 1.0])
def test_confidence_includes_bounds(finding_payload, confidence):
    finding_payload["confidence"] = confidence
    assert SecurityFinding.model_validate(finding_payload).confidence == confidence


@pytest.mark.parametrize(
    ("severity", "expected"),
    [
        ("critical", "critical"),
        ("CRITICAL", "critical"),
        ("Critical", "critical"),
        ("high", "high"),
        ("HIGH", "high"),
        ("High", "high"),
        ("medium", "medium"),
        ("MEDIUM", "medium"),
        ("Medium", "medium"),
        ("low", "low"),
        ("LOW", "low"),
        ("Low", "low"),
    ],
)
def test_severity_is_case_insensitive(finding_payload, severity, expected):
    finding_payload["severity"] = severity
    finding = SecurityFinding.model_validate(finding_payload)
    assert finding.severity == expected
    assert finding.model_dump(mode="json")["severity"] == expected


@pytest.mark.parametrize("severity", ["Severe", "unknown", "", None, 1])
def test_severity_rejects_invalid_values(finding_payload, severity):
    finding_payload["severity"] = severity
    with pytest.raises(ValidationError) as exc:
        SecurityFinding.model_validate(finding_payload)
    assert exc.value.errors()[0]["loc"] == ("severity",)


@pytest.mark.parametrize(
    ("field", "value"),
    [("confidence", -0.1), ("confidence", 1.1), ("evidence", [])],
)
def test_finding_rejects_invalid_fields(finding_payload, field, value):
    finding_payload[field] = value
    with pytest.raises(ValidationError) as exc:
        SecurityFinding.model_validate(finding_payload)
    assert exc.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize(
    ("field", "value"),
    [("file_path", ""), ("observation", ""),
     ("line_start", 0), ("line_end", 0)],
)
def test_evidence_rejects_invalid_fields(finding_payload, field, value):
    evidence = finding_payload["evidence"][0]
    evidence[field] = value
    with pytest.raises(ValidationError) as exc:
        Evidence.model_validate(evidence)
    assert exc.value.errors()[0]["loc"] == (field,)


def test_evidence_end_line_is_optional(finding_payload):
    evidence = finding_payload["evidence"][0]
    del evidence["line_end"]
    assert Evidence.model_validate(evidence).line_end is None


@pytest.mark.parametrize("field", ["uncertainty", "requires_human_review"])
def test_finding_requires_explicit_review_context(finding_payload, field):
    del finding_payload[field]
    with pytest.raises(ValidationError) as exc:
        SecurityFinding.model_validate(finding_payload)
    assert exc.value.errors()[0]["loc"] == (field,)


def test_agent_output_rejects_unknown_status():
    with pytest.raises(ValidationError):
        AgentOutput(agent_name="cicd", findings=[], status="unknown") # type: ignore


def test_evidence_rejects_reversed_line_range(finding_payload):
    finding_payload["evidence"][0].update(line_start=5, line_end=2)
    with pytest.raises(ValidationError, match="line_end must be greater than or equal"):
        SecurityFinding.model_validate(finding_payload)


@pytest.mark.parametrize("line_end", [12, 14, None])
def test_evidence_accepts_valid_line_ranges(finding_payload, line_end):
    evidence = finding_payload["evidence"][0]
    evidence["line_end"] = line_end
    assert Evidence.model_validate(evidence).line_end == line_end


@pytest.mark.parametrize("status", ["failure", "partial"])
def test_unsuccessful_output_requires_error_message(status):
    with pytest.raises(ValidationError, match="requires a nonblank error_message"):
        AgentOutput(agent_name="cicd", findings=[], status=status)


@pytest.mark.parametrize("status", ["failure", "partial"])
@pytest.mark.parametrize("error_message", [None, "", " \t"])
def test_unsuccessful_output_rejects_blank_errors(status, error_message):
    with pytest.raises(ValidationError, match="requires a nonblank error_message"):
        AgentOutput(
            agent_name="cicd", findings=[], status=status, error_message=error_message
        )


@pytest.mark.parametrize("error_message", ["Unexpected failure", ""])
def test_successful_output_rejects_error_message(error_message):
    with pytest.raises(ValidationError, match="must not include an error_message"):
        AgentOutput(
            agent_name="cicd", findings=[], status="success", error_message=error_message
        )


def test_agent_output_rejects_mismatched_finding_agent(finding_payload):
    other_finding = {**finding_payload, "agent": "dependency"}
    with pytest.raises(ValidationError, match="agent must match agent_name"):
        AgentOutput(
            agent_name="cicd", findings=[finding_payload, other_finding], status="success"
        )


def test_partial_output_preserves_findings_and_error(finding_payload):
    output = AgentOutput(
        agent_name="cicd",
        findings=[finding_payload],
        status="partial",
        error_message="Could not retrieve another file.",
    )
    assert len(output.findings) == 1
    assert output.error_message == "Could not retrieve another file."
    assert AgentOutput.model_validate_json(output.model_dump_json()) == output
