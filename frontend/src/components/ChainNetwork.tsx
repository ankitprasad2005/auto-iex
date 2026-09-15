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
    <div className="overflow-x-auto">
      <table className="w-full min-w-[720px] font-mono text-xs text-nd-text-primary border-collapse">
        <thead>
          <tr className="text-left text-nd-text-secondary uppercase tracking-label text-[11px]">
            <th className="py-2 pr-2 w-6" aria-hidden="true"></th>
            <th className="py-2 pr-4">Block</th>
            <th className="py-2 pr-4">Hash</th>
            <th className="py-2 pr-4">Prev hash</th>
            <th className="py-2 pr-4">Timestamp</th>
            <th className="py-2 pr-4">Payload</th>
          </tr>
        </thead>
        <tbody>
          {blocks.map((block, i) => (
            <tr key={block.index} data-testid="chain-node" className="border-t border-nd-border">
              <td className="py-2 pr-2 text-center text-nd-border-visible">
                {i < blocks.length - 1 && (
                  <span data-testid="chain-arrow" aria-hidden="true">
                    ↓
                  </span>
                )}
              </td>
              <td className="py-2 pr-4 text-nd-text-secondary">#{block.index}</td>
              <td className="py-2 pr-4 text-nd-text-display">{block.hash.slice(0, 8)}…</td>
              <td className="py-2 pr-4 text-nd-text-disabled">prev: {block.prev_hash.slice(0, 8)}…</td>
              <td className="py-2 pr-4 text-nd-text-disabled whitespace-nowrap">
                {new Date(block.timestamp).toLocaleString()}
              </td>
              <td className="py-2 pr-4 text-nd-text-secondary break-all">{JSON.stringify(block.payload)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
