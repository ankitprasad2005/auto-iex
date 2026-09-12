import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ComparisonView } from "./ComparisonView";
import type { ComparisonResult } from "../api/types";

const emptyResult: ComparisonResult = {
  blocks: [],
  dam_total_rs: "0",
  rtm_total_rs: "0",
  hybrid_total_rs: "0",
  dam_pending_blocks: 96,
  rtm_pending_blocks: 96,
};

describe("ComparisonView", () => {
  it("renders a placeholder when there is no result yet", () => {
    render(<ComparisonView result={null} />);
    expect(screen.getByText(/add a consumption range/i)).toBeInTheDocument();
  });

  it("renders totals and pending block counts", () => {
    render(<ComparisonView result={emptyResult} />);
    expect(screen.getByText(/dam total/i)).toBeInTheDocument();
    expect(screen.getAllByText(/96.*pending/i).length).toBeGreaterThan(0);
  });

  it("renders one row per block", () => {
    const result: ComparisonResult = {
      ...emptyResult,
      dam_pending_blocks: 0,
      rtm_pending_blocks: 0,
      blocks: [
        { block_index: 0, predicted_kwh: 1, dam_cost_rs: "4", rtm_cost_rs: "3", dam_pending: false, rtm_pending: false },
      ],
    };
    render(<ComparisonView result={result} />);
    expect(screen.getAllByRole("row").length).toBeGreaterThan(1); // header + 1 data row
  });

  it("wraps the table in a horizontally scrollable container so narrow viewports scroll instead of squishing columns", () => {
    const result: ComparisonResult = {
      ...emptyResult,
      blocks: [
        { block_index: 0, predicted_kwh: 1, dam_cost_rs: "4", rtm_cost_rs: "3", dam_pending: false, rtm_pending: false },
      ],
    };
    render(<ComparisonView result={result} />);
    const table = screen.getByRole("table");
    expect(table.parentElement).toHaveClass("overflow-x-auto");
  });
});
