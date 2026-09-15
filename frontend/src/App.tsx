import { useEffect, useState } from "react";
import { ConsumptionForm } from "./components/ConsumptionForm";
import { ComparisonView } from "./components/ComparisonView";
import { ChainNetwork } from "./components/ChainNetwork";
import { PricesView } from "./components/PricesView";
import { RangeList } from "./components/RangeList";
import { ScrapeStatus } from "./components/ScrapeStatus";
import { SettlementLedger } from "./components/SettlementLedger";
import {
  checkLedgerNow,
  createScenario,
  getChain,
  getComparison,
  getLedger,
  getPrices,
  triggerScrape,
} from "./api/client";
import { mergePriceSeries, type MergedPricePoint } from "./lib/priceSeries";
import type { ChainBlock, ComparisonResult, ConsumptionRangeInput, Market, SettlementBlock } from "./api/types";

type Tab = "dashboard" | "prices" | "chain" | "ledger";

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
  const [pricesDate, setPricesDate] = useState(defaultDate());
  const [priceSeries, setPriceSeries] = useState<MergedPricePoint[]>(mergePriceSeries([], []));
  const [ledgerBlocks, setLedgerBlocks] = useState<SettlementBlock[]>([]);
  const [checkingLedger, setCheckingLedger] = useState(false);

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

  async function loadPrices(forDate: string) {
    const [dam, rtm] = await Promise.all([getPrices(forDate, "DAM"), getPrices(forDate, "RTM")]);
    setPriceSeries(mergePriceSeries(dam, rtm));
  }

  async function handleSelectPricesTab() {
    setTab("prices");
    await loadPrices(pricesDate);
  }

  async function handlePricesDateChange(nextDate: string) {
    setPricesDate(nextDate);
    await loadPrices(nextDate);
  }

  async function handleSelectLedgerTab() {
    setTab("ledger");
    setLedgerBlocks(await getLedger());
  }

  async function handleCheckLedgerNow() {
    setCheckingLedger(true);
    try {
      await checkLedgerNow();
      setLedgerBlocks(await getLedger());
    } finally {
      setCheckingLedger(false);
    }
  }

  return (
    <div className="min-h-screen bg-nd-black text-nd-text-primary font-body p-4 sm:p-8">
      <div className="max-w-5xl mx-auto flex flex-col gap-8">
        <header>
          <h1 className="font-display text-2xl text-nd-text-display mb-6">auto-iex</h1>
          <div role="tablist" className="flex gap-8 border-b border-nd-border">
            <TabButton label="Dashboard" active={tab === "dashboard"} onClick={() => setTab("dashboard")} />
            <TabButton label="Prices" active={tab === "prices"} onClick={handleSelectPricesTab} />
            <TabButton label="Chain" active={tab === "chain"} onClick={handleSelectChainTab} />
            <TabButton label="Ledger" active={tab === "ledger"} onClick={handleSelectLedgerTab} />
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

        {tab === "prices" && (
          <PricesView date={pricesDate} onDateChange={handlePricesDateChange} data={priceSeries} />
        )}

        {tab === "chain" && <ChainNetwork blocks={chainBlocks} />}

        {tab === "ledger" && (
          <SettlementLedger blocks={ledgerBlocks} onCheckNow={handleCheckLedgerNow} checking={checkingLedger} />
        )}
      </div>
    </div>
  );
}
