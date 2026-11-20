/** Helpers for the expanded finding view and review actions. No UI, no data fetching. */

import type { Evidence, SecurityFinding } from "@/types/findings";
import type { ReviewAction, ReviewDecisionDraft, ReviewStatus } from "@/types/review";
import { STATUS_AFTER_ACTION } from "@/types/review";

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
 * Stable identity for a finding. SecurityFinding has no id field, so this
 * uses the same rule combine_findings() uses for duplicates: agent, title and
 * the set of evidence locations. Review decisions are keyed on it.
 */
export function findingKey(finding: SecurityFinding): string {
  const locations = finding.evidence
    .map((e) => `${e.file_path}:${e.line_start}:${e.line_end ?? ""}`)
    .sort()
    .join("|");
  return `${finding.agent}::${finding.title}::${locations}`;
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
