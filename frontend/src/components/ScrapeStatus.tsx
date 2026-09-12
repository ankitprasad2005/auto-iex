import type { ChainBlock, Market } from "../api/types";

interface Props {
  chainBlocks: ChainBlock[];
  onScrape: (market: Market) => void;
  scraping: Record<Market, boolean>;
  errors: Record<Market, string | null>;
}

const MARKETS: Market[] = ["DAM", "RTM"];

function lastScrapedAt(chainBlocks: ChainBlock[], market: Market): string | null {
  const timestamps = chainBlocks
    .filter((b) => b.payload.market === market)
    .map((b) => b.timestamp);
  if (timestamps.length === 0) return null;
  return timestamps.reduce((latest, ts) => (ts > latest ? ts : latest));
}

export function ScrapeStatus({ chainBlocks, onScrape, scraping, errors }: Props) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:gap-8">
      {MARKETS.map((market) => {
        const lastScraped = lastScrapedAt(chainBlocks, market);
        const isScraping = scraping[market];
        const error = errors[market];
        return (
          <div key={market} className="flex flex-col gap-1">
            <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
              {market} last scraped
            </span>
            <span className="font-mono text-xs text-nd-text-primary">
              {lastScraped ? new Date(lastScraped).toLocaleString() : "Never"}
            </span>
            <button
              type="button"
              onClick={() => onScrape(market)}
              disabled={isScraping}
              className="self-start font-mono text-[11px] uppercase tracking-label px-3 py-1.5 border border-nd-border-visible text-nd-text-primary hover:border-nd-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isScraping ? "Scraping…" : `Scrape ${market} now`}
            </button>
            {error && (
              <span role="alert" className="font-mono text-[11px] text-nd-accent">
                {error}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
