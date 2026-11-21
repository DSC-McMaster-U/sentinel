/** Formatting and grouping helpers for findings. No UI, no data fetching. */

import { SEVERITIES } from "@/types/findings";
import type { Evidence, ReviewReport, SecurityFinding, Severity } from "@/types/findings";
import type { ReviewAction, ReviewDecisionDraft, ReviewStatus } from "@/types/review";
import { STATUS_AFTER_ACTION } from "@/types/review";

export const SEVERITY_LABEL: Record<Severity, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

/** Severity counts for a report. Mirrors ReviewReport.severity_counts, which is
 * a Python property and so is not included in the API response. */
export function severityCounts(findings: SecurityFinding[]): Record<Severity, number> {
  const counts: Record<Severity, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const finding of findings) counts[finding.severity] += 1;
  return counts;
}

/** Sort by severity (most severe first), then by confidence (highest first). */
export function sortFindings(findings: SecurityFinding[]): SecurityFinding[] {
  const rank = (s: Severity) => SEVERITIES.indexOf(s);
  return [...findings].sort(
    (a, b) => rank(a.severity) - rank(b.severity) || b.confidence - a.confidence,
  );
}

export type ConfidenceBand = "high" | "moderate" | "low";

/** Display bands for confidence. They are a reading aid and are never used to
 * hide a finding or to decide whether it needs human review. */
export function confidenceBand(confidence: number): ConfidenceBand {
  if (confidence >= 0.8) return "high";
  if (confidence >= 0.5) return "moderate";
  return "low";
}

export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

/** "path/to/file.yml:12" or "path/to/file.yml:12-18". */
export function formatLocation(evidence: Evidence): string {
  const { file_path, line_start, line_end } = evidence;
  return line_end && line_end !== line_start
    ? `${file_path}:${line_start}-${line_end}`
    : `${file_path}:${line_start}`;
}

/** Link to the evidence lines on GitHub at the reviewed commit, so the code
 * shown is exactly what the agent saw rather than the branch's latest state. */
export function evidenceUrl(repoUrl: string, commitSha: string, evidence: Evidence): string {
  const base = repoUrl.replace(/\/+$/, "");
  const path = evidence.file_path.split("/").map(encodeURIComponent).join("/");
  const lines =
    evidence.line_end && evidence.line_end !== evidence.line_start
      ? `L${evidence.line_start}-L${evidence.line_end}`
      : `L${evidence.line_start}`;
  return `${base}/blob/${encodeURIComponent(commitSha)}/${path}#${lines}`;
}

/**
 * Backend identity within a repository and PR. The parent must scope saved
 * review history to that repository and PR, and decisions to their commit.
 */
export function findingKey(finding: SecurityFinding): string {
  return finding.id;
}

export interface CoverageNotice {
  tone: "warning" | "info";
  message: string;
}

/** Explain what an empty or partial report does and does not mean. */
export function coverageNotices(report: ReviewReport): CoverageNotice[] {
  const notices: CoverageNotice[] = [];
  if (report.agents_failed.length > 0) {
    notices.push({
      tone: "warning",
      message: `${report.agents_failed.join(", ")} failed and reported no findings. Files they cover were not checked.`,
    });
  }
  if (report.agents_partial.length > 0) {
    notices.push({
      tone: "warning",
      message: `${report.agents_partial.join(", ")} only partially completed. Their findings may be incomplete.`,
    });
  }
  if (report.agents_run.length === 0) {
    notices.push({
      tone: "info",
      message: "No agent covered the files in this pull request, so nothing was checked.",
    });
  }
  return notices;
}

/** Client-side validation that mirrors the decision rules in the design doc. */
export function validateDecision(draft: ReviewDecisionDraft): string | null {
  if (draft.action === "dismiss" && !draft.dismiss_reason) {
    return "Choose why this finding is being dismissed.";
  }
  if (draft.action !== "confirm" && draft.note.trim() === "") {
    return draft.action === "dismiss"
      ? "Add a note explaining the dismissal."
      : "Describe what needs to be investigated.";
  }
  return null;
}

export function statusAfter(action: ReviewAction): ReviewStatus {
  return STATUS_AFTER_ACTION[action];
}
