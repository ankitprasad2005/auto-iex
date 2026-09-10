import { useState } from "react";
import { ConsumptionForm } from "./components/ConsumptionForm";
import { ComparisonView } from "./components/ComparisonView";
import { ChainNetwork } from "./components/ChainNetwork";
import { createScenario, getChain, getComparison } from "./api/client";
import type { ChainBlock, ComparisonResult, ConsumptionRangeInput } from "./api/types";

type Tab = "dashboard" | "chain";

const TODAY = new Date().toISOString().slice(0, 10);

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
  const [ranges, setRanges] = useState<ConsumptionRangeInput[]>([]);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [chainBlocks, setChainBlocks] = useState<ChainBlock[]>([]);

  async function handleAddRange(range: ConsumptionRangeInput) {
    const nextRanges = [...ranges, range];
    setRanges(nextRanges);
    const scenario = await createScenario("scenario", nextRanges);
    const result = await getComparison(scenario.id, TODAY);
    setComparison(result);
  }

  async function handleSelectChainTab() {
    setTab("chain");
    setChainBlocks(await getChain());
  }

  return (
    <div className="min-h-screen bg-nd-black text-nd-text-primary font-body p-8">
      <header className="mb-8">
        <h1 className="font-display text-2xl text-nd-text-display mb-6">auto-iex</h1>
        <div role="tablist" className="flex gap-8 border-b border-nd-border">
          <TabButton label="Dashboard" active={tab === "dashboard"} onClick={() => setTab("dashboard")} />
          <TabButton label="Chain" active={tab === "chain"} onClick={handleSelectChainTab} />
        </div>
      </header>

      {tab === "dashboard" && (
        <div className="flex flex-col gap-8">
          <ConsumptionForm onAddRange={handleAddRange} />
          <ComparisonView result={comparison} />
        </div>
      )}

      {tab === "chain" && <ChainNetwork blocks={chainBlocks} />}
    </div>
  );
}
