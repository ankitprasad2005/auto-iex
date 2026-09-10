import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConsumptionForm } from "./ConsumptionForm";

describe("ConsumptionForm", () => {
  it("calls onAddRange with parsed values on valid submit", () => {
    const onAddRange = vi.fn();
    render(<ConsumptionForm onAddRange={onAddRange} />);

    fireEvent.change(screen.getByLabelText(/start time/i), { target: { value: "18:00" } });
    fireEvent.change(screen.getByLabelText(/end time/i), { target: { value: "19:00" } });
    fireEvent.change(screen.getByLabelText(/predicted kw/i), { target: { value: "4.5" } });
    fireEvent.click(screen.getByRole("button", { name: /add range/i }));

    expect(onAddRange).toHaveBeenCalledWith({ start_time: "18:00", end_time: "19:00", predicted_kw: 4.5 });
  });

  it("shows a validation error and does not submit when end <= start", () => {
    const onAddRange = vi.fn();
    render(<ConsumptionForm onAddRange={onAddRange} />);

    fireEvent.change(screen.getByLabelText(/start time/i), { target: { value: "19:00" } });
    fireEvent.change(screen.getByLabelText(/end time/i), { target: { value: "18:00" } });
    fireEvent.change(screen.getByLabelText(/predicted kw/i), { target: { value: "4" } });
    fireEvent.click(screen.getByRole("button", { name: /add range/i }));

    expect(onAddRange).not.toHaveBeenCalled();
    expect(screen.getByText(/end time must be after start time/i)).toBeInTheDocument();
  });

  it("shows a validation error when predicted_kw is zero or negative", () => {
    const onAddRange = vi.fn();
    render(<ConsumptionForm onAddRange={onAddRange} />);

    fireEvent.change(screen.getByLabelText(/start time/i), { target: { value: "18:00" } });
    fireEvent.change(screen.getByLabelText(/end time/i), { target: { value: "19:00" } });
    fireEvent.change(screen.getByLabelText(/predicted kw/i), { target: { value: "0" } });
    fireEvent.click(screen.getByRole("button", { name: /add range/i }));

    expect(onAddRange).not.toHaveBeenCalled();
    expect(screen.getByText(/predicted kw must be positive/i)).toBeInTheDocument();
  });
});
