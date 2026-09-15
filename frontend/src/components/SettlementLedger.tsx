import type { SettlementBlock } from "../api/types";

interface Props {
  blocks: SettlementBlock[];
  onCheckNow: () => void;
  checking: boolean;
}

function minutesToHHMM(minutes: number): string {
  const h = String(Math.floor(minutes / 60)).padStart(2, "0");
  const m = String(minutes % 60).padStart(2, "0");
  return `${h}:${m}`;
}

export function SettlementLedger({ blocks, onCheckNow, checking }: Props) {
  const totalCost = blocks.reduce((sum, b) => sum + b.payload.cost_rs, 0);

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
            Total realized cost
          </span>
          <span className="font-display text-4xl text-nd-text-display">₹{totalCost.toFixed(2)}</span>
        </div>
        <button
          type="button"
          onClick={onCheckNow}
          disabled={checking}
          className="font-mono text-[11px] uppercase tracking-label px-3 py-1.5 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {checking ? "Checking…" : "Check now"}
        </button>
      </div>

      {blocks.length === 0 ? (
        <p className="font-mono text-sm text-nd-text-secondary">
          No settlements yet — ranges settle automatically once their scheduled time arrives.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] font-mono text-xs text-nd-text-primary border-collapse">
            <thead>
              <tr className="text-left text-nd-text-secondary uppercase tracking-label text-[11px]">
                <th className="py-2 pr-2 w-6" aria-hidden="true"></th>
                <th className="py-2 pr-4">Range</th>
                <th className="py-2 pr-4">Predicted kW</th>
                <th className="py-2 pr-4">Energy (kWh)</th>
                <th className="py-2 pr-4">Market</th>
                <th className="py-2 pr-4">Cost (₹)</th>
                <th className="py-2 pr-4">Status</th>
                <th className="py-2 pr-4">Settled at</th>
              </tr>
            </thead>
            <tbody>
              {blocks.map((block, i) => {
                const p = block.payload;
                return (
                  <tr key={block.index} data-testid="settlement-node" className="border-t border-nd-border">
                    <td className="py-2 pr-2 text-center text-nd-border-visible">
                      {i < blocks.length - 1 && (
                        <span data-testid="settlement-arrow" aria-hidden="true">
                          ↓
                        </span>
                      )}
                    </td>
                    <td className="py-2 pr-4 whitespace-nowrap">
                      {minutesToHHMM(p.start_minute)}–{minutesToHHMM(p.end_minute)}
                    </td>
                    <td className="py-2 pr-4">{p.predicted_kw}</td>
                    <td className="py-2 pr-4">{p.total_kwh.toFixed(3)}</td>
                    <td className="py-2 pr-4">{p.markets_used.join(", ")}</td>
                    <td className="py-2 pr-4">{p.cost_rs.toFixed(2)}</td>
                    <td className="py-2 pr-4">
                      {p.fully_priced ? (
                        <span className="text-nd-success">SETTLED</span>
                      ) : (
                        <span className="text-nd-warning">PARTIAL</span>
                      )}
                    </td>
                    <td className="py-2 pr-4 text-nd-text-disabled">
                      {new Date(p.settled_at).toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
