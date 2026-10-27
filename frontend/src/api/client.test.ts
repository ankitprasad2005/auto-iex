import { describe, expect, it, vi, afterEach } from "vitest";
import {
  anchorNow,
  checkLedgerNow,
  checkPriceLedgerNow,
  createScenario,
  getAnchorInterval,
  getAnchors,
  getAnchorStatus,
  getBillingHistory,
  getChain,
  getComparison,
  getLedger,
  getPriceLedger,
  getPrices,
  getRtmInterval,
  loadDemoBillingData,
  triggerScrape,
  updateAnchorInterval,
  updateRtmInterval,
  verifyAnchor,
} from "./client";
import type { Anchor } from "./types";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("createScenario", () => {
  it("posts to /scenarios and returns the created scenario", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, name: "evening" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await createScenario("evening", [{ start_time: "18:00", end_time: "19:00", predicted_kw: 4 }]);

    expect(result).toEqual({ id: 1, name: "evening" });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/scenarios"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422 }));
    await expect(createScenario("bad", [])).rejects.toThrow("422");
  });
});

describe("getComparison", () => {
  it("fetches the comparison for a scenario and date", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ blocks: [], dam_total_rs: "0", rtm_total_rs: "0", hybrid_total_rs: "0", dam_pending_blocks: 96, rtm_pending_blocks: 96 }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await getComparison(1, "2026-09-10");
    expect(result.dam_pending_blocks).toBe(96);
    expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining("/scenarios/1/comparison?date=2026-09-10"));
  });
});

describe("getChain", () => {
  it("fetches chain blocks", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));
    const result = await getChain();
    expect(result).toEqual([]);
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getChain()).rejects.toThrow("500");
  });
});

describe("getPrices", () => {
  it("fetches prices for a date and market", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "3245.5000" }],
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await getPrices("2026-09-13", "DAM");
    expect(result).toEqual([{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "3245.5000" }]);
    expect(mockFetch).toHaveBeenCalledWith(expect.stringContaining("/prices?date=2026-09-13&market=DAM"));
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getPrices("2026-09-13", "RTM")).rejects.toThrow("500");
  });
});

describe("triggerScrape", () => {
  it("posts to /scrape/{market} with the date and returns the result", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ written: 96, skipped_duplicate: false, chain_block_index: 3 }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await triggerScrape("DAM", "2026-09-13");

    expect(result).toEqual({ written: 96, skipped_duplicate: false, chain_block_index: 3 });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/scrape/DAM?date=2026-09-13"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 502 }));
    await expect(triggerScrape("RTM", "2026-09-12")).rejects.toThrow("502");
  });
});

describe("getLedger", () => {
  it("fetches settlement ledger blocks", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));
    const result = await getLedger();
    expect(result).toEqual([]);
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getLedger()).rejects.toThrow("500");
  });
});

describe("checkLedgerNow", () => {
  it("posts to /ledger/check and returns the settled count", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ settled_count: 2 }) });
    vi.stubGlobal("fetch", mockFetch);

    const result = await checkLedgerNow();

    expect(result).toEqual({ settled_count: 2 });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/ledger/check"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(checkLedgerNow()).rejects.toThrow("500");
  });
});

describe("getPriceLedger", () => {
  it("fetches price ledger blocks", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));
    const result = await getPriceLedger();
    expect(result).toEqual([]);
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getPriceLedger()).rejects.toThrow("500");
  });
});

describe("checkPriceLedgerNow", () => {
  it("posts to /price-ledger/check and returns the recorded count", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ recorded_count: 3 }) });
    vi.stubGlobal("fetch", mockFetch);

    const result = await checkPriceLedgerNow();

    expect(result).toEqual({ recorded_count: 3 });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/price-ledger/check"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(checkPriceLedgerNow()).rejects.toThrow("500");
  });
});

describe("getRtmInterval", () => {
  it("fetches the current RTM auto-scrape interval", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ seconds: 30 }) }));
    const result = await getRtmInterval();
    expect(result).toEqual({ seconds: 30 });
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getRtmInterval()).rejects.toThrow("500");
  });
});

describe("updateRtmInterval", () => {
  it("patches /scheduler/rtm-interval with the new seconds value", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ seconds: 120 }) });
    vi.stubGlobal("fetch", mockFetch);

    const result = await updateRtmInterval(120);

    expect(result).toEqual({ seconds: 120 });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/scheduler/rtm-interval"),
      expect.objectContaining({
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seconds: 120 }),
      }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422 }));
    await expect(updateRtmInterval(5)).rejects.toThrow("422");
  });
});

describe("getBillingHistory", () => {
  it("fetches billing history with totals", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ records: [], total_kwh: "0", total_cost_rs: "0" }),
    });
    vi.stubGlobal("fetch", mockFetch);

    const result = await getBillingHistory();
    expect(result).toEqual({ records: [], total_kwh: "0", total_cost_rs: "0" });
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getBillingHistory()).rejects.toThrow("500");
  });
});

