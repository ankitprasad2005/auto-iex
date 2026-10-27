import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, render, screen, fireEvent, within } from "@testing-library/react";
import App from "./App";
import * as client from "./api/client";
import type { Anchor, AnchorStatus } from "./api/types";

const ANCHOR_STATUS: AnchorStatus = {
  enabled: true,
  network: "Polygon Amoy",
  chain_id: 80002,
  wallet_address: "0x1234567890abcdef1234567890abcdef12345678",
  explorer_tx_url: "https://amoy.polygonscan.com/tx/",
};

const TX = "0x" + "c".repeat(64);
const ANCHOR: Anchor = {
  id: 5,
  created_at: "2026-10-27T10:00:00Z",
  scrape_head_index: 3,
  scrape_head_hash: "a".repeat(64),
  settlement_head_index: -1,
  settlement_head_hash: "0".repeat(64),
  price_ledger_head_index: 7,
  price_ledger_head_hash: "b".repeat(64),
  tx_hash: TX,
  status: "confirmed",
  block_number: 4242,
  error: null,
  explorer_url: `https://amoy.polygonscan.com/tx/${TX}`,
};

// The Dashboard renders two PollingIntervalControls with identical "Update"
// buttons, so scope interactions to the control holding a given input.
function intervalControl(label: RegExp) {
  const input = screen.getByLabelText(label) as HTMLInputElement;
  const container = input.closest("div.flex-col") as HTMLElement;
  return { input, update: within(container).getByRole("button", { name: /^update$/i }) };
}

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
  getBillingHistory: vi.fn().mockResolvedValue({ records: [], total_kwh: "0", total_cost_rs: "0" }),
  loadDemoBillingData: vi.fn().mockResolvedValue({ created_count: 0 }),
  getAnchorStatus: vi.fn().mockResolvedValue(null),
  getAnchors: vi.fn().mockResolvedValue([]),
  anchorNow: vi.fn().mockResolvedValue({ anchored: false, reason: "unchanged", anchor: null }),
  verifyAnchor: vi.fn().mockResolvedValue({
    valid: true, on_chain_matches_record: true, ledger_matches_record: true, mismatches: [],
  }),
  getAnchorInterval: vi.fn().mockResolvedValue({ seconds: 900 }),
  updateAnchorInterval: vi.fn().mockResolvedValue({ seconds: 900 }),
}));

