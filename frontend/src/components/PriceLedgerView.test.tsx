import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PriceLedgerView } from "./PriceLedgerView";
import type { ChainBlock } from "../api/types";

describe("PriceLedgerView", () => {
  it("shows the chain's empty-state placeholder when there are no blocks", () => {
    render(<PriceLedgerView blocks={[]} onCheckNow={vi.fn()} checking={false} />);
    expect(screen.getByText(/no blocks yet/i)).toBeInTheDocument();
  });

  it("renders the chain's blocks as boxes", () => {
    const blocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-15T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
      { index: 1, timestamp: "2026-09-15T06:00:00Z", payload: { block_index: 24, dam_price: 4000 }, prev_hash: "a".repeat(64), hash: "b".repeat(64) },
    ];
    render(<PriceLedgerView blocks={blocks} onCheckNow={vi.fn()} checking={false} />);
    expect(screen.getAllByTestId("chain-node")).toHaveLength(2);
  });

  it("calls onCheckNow when the check button is clicked", () => {
    const onCheckNow = vi.fn();
    render(<PriceLedgerView blocks={[]} onCheckNow={onCheckNow} checking={false} />);
    fireEvent.click(screen.getByRole("button", { name: /check now/i }));
    expect(onCheckNow).toHaveBeenCalled();
  });

  it("disables the check button while checking", () => {
    render(<PriceLedgerView blocks={[]} onCheckNow={vi.fn()} checking={true} />);
    expect(screen.getByRole("button", { name: /checking/i })).toBeDisabled();
  });
});
