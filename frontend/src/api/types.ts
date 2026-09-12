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
