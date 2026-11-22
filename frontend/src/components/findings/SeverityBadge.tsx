import type { Severity } from "@/types/findings";
import { SEVERITY_LABEL } from "@/lib/findings";

// Colour is never the only signal: every badge also carries a text label and
// a distinct marker so severity reads the same in greyscale and to screen readers.
const STYLES: Record<Severity, { className: string; marker: string }> = {
  critical: { className: "bg-red-700 text-white ring-red-800", marker: "◆" },
  high: { className: "bg-orange-100 text-orange-900 ring-orange-300", marker: "▲" },
  medium: { className: "bg-amber-50 text-amber-900 ring-amber-300", marker: "●" },
  low: { className: "bg-slate-100 text-slate-700 ring-slate-300", marker: "○" },
};

export interface SeverityBadgeProps {
  severity: Severity;
  /** Optional count, used in the report summary ("High 3"). */
  count?: number;
}

export function SeverityBadge({ severity, count }: SeverityBadgeProps) {
  const style = STYLES[severity];
  return (
    <span
      className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-semibold ring-1 ring-inset ${style.className}`}
    >
      <span aria-hidden="true">{style.marker}</span>
      <span>
        {SEVERITY_LABEL[severity]}
        {count !== undefined && <span className="sr-only"> severity findings:</span>}
      </span>
      {count !== undefined && <span className="tabular-nums">{count}</span>}
    </span>
  );
}
