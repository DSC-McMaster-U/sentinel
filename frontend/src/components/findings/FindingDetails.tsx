import type { SecurityFinding } from "@/types/findings";
import type { ReviewDecision, ReviewDecisionDraft, ReviewStatus } from "@/types/review";

import { EvidenceList } from "./EvidenceList";
import { ReviewActions } from "./ReviewActions";
import { UncertaintyList } from "./UncertaintyList";

export interface FindingDetailsProps {
  finding: SecurityFinding;
  findingKey: string;
  repoUrl: string;
  /** The reviewed commit (ReviewReport.commit_sha). */
  commitSha: string;
  status: ReviewStatus;
  /** Most recent decision first. */
  history?: ReviewDecision[];
  onDecision: (draft: ReviewDecisionDraft) => void;
  /** Id for the region, so the collapsed card header can point aria-controls at it. */
  id?: string;
}

/**
 * The expanded finding view: the reasoning a reviewer needs before acting.
 * Order is deliberate: what the claim is, the evidence for it, what was not
 * verified, what to do, then the reviewer's decision.
 *
 * The collapsed card header (severity, confidence, needs-review badge) is
 * rendered by the findings list and is not part of this component.
 */
export function FindingDetails({
  finding,
  findingKey,
  repoUrl,
  commitSha,
  status,
  history = [],
  onDecision,
  id,
}: FindingDetailsProps) {
  return (
    <div id={id} className="space-y-4 p-4">
      <section aria-label="Description">
        {/* Agent text is derived from untrusted PR content: plain text only. */}
        <p className="text-sm text-slate-800">{finding.description}</p>
      </section>

      <EvidenceList evidence={finding.evidence} repoUrl={repoUrl} commitSha={commitSha} />

      <UncertaintyList uncertainty={finding.uncertainty} />

      <section aria-label="Recommendation" className="rounded bg-emerald-50 p-3">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-emerald-800">
          Recommendation
        </h4>
        <p className="mt-0.5 text-sm text-emerald-950">{finding.recommendation}</p>
      </section>

      <ReviewActions findingKey={findingKey} status={status} onDecision={onDecision} />

      {history.length > 0 && (
        <section aria-label="Review history">
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">History</h4>
          <ul className="mt-1 space-y-1 text-xs text-slate-600">
            {history.map((d) => (
              <li key={`${d.decided_at}-${d.reviewer}`}>
                <span className="font-medium">{d.reviewer}</span> chose {d.action}
                {d.dismiss_reason && ` (${d.dismiss_reason.replace(/_/g, " ")})`} on{" "}
                <time dateTime={d.decided_at}>{new Date(d.decided_at).toLocaleString()}</time>
                {d.commit_sha !== commitSha && ` for an earlier commit ${d.commit_sha.slice(0, 7)}`}
                {d.note && `: ${d.note}`}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
