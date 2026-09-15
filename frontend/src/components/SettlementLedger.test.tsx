import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { SettlementLedger } from "./SettlementLedger";
import type { SettlementBlock } from "../api/types";

function makeBlock(overrides: Partial<SettlementBlock["payload"]> = {}, index = 1): SettlementBlock {
  return {
    index,
    timestamp: "2026-09-15T06:00:00Z",
    prev_hash: "a".repeat(64),
    hash: "b".repeat(64),
    payload: {
      scenario_id: 1,
      range_id: 1,
      date: "2026-09-15",
      start_minute: 360,
      end_minute: 375,
      predicted_kw: 5,
      total_kwh: 1.25,
      priced_kwh: 1.25,
      cost_rs: 5,
      markets_used: ["DAM"],
      fully_priced: true,
      settled_at: "2026-09-15T06:00:00Z",
      ...overrides,
    },
  };
}

describe("SettlementLedger", () => {
  it("shows a placeholder when there are no settlements yet", () => {
    render(<SettlementLedger blocks={[]} onCheckNow={vi.fn()} checking={false} />);
    expect(screen.getByText(/no settlements yet/i)).toBeInTheDocument();
  });

  it("renders a table row per settlement with range, market, and cost", () => {
    render(<SettlementLedger blocks={[makeBlock()]} onCheckNow={vi.fn()} checking={false} />);
    expect(screen.getByText(/06:00.*06:15/)).toBeInTheDocument();
    expect(screen.getByText("DAM")).toBeInTheDocument();
    expect(screen.getByText("5.00")).toBeInTheDocument();
  });

  it("flags a partially priced settlement", () => {
    render(<SettlementLedger blocks={[makeBlock({ fully_priced: false })]} onCheckNow={vi.fn()} checking={false} />);
    expect(screen.getByText(/partial/i)).toBeInTheDocument();
  });

  it("calls onCheckNow when the check button is clicked", () => {
    const onCheckNow = vi.fn();
    render(<SettlementLedger blocks={[]} onCheckNow={onCheckNow} checking={false} />);
    fireEvent.click(screen.getByRole("button", { name: /check now/i }));
    expect(onCheckNow).toHaveBeenCalled();
  });

  it("disables the check button while checking", () => {
    render(<SettlementLedger blocks={[]} onCheckNow={vi.fn()} checking={true} />);
    expect(screen.getByRole("button", { name: /checking/i })).toBeDisabled();
  });

  it("shows the total realized cost across all settlements", () => {
    const blocks = [makeBlock({ cost_rs: 5 }, 1), makeBlock({ cost_rs: 3.5 }, 2)];
    render(<SettlementLedger blocks={blocks} onCheckNow={vi.fn()} checking={false} />);
    expect(screen.getByText(/8\.50/)).toBeInTheDocument();
  });
});
