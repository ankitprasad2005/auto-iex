import { useEffect, useState } from "react";
import { ConsumptionForm } from "./components/ConsumptionForm";
import { ComparisonView } from "./components/ComparisonView";
import { ChainNetwork } from "./components/ChainNetwork";
import { RangeList } from "./components/RangeList";
import { ScrapeStatus } from "./components/ScrapeStatus";
import { createScenario, getChain, getComparison, triggerScrape } from "./api/client";
import type { ChainBlock, ComparisonResult, ConsumptionRangeInput, Market } from "./api/types";

type Tab = "dashboard" | "chain";

function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

// DAM prices for a given delivery date are published the day before, so on
// a fresh deployment "tomorrow" is the first date likely to have DAM data
// once the scheduler's first run completes. The date picker lets the user
// pick any other date once real scrape history builds up.
function defaultDate(): string {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return isoDate(tomorrow);
}

function TabButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={`font-mono text-xs uppercase tracking-label px-1 pb-2 border-b-2 transition-colors ${
        active
          ? "border-nd-accent text-nd-text-display"
          : "border-transparent text-nd-text-secondary hover:text-nd-text-primary"
      }`}
    >
      {label}
    </button>
  );
}

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const [date, setDate] = useState(defaultDate());
  const [ranges, setRanges] = useState<ConsumptionRangeInput[]>([]);
  const [scenarioId, setScenarioId] = useState<number | null>(null);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [chainBlocks, setChainBlocks] = useState<ChainBlock[]>([]);
  const [scraping, setScraping] = useState<Record<Market, boolean>>({ DAM: false, RTM: false });
  const [scrapeErrors, setScrapeErrors] = useState<Record<Market, string | null>>({ DAM: null, RTM: null });

  useEffect(() => {
    getChain().then(setChainBlocks);
  }, []);

  async function refreshComparison(nextRanges: ConsumptionRangeInput[], forDate: string) {
    if (nextRanges.length === 0) {
      setScenarioId(null);
      setComparison(null);
      return;
    }
    const scenario = await createScenario("scenario", nextRanges);
    setScenarioId(scenario.id);
    setComparison(await getComparison(scenario.id, forDate));
  }

  async function handleAddRange(range: ConsumptionRangeInput) {
    const nextRanges = [...ranges, range];
    setRanges(nextRanges);
    await refreshComparison(nextRanges, date);
  }

  async function handleRemoveRange(index: number) {
    const nextRanges = ranges.filter((_, i) => i !== index);
    setRanges(nextRanges);
    await refreshComparison(nextRanges, date);
  }

  async function handleDateChange(nextDate: string) {
    setDate(nextDate);
    if (scenarioId !== null) {
      setComparison(await getComparison(scenarioId, nextDate));
    }
  }

  async function handleScrape(market: Market) {
    setScraping((s) => ({ ...s, [market]: true }));
    setScrapeErrors((e) => ({ ...e, [market]: null }));
    try {
      await triggerScrape(market, date);
      setChainBlocks(await getChain());
    } catch (err) {
      setScrapeErrors((e) => ({ ...e, [market]: err instanceof Error ? err.message : String(err) }));
    } finally {
      setScraping((s) => ({ ...s, [market]: false }));
    }
  }

  async function handleSelectChainTab() {
    setTab("chain");
    setChainBlocks(await getChain());
  }

  return (
    <div className="min-h-screen bg-nd-black text-nd-text-primary font-body p-4 sm:p-8">
      <div className="max-w-5xl mx-auto flex flex-col gap-8">
        <header>
          <h1 className="font-display text-2xl text-nd-text-display mb-6">auto-iex</h1>
          <div role="tablist" className="flex gap-8 border-b border-nd-border">
            <TabButton label="Dashboard" active={tab === "dashboard"} onClick={() => setTab("dashboard")} />
            <TabButton label="Chain" active={tab === "chain"} onClick={handleSelectChainTab} />
          </div>
        </header>

        {tab === "dashboard" && (
          <div className="flex flex-col gap-8">
            <ScrapeStatus
              chainBlocks={chainBlocks}
              onScrape={handleScrape}
              scraping={scraping}
              errors={scrapeErrors}
            />

            <label htmlFor="comparison-date" className="flex flex-col gap-1 max-w-xs">
              <span className="font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
                Delivery date
              </span>
              <input
                id="comparison-date"
                type="date"
                value={date}
                onChange={(e) => handleDateChange(e.target.value)}
                className="bg-nd-surface border border-nd-border-visible text-nd-text-primary font-mono text-sm px-3 py-2 focus:outline-none focus:border-nd-accent"
              />
            </label>

            <div className="flex flex-col gap-4 sm:flex-row sm:gap-8">
              <div className="flex-1">
                <ConsumptionForm onAddRange={handleAddRange} />
              </div>
              <div className="flex-1">
                <RangeList ranges={ranges} onRemove={handleRemoveRange} />
              </div>
            </div>

            <ComparisonView result={comparison} />
          </div>
        )}

        {tab === "chain" && <ChainNetwork blocks={chainBlocks} />}
      </div>
    </div>
  );
}
