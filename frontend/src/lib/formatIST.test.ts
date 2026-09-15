import { describe, expect, it } from "vitest";
import { formatIST } from "./formatIST";

describe("formatIST", () => {
  it("converts a UTC timestamp to IST (UTC+5:30), regardless of the viewer's local timezone", () => {
    // 05:19:47 UTC + 5:30 = 10:49:47 IST
    const result = formatIST("2026-09-15T05:19:47.000Z");
    expect(result).toContain("15/09/2026");
    expect(result).toContain("10:49:47");
    expect(result.toLowerCase()).toContain("am");
    expect(result).toContain("IST");
  });

  it("handles a time that crosses midnight into the next IST day", () => {
    // 19:00 UTC on the 14th + 5:30 = 00:30 IST on the 15th
    const result = formatIST("2026-09-14T19:00:00.000Z");
    expect(result).toContain("15/09/2026");
    expect(result).toContain("12:30:00");
    expect(result.toLowerCase()).toContain("am");
  });

  it("formats a PM time correctly", () => {
    // 10:00 UTC + 5:30 = 15:30 IST = 3:30 PM
    const result = formatIST("2026-09-15T10:00:00.000Z");
    expect(result).toContain("03:30:00");
    expect(result.toLowerCase()).toContain("pm");
  });
});
