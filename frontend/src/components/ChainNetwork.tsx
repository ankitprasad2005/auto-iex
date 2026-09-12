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
    <div className="dot-grid grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 sm:p-8 bg-nd-black">
      {blocks.map((block) => (
        <div
          key={block.index}
          data-testid="chain-node"
          className="flex flex-col gap-2 bg-nd-surface border border-nd-border-visible px-4 py-3 min-w-0"
        >
          <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
            Block #{block.index}
          </span>
          <span className="font-mono text-sm text-nd-text-display truncate">{block.hash.slice(0, 8)}…</span>
          <span className="font-mono text-[11px] text-nd-text-disabled truncate">
            prev: {block.prev_hash.slice(0, 8)}…
          </span>
          <span className="font-mono text-[11px] text-nd-text-disabled">
            {new Date(block.timestamp).toLocaleString()}
          </span>
          <span className="font-mono text-[11px] text-nd-text-secondary break-all">
            {JSON.stringify(block.payload)}
          </span>
        </div>
      ))}
    </div>
  );
}
