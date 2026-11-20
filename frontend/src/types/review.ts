/**
 * Human review decisions on findings.
 *
 * PROPOSED (#6): the backend has no review-decision schema yet. These types
 * describe the design in docs/architecture/findings-dashboard.md so the UI
 * prototype has something concrete to target. They should move into
 * backend/app/schemas/ (owned by #7) when decisions are persisted in Sprint 4.
 */

/** What a reviewer can do with a finding. */
export type ReviewAction = "confirm" | "dismiss" | "investigate";

/** Where a finding stands in review. "open" means nobody has acted yet. */
export type ReviewStatus = "open" | "confirmed" | "dismissed" | "investigating";

/** Why a finding was dismissed. Dismissals always need a reason. */
export type DismissReason =
  /** The claim is wrong: the evidence does not show the issue. */
  | "false_positive"
  /** The claim is right, but the risk is understood and accepted. */
  | "accepted_risk"
  /** The claim is right in general but does not apply in this repository. */
  | "not_applicable";

export interface ReviewDecision {
  /** Stable finding identity; see findingKey() in src/lib/findings.ts. */
  finding_key: string;
  /** The commit the decision was made against (ReviewReport.commit_sha). */
  commit_sha: string;
  action: ReviewAction;
  /** Required when action is "dismiss". */
  dismiss_reason: DismissReason | null;
  /** Required for "dismiss" and "investigate", optional for "confirm". */
  note: string;
  /** GitHub login of the reviewer. */
  reviewer: string;
  /** ISO 8601 timestamp. */
  decided_at: string;
}

/** The draft a reviewer submits; the server adds reviewer and timestamp. */
export type ReviewDecisionDraft = Pick<
  ReviewDecision,
  "finding_key" | "action" | "dismiss_reason" | "note"
>;

/** Status a finding moves to after each action. */
export const STATUS_AFTER_ACTION: Record<ReviewAction, ReviewStatus> = {
  confirm: "confirmed",
  dismiss: "dismissed",
  investigate: "investigating",
};