describe("loadDemoBillingData", () => {
  it("posts to /billing/demo and returns the created count", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ created_count: 45 }) });
    vi.stubGlobal("fetch", mockFetch);

    const result = await loadDemoBillingData();

    expect(result).toEqual({ created_count: 45 });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/billing/demo"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(loadDemoBillingData()).rejects.toThrow("500");
  });
});

const sampleAnchor: Anchor = {
  id: 1,
  created_at: "2026-10-27T10:00:00Z",
  scrape_head_index: 3,
  scrape_head_hash: "a".repeat(64),
  settlement_head_index: -1,
  settlement_head_hash: "0".repeat(64),
  price_ledger_head_index: 7,
  price_ledger_head_hash: "b".repeat(64),
  tx_hash: "0x" + "c".repeat(64),
  status: "confirmed",
  block_number: 123,
  error: null,
  explorer_url: "https://amoy.polygonscan.com/tx/0x" + "c".repeat(64),
};

describe("getAnchorStatus", () => {
  it("fetches /anchors/status", async () => {
    const status = {
      enabled: true,
      network: "Polygon Amoy",
      chain_id: 80002,
      wallet_address: "0xabc",
      explorer_tx_url: "https://amoy.polygonscan.com/tx/",
    };
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => status });
    vi.stubGlobal("fetch", mockFetch);
    expect(await getAnchorStatus()).toEqual(status);
    expect(mockFetch).toHaveBeenCalledWith(expect.stringMatching(/\/anchors\/status$/));
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getAnchorStatus()).rejects.toThrow("500");
  });
});

describe("getAnchors", () => {
  it("fetches /anchors", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [sampleAnchor] });
    vi.stubGlobal("fetch", mockFetch);
    expect(await getAnchors()).toEqual([sampleAnchor]);
    expect(mockFetch).toHaveBeenCalledWith(expect.stringMatching(/\/anchors$/));
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getAnchors()).rejects.toThrow("500");
  });
});

describe("anchorNow", () => {
  it("posts to /anchors/now and returns the result", async () => {
    const result = { anchored: true, reason: null, anchor: sampleAnchor };
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => result });
    vi.stubGlobal("fetch", mockFetch);
    expect(await anchorNow()).toEqual(result);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/anchors\/now$/),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("surfaces the backend's detail message on error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 503, json: async () => ({ detail: "anchoring not configured" }) }),
    );
    await expect(anchorNow()).rejects.toThrow(/503.*anchoring not configured/);
  });

  it("falls back to the status code when the error body is not JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        json: async () => {
          throw new SyntaxError("Unexpected token");
        },
      }),
    );
    await expect(anchorNow()).rejects.toThrow("failed to anchor: 502");
  });

  it("falls back to the status code when the response has no json method", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(anchorNow()).rejects.toThrow("failed to anchor: 500");
  });

  it("ignores a non-string detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: [{ msg: "bad" }] }) }),
    );
    await expect(anchorNow()).rejects.toThrow(/^failed to anchor: 422$/);
  });

  it("ignores a null JSON body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500, json: async () => null }));
    await expect(anchorNow()).rejects.toThrow(/^failed to anchor: 500$/);
  });
});

describe("verifyAnchor", () => {
  it("fetches /anchors/{id}/verify", async () => {
    const result = { valid: true, on_chain_matches_record: true, ledger_matches_record: true, mismatches: [] };
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => result });
    vi.stubGlobal("fetch", mockFetch);
    expect(await verifyAnchor(42)).toEqual(result);
    expect(mockFetch).toHaveBeenCalledWith(expect.stringMatching(/\/anchors\/42\/verify$/));
  });

  it("surfaces the backend's detail message for a 404", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 404, json: async () => ({ detail: "anchor not found" }) }),
    );
    await expect(verifyAnchor(999)).rejects.toThrow(/404.*anchor not found/);
  });

  it("surfaces the backend's detail message for a 409", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 409, json: async () => ({ detail: "anchor has no transaction" }) }),
    );
    await expect(verifyAnchor(2)).rejects.toThrow(/409.*anchor has no transaction/);
  });

  it("falls back to the status code without a detail", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 503, json: async () => ({}) }));
    await expect(verifyAnchor(1)).rejects.toThrow(/^failed to verify anchor: 503$/);
  });
});

describe("getAnchorInterval", () => {
  it("fetches /scheduler/anchor-interval", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ seconds: 900 }) });
    vi.stubGlobal("fetch", mockFetch);
    expect(await getAnchorInterval()).toEqual({ seconds: 900 });
    expect(mockFetch).toHaveBeenCalledWith(expect.stringMatching(/\/scheduler\/anchor-interval$/));
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 500 }));
    await expect(getAnchorInterval()).rejects.toThrow("500");
  });
});

describe("updateAnchorInterval", () => {
  it("patches /scheduler/anchor-interval with the new seconds value", async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ seconds: 600 }) });
    vi.stubGlobal("fetch", mockFetch);
    expect(await updateAnchorInterval(600)).toEqual({ seconds: 600 });
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringMatching(/\/scheduler\/anchor-interval$/),
      expect.objectContaining({
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seconds: 600 }),
      }),
    );
  });

  it("throws when the API returns an error status", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422 }));
    await expect(updateAnchorInterval(100)).rejects.toThrow("422");
  });
});
