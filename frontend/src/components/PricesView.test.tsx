import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PricesView } from "./PricesView";
import { mergePriceSeries } from "../lib/priceSeries";

describe("PricesView", () => {
  it("renders a date input reflecting the given date", () => {
    render(<PricesView date="2026-09-13" onDateChange={vi.fn()} data={mergePriceSeries([], [])} />);
    const input = screen.getByLabelText(/date/i) as HTMLInputElement;
    expect(input.value).toBe("2026-09-13");
  });

  it("calls onDateChange when the date input changes", () => {
    const onDateChange = vi.fn();
    render(<PricesView date="2026-09-13" onDateChange={onDateChange} data={mergePriceSeries([], [])} />);
    fireEvent.change(screen.getByLabelText(/date/i), { target: { value: "2026-09-14" } });
    expect(onDateChange).toHaveBeenCalledWith("2026-09-14");
  });

  it("renders a table row per block with DAM and RTM prices", () => {
    const dam = [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "3245.5000" }];
    const rtm = [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "2900.0000" }];
    render(<PricesView date="2026-09-13" onDateChange={vi.fn()} data={mergePriceSeries(dam, rtm)} />);
    expect(screen.getAllByRole("row").length).toBe(97); // header + 96 blocks
    expect(screen.getByText("3245.50")).toBeInTheDocument();
    expect(screen.getByText("2900.00")).toBeInTheDocument();
  });

  it("shows PENDING for blocks missing a price", () => {
    render(<PricesView date="2026-09-13" onDateChange={vi.fn()} data={mergePriceSeries([], [])} />);
    expect(screen.getAllByText("PENDING").length).toBeGreaterThan(0);
  });
});
