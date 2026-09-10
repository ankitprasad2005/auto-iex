import type { ChainBlock } from "../api/types";

interface Props {
  blocks: ChainBlock[];
}

export function ChainNetwork({ blocks }: Props) {
  if (blocks.length === 0) {
    return (
      <p className="font-mono text-sm text-nd-text-secondary">
        No blocks yet — the chain grows as scrapes complete.
      </p>
    );
  }

  return (
    <div className="dot-grid flex flex-wrap items-center gap-0 p-8 bg-nd-black">
      {blocks.map((block, i) => (
        <div key={block.index} className="flex items-center">
          <div
            data-testid="chain-node"
            className="flex flex-col gap-2 bg-nd-surface border border-nd-border-visible px-4 py-3 min-w-[180px]"
          >
            <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
              Block #{block.index}
            </span>
            <span className="font-mono text-sm text-nd-text-display">{block.hash.slice(0, 8)}…</span>
            <span className="font-mono text-[11px] text-nd-text-disabled">
              {new Date(block.timestamp).toLocaleString()}
            </span>
            <span className="font-mono text-[11px] text-nd-text-secondary break-all">
              {JSON.stringify(block.payload)}
            </span>
          </div>
          {i < blocks.length - 1 && (
            <span className="font-mono text-nd-border-visible px-2" aria-hidden="true">
              →
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
