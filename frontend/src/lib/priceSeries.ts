import type { PricePoint } from "../api/types";

export interface MergedPricePoint {
  blockIndex: number;
  time: string;
  damPrice: number | null;
  rtmPrice: number | null;
}

const BLOCKS_PER_DAY = 96;
const BLOCK_MINUTES = 15;

function blockStartKey(index: number): string {
  const totalMinutes = index * BLOCK_MINUTES;
  const hh = String(Math.floor(totalMinutes / 60)).padStart(2, "0");
  const mm = String(totalMinutes % 60).padStart(2, "0");
  return `${hh}:${mm}:00`;
}

function toPriceMap(points: PricePoint[]): Map<string, number> {
  return new Map(points.map((p) => [p.block_start, Number(p.mcp_rs_per_mwh)]));
}

export function mergePriceSeries(damPrices: PricePoint[], rtmPrices: PricePoint[]): MergedPricePoint[] {
  const damMap = toPriceMap(damPrices);
  const rtmMap = toPriceMap(rtmPrices);

  return Array.from({ length: BLOCKS_PER_DAY }, (_, blockIndex) => {
    const key = blockStartKey(blockIndex);
    return {
      blockIndex,
      time: key.slice(0, 5),
      damPrice: damMap.get(key) ?? null,
      rtmPrice: rtmMap.get(key) ?? null,
    };
  });
}
