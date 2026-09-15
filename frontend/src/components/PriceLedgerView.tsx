import { ChainNetwork } from "./ChainNetwork";
import type { ChainBlock } from "../api/types";

interface Props {
  blocks: ChainBlock[];
  onCheckNow: () => void;
  checking: boolean;
}

export function PriceLedgerView({ blocks, onCheckNow, checking }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-4">
        <p className="font-mono text-xs text-nd-text-secondary max-w-md">
          Every 15-minute block is recorded here the moment its delivery time
          arrives, capturing whichever of DAM/RTM is published then —
          independent of any consumption scenario.
        </p>
        <button
          type="button"
          onClick={onCheckNow}
          disabled={checking}
          className="font-mono text-[11px] uppercase tracking-label px-3 py-1.5 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0"
        >
          {checking ? "Checking…" : "Check now"}
        </button>
      </div>
      <ChainNetwork blocks={blocks} />
    </div>
  );
}
