import type { Evidence } from "@/types/findings";
import { evidenceUrl, formatLocation } from "@/lib/findings";

export interface EvidenceListProps {
  evidence: Evidence[];
  repoUrl: string;
  /** The reviewed commit, so links open the exact code the agent saw. */
  commitSha: string;
}

export function EvidenceList({ evidence, repoUrl, commitSha }: EvidenceListProps) {
  return (
    <section aria-label="Evidence">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        Evidence ({evidence.length})
      </h4>
      <ol className="mt-1 space-y-2">
        {evidence.map((item) => (
          <li
            key={formatLocation(item)}
            className="rounded border border-slate-200 bg-slate-50 px-3 py-2"
          >
            <a
              href={evidenceUrl(repoUrl, commitSha, item)}
              target="_blank"
              rel="noreferrer noopener"
              className="font-mono text-xs text-blue-700 underline-offset-2 hover:underline"
            >
              {formatLocation(item)}
            </a>
            {/* Observations come from agent output, which is derived from
                untrusted PR content: render as text, never as HTML. */}
            <p className="mt-0.5 text-sm text-slate-800">{item.observation}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
