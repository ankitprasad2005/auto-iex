import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, within } from "@testing-library/react";
import { AnchorsView, shortHash } from "./AnchorsView";
import type { Anchor, AnchorStatus, AnchorVerifyResult } from "../api/types";
import { formatIST } from "../lib/formatIST";

const WALLET = "0x1234567890abcdef1234567890abcdef12345678";

const enabledStatus: AnchorStatus = {
  enabled: true,
  network: "Polygon Amoy",
  chain_id: 80002,
  wallet_address: WALLET,
  explorer_tx_url: "https://amoy.polygonscan.com/tx/",
};

const disabledStatus: AnchorStatus = { ...enabledStatus, enabled: false, wallet_address: null };

const TX = "0x" + "c".repeat(64);

const confirmed: Anchor = {
  id: 2,
  created_at: "2026-10-27T10:00:00Z",
  scrape_head_index: 3,
  scrape_head_hash: "a1".repeat(32),
  settlement_head_index: -1,
  settlement_head_hash: "0".repeat(64),
  price_ledger_head_index: 7,
  price_ledger_head_hash: "b2".repeat(32),
  tx_hash: TX,
  status: "confirmed",
  block_number: 123,
  error: null,
  explorer_url: `https://amoy.polygonscan.com/tx/${TX}`,
};

const failed: Anchor = {
  ...confirmed,
  id: 1,
  created_at: "2026-10-27T09:00:00Z",
  tx_hash: null,
  status: "failed",
  block_number: null,
  error: "insufficient funds for gas",
  explorer_url: null,
};

type ViewProps = Parameters<typeof AnchorsView>[0];

function renderView(overrides: Partial<ViewProps> = {}) {
  const props: ViewProps = {
    status: enabledStatus,
    anchors: [],
    onAnchorNow: vi.fn(),
    anchoring: false,
    onVerify: vi.fn(),
    verifyResults: {},
    message: null,
    ...overrides,
  };
  render(<AnchorsView {...props} />);
  return props;
}

describe("shortHash", () => {
  it("keeps the first 10 characters and appends an ellipsis", () => {
    expect(shortHash("abcdefghijklmnop")).toBe("abcdefghij…");
  });

  it("returns short values unchanged", () => {
    expect(shortHash("abc")).toBe("abc");
    expect(shortHash("abcdefghij")).toBe("abcdefghij");
  });
});

