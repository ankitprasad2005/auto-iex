import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { PollingIntervalControl } from "./PollingIntervalControl";

describe("PollingIntervalControl", () => {
  it("shows the current interval", () => {
    render(<PollingIntervalControl seconds={30} onUpdate={vi.fn()} updating={false} />);
    const input = screen.getByLabelText(/rtm auto-scrape interval/i) as HTMLInputElement;
    expect(input.value).toBe("30");
  });

  it("calls onUpdate with the new value when saved", () => {
    const onUpdate = vi.fn();
    render(<PollingIntervalControl seconds={30} onUpdate={onUpdate} updating={false} />);
    fireEvent.change(screen.getByLabelText(/rtm auto-scrape interval/i), { target: { value: "120" } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(onUpdate).toHaveBeenCalledWith(120);
  });

  it("rejects a value below the 10 second minimum without calling onUpdate", () => {
    const onUpdate = vi.fn();
    render(<PollingIntervalControl seconds={30} onUpdate={onUpdate} updating={false} />);
    fireEvent.change(screen.getByLabelText(/rtm auto-scrape interval/i), { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(onUpdate).not.toHaveBeenCalled();
    expect(screen.getByText(/at least 10 seconds/i)).toBeInTheDocument();
  });

  it("disables the update button while updating", () => {
    render(<PollingIntervalControl seconds={30} onUpdate={vi.fn()} updating={true} />);
    expect(screen.getByRole("button", { name: /updating/i })).toBeDisabled();
  });
});
