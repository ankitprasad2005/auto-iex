import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";

vi.mock("./api/client", () => ({
  createScenario: vi.fn().mockResolvedValue({ id: 1, name: "scenario" }),
  getComparison: vi.fn().mockResolvedValue({
    blocks: [], dam_total_rs: "0", rtm_total_rs: "0", hybrid_total_rs: "0",
    dam_pending_blocks: 96, rtm_pending_blocks: 96,
  }),
  getChain: vi.fn().mockResolvedValue([]),
}));

describe("App", () => {
  it("renders the Dashboard tab by default", () => {
    render(<App />);
    expect(screen.getByRole("tab", { name: /dashboard/i })).toHaveAttribute("aria-selected", "true");
  });

  it("switches to the Chain tab on click", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: /chain/i }));
    expect(screen.getByRole("tab", { name: /chain/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText(/no blocks yet/i)).toBeInTheDocument();
  });
});