describe("AnchorsView", () => {
  it("shows the network, chain id, full wallet address and Enabled when configured", () => {
    renderView();
    expect(screen.getByText("Polygon Amoy")).toBeInTheDocument();
    expect(screen.getByText("80002")).toBeInTheDocument();
    const wallet = screen.getByText(WALLET);
    expect(wallet).toHaveClass("font-mono");
    expect(screen.getByText("Enabled")).toBeInTheDocument();
    expect(screen.queryByText(/ANCHOR_PRIVATE_KEY/)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /anchor now/i })).toBeEnabled();
  });

  it("explains why anchoring is disabled and disables the Anchor now button", () => {
    renderView({ status: disabledStatus });
    expect(screen.getByText("Disabled")).toBeInTheDocument();
    expect(screen.getByText(/ANCHOR_PRIVATE_KEY/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /anchor now/i })).toBeDisabled();
    // No wallet configured: a placeholder instead of an address.
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("shows a loading state and disables the button while the status is unknown", () => {
    renderView({ status: null });
    expect(screen.getByText(/loading anchoring status/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /anchor now/i })).toBeDisabled();
  });

  it("calls onAnchorNow when the button is clicked", () => {
    const props = renderView();
    fireEvent.click(screen.getByRole("button", { name: /anchor now/i }));
    expect(props.onAnchorNow).toHaveBeenCalledTimes(1);
  });

  it("disables the button and shows Anchoring… while an anchor is in flight", () => {
    renderView({ anchoring: true });
    const button = screen.getByRole("button", { name: /anchoring…/i });
    expect(button).toBeDisabled();
    expect(screen.queryByRole("button", { name: /anchor now/i })).not.toBeInTheDocument();
  });

  it("shows the message line when given", () => {
    renderView({ message: "No change since last anchor" });
    expect(screen.getByRole("status")).toHaveTextContent("No change since last anchor");
  });

  it("renders no message line when there is no message", () => {
    renderView();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("shows an empty state when there are no anchors", () => {
    renderView();
    expect(screen.getByText(/no anchors yet/i)).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("renders a horizontally scrollable table with a row per anchor", () => {
    renderView({ anchors: [confirmed, failed] });
    const table = screen.getByRole("table");
    expect(table.parentElement).toHaveClass("overflow-x-auto");
    expect(screen.getAllByRole("row")).toHaveLength(3);
    expect(screen.getByRole("columnheader", { name: /scrape/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /settlement/i })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /price/i })).toBeInTheDocument();
  });

  it("shows the time in IST and the three short head hashes with full hashes as tooltips", () => {
    renderView({ anchors: [confirmed] });
    const row = screen.getAllByRole("row")[1];
    expect(within(row).getByText(formatIST(confirmed.created_at))).toBeInTheDocument();
    const scrape = within(row).getByText("a1a1a1a1a1…");
    expect(scrape).toHaveAttribute("title", confirmed.scrape_head_hash);
    expect(within(row).getByText("0000000000…")).toHaveAttribute("title", confirmed.settlement_head_hash);
    expect(within(row).getByText("b2b2b2b2b2…")).toHaveAttribute("title", confirmed.price_ledger_head_hash);
  });

  it("links a confirmed anchor's short tx hash to the explorer in a new tab", () => {
    renderView({ anchors: [confirmed] });
    const link = screen.getByRole("link", { name: "0xcccccccc…" });
    expect(link).toHaveAttribute("href", confirmed.explorer_url);
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
    expect(screen.getByText("confirmed")).toBeInTheDocument();
  });

  it("shows a failed anchor's status and error, with no tx link and no Verify button", () => {
    renderView({ anchors: [failed] });
    const row = screen.getAllByRole("row")[1];
    const status = within(row).getByText("failed");
    expect(status).toHaveAttribute("title", failed.error);
    expect(within(row).getByText(failed.error!)).toBeInTheDocument();
    expect(within(row).queryByRole("link")).not.toBeInTheDocument();
    expect(within(row).queryByRole("button", { name: /verify/i })).not.toBeInTheDocument();
  });

  it("shows a failed anchor without an error message", () => {
    renderView({ anchors: [{ ...failed, error: null }] });
    const row = screen.getAllByRole("row")[1];
    expect(within(row).getByText("failed")).not.toHaveAttribute("title");
  });

  it("shows the tx hash as plain text when there is no explorer url", () => {
    renderView({ anchors: [{ ...confirmed, explorer_url: null }] });
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
    expect(screen.getByText("0xcccccccc…")).toBeInTheDocument();
  });

  it("calls onVerify with the anchor id", () => {
    const props = renderView({ anchors: [confirmed] });
    fireEvent.click(screen.getByRole("button", { name: /verify/i }));
    expect(props.onVerify).toHaveBeenCalledWith(2);
  });

  it("shows VALID in normal text for a valid verify result", () => {
    const valid: AnchorVerifyResult = {
      valid: true,
      on_chain_matches_record: true,
      ledger_matches_record: true,
      mismatches: [],
    };
    renderView({ anchors: [confirmed], verifyResults: { 2: valid } });
    const label = screen.getByText("VALID");
    expect(label).not.toHaveClass("text-nd-accent");
    expect(screen.queryByText("TAMPERED")).not.toBeInTheDocument();
  });

  it("shows TAMPERED and the mismatch list in accent red for an invalid result", () => {
    const tampered: AnchorVerifyResult = {
      valid: false,
      on_chain_matches_record: true,
      ledger_matches_record: false,
      mismatches: ["settlement head hash differs", "price ledger head hash differs"],
    };
    renderView({ anchors: [confirmed], verifyResults: { 2: tampered } });
    const label = screen.getByText("TAMPERED");
    expect(label.closest(".text-nd-accent")).not.toBeNull();
    const items = screen.getAllByRole("listitem");
    expect(items.map((li) => li.textContent)).toEqual([
      "settlement head hash differs",
      "price ledger head hash differs",
    ]);
  });

  it("shows TAMPERED with no list when there are no mismatch details", () => {
    const tampered: AnchorVerifyResult = {
      valid: false,
      on_chain_matches_record: false,
      ledger_matches_record: true,
      mismatches: [],
    };
    renderView({ anchors: [confirmed], verifyResults: { 2: tampered } });
    expect(screen.getByText("TAMPERED")).toBeInTheDocument();
    expect(screen.queryByRole("list")).not.toBeInTheDocument();
  });

  it("shows a verify error string inline", () => {
    renderView({ anchors: [confirmed], verifyResults: { 2: "failed to verify anchor: 503 anchoring not configured" } });
    const err = screen.getByText(/anchoring not configured/);
    expect(err).toHaveClass("text-nd-accent");
  });

  it("only shows a verify result on the row it belongs to", () => {
    const other: Anchor = { ...confirmed, id: 3 };
    const valid: AnchorVerifyResult = {
      valid: true,
      on_chain_matches_record: true,
      ledger_matches_record: true,
      mismatches: [],
    };
    renderView({ anchors: [other, confirmed], verifyResults: { 2: valid } });
    const rows = screen.getAllByRole("row");
    expect(within(rows[1]).queryByText("VALID")).not.toBeInTheDocument();
    expect(within(rows[2]).getByText("VALID")).toBeInTheDocument();
  });
});
