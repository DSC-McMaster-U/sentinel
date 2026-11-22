import type { SecurityFinding } from "@/types/findings";
import type { ReviewDecision, ReviewDecisionDraft, ReviewStatus } from "@/types/review";
import { formatLocation } from "@/lib/findings";

import { ConfidenceIndicator } from "./ConfidenceIndicator";
import { EvidenceList } from "./EvidenceList";
import { ReviewActions } from "./ReviewActions";
import { SeverityBadge } from "./SeverityBadge";
import { UncertaintyList } from "./UncertaintyList";

const STATUS_LABEL: Record<ReviewStatus, string> = {
  open: "Awaiting review",
  confirmed: "Confirmed",
  dismissed: "Dismissed",
  investigating: "Investigation requested",
};

export interface FindingCardProps {
  finding: SecurityFinding;
  findingKey: string;
  repoUrl: string;
  commitSha: string;
  status: ReviewStatus;
  /** Most recent decision first. */
  history?: ReviewDecision[];
  expanded?: boolean;
  onToggle?: () => void;
  onDecision: (draft: ReviewDecisionDraft) => void;
}

/**
 * One finding. Collapsed, it answers "what, how bad, how sure, where".
 * Expanded, it adds the reasoning a reviewer needs to act on it.
 */
export function FindingCard({
  finding,
  findingKey,
  repoUrl,
  commitSha,
  status,
  history = [],
  expanded = false,
  onToggle,
  onDecision,
}: FindingCardProps) {
  const detailsId = `finding-${encodeURIComponent(findingKey)}`;
  const decided = status === "confirmed" || status === "dismissed";

  return (
    <article
      className={`rounded-lg border bg-white shadow-sm ${decided ? "border-slate-200 opacity-75" : "border-slate-300"}`}
    >
      <header className="flex flex-wrap items-start gap-x-3 gap-y-1 p-4">
        <SeverityBadge severity={finding.severity} />
        <div className="min-w-0 flex-1">
          <h3 className="text-base font-semibold text-slate-900">
            <button
              type="button"
              className="text-left hover:underline"
              aria-expanded={expanded}
              aria-controls={detailsId}
              onClick={onToggle}
            >
              {finding.title}
            </button>
          </h3>
          <p className="mt-0.5 font-mono text-xs text-slate-500">
            {finding.agent} · {formatLocation(finding.evidence[0])}
            {finding.evidence.length > 1 && ` +${finding.evidence.length - 1} more`}
          </p>
          <div className="mt-1.5">
            <ConfidenceIndicator confidence={finding.confidence} />
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          {finding.requires_human_review && (
            <span className="rounded bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-900">
              Needs human review
            </span>
          )}
          <span className="text-xs text-slate-500">{STATUS_LABEL[status]}</span>
        </div>
      </header>

      {expanded && (
        <div id={detailsId} className="space-y-4 border-t border-slate-200 p-4">
          <section aria-label="Description">
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
              <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                History
              </h4>
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
      )}
    </article>
  );
}
