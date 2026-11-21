"use client";

import { useMemo, useState } from "react";

import { SEVERITIES } from "@/types/findings";
import type { ReviewReport, Severity } from "@/types/findings";
import type { ReviewDecision, ReviewDecisionDraft, ReviewStatus } from "@/types/review";
import { findingKey, sortFindings, SEVERITY_LABEL } from "@/lib/findings";

import { FindingCard } from "./FindingCard";
import { ReportSummary } from "./ReportSummary";

export interface FindingsListProps {
  report: ReviewReport;
  /** Current status per finding key; missing keys are "open". */
  statuses: Record<string, ReviewStatus>;
  /** Decision history per finding key, most recent first. */
  history?: Record<string, ReviewDecision[]>;
  onDecision: (draft: ReviewDecisionDraft) => void;
}

type StatusFilter = "unresolved" | "all";

/** The review page body: summary, filters and the finding cards. Data comes
 * in through props; the page that renders this owns fetching and saving. */
export function FindingsList({ report, statuses, history = {}, onDecision }: FindingsListProps) {
  const [severityFilter, setSeverityFilter] = useState<Set<Severity>>(new Set(SEVERITIES));
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("unresolved");
  const [expanded, setExpanded] = useState<string | null>(null);

  const rows = useMemo(
    () =>
      sortFindings(report.findings).map((finding) => {
        const key = findingKey(finding);
        return { finding, key, status: statuses[key] ?? "open" };
      }),
    [report.findings, statuses],
  );

  const openCount = rows.filter((r) => r.status === "open").length;
  const visible = rows.filter(
    (r) =>
      severityFilter.has(r.finding.severity) &&
      (statusFilter === "all" || r.status === "open" || r.status === "investigating"),
  );

  function toggleSeverity(severity: Severity) {
    setSeverityFilter((current) => {
      const next = new Set(current);
      if (next.has(severity)) next.delete(severity);
      else next.add(severity);
      return next;
    });
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-4">
      <ReportSummary report={report} openCount={openCount} />

      {rows.length > 0 && (
        <div className="flex flex-wrap items-center gap-3 text-sm" role="group" aria-label="Filters">
          {SEVERITIES.map((s) => (
            <label key={s} className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={severityFilter.has(s)}
                onChange={() => toggleSeverity(s)}
              />
              {SEVERITY_LABEL[s]}
            </label>
          ))}
          <select
            aria-label="Review status"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
            className="rounded border border-slate-300 px-2 py-1"
          >
            <option value="unresolved">Unresolved</option>
            <option value="all">All findings</option>
          </select>
        </div>
      )}

      {rows.length === 0 ? (
        <p className="rounded border border-dashed border-slate-300 p-6 text-center text-sm text-slate-600">
          No findings from the agents that ran
          {report.agents_run.length > 0 ? ` (${report.agents_run.join(", ")})` : ""}. This is not a
          guarantee that the pull request is safe.
        </p>
      ) : visible.length === 0 ? (
        <p className="p-6 text-center text-sm text-slate-600">
          No findings match these filters. {rows.length - visible.length} hidden.
        </p>
      ) : (
        <ul className="space-y-3">
          {visible.map(({ finding, key, status }) => (
            <li key={key}>
              <FindingCard
                finding={finding}
                findingKey={key}
                repoUrl={report.repo_url}
                commitSha={report.commit_sha}
                status={status}
                history={history[key]}
                expanded={expanded === key}
                onToggle={() => setExpanded((cur) => (cur === key ? null : key))}
                onDecision={onDecision}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
