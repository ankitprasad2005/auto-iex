export interface ConsumptionRangeInput {
  start_time: string;
  end_time: string;
  predicted_kw: number;
}

export interface ScenarioOut {
  id: number;
  name: string;
}

export interface BlockComparison {
  block_index: number;
  predicted_kwh: number;
  dam_cost_rs: string | null;
  rtm_cost_rs: string | null;
  dam_pending: boolean;
  rtm_pending: boolean;
}

export interface ComparisonResult {
  blocks: BlockComparison[];
  dam_total_rs: string;
  rtm_total_rs: string;
  hybrid_total_rs: string;
  dam_pending_blocks: number;
  rtm_pending_blocks: number;
}

export interface ChainBlock {
  index: number;
  timestamp: string;
  payload: Record<string, unknown>;
  prev_hash: string;
  hash: string;
}

export type Market = "DAM" | "RTM";

export interface ScrapeResult {
  written: number;
  skipped_duplicate: boolean;
  chain_block_index: number | null;
}

export interface PricePoint {
  block_start: string;
  block_end: string;
  mcp_rs_per_mwh: string;
}

export interface SettlementPayload {
  scenario_id: number;
  range_id: number;
  date: string;
  start_minute: number;
  end_minute: number;
  predicted_kw: number;
  total_kwh: number;
  priced_kwh: number;
  cost_rs: number;
  markets_used: Market[];
  fully_priced: boolean;
  settled_at: string;
}

export interface SettlementBlock {
  index: number;
  timestamp: string;
  payload: SettlementPayload;
  prev_hash: string;
  hash: string;
}

export interface CheckLedgerResult {
  settled_count: number;
}
