import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChainNetwork } from "./ChainNetwork";
import { formatIST } from "../lib/formatIST";
import type { ChainBlock } from "../api/types";

describe("ChainNetwork", () => {
  it("renders a placeholder when the chain is empty", () => {
    render(<ChainNetwork blocks={[]} />);
    expect(screen.getByText(/no blocks yet/i)).toBeInTheDocument();
  });

  it("renders one box per block with a shortened hash", () => {
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
    expect(screen.getByText(/prev.*aaaaaaaa/i)).toBeInTheDocument();
  });

  it("displays block timestamps in IST", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-15T05:19:47.000Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    expect(screen.getByText(formatIST("2026-09-15T05:19:47.000Z"))).toBeInTheDocument();
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

  it("wraps the boxes in a horizontally scrollable row instead of wrapping to a new line", () => {
    // Regression guard: an earlier flex-wrap layout let boxes overlap once
    // they wrapped to a second row. A strict single-row flex container with
    // overflow-x-auto can't wrap at all, so it can't reproduce that bug.
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
    ];
    render(<ChainNetwork blocks={blocks} />);
    const scrollContainer = screen.getByTestId("chain-scroll-container");
    expect(scrollContainer).toHaveClass("overflow-x-auto");
    const row = screen.getByTestId("chain-row");
    expect(row.className).not.toMatch(/flex-wrap/);
  });
});
