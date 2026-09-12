import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { RangeList } from "./RangeList";
import type { ConsumptionRangeInput } from "../api/types";

describe("RangeList", () => {
  it("renders nothing meaningful when there are no ranges", () => {
    render(<RangeList ranges={[]} onRemove={vi.fn()} />);
    expect(screen.getByText(/no ranges added yet/i)).toBeInTheDocument();
  });

  it("renders one row per range with its time and power", () => {
    const ranges: ConsumptionRangeInput[] = [
      { start_time: "18:00", end_time: "19:00", predicted_kw: 4.5 },
      { start_time: "06:00", end_time: "07:30", predicted_kw: 2 },
    ];
    render(<RangeList ranges={ranges} onRemove={vi.fn()} />);
    expect(screen.getByText(/18:00/)).toBeInTheDocument();
    expect(screen.getByText(/19:00/)).toBeInTheDocument();
    expect(screen.getByText(/4\.5/)).toBeInTheDocument();
    expect(screen.getByText(/06:00/)).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(2);
  });

  it("calls onRemove with the range's index when its remove button is clicked", () => {
    const onRemove = vi.fn();
    const ranges: ConsumptionRangeInput[] = [
      { start_time: "18:00", end_time: "19:00", predicted_kw: 4.5 },
      { start_time: "06:00", end_time: "07:30", predicted_kw: 2 },
    ];
    render(<RangeList ranges={ranges} onRemove={onRemove} />);
    fireEvent.click(screen.getAllByRole("button", { name: /remove/i })[1]);
    expect(onRemove).toHaveBeenCalledWith(1);
  });
});
