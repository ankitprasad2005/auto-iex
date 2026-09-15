import { describe, expect, it } from "vitest";
import { mergePriceSeries } from "./priceSeries";
import type { PricePoint } from "../api/types";

describe("mergePriceSeries", () => {
  it("returns all 96 blocks even when both inputs are empty", () => {
    const result = mergePriceSeries([], []);
    expect(result).toHaveLength(96);
    expect(result[0]).toEqual({ blockIndex: 0, time: "00:00", damPrice: null, rtmPrice: null });
    expect(result[95].time).toBe("23:45");
  });

  it("fills in DAM and RTM prices at the matching block, leaving others null", () => {
    const dam: PricePoint[] = [{ block_start: "00:00:00", block_end: "00:15:00", mcp_rs_per_mwh: "3245.5000" }];
    const rtm: PricePoint[] = [{ block_start: "00:15:00", block_end: "00:30:00", mcp_rs_per_mwh: "2900.0000" }];

    const result = mergePriceSeries(dam, rtm);

    expect(result[0]).toEqual({ blockIndex: 0, time: "00:00", damPrice: 3245.5, rtmPrice: null });
    expect(result[1]).toEqual({ blockIndex: 1, time: "00:15", damPrice: null, rtmPrice: 2900 });
    expect(result[2].damPrice).toBeNull();
    expect(result[2].rtmPrice).toBeNull();
  });

  it("ignores price points for block starts outside the 96-block grid", () => {
    const dam: PricePoint[] = [{ block_start: "99:99:00", block_end: "00:00:00", mcp_rs_per_mwh: "1.0" }];
    const result = mergePriceSeries(dam, []);
    expect(result.every((p) => p.damPrice === null)).toBe(true);
  });
});
