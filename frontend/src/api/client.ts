import type {
  ChainBlock,
  CheckLedgerResult,
  CheckPriceLedgerResult,
  ComparisonResult,
  ConsumptionRangeInput,
  Market,
  PricePoint,
  RtmIntervalResult,
  ScenarioOut,
  ScrapeResult,
  SettlementBlock,
} from "./types";

// Relative by default so the built app works unmodified behind nginx's
// /api/ reverse proxy in Docker (see frontend/nginx.conf.template) — no
// build-time backend address needs to be baked in for that deployment.
// Local dev (`npm run dev`, no proxy in front) overrides this directly with
// VITE_API_BASE_URL to reach the backend dev server.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

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

export async function getPrices(date: string, market: Market): Promise<PricePoint[]> {
  const res = await fetch(`${BASE_URL}/prices?date=${date}&market=${market}`);
  if (!res.ok) throw new Error(`failed to fetch prices: ${res.status}`);
  return res.json();
}

export async function getLedger(): Promise<SettlementBlock[]> {
  const res = await fetch(`${BASE_URL}/ledger`);
  if (!res.ok) throw new Error(`failed to fetch ledger: ${res.status}`);
  return res.json();
}

export async function checkLedgerNow(): Promise<CheckLedgerResult> {
  const res = await fetch(`${BASE_URL}/ledger/check`, { method: "POST" });
  if (!res.ok) throw new Error(`failed to check ledger: ${res.status}`);
  return res.json();
}

export async function getPriceLedger(): Promise<ChainBlock[]> {
  const res = await fetch(`${BASE_URL}/price-ledger`);
  if (!res.ok) throw new Error(`failed to fetch price ledger: ${res.status}`);
  return res.json();
}

export async function checkPriceLedgerNow(): Promise<CheckPriceLedgerResult> {
  const res = await fetch(`${BASE_URL}/price-ledger/check`, { method: "POST" });
  if (!res.ok) throw new Error(`failed to check price ledger: ${res.status}`);
  return res.json();
}

export async function getRtmInterval(): Promise<RtmIntervalResult> {
  const res = await fetch(`${BASE_URL}/scheduler/rtm-interval`);
  if (!res.ok) throw new Error(`failed to fetch RTM interval: ${res.status}`);
  return res.json();
}

export async function updateRtmInterval(seconds: number): Promise<RtmIntervalResult> {
  const res = await fetch(`${BASE_URL}/scheduler/rtm-interval`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seconds }),
  });
  if (!res.ok) throw new Error(`failed to update RTM interval: ${res.status}`);
  return res.json();
}
