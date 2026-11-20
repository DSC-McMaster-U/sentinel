"use client";

import { useId, useState } from "react";

import { validateDecision } from "@/lib/findings";
import type { DismissReason, ReviewAction, ReviewDecisionDraft, ReviewStatus } from "@/types/review";

const DISMISS_REASONS: { value: DismissReason; label: string }[] = [
  { value: "false_positive", label: "False positive: the evidence does not show this issue" },
  { value: "accepted_risk", label: "Accepted risk: real, but understood and accepted" },
  { value: "not_applicable", label: "Not applicable to this repository" },
];

const ACTIONS: { action: ReviewAction; label: string; className: string }[] = [
  { action: "confirm", label: "Confirm", className: "bg-slate-900 text-white hover:bg-slate-700" },
  {
    action: "investigate",
    label: "Request investigation",
    className: "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50",
  },
  {
    action: "dismiss",
    label: "Dismiss",
    className: "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50",
  },
];

export interface ReviewActionsProps {
  findingKey: string;
  status: ReviewStatus;
  /** Called with a validated draft. The parent persists it and updates status. */
  onDecision: (draft: ReviewDecisionDraft) => void;
  disabled?: boolean;
}

export function ReviewActions({ findingKey, status, onDecision, disabled }: ReviewActionsProps) {
  const [pending, setPending] = useState<ReviewAction | null>(null);
  const [reason, setReason] = useState<DismissReason | null>(null);
  const [note, setNote] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [changing, setChanging] = useState(false);
  const noteId = useId();

  function reset() {
    setChanging(false);
    setPending(null);
    setReason(null);
    setNote("");
    setError(null);
  }

  // Switching between dismiss and investigate starts a fresh form: a note
  // written for one action must not be submitted as the other.
  function choose(action: ReviewAction) {
    setPending(action);
    setReason(null);
    setNote("");
    setError(null);
  }

  function submit(action: ReviewAction) {
    const draft: ReviewDecisionDraft = {
      finding_key: findingKey,
      action,
      dismiss_reason: action === "dismiss" ? reason : null,
      note,
    };
    const problem = validateDecision(draft);
    if (problem) {
      setError(problem);
      return;
    }
    onDecision(draft);
    reset();
  }

  // A decided finding shows its outcome; changing it records a new decision
  // and keeps the earlier one in the history.
  if ((status === "confirmed" || status === "dismissed") && !changing) {
    return (
      <button
        type="button"
        className="text-xs text-blue-700 hover:underline disabled:opacity-50"
        onClick={() => setChanging(true)}
        disabled={disabled}
      >
        Change decision
      </button>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2" role="group" aria-label="Review actions">
        {ACTIONS.filter((a) => !(status === "investigating" && a.action === "investigate")).map(
          ({ action, label, className }) => (
            <button
              key={action}
              type="button"
              disabled={disabled}
              aria-pressed={pending === action}
              className={`rounded px-3 py-1.5 text-sm font-medium disabled:opacity-50 ${className}`}
              onClick={() => (action === "confirm" ? submit("confirm") : choose(action))}
            >
              {label}
            </button>
          ),
        )}
        {changing && pending === null && (
          <button type="button" className="px-3 py-1.5 text-sm text-slate-600" onClick={reset}>
            Cancel
          </button>
        )}
      </div>

      {pending && pending !== "confirm" && (
        <div className="space-y-2 rounded border border-slate-200 p-3">
          {pending === "dismiss" && (
            <fieldset>
              <legend className="text-xs font-semibold text-slate-600">Reason</legend>
              {DISMISS_REASONS.map(({ value, label }) => (
                <label key={value} className="mt-1 flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name={`${noteId}-reason`}
                    checked={reason === value}
                    onChange={() => setReason(value)}
                  />
                  {label}
                </label>
              ))}
            </fieldset>
          )}
          <label htmlFor={noteId} className="block text-xs font-semibold text-slate-600">
            {pending === "dismiss" ? "Note (required)" : "What should be checked? (required)"}
          </label>
          <textarea
            id={noteId}
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows={2}
            className="w-full rounded border border-slate-300 p-2 text-sm"
          />
          {error && (
            <p role="alert" className="text-sm text-red-700">
              {error}
            </p>
          )}
          <div className="flex gap-2">
            <button
              type="button"
              className="rounded bg-slate-900 px-3 py-1.5 text-sm font-medium text-white"
              onClick={() => submit(pending)}
            >
              {pending === "dismiss" ? "Dismiss finding" : "Request investigation"}
            </button>
            <button type="button" className="px-3 py-1.5 text-sm text-slate-600" onClick={reset}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
