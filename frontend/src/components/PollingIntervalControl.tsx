import { useState } from "react";

const MIN_SECONDS = 10;

interface Props {
  seconds: number;
  onUpdate: (seconds: number) => void;
  updating: boolean;
}

export function PollingIntervalControl({ seconds, onUpdate, updating }: Props) {
  const [draft, setDraft] = useState(String(seconds));
  const [error, setError] = useState<string | null>(null);

  function handleUpdate() {
    const value = Number(draft);
    if (!Number.isFinite(value) || value < MIN_SECONDS) {
      setError(`Interval must be at least ${MIN_SECONDS} seconds.`);
      return;
    }
    setError(null);
    onUpdate(value);
  }

  return (
    <div className="flex flex-col gap-1 max-w-xs">
      <label htmlFor="rtm-interval" className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
        RTM auto-scrape interval (seconds)
      </label>
      <div className="flex gap-2">
        <input
          id="rtm-interval"
          type="number"
          min={MIN_SECONDS}
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
