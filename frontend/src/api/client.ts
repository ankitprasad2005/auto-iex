import type { ChainBlock, ComparisonResult, ConsumptionRangeInput, Market, ScenarioOut, ScrapeResult } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function createScenario(name: string, ranges: ConsumptionRangeInput[]): Promise<ScenarioOut> {
  const res = await fetch(`${BASE_URL}/scenarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, ranges }),
  });
  if (!res.ok) throw new Error(`failed to create scenario: ${res.status}`);
  return res.json();
}

export async function getComparison(scenarioId: number, date: string): Promise<ComparisonResult> {
  const res = await fetch(`${BASE_URL}/scenarios/${scenarioId}/comparison?date=${date}`);
  if (!res.ok) throw new Error(`failed to fetch comparison: ${res.status}`);
  return res.json();
}

export async function getChain(): Promise<ChainBlock[]> {
  const res = await fetch(`${BASE_URL}/chain`);
  if (!res.ok) throw new Error(`failed to fetch chain: ${res.status}`);
  return res.json();
}

export async function triggerScrape(market: Market, date: string): Promise<ScrapeResult> {
  const res = await fetch(`${BASE_URL}/scrape/${market}?date=${date}`, { method: "POST" });
  if (!res.ok) throw new Error(`failed to trigger scrape: ${res.status}`);
  return res.json();
}
