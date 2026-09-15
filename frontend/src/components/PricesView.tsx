import type { MergedPricePoint } from "../lib/priceSeries";
import { PriceChart } from "./PriceChart";

interface Props {
  date: string;
  onDateChange: (date: string) => void;
  data: MergedPricePoint[];
}

function formatPrice(value: number | null): string {
  return value === null ? "PENDING" : value.toFixed(2);
}

export function PricesView({ date, onDateChange, data }: Props) {
  return (
    <div className="flex flex-col gap-8">
      <label htmlFor="prices-date" className="flex flex-col gap-1 max-w-xs">
        <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">Date</span>
        <input
          id="prices-date"
          type="date"
          value={date}
          onChange={(e) => onDateChange(e.target.value)}
          className="bg-nd-surface border border-nd-border-visible text-nd-text-primary font-mono text-sm px-3 py-2 focus:outline-none focus:border-nd-accent"
        />
      </label>

      <PriceChart data={data} />

      <div className="overflow-x-auto">
        <table className="w-full min-w-[420px] font-mono text-xs text-nd-text-primary border-collapse">
          <thead>
            <tr className="text-left text-nd-text-secondary uppercase tracking-label text-[11px]">
              <th className="py-2 pr-4">Block</th>
              <th className="py-2 pr-4">Time</th>
              <th className="py-2 pr-4">DAM (₹/MWh)</th>
              <th className="py-2 pr-4">RTM (₹/MWh)</th>
            </tr>
          </thead>
          <tbody>
            {data.map((p) => (
              <tr key={p.blockIndex} className="border-t border-nd-border">
                <td className="py-1.5 pr-4">{p.blockIndex}</td>
                <td className="py-1.5 pr-4">{p.time}</td>
                <td className="py-1.5 pr-4">{formatPrice(p.damPrice)}</td>
                <td className="py-1.5 pr-4">{formatPrice(p.rtmPrice)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
