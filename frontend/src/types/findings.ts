/**
 * TypeScript mirrors of the shared Pydantic contracts in backend/app/schemas/
 * (#7). Field names stay snake_case so API responses can be used as-is.
 *
 * Keep these in sync with:
 * - Evidence, FindingSubject, SecurityFinding -> backend/app/schemas/finding.py
 * - AgentOutput                -> backend/app/schemas/agent.py
 * - ReviewReport               -> backend/app/schemas/review_report.py
 *
 * See docs/architecture/CONTRACTS.md for example payloads.
 */

/** Potential impact if the finding is true. The backend normalizes to lowercase. */
export type Severity = "critical" | "high" | "medium" | "low";

/** Every severity, most to least severe. Matches the backend sort order. */
export const SEVERITIES: readonly Severity[] = ["critical", "high", "medium", "low"];

/** An observation tied to a location in the reviewed code. */
export interface Evidence {
  file_path: string;
  /** 1-based line in the file at the reviewed commit. */
  line_start: number;
  /** Inclusive end line; null for a single-line observation. */
  line_end: number | null;
  observation: string;
}

/** A logical object identified by a check, independent of evidence line numbers. */
export interface FindingSubject {
  file_path: string;
  /** Stable check-specific key, e.g. dependencies/lodash or jobs/build. */
  key: string;
}

/** A security claim with supporting evidence and explicit review needs. */
export interface SecurityFinding {
  /** Backend-derived identity. Scope stored history by repository + PR + id. */
  readonly id: string;
  /** Name of the agent that produced the finding, e.g. "dependency". */
  agent: string;
  check_id: string;
  subject: FindingSubject;
  title: string;
  description: string;
  severity: Severity;
  recommendation: string;
  /** Always at least one item. */
  evidence: Evidence[];
  /** 0.0 to 1.0: confidence that the evidence supports the claim. */
  confidence: number;
  /** Missing context or assumptions. Empty means none were reported, not certainty. */
  uncertainty: string[];
  /** The agent's explicit review decision, independent of confidence. */
  requires_human_review: boolean;
}

export type AgentStatus = "success" | "failure" | "partial";

/** One agent's result. error_message is set whenever status is not "success". */
export interface AgentOutput {
  agent_name: string;
  findings: SecurityFinding[];
  status: AgentStatus;
  error_message: string | null;
}

/** The combined, deduplicated, severity-ordered result of a review. */
export interface ReviewReport {
  pr_number: number;
  repo_url: string;
  commit_sha: string;
  /** ISO 8601 timestamp. */
  generated_at: string;
  findings: SecurityFinding[];
  agents_run: string[];
  /** Agents whose status was "failure"; they contributed no findings. */
  agents_failed: string[];
  /** Agents whose status was "partial"; their findings may be incomplete. */
  agents_partial: string[];
  requires_human_review: boolean;
}
