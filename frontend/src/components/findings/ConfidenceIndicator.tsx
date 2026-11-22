import { confidenceBand, formatConfidence } from "@/lib/findings";

const BAND_STYLE = {
  high: { bar: "bg-slate-700", text: "High confidence" },
  moderate: { bar: "bg-slate-500", text: "Moderate confidence" },
  low: { bar: "bg-slate-300", text: "Low confidence" },
} as const;

export interface ConfidenceIndicatorProps {
  /** 0.0 to 1.0. */
  confidence: number;
}

/**
 * Confidence is shown on a neutral scale, separate from severity, so a
 * high-severity claim with weak evidence still reads as high severity.
 */
export function ConfidenceIndicator({ confidence }: ConfidenceIndicatorProps) {
  const band = BAND_STYLE[confidenceBand(confidence)];
  const percent = formatConfidence(confidence);
  return (
    <div className="flex items-center gap-2 text-xs text-slate-600">
      <div
        role="meter"
        aria-label="Confidence"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(confidence * 100)}
        aria-valuetext={`${percent}, ${band.text.toLowerCase()}`}
        className="h-1.5 w-16 overflow-hidden rounded-full bg-slate-100"
      >
        <div className={`h-full ${band.bar}`} style={{ width: percent }} />
      </div>
      <span className="tabular-nums">{percent}</span>
      <span>{band.text}</span>
    </div>
  );
}
