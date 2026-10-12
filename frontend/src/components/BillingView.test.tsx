import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BillingView } from "./BillingView";
import type { BillingHistory } from "../api/types";

const emptyHistory: BillingHistory = { records: [], total_kwh: "0", total_cost_rs: "0" };

describe("BillingView", () => {
  it("shows a placeholder and no totals when there is no billing history yet", () => {
    render(<BillingView history={emptyHistory} onLoadDemo={vi.fn()} loading={false} />);
    expect(screen.getByText(/no billing history yet/i)).toBeInTheDocument();
  });

  it("renders the monthly totals and a row per record when history exists", () => {
    const history: BillingHistory = {
      records: [
        { date: "2026-09-10", time_label: "18:00-19:00", market: "DAM", kwh: "4.500", cost_rs: "18.00" },
        { date: "2026-09-11", time_label: "06:00-07:00", market: "RTM", kwh: "2.100", cost_rs: "7.35" },
      ],
      total_kwh: "6.600",
      total_cost_rs: "25.35",
    };
    render(<BillingView history={history} onLoadDemo={vi.fn()} loading={false} />);

    expect(screen.getByText(/25\.35/)).toBeInTheDocument();
    expect(screen.getByText(/6\.600/)).toBeInTheDocument();
    expect(screen.getAllByRole("row").length).toBe(3); // header + 2 records
    expect(screen.getByText("18:00-19:00")).toBeInTheDocument();
    expect(screen.getByText("DAM")).toBeInTheDocument();
  });

  it("calls onLoadDemo when the demo button is clicked", () => {
    const onLoadDemo = vi.fn();
    render(<BillingView history={emptyHistory} onLoadDemo={onLoadDemo} loading={false} />);
    fireEvent.click(screen.getByRole("button", { name: /load demo data/i }));
    expect(onLoadDemo).toHaveBeenCalled();
  });

  it("disables the demo button while loading", () => {
    render(<BillingView history={emptyHistory} onLoadDemo={vi.fn()} loading={true} />);
    expect(screen.getByRole("button", { name: /loading/i })).toBeDisabled();
  });
});
