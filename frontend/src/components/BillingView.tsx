import type { BillingHistory } from "../api/types";

interface Props {
  history: BillingHistory;
  onLoadDemo: () => void;
  loading: boolean;
}

export function BillingView({ history, onLoadDemo, loading }: Props) {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between gap-4">
        <div className="flex gap-12">
          <div className="flex flex-col gap-1">
            <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
              Total billed
            </span>
            <span className="font-display text-4xl text-nd-text-display">₹{history.total_cost_rs}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
              Total energy
            </span>
            <span className="font-display text-4xl text-nd-text-display">{history.total_kwh} kWh</span>
          </div>
        </div>
        <button
          type="button"
          onClick={onLoadDemo}
          disabled={loading}
          className="font-mono text-[11px] uppercase tracking-label px-3 py-1.5 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
        >
          {loading ? "Loading…" : "Load demo data"}
        </button>
      </div>

      {history.records.length === 0 ? (
        <p className="font-mono text-sm text-nd-text-secondary">
          No billing history yet — click "Load demo data" to see a sample month.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[560px] font-mono text-xs text-nd-text-primary border-collapse">
            <thead>
              <tr className="text-left text-nd-text-secondary uppercase tracking-label text-[11px]">
                <th className="py-2 pr-4">Date</th>
                <th className="py-2 pr-4">Time</th>
                <th className="py-2 pr-4">Market</th>
                <th className="py-2 pr-4">Energy (kWh)</th>
                <th className="py-2 pr-4">Cost (₹)</th>
              </tr>
            </thead>
            <tbody>
              {history.records.map((r, i) => (
                <tr key={`${r.date}-${r.time_label}-${i}`} className="border-t border-nd-border">
                  <td className="py-1.5 pr-4 whitespace-nowrap">{r.date}</td>
                  <td className="py-1.5 pr-4 whitespace-nowrap">{r.time_label}</td>
                  <td className="py-1.5 pr-4">{r.market}</td>
                  <td className="py-1.5 pr-4">{r.kwh}</td>
                  <td className="py-1.5 pr-4">{r.cost_rs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
