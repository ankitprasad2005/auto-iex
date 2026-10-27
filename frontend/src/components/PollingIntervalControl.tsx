import { useEffect, useId, useState } from "react";

const DEFAULT_LABEL = "RTM auto-scrape interval (seconds)";
const DEFAULT_MIN_SECONDS = 10;

interface Props {
  seconds: number;
  onUpdate: (seconds: number) => void;
  updating: boolean;
  label?: string;
  min?: number;
}

export function PollingIntervalControl({
  seconds,
  onUpdate,
  updating,
  label = DEFAULT_LABEL,
  min = DEFAULT_MIN_SECONDS,
}: Props) {
  const [draft, setDraft] = useState(String(seconds));
  const [error, setError] = useState<string | null>(null);
  // useId keeps label/input pairing unique when several controls render on
  // the same page (RTM scrape interval + testnet anchor interval).
  const inputId = useId();

  // The interval is fetched after mount, so the prop can change after the
  // first render; reflect the server's value in the input when it does.
  useEffect(() => {
    setDraft(String(seconds));
  }, [seconds]);

  function handleUpdate() {
    const value = Number(draft);
    if (draft.trim() === "" || !Number.isFinite(value) || value < min) {
      setError(`Interval must be at least ${min} seconds.`);
      return;
    }
    setError(null);
    onUpdate(value);
  }

  return (
    <div className="flex flex-col gap-1 max-w-xs">
      <label htmlFor={inputId} className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
        {label}
      </label>
      <div className="flex gap-2">
        <input
          id={inputId}
          type="number"
          min={min}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="flex-1 bg-nd-surface border border-nd-border-visible text-nd-text-primary font-mono text-sm px-3 py-2 focus:outline-none focus:border-nd-accent"
        />
        <button
          type="button"
          onClick={handleUpdate}
          disabled={updating}
          className="font-mono text-[11px] uppercase tracking-label px-3 py-1.5 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {updating ? "Updating…" : "Update"}
        </button>
      </div>
      {error && (
        <span role="alert" className="font-mono text-[11px] text-nd-accent">
          {error}
        </span>
      )}
    </div>
  );
}
