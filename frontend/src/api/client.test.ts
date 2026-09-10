import { describe, expect, it, vi, afterEach } from "vitest";
import { createScenario, getChain, getComparison } from "./client";

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
