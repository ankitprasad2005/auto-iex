import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, render, screen, fireEvent } from "@testing-library/react";
import App from "./App";
import * as client from "./api/client";

vi.mock("./api/client", () => ({
  createScenario: vi.fn().mockResolvedValue({ id: 1, name: "scenario" }),
  getComparison: vi.fn().mockResolvedValue({
    blocks: [], dam_total_rs: "0", rtm_total_rs: "0", hybrid_total_rs: "0",
    dam_pending_blocks: 96, rtm_pending_blocks: 96,
  }),
  getChain: vi.fn().mockResolvedValue([]),
  triggerScrape: vi.fn().mockResolvedValue({ written: 96, skipped_duplicate: false, chain_block_index: 1 }),
  getPrices: vi.fn().mockResolvedValue([]),
  getLedger: vi.fn().mockResolvedValue([]),
  checkLedgerNow: vi.fn().mockResolvedValue({ settled_count: 0 }),
  getPriceLedger: vi.fn().mockResolvedValue([]),
  checkPriceLedgerNow: vi.fn().mockResolvedValue({ recorded_count: 0 }),
  getRtmInterval: vi.fn().mockResolvedValue({ seconds: 30 }),
  updateRtmInterval: vi.fn().mockResolvedValue({ seconds: 30 }),
}));

beforeEach(() => {
  vi.mocked(client.getChain).mockResolvedValue([]);
  vi.mocked(client.createScenario).mockResolvedValue({ id: 1, name: "scenario" });
  vi.mocked(client.getComparison).mockResolvedValue({
    blocks: [], dam_total_rs: "0", rtm_total_rs: "0", hybrid_total_rs: "0",
    dam_pending_blocks: 96, rtm_pending_blocks: 96,
  });
  vi.mocked(client.triggerScrape).mockResolvedValue({ written: 96, skipped_duplicate: false, chain_block_index: 1 });
  vi.mocked(client.getPrices).mockResolvedValue([]);
  vi.mocked(client.getLedger).mockResolvedValue([]);
  vi.mocked(client.checkLedgerNow).mockResolvedValue({ settled_count: 0 });
  vi.mocked(client.getPriceLedger).mockResolvedValue([]);
  vi.mocked(client.checkPriceLedgerNow).mockResolvedValue({ recorded_count: 0 });
  vi.mocked(client.getRtmInterval).mockResolvedValue({ seconds: 30 });
  vi.mocked(client.updateRtmInterval).mockResolvedValue({ seconds: 30 });
});

describe("App", () => {
  it("renders the Dashboard tab by default", async () => {
    render(<App />);
    expect(screen.getByRole("tab", { name: /dashboard/i })).toHaveAttribute("aria-selected", "true");
    // App fetches the chain on mount (for scrape-status display); flush that
    // pending state update instead of leaving it to warn outside act().
    await act(async () => {});
  });

  it("switches to the Chain tab on click", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: /chain/i }));
    expect(screen.getByRole("tab", { name: /chain/i })).toHaveAttribute("aria-selected", "true");
    // getChain() resolves asynchronously, so wait for the state update it
    // triggers instead of asserting before React has re-rendered.
    expect(await screen.findByText(/no blocks yet/i)).toBeInTheDocument();
  });

  it("adding a range shows it in the range list", async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/start time/i), { target: { value: "18:00" } });
    fireEvent.change(screen.getByLabelText(/end time/i), { target: { value: "19:00" } });
    fireEvent.change(screen.getByLabelText(/predicted kw/i), { target: { value: "4.5" } });
    fireEvent.click(screen.getByRole("button", { name: /add range/i }));

    expect(await screen.findByText(/18:00.*19:00/)).toBeInTheDocument();
  });

  it("removing a range clears it from the range list", async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/start time/i), { target: { value: "18:00" } });
    fireEvent.change(screen.getByLabelText(/end time/i), { target: { value: "19:00" } });
    fireEvent.change(screen.getByLabelText(/predicted kw/i), { target: { value: "4.5" } });
    fireEvent.click(screen.getByRole("button", { name: /add range/i }));
    await screen.findByText(/18:00.*19:00/);

    fireEvent.click(screen.getByRole("button", { name: /remove/i }));

    expect(await screen.findByText(/no ranges added yet/i)).toBeInTheDocument();
  });

  it("renders a date picker defaulting to a non-empty date", async () => {
    render(<App />);
    const input = screen.getByLabelText(/delivery date/i) as HTMLInputElement;
    expect(input.value).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    await act(async () => {});
  });

  it("shows scrape status controls and triggers a scrape on click", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /scrape dam now/i }));
    expect(await screen.findByText(/scraping/i)).toBeInTheDocument();
  });

  it("switches to the Prices tab and loads DAM/RTM price data for both markets", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: /prices/i }));
    expect(screen.getByRole("tab", { name: /prices/i })).toHaveAttribute("aria-selected", "true");
    await screen.findByRole("table");
    expect(client.getPrices).toHaveBeenCalledWith(expect.any(String), "DAM");
    expect(client.getPrices).toHaveBeenCalledWith(expect.any(String), "RTM");
  });

  it("switches to the Ledger tab, loads settlements, and can trigger a manual check", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Ledger" }));
    expect(screen.getByRole("tab", { name: "Ledger" })).toHaveAttribute("aria-selected", "true");
    await screen.findByText(/no settlements yet/i);
    expect(client.getLedger).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /check now/i }));
    await screen.findByRole("button", { name: /check now/i }); // waits for "Checking…" to revert
    expect(client.checkLedgerNow).toHaveBeenCalled();
  });

  it("switches to the Price Ledger tab, loads blocks, and can trigger a manual check", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Price Ledger" }));
    expect(screen.getByRole("tab", { name: "Price Ledger" })).toHaveAttribute("aria-selected", "true");
    await screen.findByText(/no blocks yet/i);
    expect(client.getPriceLedger).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /check now/i }));
    await screen.findByRole("button", { name: /check now/i });
    expect(client.checkPriceLedgerNow).toHaveBeenCalled();
  });

  it("loads the RTM interval on mount and can update it from the Dashboard", async () => {
    render(<App />);
    const input = await screen.findByLabelText(/rtm auto-scrape interval/i);
    expect((input as HTMLInputElement).value).toBe("30");

    fireEvent.change(input, { target: { value: "60" } });
    fireEvent.click(screen.getByRole("button", { name: /^update$/i }));
    await act(async () => {});
    expect(client.updateRtmInterval).toHaveBeenCalledWith(60);
  });
});
