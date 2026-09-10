import { FormEvent, useState } from "react";
import type { ConsumptionRangeInput } from "../api/types";

interface Props {
  onAddRange: (range: ConsumptionRangeInput) => void;
}

function toMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

export function ConsumptionForm({ onAddRange }: Props) {
  const [startTime, setStartTime] = useState("00:00");
  const [endTime, setEndTime] = useState("00:15");
  const [predictedKw, setPredictedKw] = useState("1");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const kw = Number(predictedKw);

    if (toMinutes(endTime) <= toMinutes(startTime)) {
      setError("End time must be after start time.");
      return;
    }
    if (!(kw > 0)) {
      setError("Predicted kW must be positive.");
      return;
    }

    setError(null);
    onAddRange({ start_time: startTime, end_time: endTime, predicted_kw: kw });
  }

  const labelClass = "font-mono text-[11px] uppercase tracking-label text-nd-text-secondary";
  const inputClass =
    "mt-1 w-full bg-nd-surface border border-nd-border-visible text-nd-text-primary font-mono text-sm px-3 py-2 focus:outline-none focus:border-nd-accent";

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 bg-nd-black p-6 border border-nd-border">
      <label htmlFor="start-time" className={labelClass}>
        Start time
        <input
          id="start-time"
          type="time"
          value={startTime}
          onChange={(e) => setStartTime(e.target.value)}
          className={inputClass}
        />
      </label>
      <label htmlFor="end-time" className={labelClass}>
        End time
        <input
          id="end-time"
          type="time"
          value={endTime}
          onChange={(e) => setEndTime(e.target.value)}
          className={inputClass}
        />
      </label>
      <label htmlFor="predicted-kw" className={labelClass}>
        Predicted kW
        <input
          id="predicted-kw"
          type="number"
          step="0.1"
          value={predictedKw}
          onChange={(e) => setPredictedKw(e.target.value)}
          className={inputClass}
        />
      </label>
      {error && (
        <p role="alert" className="font-mono text-xs text-nd-accent">
          {error}
        </p>
      )}
      <button
        type="submit"
        className="self-start bg-nd-text-primary text-nd-black font-mono text-xs uppercase tracking-label px-4 py-2 hover:bg-white transition-colors"
      >
        Add range
      </button>
    </form>
  );
}
