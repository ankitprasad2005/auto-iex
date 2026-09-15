import { useState } from "react";
import type { MergedPricePoint } from "../lib/priceSeries";

interface Props {
  data: MergedPricePoint[];
}

// Palette validated with the dataviz skill's colorblind-safety script
// (OKLCH lightness band, CVD ΔE, contrast) for a 2-series categorical chart
// on the app's dark surface. Fixed assignment: DAM is always first/red,
// RTM is always second/blue — never swapped or reused for another series.
const DAM_COLOR = "#D71921";
const RTM_COLOR = "#3D7DD8";

const WIDTH = 960;
const HEIGHT = 300;
const PADDING = { top: 16, right: 16, bottom: 28, left: 56 };

function buildSegments(data: MergedPricePoint[], key: "damPrice" | "rtmPrice", xOf: (i: number) => number, yOf: (v: number) => number): string[] {
  const segments: string[] = [];
  let current: string[] = [];
  for (const point of data) {
    const value = point[key];
    if (value === null) {
      if (current.length > 1) segments.push(current.join(" "));
      current = [];
      continue;
    }
    current.push(`${xOf(point.blockIndex)},${yOf(value)}`);
  }
  if (current.length > 1) segments.push(current.join(" "));
  return segments;
}

function formatPrice(value: number | null): string {
  return value === null ? "PENDING" : value.toFixed(2);
}

export function PriceChart({ data }: Props) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const values = data.flatMap((p) => [p.damPrice, p.rtmPrice]).filter((v): v is number => v !== null);
  if (values.length === 0) {
    return (
      <p className="font-mono text-sm text-nd-text-secondary">
        No price data for this date yet — trigger a scrape or pick another date.
      </p>
    );
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const yRange = max - min || 1;

  const plotWidth = WIDTH - PADDING.left - PADDING.right;
  const plotHeight = HEIGHT - PADDING.top - PADDING.bottom;

  const xOf = (blockIndex: number) => PADDING.left + (blockIndex / (data.length - 1)) * plotWidth;
  const yOf = (value: number) => PADDING.top + plotHeight - ((value - min) / yRange) * plotHeight;

  const damSegments = buildSegments(data, "damPrice", xOf, yOf);
  const rtmSegments = buildSegments(data, "rtmPrice", xOf, yOf);

  const gridSteps = 4;
  const gridLines = Array.from({ length: gridSteps + 1 }, (_, i) => {
    const value = min + (yRange * i) / gridSteps;
    return { value, y: yOf(value) };
  });

  const xTickEvery = 16; // every 4 hours (16 * 15min blocks)
  const xTicks = data.filter((p) => p.blockIndex % xTickEvery === 0);

  function handleMouseMove(e: React.MouseEvent<SVGRectElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    const relativeX = e.clientX - rect.left;
    const fraction = Math.min(1, Math.max(0, relativeX / rect.width));
    const index = Math.round(fraction * (data.length - 1));
    setHoveredIndex(index);
  }

  const hovered = hoveredIndex !== null ? data[hoveredIndex] : null;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex gap-6">
        <span className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
          <span className="inline-block w-4 h-0.5" style={{ backgroundColor: DAM_COLOR }} aria-hidden="true" />
          DAM
        </span>
        <span className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-label text-nd-text-secondary">
          <span className="inline-block w-4 h-0.5" style={{ backgroundColor: RTM_COLOR }} aria-hidden="true" />
          RTM
        </span>
      </div>

      <div className="relative">
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full h-auto" role="img" aria-label="DAM and RTM price chart">
          {gridLines.map(({ value, y }) => (
            <g key={value}>
              <line x1={PADDING.left} y1={y} x2={WIDTH - PADDING.right} y2={y} stroke="#222222" strokeWidth={1} />
              <text x={PADDING.left - 8} y={y} textAnchor="end" dominantBaseline="middle" className="fill-nd-text-secondary" fontSize={10} fontFamily="monospace">
                {Math.round(value)}
              </text>
            </g>
          ))}

          {xTicks.map((p) => (
            <text
              key={p.blockIndex}
              x={xOf(p.blockIndex)}
              y={HEIGHT - 8}
              textAnchor="middle"
              className="fill-nd-text-secondary"
              fontSize={10}
              fontFamily="monospace"
            >
              {p.time}
            </text>
          ))}

          {damSegments.map((d, i) => (
            <polyline key={`dam-${i}`} points={d} fill="none" stroke={DAM_COLOR} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
          ))}
          {rtmSegments.map((d, i) => (
            <polyline key={`rtm-${i}`} points={d} fill="none" stroke={RTM_COLOR} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
          ))}

          {hovered && (
            <line
              x1={xOf(hovered.blockIndex)}
              y1={PADDING.top}
              x2={xOf(hovered.blockIndex)}
              y2={HEIGHT - PADDING.bottom}
              stroke="#333333"
              strokeWidth={1}
            />
          )}

          <rect
            data-testid="price-chart-overlay"
            x={PADDING.left}
            y={PADDING.top}
            width={plotWidth}
            height={plotHeight}
            fill="transparent"
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setHoveredIndex(null)}
          />
        </svg>

        {hovered && (
          <div
            data-testid="price-chart-tooltip"
            className="absolute top-0 right-0 bg-nd-surface border border-nd-border-visible px-3 py-2 font-mono text-xs text-nd-text-primary pointer-events-none"
          >
            <p className="text-nd-text-secondary">{hovered.time}</p>
            <p>
              <span style={{ color: DAM_COLOR }}>■</span> DAM {formatPrice(hovered.damPrice)}
            </p>
            <p>
              <span style={{ color: RTM_COLOR }}>■</span> RTM {formatPrice(hovered.rtmPrice)}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