beforeEach(() => {
  // Reset call history (implementations are re-set below) so call-count
  // assertions don't see calls from earlier tests.
  vi.clearAllMocks();
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
  vi.mocked(client.getBillingHistory).mockResolvedValue({ records: [], total_kwh: "0", total_cost_rs: "0" });
  vi.mocked(client.loadDemoBillingData).mockResolvedValue({ created_count: 0 });
  vi.mocked(client.getAnchorStatus).mockResolvedValue(ANCHOR_STATUS);
  vi.mocked(client.getAnchors).mockResolvedValue([]);
  vi.mocked(client.anchorNow).mockResolvedValue({ anchored: false, reason: "unchanged", anchor: null });
  vi.mocked(client.verifyAnchor).mockResolvedValue({
    valid: true, on_chain_matches_record: true, ledger_matches_record: true, mismatches: [],
  });
  vi.mocked(client.getAnchorInterval).mockResolvedValue({ seconds: 900 });
  vi.mocked(client.updateAnchorInterval).mockResolvedValue({ seconds: 900 });
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
    await screen.findByLabelText(/rtm auto-scrape interval/i);
    await act(async () => {});
    const { input, update } = intervalControl(/rtm auto-scrape interval/i);
    expect(input.value).toBe("30");

    fireEvent.change(input, { target: { value: "60" } });
    fireEvent.click(update);
    await act(async () => {});
    expect(client.updateRtmInterval).toHaveBeenCalledWith(60);
  });

  it("switches to the Billing tab, loads history, and can load demo data", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Billing" }));
    expect(screen.getByRole("tab", { name: "Billing" })).toHaveAttribute("aria-selected", "true");
    await screen.findByText(/no billing history yet/i);
    expect(client.getBillingHistory).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /load demo data/i }));
    await screen.findByRole("button", { name: /load demo data/i }); // waits for "Loading…" to revert
    expect(client.loadDemoBillingData).toHaveBeenCalled();
  });

  it("loads the anchor interval on mount and can update it from the Dashboard", async () => {
    vi.mocked(client.getAnchorInterval).mockResolvedValue({ seconds: 1200 });
    vi.mocked(client.updateAnchorInterval).mockResolvedValue({ seconds: 600 });
    render(<App />);
    await act(async () => {});
    const { input, update } = intervalControl(/testnet anchor interval/i);
    expect(input.value).toBe("1200");
    expect(input.min).toBe("300");

    fireEvent.change(input, { target: { value: "600" } });
    fireEvent.click(update);
    await act(async () => {});
    expect(client.updateAnchorInterval).toHaveBeenCalledWith(600);
    expect(client.updateRtmInterval).not.toHaveBeenCalled();
    expect(input.value).toBe("600");
  });

  it("rejects an anchor interval below 300 seconds without calling the API", async () => {
    render(<App />);
    await act(async () => {});
    const { input, update } = intervalControl(/testnet anchor interval/i);
    fireEvent.change(input, { target: { value: "120" } });
    fireEvent.click(update);
    expect(await screen.findByText(/at least 300 seconds/i)).toBeInTheDocument();
    expect(client.updateAnchorInterval).not.toHaveBeenCalled();
  });

  it("keeps the Dashboard working when the anchor interval cannot be loaded", async () => {
    vi.mocked(client.getAnchorInterval).mockRejectedValue(new Error("failed to fetch anchor interval: 500"));
    render(<App />);
    await act(async () => {});
    expect(screen.getByLabelText(/rtm auto-scrape interval/i)).toBeInTheDocument();
    expect((screen.getByLabelText(/testnet anchor interval/i) as HTMLInputElement).value).toBe("900");
  });

  it("re-enables the anchor interval control when the update fails", async () => {
    vi.mocked(client.updateAnchorInterval).mockRejectedValue(new Error("failed to update anchor interval: 422"));
    render(<App />);
    await act(async () => {});
    const { input, update } = intervalControl(/testnet anchor interval/i);
    fireEvent.change(input, { target: { value: "600" } });
    fireEvent.click(update);
    await act(async () => {});
    expect(update).toBeEnabled();
  });

  it("switches to the Testnet tab and loads the anchoring status and anchors", async () => {
    vi.mocked(client.getAnchors).mockResolvedValue([ANCHOR]);
    render(<App />);
    const tab = screen.getByRole("tab", { name: "Testnet" });
    fireEvent.click(tab);
    expect(tab).toHaveAttribute("aria-selected", "true");
    expect(await screen.findByText("Polygon Amoy")).toBeInTheDocument();
    expect(await screen.findByRole("link", { name: "0xcccccccc…" })).toBeInTheDocument();
    expect(client.getAnchorStatus).toHaveBeenCalled();
    expect(client.getAnchors).toHaveBeenCalled();
  });

  it("shows the empty state on the Testnet tab when there are no anchors", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    expect(await screen.findByText(/no anchors yet/i)).toBeInTheDocument();
  });

  it("anchors now and reports the block number, then refreshes the anchors", async () => {
    vi.mocked(client.anchorNow).mockResolvedValue({ anchored: true, reason: null, anchor: ANCHOR });
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    await screen.findByText("Polygon Amoy");
    vi.mocked(client.getAnchors).mockResolvedValue([ANCHOR]);

    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(await screen.findByRole("status")).toHaveTextContent("Anchored in block 4242");
    expect(await screen.findByRole("link", { name: "0xcccccccc…" })).toBeInTheDocument();
    expect(client.anchorNow).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("button", { name: /anchor now/i })).toBeEnabled();
  });

  it("reports when nothing changed since the last anchor", async () => {
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    await screen.findByText("Polygon Amoy");
    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(await screen.findByRole("status")).toHaveTextContent("No change since last anchor");
  });

  it("reports a failed anchor attempt with its error", async () => {
    vi.mocked(client.anchorNow).mockResolvedValue({
      anchored: false,
      reason: "failed",
      anchor: { ...ANCHOR, status: "failed", tx_hash: null, error: "insufficient funds", explorer_url: null },
    });
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    await screen.findByText("Polygon Amoy");
    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(await screen.findByRole("status")).toHaveTextContent("Anchor failed: insufficient funds");
  });

  it("reports a failed anchor attempt with no anchor record", async () => {
    vi.mocked(client.anchorNow).mockResolvedValue({ anchored: false, reason: "failed", anchor: null });
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    await screen.findByText("Polygon Amoy");
    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(await screen.findByRole("status")).toHaveTextContent("Anchor failed: unknown error");
  });

  it("shows the thrown error message when anchoring is rejected", async () => {
    vi.mocked(client.anchorNow).mockRejectedValue(new Error("failed to anchor: 503 anchoring not configured"));
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    await screen.findByText("Polygon Amoy");
    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(await screen.findByRole("status")).toHaveTextContent("failed to anchor: 503 anchoring not configured");
    expect(screen.getByRole("button", { name: /anchor now/i })).toBeEnabled();
  });

  it("shows a non-Error rejection as a string", async () => {
    vi.mocked(client.anchorNow).mockRejectedValue("boom");
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    await screen.findByText("Polygon Amoy");
    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(await screen.findByRole("status")).toHaveTextContent("boom");
  });

  it("verifies an anchor and shows the result inline", async () => {
    vi.mocked(client.getAnchors).mockResolvedValue([ANCHOR]);
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    fireEvent.click(await screen.findByRole("button", { name: /verify/i }));
    expect(await screen.findByText("VALID")).toBeInTheDocument();
    expect(client.verifyAnchor).toHaveBeenCalledWith(5);
  });

  it("shows a verify error inline", async () => {
    vi.mocked(client.getAnchors).mockResolvedValue([ANCHOR]);
    vi.mocked(client.verifyAnchor).mockRejectedValue(new Error("failed to verify anchor: 409 anchor has no transaction"));
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    fireEvent.click(await screen.findByRole("button", { name: /verify/i }));
    expect(await screen.findByText(/409 anchor has no transaction/)).toBeInTheDocument();
  });

  it("shows a non-Error verify rejection as a string", async () => {
    vi.mocked(client.getAnchors).mockResolvedValue([ANCHOR]);
    vi.mocked(client.verifyAnchor).mockRejectedValue("nope");
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    fireEvent.click(await screen.findByRole("button", { name: /verify/i }));
    expect(await screen.findByText("nope")).toBeInTheDocument();
  });

  it("shows the disabled state on the Testnet tab when anchoring is not configured", async () => {
    vi.mocked(client.getAnchorStatus).mockResolvedValue({ ...ANCHOR_STATUS, enabled: false, wallet_address: null });
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    expect(await screen.findByText(/ANCHOR_PRIVATE_KEY/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /anchor now/i })).toBeDisabled();
  });

  it("surfaces an error message when the Testnet tab fails to load", async () => {
    vi.mocked(client.getAnchorStatus).mockRejectedValue(new Error("failed to fetch anchor status: 500"));
    render(<App />);
    fireEvent.click(screen.getByRole("tab", { name: "Testnet" }));
    expect(await screen.findByRole("status")).toHaveTextContent("failed to fetch anchor status: 500");
  });
});
