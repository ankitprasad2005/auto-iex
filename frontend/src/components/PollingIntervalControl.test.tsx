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

  it("uses a custom label when given", () => {
    render(
      <PollingIntervalControl
        seconds={900}
        onUpdate={vi.fn()}
        updating={false}
        label="Testnet anchor interval (seconds)"
      />,
    );
    const input = screen.getByLabelText(/testnet anchor interval/i) as HTMLInputElement;
    expect(input.value).toBe("900");
    expect(screen.queryByLabelText(/rtm auto-scrape interval/i)).not.toBeInTheDocument();
  });

  it("enforces a custom minimum", () => {
    const onUpdate = vi.fn();
    render(<PollingIntervalControl seconds={900} onUpdate={onUpdate} updating={false} min={300} />);
    const input = screen.getByLabelText(/interval/i) as HTMLInputElement;
    expect(input.min).toBe("300");
    fireEvent.change(input, { target: { value: "299" } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(onUpdate).not.toHaveBeenCalled();
    expect(screen.getByRole("alert")).toHaveTextContent(/at least 300 seconds/i);
  });

  it("accepts exactly the custom minimum and clears a previous error", () => {
    const onUpdate = vi.fn();
    render(<PollingIntervalControl seconds={900} onUpdate={onUpdate} updating={false} min={300} />);
    const input = screen.getByLabelText(/interval/i);
    fireEvent.change(input, { target: { value: "10" } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(screen.getByRole("alert")).toBeInTheDocument();
    fireEvent.change(input, { target: { value: "300" } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(onUpdate).toHaveBeenCalledWith(300);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("accepts exactly the default 10 second minimum", () => {
    const onUpdate = vi.fn();
    render(<PollingIntervalControl seconds={30} onUpdate={onUpdate} updating={false} />);
    fireEvent.change(screen.getByLabelText(/rtm auto-scrape interval/i), { target: { value: "10" } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(onUpdate).toHaveBeenCalledWith(10);
  });

  it.each(["", "abc", "Infinity"])("rejects a non-numeric or infinite value %j", (value) => {
    const onUpdate = vi.fn();
    render(<PollingIntervalControl seconds={30} onUpdate={onUpdate} updating={false} />);
    fireEvent.change(screen.getByLabelText(/rtm auto-scrape interval/i), { target: { value } });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));
    expect(onUpdate).not.toHaveBeenCalled();
  });

  it("gives each instance a distinct input id so labels stay unambiguous", () => {
    render(
      <>
        <PollingIntervalControl seconds={30} onUpdate={vi.fn()} updating={false} />
        <PollingIntervalControl seconds={900} onUpdate={vi.fn()} updating={false} label="Testnet anchor interval" min={300} />
      </>,
    );
    const rtm = screen.getByLabelText(/rtm auto-scrape interval/i) as HTMLInputElement;
    const anchor = screen.getByLabelText(/testnet anchor interval/i) as HTMLInputElement;
    expect(rtm.id).not.toBe(anchor.id);
    expect(rtm.value).toBe("30");
    expect(anchor.value).toBe("900");
  });

  it("updates the input when the seconds prop changes (e.g. after loading from the server)", () => {
    const { rerender } = render(<PollingIntervalControl seconds={30} onUpdate={vi.fn()} updating={false} />);
    rerender(<PollingIntervalControl seconds={45} onUpdate={vi.fn()} updating={false} />);
    expect((screen.getByLabelText(/rtm auto-scrape interval/i) as HTMLInputElement).value).toBe("45");
  });
});
