import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChainNetwork } from "./ChainNetwork";
import type { ChainBlock } from "../api/types";

describe("ChainNetwork", () => {
  it("renders a placeholder when the chain is empty", () => {
    render(<ChainNetwork blocks={[]} />);
    expect(screen.getByText(/no blocks yet/i)).toBeInTheDocument();
  });

  it("renders one node per block with a shortened hash", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
      { index: 1, timestamp: "2026-09-10T00:15:00Z", payload: { market: "DAM" }, prev_hash: "a".repeat(64), hash: "b".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    expect(screen.getAllByTestId("chain-node")).toHaveLength(2);
    // block 0's own hash and block 1's prev_hash are both "a"*64, so both render this prefix
    expect(screen.getAllByText(/aaaaaaaa/).length).toBeGreaterThan(0);
  });

  it("shows each block's prev_hash so the chain linkage is visible without relying on layout order", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
      { index: 1, timestamp: "2026-09-10T00:15:00Z", payload: { market: "DAM" }, prev_hash: "a".repeat(64), hash: "c".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    // block 1's prev_hash ("a"*64) should appear as its own labeled text, distinct from its own hash ("c"*64)
    expect(screen.getByText(/prev.*aaaaaaaa/i)).toBeInTheDocument();
  });
});
