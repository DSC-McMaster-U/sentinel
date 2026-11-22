export interface UncertaintyListProps {
  uncertainty: string[];
}

/**
 * Lists what the agent could not check. An empty list is shown explicitly as
 * "none reported", because it means the agent named no gaps, not that the
 * finding is certain.
 */
export function UncertaintyList({ uncertainty }: UncertaintyListProps) {
  return (
    <section aria-label="Uncertainty">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        What Sentinel could not verify
      </h4>
      {uncertainty.length === 0 ? (
        <p className="mt-1 text-sm italic text-slate-500">No gaps reported by the agent.</p>
      ) : (
        <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm text-slate-800">
          {uncertainty.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
