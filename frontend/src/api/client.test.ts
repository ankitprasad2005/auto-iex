import { describe, expect, it, vi, afterEach } from "vitest";
import {
  checkLedgerNow,
  checkPriceLedgerNow,
  createScenario,
  getChain,
  getComparison,
  getLedger,
  getPriceLedger,
  getPrices,
  getRtmInterval,
  triggerScrape,
  updateRtmInterval,
} from "./client";

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
