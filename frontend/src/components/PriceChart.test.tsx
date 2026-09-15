import { describe, expect, it, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { PriceChart } from "./PriceChart";
import { mergePriceSeries } from "../lib/priceSeries";
import type { PricePoint } from "../api/types";

afterEach(cleanup);

describe("PriceChart", () => {
  it("shows a placeholder when there is no price data for either market", () => {
    const data = mergePriceSeries([], []);
    render(<PriceChart data={data} />);
    expect(screen.getByText(/no price data/i)).toBeInTheDocument();
  });

  it("renders a legend for both series when data is present", () => {
    const dam: PricePoint[] = [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "3245.5000" }];
    const data = mergePriceSeries(dam, []);
    render(<PriceChart data={data} />);
    expect(screen.getByText("DAM")).toBeInTheDocument();
    expect(screen.getByText("RTM")).toBeInTheDocument();
  });

  it("shows a tooltip with both prices at the hovered block", () => {
    const dam: PricePoint[] = [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "3245.5000" }];
    const rtm: PricePoint[] = [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "2900.0000" }];
    const data = mergePriceSeries(dam, rtm);
    render(<PriceChart data={data} />);

    const overlay = screen.getByTestId("price-chart-overlay");
    // jsdom performs no layout, so getBoundingClientRect() returns zeros
    // unless stubbed — supply a known width so the pointer-to-block math
    // (mirroring how a real, laid-out browser would resolve it) is testable.
    overlay.getBoundingClientRect = () => ({
      x: 0, y: 0, width: 960, height: 300, top: 0, left: 0, right: 960, bottom: 300, toJSON: () => {},
    });

    fireEvent.mouseMove(overlay, { clientX: 0, clientY: 10 });

    const tooltip = screen.getByTestId("price-chart-tooltip");
    expect(tooltip).toHaveTextContent("00:00");
    expect(tooltip).toHaveTextContent("3245.50");
    expect(tooltip).toHaveTextContent("2900.00");
  });
});
