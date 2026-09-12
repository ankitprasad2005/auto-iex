import type { ComparisonResult } from "../api/types";

interface Props {
  result: ComparisonResult | null;
}

function TotalStat({ label, value, pending }: { label: string; value: string; pending: number }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">{label}</span>
      <span className="font-display text-4xl text-nd-text-display">₹{value}</span>
      {pending > 0 && (
        <span className="font-mono text-[11px] text-nd-text-disabled">{pending} blocks pending</span>
      )}
    </div>
  );
}

export function ComparisonView({ result }: Props) {
  if (!result) {
    return (
      <p className="font-mono text-sm text-nd-text-secondary">
        Add a consumption range to see the DAM vs RTM comparison.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-wrap gap-6 sm:gap-12">
        <TotalStat label="DAM total" value={result.dam_total_rs} pending={result.dam_pending_blocks} />
        <TotalStat label="RTM total" value={result.rtm_total_rs} pending={result.rtm_pending_blocks} />
        <TotalStat label="Hybrid total" value={result.hybrid_total_rs} pending={0} />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[520px] font-mono text-xs text-nd-text-primary border-collapse">
          <thead>
            <tr className="text-left text-nd-text-secondary uppercase tracking-label text-[11px]">
              <th className="py-2 pr-4">Block</th>
              <th className="py-2 pr-4">Predicted kWh</th>
              <th className="py-2 pr-4">DAM cost (₹)</th>
              <th className="py-2 pr-4">RTM cost (₹)</th>
            </tr>
          </thead>
          <tbody>
            {result.blocks.map((b) => (
              <tr key={b.block_index} className="border-t border-nd-border">
                <td className="py-1.5 pr-4">{b.block_index}</td>
                <td className="py-1.5 pr-4">{b.predicted_kwh.toFixed(3)}</td>
                <td className="py-1.5 pr-4">{b.dam_pending ? "PENDING" : b.dam_cost_rs}</td>
                <td className="py-1.5 pr-4">{b.rtm_pending ? "PENDING" : b.rtm_cost_rs}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
