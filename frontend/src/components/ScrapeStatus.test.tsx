import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ScrapeStatus } from "./ScrapeStatus";
import type { ChainBlock } from "../api/types";

describe("ScrapeStatus", () => {
  it("shows 'never' for a market with no chain blocks yet", () => {
    render(
      <ScrapeStatus
        chainBlocks={[]}
        onScrape={vi.fn()}
        scraping={{ DAM: false, RTM: false }}
        errors={{ DAM: null, RTM: null }}
      />,
    );
    expect(screen.getAllByText(/never/i).length).toBe(2);
  });

  it("shows the latest timestamp per market, ignoring blocks from the other market", () => {
    const chainBlocks: ChainBlock[] = [
      { index: 0, timestamp: "2026-09-10T00:00:00Z", payload: { genesis: true }, prev_hash: "0".repeat(64), hash: "a".repeat(64) },
      { index: 1, timestamp: "2026-09-11T08:00:00Z", payload: { market: "DAM" }, prev_hash: "a".repeat(64), hash: "b".repeat(64) },
      { index: 2, timestamp: "2026-09-12T09:30:00Z", payload: { market: "DAM" }, prev_hash: "b".repeat(64), hash: "c".repeat(64) },
      { index: 3, timestamp: "2026-09-12T10:00:00Z", payload: { market: "RTM" }, prev_hash: "c".repeat(64), hash: "d".repeat(64) },
    ];
    render(
      <ScrapeStatus
        chainBlocks={chainBlocks}
        onScrape={vi.fn()}
        scraping={{ DAM: false, RTM: false }}
        errors={{ DAM: null, RTM: null }}
      />,
    );
    // DAM's latest block (index 2) timestamp should be shown, not the earlier index-1 block
    expect(screen.getByText(new Date("2026-09-12T09:30:00Z").toLocaleString())).toBeInTheDocument();
    expect(screen.getByText(new Date("2026-09-12T10:00:00Z").toLocaleString())).toBeInTheDocument();
    expect(screen.queryByText(/never/i)).not.toBeInTheDocument();
  });

  it("calls onScrape with the market when its button is clicked", () => {
    const onScrape = vi.fn();
    render(
      <ScrapeStatus
        chainBlocks={[]}
        onScrape={onScrape}
        scraping={{ DAM: false, RTM: false }}
        errors={{ DAM: null, RTM: null }}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /scrape dam/i }));
    expect(onScrape).toHaveBeenCalledWith("DAM");
  });

  it("disables the button and shows a scraping indicator while in progress", () => {
    render(
      <ScrapeStatus
        chainBlocks={[]}
        onScrape={vi.fn()}
        scraping={{ DAM: true, RTM: false }}
        errors={{ DAM: null, RTM: null }}
      />,
    );
    expect(screen.getByRole("button", { name: /scraping/i })).toBeDisabled();
  });

  it("shows an error message for a market that failed to scrape", () => {
    render(
      <ScrapeStatus
        chainBlocks={[]}
        onScrape={vi.fn()}
        scraping={{ DAM: false, RTM: false }}
        errors={{ DAM: "failed to trigger scrape: 502", RTM: null }}
      />,
    );
    expect(screen.getByText(/failed to trigger scrape: 502/i)).toBeInTheDocument();
  });
});
