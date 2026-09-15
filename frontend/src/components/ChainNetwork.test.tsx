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

  it("renders as a table of block records (Airtable-style grid, not free-floating cards)", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
      { index: 1, timestamp: "2026-09-10T00:15:00Z", payload: { market: "DAM" }, prev_hash: "a".repeat(64), hash: "b".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    expect(screen.getByRole("table")).toBeInTheDocument();
    // one header row + one row per block
    expect(screen.getAllByRole("row")).toHaveLength(3);
  });

  it("renders a connecting arrow between each consecutive pair of blocks, none after the last", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
      { index: 1, timestamp: "2026-09-10T00:15:00Z", payload: { market: "DAM" }, prev_hash: "a".repeat(64), hash: "b".repeat(64) },
      { index: 2, timestamp: "2026-09-10T00:30:00Z", payload: { market: "RTM" }, prev_hash: "b".repeat(64), hash: "c".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    // N blocks -> N-1 connectors, since the last block has nothing after it
    expect(screen.getAllByTestId("chain-arrow")).toHaveLength(2);
  });

  it("renders no connecting arrow for a single-block chain", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    expect(screen.queryByTestId("chain-arrow")).not.toBeInTheDocument();
  });
});
