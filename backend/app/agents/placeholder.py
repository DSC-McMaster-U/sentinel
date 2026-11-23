"""Shared builder for Sprint 1 placeholder agents; real checks come from #2."""

from app.schemas import (
    AgentInput,
    AgentOutput,
    Evidence,
    FindingSubject,
    SecurityFinding,
)


def build_placeholder_output(
    agent_name: str, label: str, agent_input: AgentInput
) -> AgentOutput:
    """Return one deterministic mock finding per file selected for the agent.

    File contents and patches are not inspected.
    """
    findings = [
        SecurityFinding(
            agent=agent_name,
            check_id=f"mock.{agent_name}.file-changed",
            subject=FindingSubject(file_path=file.path, key="file"),
            title=f"Mock finding: {label} changed",
            description=f"Placeholder finding showing how the {agent_name} agent reports a change.",
            severity="low",
            recommendation=f"Review the {label} changes before merging.",
            evidence=[
                Evidence(
                    file_path=file.path,
                    line_start=1,  # Placeholder required by the Evidence schema.
                    observation=f"The PR lists {file.path} as a changed file.",
                )
            ],
            confidence=0.0,
            uncertainty=["This placeholder agent does not inspect the file contents."],
            requires_human_review=False,
        )
        for file in agent_input.changed_files
    ]
    return AgentOutput(agent_name=agent_name, findings=findings, status="success")
