import { formatIST } from "../lib/formatIST";
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
    // A strict single-row flex layout (no flex-wrap) scrolling horizontally
    // instead of wrapping to a new line — a linked list is inherently 1D,
    // and this also structurally rules out the overlap an earlier
    // flex-wrap layout produced once boxes wrapped to a second row.
    <div data-testid="chain-scroll-container" className="dot-grid overflow-x-auto p-4 sm:p-8 bg-nd-black">
      <div data-testid="chain-row" className="flex items-stretch gap-0 w-max">
        {blocks.map((block, i) => (
          <div key={block.index} className="flex items-center flex-shrink-0">
            <div
              data-testid="chain-node"
              className="flex flex-col gap-2 bg-nd-surface border border-nd-border-visible px-4 py-3 w-[220px] flex-shrink-0"
            >
              <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
                Block #{block.index}
              </span>
              <span className="font-mono text-sm text-nd-text-display truncate">{block.hash.slice(0, 8)}…</span>
              <span className="font-mono text-[11px] text-nd-text-disabled truncate">
                prev: {block.prev_hash.slice(0, 8)}…
              </span>
              <span className="font-mono text-[11px] text-nd-text-disabled">{formatIST(block.timestamp)}</span>
              <span className="font-mono text-[11px] text-nd-text-secondary break-all">
                {JSON.stringify(block.payload)}
              </span>
            </div>
            {i < blocks.length - 1 && (
              <span
                data-testid="chain-arrow"
                aria-hidden="true"
                className="font-mono text-lg text-nd-border-visible px-2 flex-shrink-0"
              >
                →
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
