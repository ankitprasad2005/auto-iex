import type { ConsumptionRangeInput } from "../api/types";

interface Props {
  ranges: ConsumptionRangeInput[];
  onRemove: (index: number) => void;
}

export function RangeList({ ranges, onRemove }: Props) {
  if (ranges.length === 0) {
    return (
      <p className="font-mono text-xs text-nd-text-disabled">No ranges added yet.</p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {ranges.map((r, i) => (
        <li
          key={`${r.start_time}-${r.end_time}-${i}`}
          className="flex items-center justify-between gap-4 bg-nd-surface border border-nd-border px-3 py-2 font-mono text-xs text-nd-text-primary"
        >
          <span>
            {r.start_time}–{r.end_time} · {r.predicted_kw} kW
          </span>
          <button
            type="button"
            aria-label={`Remove range ${r.start_time}-${r.end_time}`}
            onClick={() => onRemove(i)}
            className="text-nd-text-secondary hover:text-nd-accent transition-colors"
          >
            REMOVE
          </button>
        </li>
      ))}
    </ul>
  );
}
