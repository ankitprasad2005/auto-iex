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
    expect(screen.getByText(/aaaaaaaa/)).toBeInTheDocument();
  });
});
