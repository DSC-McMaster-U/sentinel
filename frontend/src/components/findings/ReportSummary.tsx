import { SEVERITIES } from "@/types/findings";
import type { ReviewReport } from "@/types/findings";
import { coverageNotices, severityCounts } from "@/lib/findings";

import { SeverityBadge } from "./SeverityBadge";

export interface ReportSummaryProps {
  report: ReviewReport;
  /** Findings still awaiting a reviewer decision. */
  openCount: number;
}

/** Top of the review page: overall verdict, counts and agent coverage. */
export function ReportSummary({ report, openCount }: ReportSummaryProps) {
  const counts = severityCounts(report.findings);
  const notices = coverageNotices(report);
  const shortSha = report.commit_sha.slice(0, 7);

  return (
    <section aria-label="Review summary" className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-xl font-semibold text-slate-900">
          PR #{report.pr_number}{" "}
          <span className="font-mono text-sm font-normal text-slate-500">at {shortSha}</span>
        </h2>
        <p className="text-xs text-slate-500">
          Generated <time dateTime={report.generated_at}>{new Date(report.generated_at).toLocaleString()}</time>
        </p>
      </div>

      {report.requires_human_review ? (
        <p className="rounded border border-violet-300 bg-violet-50 p-3 text-sm text-violet-950">
          <strong>Human review required.</strong> {openCount} of {report.findings.length} findings
          awaiting a decision.
        </p>
      ) : (
        <p className="rounded border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
          No finding or agent result asked for human review.
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        {SEVERITIES.map((s) => (
          <SeverityBadge key={s} severity={s} count={counts[s]} />
        ))}
      </div>

      <p className="text-xs text-slate-600">
        Agents run: {report.agents_run.length > 0 ? report.agents_run.join(", ") : "none"}
      </p>

      {notices.map((n) => (
        <p
          key={n.message}
          role={n.tone === "warning" ? "alert" : undefined}
          className={`rounded p-2 text-sm ${n.tone === "warning" ? "bg-amber-50 text-amber-950" : "bg-slate-50 text-slate-700"}`}
        >
          {n.message}
        </p>
      ))}
    </section>
  );
}
